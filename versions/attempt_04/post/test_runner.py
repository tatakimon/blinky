import os, sys, time, glob
import serial

def pick_port():
    # Prefer stable by-id links
    byid = sorted(glob.glob("/dev/serial/by-id/*"))
    if byid:
        return byid[0]
    return "/dev/ttyACM0"

PORT = os.getenv("UART_PORT", pick_port())
BAUD = int(os.getenv("UART_BAUD", "115200"))
TOKEN = os.getenv("UART_TOKEN", "STWINBX1_ON_LINE").encode("utf-8")
TIMEOUT = float(os.getenv("UART_TIMEOUT", "10"))

print(f"[verify] port={PORT}")
print(f"[verify] baud={BAUD}")
print(f"[verify] token={TOKEN!r}")
print(f"[verify] timeout={TIMEOUT}s")

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.2)
except Exception as e:
    print(f"[verify] ❌ open failed: {e}")
    sys.exit(2)

deadline = time.time() + TIMEOUT
buf = b""

try:
    while time.time() < deadline:
        chunk = ser.read(256)
        if chunk:
            buf += chunk
            # Keep buffer bounded
            if len(buf) > 4096:
                buf = buf[-4096:]
            if TOKEN in buf:
                print("[verify] ✅ SUCCESS (token seen)")
                sys.exit(0)
        time.sleep(0.05)

    print(f"[verify] ❌ timeout; last bytes={buf[-32:]!r}")
    sys.exit(1)
finally:
    try:
        ser.close()
    except:
        pass
