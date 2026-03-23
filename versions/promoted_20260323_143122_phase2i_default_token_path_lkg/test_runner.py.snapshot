import os, sys, time, glob
import serial

def pick_port():
    # Prefer stable by-id links
    byid = sorted(glob.glob("/dev/serial/by-id/*"))
    if byid:
        return byid[0]
    for candidate in ("/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1"):
        if os.path.exists(candidate):
            return candidate
    return "/dev/ttyACM0"

PORT = os.getenv("UART_PORT", pick_port())
BAUD = int(os.getenv("UART_BAUD", "115200"))
TOKEN = os.getenv("UART_TOKEN", "STWINBX1_ON_LINE").encode("utf-8")
TIMEOUT = float(os.getenv("UART_TIMEOUT", "10"))
PORT_SOURCE = "env UART_PORT" if "UART_PORT" in os.environ else "auto-detect"
TOKEN_SOURCE = "env UART_TOKEN" if "UART_TOKEN" in os.environ else "default STWINBX1_ON_LINE"
BYID_PORTS = sorted(glob.glob("/dev/serial/by-id/*"))
TTY_PORTS = sorted(glob.glob("/dev/ttyACM*")) + sorted(glob.glob("/dev/ttyUSB*"))

print(f"[verify] port={PORT}")
print(f"[verify] port_source={PORT_SOURCE}")
print(f"[verify] baud={BAUD}")
print(f"[verify] token={TOKEN!r}")
print(f"[verify] token_source={TOKEN_SOURCE}")
print(f"[verify] timeout={TIMEOUT}s")

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.2)
except Exception as e:
    print(f"[verify] ❌ open failed: {e}")
    print(f"[verify] port_exists={os.path.exists(PORT)}")
    if BYID_PORTS:
        print(f"[verify] available_by_id={BYID_PORTS}")
    else:
        print("[verify] available_by_id=[]")
    if TTY_PORTS:
        print(f"[verify] available_tty={TTY_PORTS}")
    else:
        print("[verify] available_tty=[]")
    print("[verify] hint: set UART_PORT explicitly if auto-detect does not match your ST-LINK VCP device.")
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
