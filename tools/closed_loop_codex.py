#!/usr/bin/env python3
import os, sys, time, glob, subprocess, textwrap, pathlib

MAX_TRIES = int(os.getenv("MAX_TRIES", "5"))
UART_BAUD = int(os.getenv("UART_BAUD", "115200"))
UART_TOKEN = os.getenv("UART_TOKEN", "STWINBX1_ON_LINE").encode()
UART_TIMEOUT = float(os.getenv("UART_TIMEOUT", "10"))
STLINK_SERIAL = os.getenv("STLINK_SERIAL", "")  # optional
FLASH_ADDR = os.getenv("FLASH_ADDR", "0x08000000")
BIN = os.getenv("FW_BIN", "firmware.bin")

CODEX = os.getenv("CODEX_CMD", "codex")
SCHEMATIC = os.getenv("SCHEMATIC_PATH", "docs/schematics.png")  # optional

LOGDIR = pathlib.Path("logs")
LOGDIR.mkdir(exist_ok=True)

def sh(cmd, timeout=None):
  return subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)

def pick_port():
  by_id = sorted(glob.glob("/dev/serial/by-id/*"))
  if by_id:
    return by_id[0]
  for p in ["/dev/ttyACM0","/dev/ttyACM1","/dev/ttyUSB0","/dev/ttyUSB1"]:
    if os.path.exists(p):
      return p
  return None

def uart_verify():
  import serial
  port = os.getenv("UART_PORT") or pick_port()
  if not port:
    return (2, "", "No UART port found. Set UART_PORT=/dev/ttyACM0 (or use /dev/serial/by-id).")

  out_lines = [f"[verify] port={port} baud={UART_BAUD} token={UART_TOKEN!r} timeout={UART_TIMEOUT}s"]
  buf = b""
  try:
    with serial.Serial(port, UART_BAUD, timeout=0.1) as ser:
      ser.reset_input_buffer()
      end = time.time() + UART_TIMEOUT
      while time.time() < end:
        chunk = ser.read(256)
        if chunk:
          buf += chunk
          if UART_TOKEN in buf:
            out_lines.append("[verify] ✅ token seen")
            return (0, "\n".join(out_lines), "")
        time.sleep(0.05)
  except Exception as e:
    return (3, "\n".join(out_lines), f"UART open/read failed: {e}")

  tail = buf[-300:]
  return (1, "\n".join(out_lines) + f"\n[verify] ❌ timeout. last bytes={tail!r}", "")

def flash():
  serial_flag = f'--serial "{STLINK_SERIAL}" ' if STLINK_SERIAL else ""
  cmd = f'st-flash {serial_flag}write "{BIN}" {FLASH_ADDR} && st-flash {serial_flag}reset'
  return sh(cmd, timeout=60)

def build():
  return sh("make clean && make", timeout=120)

def codex_fix(kind, log_text):
  # Attach schematic if present; otherwise proceed without.
  img_flag = ""
  if os.path.exists(SCHEMATIC):
    img_flag = f' --image "{SCHEMATIC}"'
  prompt = textwrap.dedent(f"""
  You are fixing a bare-metal STM32U575/U585 project (Cortex-M33) in this repo.

  HARD RULES:
  - UART must be USART2 on PD5=TX AF7 and PD6=RX AF7.
  - Baud must be 115200.
  - Firmware must print "STWINBX1_ON_LINE\\n" on boot.

  TASK:
  - Fix the repo so the closed-loop passes.
  - Closed-loop steps (performed externally): make clean && make ; st-flash write firmware.bin 0x08000000 ; UART listens for token.
  - You MUST limit yourself to at most 1 iteration of changes per call. Make the best fixes you can.

  FAILURE TYPE: {kind}

  LOGS:
  ----------------
  {log_text}
  ----------------
  """).strip()

  out_path = LOGDIR / "codex_last_message.txt"
  cmd = f'{CODEX} exec --sandbox workspace-write --ask-for-approval never --output-last-message "{out_path}"{img_flag} - << "PROMPT"\n{prompt}\nPROMPT'
  p = sh(cmd, timeout=600)
  return p, (out_path.read_text(errors="ignore") if out_path.exists() else "")

def main():
  # Ensure pyserial is available
  try:
    import serial  # noqa
  except Exception:
    print("Missing pyserial. Run: pip install pyserial", file=sys.stderr)
    return 10

  for attempt in range(1, MAX_TRIES + 1):
    print(f"\n=== Attempt {attempt}/{MAX_TRIES} ===")

    b = build()
    (LOGDIR / f"build_{attempt}.log").write_text((b.stdout or "") + "\n" + (b.stderr or ""), errors="ignore")
    if b.returncode != 0:
      print("[build] FAIL")
      p, final = codex_fix("BUILD_FAIL", (b.stdout or "") + "\n" + (b.stderr or ""))
      (LOGDIR / f"codex_build_{attempt}.log").write_text((p.stdout or "") + "\n" + (p.stderr or "") + "\n\n" + final, errors="ignore")
      continue

    f = flash()
    (LOGDIR / f"flash_{attempt}.log").write_text((f.stdout or "") + "\n" + (f.stderr or ""), errors="ignore")
    if f.returncode != 0:
      print("[flash] FAIL")
      p, final = codex_fix("FLASH_FAIL", (f.stdout or "") + "\n" + (f.stderr or ""))
      (LOGDIR / f"codex_flash_{attempt}.log").write_text((p.stdout or "") + "\n" + (p.stderr or "") + "\n\n" + final, errors="ignore")
      continue

    rc, vout, verr = uart_verify()
    (LOGDIR / f"verify_{attempt}.log").write_text(vout + "\n" + verr, errors="ignore")
    if rc == 0:
      print(vout)
      print("[done] ✅ Closed loop passed.")
      return 0

    print("[verify] FAIL (timeout/no token)")
    p, final = codex_fix("UART_VERIFY_FAIL", vout + "\n" + verr)
    (LOGDIR / f"codex_verify_{attempt}.log").write_text((p.stdout or "") + "\n" + (p.stderr or "") + "\n\n" + final, errors="ignore")

  print("\n[done] ❌ Gave up after MAX_TRIES.")
  return 1

if __name__ == "__main__":
  raise SystemExit(main())
