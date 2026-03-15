#!/usr/bin/env python3
"""
Telegram bridge for STM32 closed-loop automation.

Modes:
- Command mode: /run always starts deployment flow.
- Natural mode: plain text is routed to either chat reply or run intent.
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT_DIR = Path(os.getenv("BOT_ROOT_DIR", "/home/kerem/stm32_sim_lab/blinky")).resolve()
DEPLOY_SH = ROOT_DIR / "deploy.sh"
OFFSET_FILE = Path(os.getenv("BOT_OFFSET_FILE", str(ROOT_DIR / "logs" / "telegram_bot.offset")))

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED_CHAT_IDS = {
    x.strip()
    for x in os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",")
    if x.strip()
}

DEFAULT_UART_TOKEN = os.getenv("BOT_DEFAULT_UART_TOKEN", "SoS")
MAX_RETRIES = os.getenv("BOT_MAX_RETRIES", "5")
USE_SUDO_FLASH = os.getenv("BOT_USE_SUDO_FLASH", "1")
ENABLE_FLASH_VERIFY = os.getenv("BOT_ENABLE_FLASH_READBACK_VERIFY", "1")
FLASH_RETRIES = os.getenv("BOT_FLASH_RETRIES", "3")
FLASH_RETRY_DELAY = os.getenv("BOT_FLASH_RETRY_DELAY", "3")
UART_BAUD = os.getenv("BOT_UART_BAUD", "115200")
UART_TIMEOUT = os.getenv("BOT_UART_TIMEOUT", "8")
UART_PORT = os.getenv("BOT_UART_PORT", "")
NATURAL_DIALOG_MODE = os.getenv("BOT_NATURAL_DIALOG_MODE", "1") == "1"

# Optional LLM middleware layer (MiniMax/OpenAI-compatible endpoint).
ENABLE_MINIMAX_LAYER = os.getenv("BOT_ENABLE_MINIMAX_LAYER", "0") == "1"
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "").strip()
MINIMAX_API_URL = os.getenv("MINIMAX_API_URL", "").strip()
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "").strip()
MINIMAX_TIMEOUT = int(os.getenv("MINIMAX_TIMEOUT", "45"))

STEVAL_MAIN_C = "Dell_2_Steval/Core/Src/main.c"
STEVAL_TASK_PREFIX = (
    "STM32U585AI (STWIN.box) strict rules: "
    f"edit only {STEVAL_MAIN_C} and only STM32Cube USER CODE blocks; "
    "do not modify MX_* calls, SystemClock_Config, or generated code; "
    "use existing USART2 setup (PD5/PD6, 115200), GREEN LED=PH12, ORANGE LED=PH10. "
)

CHAT_PATTERNS = [
    r"^(hi|hello|hey|yo|sup|what'?s up|good morning|good evening)\b",
    r"^\s*(thanks|thank you|ok|okay|cool|nice)\b",
]
RUN_PATTERNS = [
    r"\b(run|start|deploy|flash|compile|build|program)\b",
    r"\b(write|edit|update|fix|implement)\b.*\b(code|main\.c|uart|led)\b",
    r"\b(blink|uart|morse|error_handler)\b",
    r"\bstart.*system\b",
]


running_lock = threading.Lock()
running = False
running_task = ""
running_started = 0.0
running_proc: subprocess.Popen[str] | None = None


def build_strict_task(user_task: str) -> str:
    return f"{STEVAL_TASK_PREFIX}Request: {user_task.strip()}"


def is_chat_like(text: str) -> bool:
    low = text.strip().lower()
    return any(re.search(p, low) for p in CHAT_PATTERNS)


def is_run_like(text: str) -> bool:
    low = text.strip().lower()
    return any(re.search(p, low) for p in RUN_PATTERNS)


def tg_api(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def tg_send(chat_id: str, text: str) -> None:
    max_len = 3900
    chunks = [text[i : i + max_len] for i in range(0, len(text), max_len)] or [""]
    for chunk in chunks:
        try:
            tg_api(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": chunk,
                    "disable_web_page_preview": "true",
                },
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[bot] sendMessage failed: {exc}", file=sys.stderr)


def extract_llm_text(resp_json: dict[str, Any]) -> str:
    choices = resp_json.get("choices")
    if isinstance(choices, list) and choices:
        msg = choices[0].get("message", {})
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict) and isinstance(item.get("text"), str):
                        parts.append(item["text"])
                if parts:
                    return "\n".join(parts)
    for k in ("output_text", "text", "reply", "response"):
        v = resp_json.get(k)
        if isinstance(v, str):
            return v
    return json.dumps(resp_json, ensure_ascii=False)


def parse_json_from_text(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            obj = json.loads(text[start : end + 1])
            if isinstance(obj, dict):
                return obj
        except Exception:
            return None
    return None


def minimax_config_missing() -> list[str]:
    missing: list[str] = []
    if not MINIMAX_API_KEY:
        missing.append("MINIMAX_API_KEY")
    if not MINIMAX_API_URL:
        missing.append("MINIMAX_API_URL")
    if not MINIMAX_MODEL:
        missing.append("MINIMAX_MODEL")
    return missing


def minimax_request(messages: list[dict[str, str]], temperature: float = 0.1) -> tuple[dict[str, Any] | None, str | None]:
    if not ENABLE_MINIMAX_LAYER:
        return None, "disabled"
    missing = minimax_config_missing()
    if missing:
        return None, f"misconfigured (missing {', '.join(missing)})"

    payload = {
        "model": MINIMAX_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    req = urllib.request.Request(
        MINIMAX_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=MINIMAX_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        parsed = json.loads(raw)
        llm_text = extract_llm_text(parsed)
        obj = parse_json_from_text(llm_text)
        if not obj:
            return None, "invalid_json_response"
        return obj, None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def minimax_plan(task: str, uart_token: str) -> tuple[str, str, str]:
    strict_task = build_strict_task(task)
    system_prompt = (
        "You are a strict firmware planner for STM32U585AI STWIN.box closed-loop automation. "
        "Return ONLY JSON object with keys: "
        '{"task":"...", "uart_token":"...", "reason":"..."} '
        "Rules: preserve user intent exactly; do not generalize; do not change timing/strings/LED colors. "
        "Keep task concise and specific to STM32 firmware changes. "
        "If no explicit UART token requested, keep current token. "
        "Do not include markdown."
    )
    user_prompt = (
        f"Current UART token: {uart_token}\n"
        f"User request: {task}\n"
        f"Project constraints: {STEVAL_TASK_PREFIX}"
    )

    obj, err = minimax_request(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
    if err:
        if err == "disabled":
            return strict_task, uart_token, "disabled"
        if err.startswith("misconfigured"):
            return strict_task, uart_token, err
        return strict_task, uart_token, f"fallback ({err})"
    if not obj:
        return strict_task, uart_token, "fallback (planner response was not valid JSON)"

    # Keep user request stable; MiniMax may extract token/reason but should not rewrite task semantics.
    planned_task = strict_task
    planned_token = str(obj.get("uart_token", "")).strip() or uart_token
    reason = str(obj.get("reason", "")).strip()
    note = "ok"
    if reason:
        note += f": {reason[:160]}"
    return planned_task, planned_token, note


def local_dialog_route(text: str, default_token: str) -> dict[str, str]:
    t = text.strip()
    if is_run_like(t):
        return {
            "action": "run",
            "task": build_strict_task(t),
            "uart_token": default_token,
            "reason": "local_intent_run",
        }
    if is_chat_like(t):
        return {
            "action": "chat",
            "reply": "I am online. Send a firmware request or use /run to start the closed loop.",
            "reason": "local_intent_chat",
        }
    return {
        "action": "chat",
        "reply": "I can help. If you want firmware execution, describe the change or use /run.",
        "reason": "local_default_chat",
    }


def minimax_dialog_route(text: str, default_token: str) -> dict[str, str]:
    system_prompt = (
        "You route Telegram messages for STM32U585AI STWIN.box automation. "
        "Return ONLY JSON object with keys: "
        '{"action":"chat|run","reply":"...","task":"...","uart_token":"...","reason":"..."} '
        "Rules: casual messages like hello/hey/thanks must be action=chat. "
        "Firmware/code/build/flash requests must be action=run. "
        "For action=run, copy user request faithfully; do not generalize or broaden it. "
        "Do not change requested timing, strings, pins, or LED color intent. "
        "If no explicit UART token requested, keep the given default token."
    )
    user_prompt = f"Default UART token: {default_token}\nMessage: {text}"

    obj, err = minimax_request(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
    if err or not obj:
        local = local_dialog_route(text, default_token)
        local["reason"] = f"fallback_local ({err or 'invalid_json_response'})"
        return local

    action = str(obj.get("action", "")).strip().lower()
    if action not in {"chat", "run"}:
        action = "chat"
    reply = str(obj.get("reply", "")).strip()
    # Preserve original user request to avoid semantic drift from planner rewrites.
    task = text
    token = str(obj.get("uart_token", "")).strip() or default_token
    reason = str(obj.get("reason", "")).strip() or "ok"

    if action == "chat" and not reply:
        reply = "I am online. Send a firmware request when you want to start the closed loop."

    return {
        "action": action,
        "reply": reply,
        "task": build_strict_task(task) if action == "run" else task,
        "uart_token": token,
        "reason": reason,
    }


def route_natural_message(text: str, default_token: str) -> dict[str, str]:
    # Hard guardrail: never run on obvious greetings/acks even if LLM router misclassifies.
    if is_chat_like(text) and not is_run_like(text):
        return {
            "action": "chat",
            "reply": "I am online. Send firmware instructions when you want me to start.",
            "reason": "hard_chat_guard",
        }
    if ENABLE_MINIMAX_LAYER:
        return minimax_dialog_route(text, default_token)
    return local_dialog_route(text, default_token)


def tg_get_updates(offset: int | None) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {"timeout": 50}
    if offset is not None:
        payload["offset"] = offset
    try:
        out = tg_api("getUpdates", payload)
    except urllib.error.URLError as exc:
        print(f"[bot] network error: {exc}", file=sys.stderr)
        time.sleep(2)
        return []
    except Exception as exc:  # noqa: BLE001
        print(f"[bot] getUpdates failed: {exc}", file=sys.stderr)
        time.sleep(2)
        return []
    if not out.get("ok"):
        print(f"[bot] Telegram API error: {out}", file=sys.stderr)
        time.sleep(2)
        return []
    return out.get("result", [])


def load_offset() -> int | None:
    try:
        return int(OFFSET_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def save_offset(offset: int) -> None:
    OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_FILE.write_text(str(offset), encoding="utf-8")


def is_authorized(chat_id: str) -> bool:
    if not ALLOWED_CHAT_IDS:
        return False
    return str(chat_id) in ALLOWED_CHAT_IDS


def parse_run_payload(text: str) -> tuple[str, str]:
    msg = text.strip()
    payload = msg[4:].strip() if msg.startswith("/run") else msg

    token = DEFAULT_UART_TOKEN
    task = payload
    if "|" in payload:
        left, right = payload.split("|", 1)
        if left.strip():
            token = left.strip()
        task = right.strip()
    return token, task


def extract_report_summary(report_path: Path) -> str:
    if not report_path.exists():
        return f"report not found: {report_path}"
    text = report_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    out: list[str] = []
    capture = False
    for ln in lines:
        if ln.strip() == "## Attempt Summary":
            capture = True
            out.append(ln)
            continue
        if capture and ln.startswith("## "):
            break
        if capture:
            out.append(ln)
    if not out:
        out = lines[:30]
    return "\n".join(out).strip()


def run_deploy(
    chat_id: str,
    task: str,
    uart_token: str,
    *,
    preplanned: bool = False,
    planner_note_override: str = "",
) -> None:
    global running, running_task, running_started, running_proc
    with running_lock:
        if running:
            tg_send(chat_id, f"busy: another task is running\ncurrent: {running_task}")
            return
        running = True
        running_task = task
        running_started = time.time()

    try:
        if preplanned:
            planned_task = task if task.startswith("STM32U585AI (STWIN.box) strict rules:") else build_strict_task(task)
            planned_token = uart_token
            planner_note = planner_note_override or "router"
        else:
            planned_task, planned_token, planner_note = minimax_plan(task, uart_token)

        tg_send(
            chat_id,
            "started\n"
            f"token={planned_token}\n"
            f"task={planned_task}\n"
            f"max_retries={MAX_RETRIES}\n"
            f"planner=minimax ({planner_note})",
        )

        env = os.environ.copy()
        env["MAX_RETRIES"] = MAX_RETRIES
        env["USE_SUDO_FLASH"] = USE_SUDO_FLASH
        env["ENABLE_FLASH_READBACK_VERIFY"] = ENABLE_FLASH_VERIFY
        env["FLASH_RETRIES"] = FLASH_RETRIES
        env["FLASH_RETRY_DELAY"] = FLASH_RETRY_DELAY
        env["UART_BAUD"] = UART_BAUD
        env["UART_TIMEOUT"] = UART_TIMEOUT
        if UART_PORT:
            env["UART_PORT"] = UART_PORT

        cmd = [str(DEPLOY_SH), planned_task, planned_token]
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
            preexec_fn=os.setsid,
        )
        with running_lock:
            running_proc = proc

        report_path: Path | None = None
        one_line_re = re.compile(r"^(TRY \d+/\d+ \| .+|SUCCESS \| .+|FAILED \| .+)$")
        report_re = re.compile(r"report=(\S+)")

        assert proc.stdout is not None
        for raw in proc.stdout:
            line = raw.strip()
            if not line:
                continue
            m = report_re.search(line)
            if m:
                report_path = Path(m.group(1))
            if one_line_re.match(line):
                tg_send(chat_id, line)

        rc = proc.wait()
        status = "SUCCESS" if rc == 0 else "FAILED"
        final_msg = f"{status} (rc={rc})"
        if report_path:
            summary = extract_report_summary(report_path)
            final_msg += f"\nreport={report_path}\n\n{summary}"
        tg_send(chat_id, final_msg)
    except Exception as exc:  # noqa: BLE001
        tg_send(chat_id, f"bot error: {exc}")
    finally:
        with running_lock:
            running = False
            running_task = ""
            running_started = 0.0
            running_proc = None


def stop_current_run() -> tuple[bool, str]:
    global running_proc
    with running_lock:
        proc = running_proc
        is_running = running
    if not is_running or proc is None:
        return False, "idle"
    try:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            for _ in range(20):
                if proc.poll() is not None:
                    break
                time.sleep(0.1)
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
        return True, "stopped"
    except ProcessLookupError:
        return True, "already_stopped"
    except Exception as exc:  # noqa: BLE001
        return False, f"stop_failed: {exc}"


def handle_message(msg: dict[str, Any]) -> None:
    chat = msg.get("chat", {})
    chat_id = str(chat.get("id", ""))
    text = (msg.get("text") or "").strip()
    if not chat_id or not text:
        return

    if not is_authorized(chat_id):
        tg_send(chat_id, "unauthorized chat id")
        return

    if text.startswith("/start") or text.startswith("/help"):
        tg_send(
            chat_id,
            "commands:\n"
            "/run <task>\n"
            "/run <token>|<task>\n"
            "/status\n"
            "/stop\n"
            "/help\n\n"
            "natural mode: plain text is treated as chat unless it looks like a firmware request.",
        )
        return

    if text.startswith("/status"):
        with running_lock:
            if running:
                elapsed = int(time.time() - running_started)
                tg_send(chat_id, f"running ({elapsed}s)\ntask={running_task}")
            else:
                tg_send(chat_id, "idle")
        return

    if text.startswith("/stop"):
        ok, reason = stop_current_run()
        tg_send(chat_id, f"stop requested: {reason}" if ok else reason)
        return

    if text.startswith("/run"):
        token, task = parse_run_payload(text)
        if not task:
            tg_send(chat_id, "usage: /run <task> or /run <token>|<task>")
            return
        threading.Thread(target=run_deploy, args=(chat_id, task, token), daemon=True).start()
        return

    if NATURAL_DIALOG_MODE:
        route = route_natural_message(text, DEFAULT_UART_TOKEN)
        action = route.get("action", "chat")
        if action == "run":
            task = route.get("task", text)
            token = route.get("uart_token", DEFAULT_UART_TOKEN)
            note = f"router ({route.get('reason', 'n/a')})"
            threading.Thread(
                target=run_deploy,
                args=(chat_id, task, token),
                kwargs={"preplanned": True, "planner_note_override": note},
                daemon=True,
            ).start()
        else:
            reply = route.get("reply") or "I am online."
            tg_send(chat_id, reply)
        return

    token, task = parse_run_payload(text)
    if not task:
        tg_send(chat_id, "usage: /run <task> or /run <token>|<task>")
        return
    threading.Thread(target=run_deploy, args=(chat_id, task, token), daemon=True).start()


def main() -> int:
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN is required", file=sys.stderr)
        return 2
    if not ALLOWED_CHAT_IDS:
        print("TELEGRAM_ALLOWED_CHAT_IDS is required", file=sys.stderr)
        return 2
    if not DEPLOY_SH.exists():
        print(f"deploy script not found: {DEPLOY_SH}", file=sys.stderr)
        return 2

    print(f"[bot] root={ROOT_DIR}")
    print(f"[bot] offset_file={OFFSET_FILE}")
    print(f"[bot] allowed_chat_ids={','.join(sorted(ALLOWED_CHAT_IDS))}")
    print(f"[bot] natural_dialog_mode={NATURAL_DIALOG_MODE}")
    print(f"[bot] minimax_layer={ENABLE_MINIMAX_LAYER}")

    offset = load_offset()
    while True:
        updates = tg_get_updates(offset)
        for upd in updates:
            upd_id = upd.get("update_id")
            if isinstance(upd_id, int):
                offset = upd_id + 1
                save_offset(offset)
            msg = upd.get("message")
            if isinstance(msg, dict):
                handle_message(msg)
        time.sleep(0.2)


if __name__ == "__main__":
    raise SystemExit(main())
