#!/usr/bin/env python3
import os, re, sys, time, glob, shutil, subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
VERS = ROOT / "versions"
TOOLS = ROOT / "tools"

MAX_TRIES = int(os.getenv("MAX_TRIES", "5"))
UART_BAUD = int(os.getenv("UART_BAUD", "115200"))
UART_TOKEN = os.getenv("UART_TOKEN", "STWINBX1_ON_LINE").encode("utf-8") + b"\n"
UART_TIMEOUT = float(os.getenv("UART_TIMEOUT", "10"))
STLINK_SERIAL = os.getenv("STLINK_SERIAL", "").strip()

FORBIDDEN_FILES = {"Makefile", "linker.ld", "startup.s"}

def run(cmd, cwd=ROOT, inp=None):
    # Always work in text mode so stdout/stderr are strings (not bytes)
    if isinstance(inp, bytes):
        inp = inp.decode("utf-8", errors="ignore")
    p = subprocess.run(
        cmd,
        cwd=cwd,
        input=inp,
        text=True,
        capture_output=True
    )
    return p.returncode, p.stdout, p.stderr

def write_text(path: Path, s: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(s, encoding="utf-8", errors="ignore")

def copy_tree(files, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for f in files:
        src = ROOT / f
        if src.exists():
            shutil.copy2(src, dst / src.name)

def diff_patch(a: Path, b: Path) -> str:
    # Uses system diff if available, else minimal fallback
    rc, out, err = run(["bash","-lc", f"diff -u {a} {b} || true"])
    return out + err

def pick_uart_port():
    envp = os.getenv("UART_PORT", "").strip()
    if envp:
        return envp
    byid = sorted(glob.glob("/dev/serial/by-id/*"))
    if byid:
        return byid[0]
    return "/dev/ttyACM0"

def verify_uart(out_path: Path) -> bool:
    import serial

    port = pick_uart_port()
    lines = []
    lines.append(f"[verify] port={port}")
    lines.append(f"[verify] baud={UART_BAUD}")
    lines.append(f"[verify] token={UART_TOKEN!r}")
    lines.append(f"[verify] timeout={UART_TIMEOUT}s")

    try:
        ser = serial.Serial(port, UART_BAUD, timeout=0.2)
    except Exception as e:
        lines.append(f"[verify] ❌ open failed: {e}")
        write_text(out_path, "\n".join(lines) + "\n")
        return False

    deadline = time.time() + UART_TIMEOUT
    buf = b""
    try:
        while time.time() < deadline:
            chunk = ser.read(256)
            if chunk:
                buf += chunk
                if len(buf) > 4096:
                    buf = buf[-4096:]
                if UART_TOKEN in buf:
                    lines.append("[verify] ✅ SUCCESS (token seen)")
                    write_text(out_path, "\n".join(lines) + "\n")
                    return True
            time.sleep(0.05)

        lines.append(f"[verify] ❌ timeout; last bytes={buf[-32:]!r}")
        write_text(out_path, "\n".join(lines) + "\n")
        return False
    finally:
        try: ser.close()
        except: pass

def codex_available():
    rc, out, err = run(["bash","-lc","command -v codex >/dev/null 2>&1 && codex --version || true"])
    return ("codex" in out) or ("Codex" in out) or ("openai" in out)

def codex_exec_help():
    rc, out, err = run(["bash","-lc","codex exec --help || true"])
    return out + err

def run_codex(prompt: str, attempt_dir: Path) -> str:
    # Try to use --output-last-message if supported; otherwise capture stdout.
    help_txt = codex_exec_help()
    last_msg_path = attempt_dir / "codex_last_message.md"

    cmd = ["codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only"]
    use_output_last = ("--output-last-message" in help_txt)

    if use_output_last:
        cmd += ["--output-last-message", str(last_msg_path), "-"]
        rc, out, err = run(cmd, inp=prompt)
        write_text(attempt_dir / "codex_stdout.txt", out)
        write_text(attempt_dir / "codex_stderr.txt", err)
        if last_msg_path.exists():
            return last_msg_path.read_text(encoding="utf-8", errors="ignore")
        return out  # fallback
    else:
        cmd += ["-"]
        rc, out, err = run(cmd, inp=prompt)
        write_text(attempt_dir / "codex_stdout.txt", out)
        write_text(attempt_dir / "codex_stderr.txt", err)
        return out

def extract_main_c(reply: str) -> str:
    # Expect:
    # ===BEGIN_MAIN_C===
    # ... full file ...
    # ===END_MAIN_C===
    m = re.search(r"===BEGIN_MAIN_C===\s*(.*?)\s*===END_MAIN_C===", reply, re.S)
    if not m:
        return ""
    return m.group(1)

def forbidden_changed(pre_dir: Path, post_dir: Path) -> bool:
    for f in FORBIDDEN_FILES:
        a = pre_dir / f
        b = post_dir / f
        if a.exists() and b.exists():
            if a.read_bytes() != b.read_bytes():
                return True
    return False

def main():
    from pathlib import Path
    print(f"[info] runner={Path(__file__).resolve()}")
    LOGS.mkdir(parents=True, exist_ok=True)
    VERS.mkdir(parents=True, exist_ok=True)
    history = LOGS / "history.md"
    if not history.exists():
        write_text(history, "# Codex attempt history\n\n")

    print("[info] /dev/serial/by-id:")
    for p in sorted(glob.glob("/dev/serial/by-id/*")):
        print(f"  {p} -> {os.path.realpath(p)}")

    if not codex_available():
        print("[warn] codex CLI not found. The loop will still build/flash/verify, but cannot auto-fix.")
        print("       Install/auth codex, or export OPENAI_API_KEY for codex if supported.")
        # continue anyway

    tracked = ["main.c", "test_runner.py", "AGENTS.md", "Makefile", "linker.ld", "startup.s"]

    for i in range(1, MAX_TRIES + 1):
        attempt_dir = LOGS / f"attempt_{i:02d}"
        pre_dir = VERS / f"attempt_{i:02d}" / "pre"
        post_dir = VERS / f"attempt_{i:02d}" / "post"
        attempt_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n=== Attempt {i}/{MAX_TRIES} ===")

        # Snapshot pre
        copy_tree(tracked, pre_dir)

        # Step: build
        print("[step] build")
        rc, out, err = run(["bash","-lc","make clean && make"])
        write_text(attempt_dir / "build_stdout.txt", out)
        write_text(attempt_dir / "build_stderr.txt", err)
        if rc != 0:
            print("[result] BUILD FAIL")
            hypothesis = "Build failed (compiler/linker error)."
            change = "Ask Codex to return a corrected full main.c (no new headers, no touching Makefile/linker/startup)."
            # Codex prompt
            prompt = f"""You are fixing a bare-metal STM32U575/U585 project.

STRICT RULES:
- You may ONLY change main.c (do not modify Makefile/linker.ld/startup.s/test_runner.py).
- Do NOT add any new headers like stm32u5xx.h.
- Do NOT use __attribute__((constructor)) or HAL.
- Keep USART2 on PD5/PD6 AF7 @115200.
- The firmware must print the exact token repeatedly: "STWINBX1_ON_LINE\\n".
- Use LEDs: PH12 green heartbeat toggle; PH10 orange pulse on RX 'p' (optional).

Task:
Return a FULL replacement for main.c.

Format EXACTLY:
===BEGIN_MAIN_C===
<full file>
===END_MAIN_C===

Build error:
{err}
"""
            if codex_available():
                reply = run_codex(prompt, attempt_dir)
                write_text(attempt_dir / "codex_prompt.txt", prompt)
                write_text(attempt_dir / "codex_reply.txt", reply)
                new_main = extract_main_c(reply)
                if new_main:
                    (ROOT / "main.c").write_text(new_main, encoding="utf-8", errors="ignore")

            # Snapshot post + diff
            copy_tree(tracked, post_dir)
            write_text(attempt_dir / "diff.patch", diff_patch(pre_dir/"main.c", post_dir/"main.c"))

            # history
            with history.open("a", encoding="utf-8") as f:
                f.write(f"\n## Attempt {i}\nHYPOTHESIS: {hypothesis}\nCHANGE: {change}\nNEXT: Re-run build/flash/verify.\n")
		print(f"[summary] Attempt {i}: {hypothesis} | {change}") 
            continue

        # Step: flash
        print("[step] flash")
        flash_cmd = "st-flash "
        if STLINK_SERIAL:
            flash_cmd += f"--serial {STLINK_SERIAL} "
        flash_cmd += "--reset write firmware.bin 0x08000000"
        rc, out, err = run(["bash","-lc", flash_cmd])
        write_text(attempt_dir / "flash_stdout.txt", out)
        write_text(attempt_dir / "flash_stderr.txt", err)
        if rc != 0:
            print("[result] FLASH FAIL")
            with history.open("a", encoding="utf-8") as f:
                f.write(f"\n## Attempt {i}\nHYPOTHESIS: Flash failed (ST-LINK not reachable / permissions / USB attach).\nCHANGE: No code change; check USBIPD attach + udev.\nNEXT: Ensure lsusb shows STLINK-V3 and st-info --probe works.\n")
            # Snapshot post anyway
            copy_tree(tracked, post_dir)
            continue

        # Step: verify
        print("[step] verify (UART)")
        ok = verify_uart(attempt_dir / "verify.txt")
        if ok:
            print("[done] ✅ SUCCESS")
            copy_tree(tracked, post_dir)
            write_text(attempt_dir / "diff.patch", diff_patch(pre_dir/"main.c", post_dir/"main.c"))
            with history.open("a", encoding="utf-8") as f:
                f.write(f"\n## Attempt {i}\nHYPOTHESIS: Token present.\nCHANGE: None.\nNEXT: Done.\n")
            sys.exit(0)

        print("[result] VERIFY FAIL")
        # Ask Codex to adjust main.c (still only main.c)
        hypothesis = "No UART token observed (clock/baud/pins not actually driving ST-LINK VCP, or firmware not running)."
        change = "Ask Codex to return a corrected full main.c; prioritize: HSI16 on, USART2SEL=HSI16, PD5/PD6 AF7, token spam in loop."
        prompt = f"""You are fixing a bare-metal STM32U575/U585 project.

STRICT RULES:
- You may ONLY change main.c (do not modify Makefile/linker.ld/startup.s/test_runner.py).
- Do NOT add any new headers like stm32u5xx.h.
- Do NOT use __attribute__((constructor)) or HAL.
- Keep USART2 on PD5/PD6 AF7 @115200.
- The firmware must print the exact token repeatedly: "STWINBX1_ON_LINE\\n".
- Use LEDs: PH12 green heartbeat toggle; PH10 orange pulse on RX 'p' (optional).
- Make token appear even if host opens UART late (print in main loop, not only at boot).

Task:
Return a FULL replacement for main.c.

Format EXACTLY:
===BEGIN_MAIN_C===
<full file>
===END_MAIN_C===

Verification log:
{(attempt_dir/'verify.txt').read_text(encoding='utf-8', errors='ignore')}
"""
        if codex_available():
            reply = run_codex(prompt, attempt_dir)
            write_text(attempt_dir / "codex_prompt.txt", prompt)
            write_text(attempt_dir / "codex_reply.txt", reply)
            new_main = extract_main_c(reply)
            if new_main:
                (ROOT / "main.c").write_text(new_main, encoding="utf-8", errors="ignore")

        # Snapshot post + diff
        copy_tree(tracked, post_dir)
        write_text(attempt_dir / "diff.patch", diff_patch(pre_dir/"main.c", post_dir/"main.c"))

        with history.open("a", encoding="utf-8") as f:
            f.write(f"\n## Attempt {i}\nHYPOTHESIS: {hypothesis}\nCHANGE: {change}\nNEXT: Re-run build/flash/verify.\n")

    print("\n[done] ❌ Gave up after MAX_TRIES.")
    print("See logs/history.md and logs/attempt_XX/ + versions/attempt_XX/")
    sys.exit(1)

if __name__ == "__main__":
    main()
