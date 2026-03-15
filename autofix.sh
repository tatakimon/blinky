#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: ./autofix.sh \"Your command here\" [UART_TOKEN]"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$ROOT_DIR/Dell_2_Steval"
DEBUG_DIR="$PROJECT_DIR/Debug"
MAIN_C="$PROJECT_DIR/Core/Src/main.c"
LINKER_SCRIPT="$PROJECT_DIR/STM32U585AIIXQ_FLASH.ld"
ELF_PATH="$DEBUG_DIR/Dell_2_Steval.elf"
BIN_PATH="/tmp/Dell_2_Steval.bin"
READBACK_PATH="/tmp/Dell_2_Steval.readback.bin"

TASK="$1"
UART_TOKEN="${2:-SoS}"
UART_TOKEN_SOURCE="${UART_TOKEN_SOURCE:-}"
if [ -z "$UART_TOKEN_SOURCE" ]; then
  UART_TOKEN_SOURCE="cli-arg"
  if [ $# -lt 2 ]; then
    UART_TOKEN_SOURCE="default"
  fi
fi
UART_BAUD="${UART_BAUD:-115200}"
UART_TIMEOUT="${UART_TIMEOUT:-8}"
UART_PORT="${UART_PORT:-}"
UART_PORT_SOURCE="env"
MAX_RETRIES="${MAX_RETRIES:-5}"
USE_SUDO_FLASH="${USE_SUDO_FLASH:-0}"
ENABLE_FLASH_READBACK_VERIFY="${ENABLE_FLASH_READBACK_VERIFY:-1}"
FLASH_RETRIES="${FLASH_RETRIES:-3}"
FLASH_RETRY_DELAY="${FLASH_RETRY_DELAY:-3}"
STLINK_PROBE_PATH="/tmp/stlink_probe.bin"

VERBOSE_LOG="$ROOT_DIR/verbose.log"
REPORT_DIR="$ROOT_DIR/logs"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_FILE="$REPORT_DIR/closed_loop_report_${TIMESTAMP}.md"
STRATEGY_LOG="$ROOT_DIR/strategy_log.txt"

mkdir -p "$REPORT_DIR"
: > "$VERBOSE_LOG"
: > "$STRATEGY_LOG"

append_report() {
  echo "$1" >> "$REPORT_FILE"
}

run_step() {
  local step="$1"
  shift
  local cmd="$*"
  {
    echo ""
    echo "[$(date -Iseconds)] STEP=$step"
    echo "CMD: $cmd"
    eval "$cmd"
  } >> "$VERBOSE_LOG" 2>&1
  return $?
}

last_reason() {
  tail -n 1 "$VERBOSE_LOG" | tr -d '\r'
}

log_tail() {
  tail -n 40 "$VERBOSE_LOG"
}

file_hash() {
  local f="$1"
  sha256sum "$f" | awk '{print $1}'
}

codex_tail() {
  tail -n 240 "$VERBOSE_LOG"
}

codex_soft_success() {
  codex_tail | grep -Eqi "No code change was necessary|already satisfies|already correctly implemented|Requested behavior is already|Build verification passed"
}

codex_infra_failure() {
  codex_tail | grep -Eqi "stream disconnected|Failed to shutdown rollout recorder|failed to queue rollout items: channel closed|failed to flush rollout recorder|failed to install system skills|failed to create shell snapshot"
}

is_no_stlink_error() {
  tail -n 120 "$VERBOSE_LOG" | grep -Eqi "Couldn't find any ST-Link devices|Found 0 stlink programmers|No ST-Link detected"
}

is_libusb_error() {
  tail -n 120 "$VERBOSE_LOG" | grep -Eqi "failed to init libusb context|libusb"
}

detect_uart_port() {
  python3 - <<'PY'
import glob
import os

byid = sorted(glob.glob("/dev/serial/by-id/*"))
if byid:
    print(os.path.realpath(byid[0]))
    raise SystemExit(0)

for candidate in ("/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1"):
    if os.path.exists(candidate):
        print(candidate)
        raise SystemExit(0)

print("")
PY
}

run_with_stlink_retry() {
  local step_prefix="$1"
  shift
  local cmd="$*"
  local t
  for ((t=1; t<=FLASH_RETRIES; t++)); do
    if run_step "${step_prefix}_try_${t}" "$cmd"; then
      return 0
    fi
    if is_no_stlink_error && [ "$t" -lt "$FLASH_RETRIES" ]; then
      echo "[$(date -Iseconds)] WARN ${step_prefix}: ST-Link not detected, retrying ${t}/${FLASH_RETRIES} after ${FLASH_RETRY_DELAY}s" >> "$VERBOSE_LOG"
      echo "    ↳ ST-Link not detected, retrying (${t}/${FLASH_RETRIES})..."
      sleep "$FLASH_RETRY_DELAY"
      continue
    fi
    return 1
  done
  return 1
}

require_tool() {
  local tool="$1"
  command -v "$tool" >/dev/null 2>&1 || {
    echo "Missing required tool: $tool"
    exit 2
  }
}

require_tool codex
require_tool arm-none-eabi-gcc
require_tool arm-none-eabi-objcopy
require_tool st-flash
require_tool python3
require_tool cmp
require_tool stat

if [ ! -f "$MAIN_C" ]; then
  echo "Missing main.c: $MAIN_C"
  exit 2
fi

if [ ! -f "$DEBUG_DIR/objects.list" ]; then
  echo "Missing objects.list: $DEBUG_DIR/objects.list"
  exit 2
fi

if [ ! -f "$LINKER_SCRIPT" ]; then
  echo "Missing linker script: $LINKER_SCRIPT"
  exit 2
fi

if [ -z "$UART_PORT" ]; then
  UART_PORT_SOURCE="auto-detect"
  UART_PORT="$(detect_uart_port)"
fi

echo "Effective UART token: $UART_TOKEN (source: $UART_TOKEN_SOURCE)"
echo "Effective UART port: ${UART_PORT:-<none>} (source: $UART_PORT_SOURCE)"
echo "Effective UART baud/timeout: ${UART_BAUD}/${UART_TIMEOUT}s"
echo "Flash readback verify: $ENABLE_FLASH_READBACK_VERIFY"
echo "Flash retries: $FLASH_RETRIES (delay ${FLASH_RETRY_DELAY}s)"
if [ "$UART_TOKEN_SOURCE" = "default" ]; then
  echo "WARN: UART token was not passed explicitly; using default '$UART_TOKEN'."
fi

if [ -z "$UART_PORT" ]; then
  echo "ERROR: No UART serial endpoint found. Checked /dev/serial/by-id and /dev/ttyACM*/ttyUSB*."
  echo "Set UART_PORT explicitly and retry."
  exit 2
fi

if [ ! -e "$UART_PORT" ]; then
  echo "ERROR: UART port '$UART_PORT' does not exist."
  echo "Set UART_PORT explicitly to a valid device and retry."
  exit 2
fi

if ! UART_OPEN_ERR="$(python3 - "$UART_PORT" <<'PY'
import os
import sys

path = sys.argv[1]
try:
    fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
    os.close(fd)
except Exception as exc:
    print(exc)
    raise SystemExit(1)
PY
)"; then
  echo "ERROR: UART port '$UART_PORT' is not accessible: $UART_OPEN_ERR"
  echo "Hint: check serial permissions/groups, device ownership, and whether another process has the port open."
  exit 2
fi

echo "Start task: $TASK" > "$STRATEGY_LOG"
echo "UART token: $UART_TOKEN" >> "$STRATEGY_LOG"
echo "UART token source: $UART_TOKEN_SOURCE" >> "$STRATEGY_LOG"
echo "UART port: $UART_PORT" >> "$STRATEGY_LOG"
echo "UART port source: $UART_PORT_SOURCE" >> "$STRATEGY_LOG"
echo "UART baud: $UART_BAUD" >> "$STRATEGY_LOG"
echo "UART timeout: $UART_TIMEOUT" >> "$STRATEGY_LOG"
echo "Max retries: $MAX_RETRIES" >> "$STRATEGY_LOG"

append_report "# Closed Loop Report"
append_report "- Date: $(date -Iseconds)"
append_report "- Task: $TASK"
append_report "- Main file: $MAIN_C"
append_report "- UART: $UART_PORT @ $UART_BAUD"
append_report "- UART token: $UART_TOKEN"
append_report "- UART token source: $UART_TOKEN_SOURCE"
append_report "- UART port source: $UART_PORT_SOURCE"
append_report "- Max tries: $MAX_RETRIES"
append_report "- Flash readback verify: $ENABLE_FLASH_READBACK_VERIFY"
append_report "- Flash retries: $FLASH_RETRIES (delay ${FLASH_RETRY_DELAY}s)"
append_report ""
append_report "## Attempt Summary"

FAILED_STAGE="none"
FAILED_REASON="none"
FAILED_TAIL="none"
SUCCESS=0

STLINK_PROBE_CMD="st-flash read '$STLINK_PROBE_PATH' 0x08000000 4"
STLINK_PROBE_RM_CMD="rm -f '$STLINK_PROBE_PATH'"
if [ "$USE_SUDO_FLASH" = "1" ]; then
  STLINK_PROBE_CMD="sudo $STLINK_PROBE_CMD"
  STLINK_PROBE_RM_CMD="sudo rm -f '$STLINK_PROBE_PATH'"
fi

echo "Running ST-LINK preflight probe..."
if ! run_with_stlink_retry "stlink_preflight" "$STLINK_PROBE_CMD"; then
  if is_no_stlink_error; then
    FAILED_REASON="ST-LINK preflight failed: device not detected (USB disconnected or in use)"
  elif is_libusb_error; then
    FAILED_REASON="ST-LINK preflight failed: libusb context unavailable"
  else
    FAILED_REASON="ST-LINK preflight failed: $(last_reason)"
  fi
  echo "ERROR: $FAILED_REASON"
  echo "Hint: attach ST-LINK USB, close competing tools, and verify host USB/libusb setup."
  append_report "- PRECHECK: FAIL ($FAILED_REASON)"
  append_report "- PRECHECK_HINT: attach ST-LINK and verify USB/libusb visibility before retrying."
  echo "FAILED | report=$REPORT_FILE"
  exit 2
fi
run_step "stlink_preflight_cleanup" "$STLINK_PROBE_RM_CMD" || true
append_report "- PRECHECK: OK (ST-LINK probe read succeeded)"

for ((i=1; i<=MAX_RETRIES; i++)); do
  ATTEMPT_PREFIX="TRY $i/$MAX_RETRIES"

  PROMPT_FILE="/tmp/codex_prompt_attempt_${i}.txt"
  cat > "$PROMPT_FILE" <<PROMPT
TASK:
$TASK

STRICT FILE RULES:
- Edit ONLY: $MAIN_C
- Edit ONLY inside STM32Cube user blocks:
  - /* USER CODE BEGIN ... */
  - /* USER CODE END ... */
- Do not edit any other files.
- Do not modify generated code outside user blocks.

HARDWARE RULES:
- Board: STM32U585 (STWIN.box)
- UART2: PD5/PD6, 115200
- Green LED: PH12 must keep blinking (heartbeat, SOS style is acceptable)
- Orange LED: PH10 should blink in Error_Handler failure loop
- UART output: print "$UART_TOKEN" every 1 second

LAST ATTEMPT FAILURE:
- Stage: $FAILED_STAGE
- Reason: $FAILED_REASON

LAST LOG TAIL:
$FAILED_TAIL

Apply minimal valid fix now.
PROMPT

  MAIN_HASH_BEFORE="$(file_hash "$MAIN_C")"
  if run_step "codex" "cat '$PROMPT_FILE' | codex exec --skip-git-repo-check --sandbox workspace-write -"; then
    CODEX_RC=0
  else
    CODEX_RC=$?
  fi
  MAIN_HASH_AFTER="$(file_hash "$MAIN_C")"

  if [ "$CODEX_RC" -ne 0 ]; then
    if [ "$MAIN_HASH_BEFORE" != "$MAIN_HASH_AFTER" ]; then
      echo "$ATTEMPT_PREFIX | codex=WARN | reason=nonzero exit but main.c changed; continuing"
      append_report "- $ATTEMPT_PREFIX: codex=WARN (nonzero exit but main.c changed; continuing)"
    elif codex_soft_success; then
      echo "$ATTEMPT_PREFIX | codex=WARN | reason=nonzero exit but codex reported success/no-change; continuing"
      append_report "- $ATTEMPT_PREFIX: codex=WARN (nonzero exit but codex reported success/no-change; continuing)"
    elif codex_infra_failure; then
      echo "$ATTEMPT_PREFIX | codex=WARN | reason=infrastructure/stream issue; continuing with current code"
      append_report "- $ATTEMPT_PREFIX: codex=WARN (infrastructure/stream issue; continuing with current code)"
    else
      FAILED_STAGE="codex"
      FAILED_REASON="$(last_reason)"
      FAILED_TAIL="$(log_tail)"
      echo "$ATTEMPT_PREFIX | codex=FAIL | reason=$FAILED_REASON"
      append_report "- $ATTEMPT_PREFIX: codex=FAIL ($FAILED_REASON)"
      continue
    fi
  fi

  if ! run_step "compile_main" "cd '$DEBUG_DIR' && mkdir -p Core/Src && arm-none-eabi-gcc ../Core/Src/main.c -mcpu=cortex-m33 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32U585xx -c -I../Core/Inc -I../Drivers/STM32U5xx_HAL_Driver/Inc -I../Drivers/STM32U5xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32U5xx/Include -I../Drivers/CMSIS/Include -O0 -ffunction-sections -fdata-sections -Wall --specs=nano.specs -mfpu=fpv5-sp-d16 -mfloat-abi=hard -mthumb -o ./Core/Src/main.o"; then
    FAILED_STAGE="compile_main"
    FAILED_REASON="$(last_reason)"
    FAILED_TAIL="$(log_tail)"
    echo "$ATTEMPT_PREFIX | build=FAIL:compile_main | reason=$FAILED_REASON"
    append_report "- $ATTEMPT_PREFIX: build=FAIL:compile_main ($FAILED_REASON)"
    continue
  fi

  if ! run_step "link" "cd '$DEBUG_DIR' && arm-none-eabi-gcc -o Dell_2_Steval.elf @objects.list -mcpu=cortex-m33 -T../STM32U585AIIXQ_FLASH.ld --specs=nosys.specs -Wl,-Map=Dell_2_Steval.map -Wl,--gc-sections -static --specs=nano.specs -mfpu=fpv5-sp-d16 -mfloat-abi=hard -mthumb -Wl,--start-group -lc -lm -Wl,--end-group"; then
    FAILED_STAGE="link"
    FAILED_REASON="$(last_reason)"
    FAILED_TAIL="$(log_tail)"
    echo "$ATTEMPT_PREFIX | build=FAIL:link | reason=$FAILED_REASON"
    append_report "- $ATTEMPT_PREFIX: build=FAIL:link ($FAILED_REASON)"
    continue
  fi

  if ! run_step "objcopy" "cd '$DEBUG_DIR' && arm-none-eabi-objcopy -O binary '$ELF_PATH' '$BIN_PATH'"; then
    FAILED_STAGE="objcopy"
    FAILED_REASON="$(last_reason)"
    FAILED_TAIL="$(log_tail)"
    echo "$ATTEMPT_PREFIX | build=FAIL:objcopy | reason=$FAILED_REASON"
    append_report "- $ATTEMPT_PREFIX: build=FAIL:objcopy ($FAILED_REASON)"
    continue
  fi

  FLASH_CMD="st-flash --reset write '$BIN_PATH' 0x08000000"
  FLASH_READ_CMD="st-flash read"
  FLASH_RM_CMD="rm -f '$READBACK_PATH'"
  if [ "$USE_SUDO_FLASH" = "1" ]; then
    FLASH_CMD="sudo $FLASH_CMD"
    FLASH_READ_CMD="sudo $FLASH_READ_CMD"
    FLASH_RM_CMD="sudo rm -f '$READBACK_PATH'"
  fi

  if ! run_with_stlink_retry "flash" "$FLASH_CMD"; then
    FAILED_STAGE="flash"
    FAILED_REASON="$(last_reason)"
    if is_no_stlink_error; then
      FAILED_REASON="ST-Link not detected (USB disconnected or in use by another app)"
    fi
    FAILED_TAIL="$(log_tail)"
    echo "$ATTEMPT_PREFIX | flash=FAIL | reason=$FAILED_REASON"
    append_report "- $ATTEMPT_PREFIX: flash=FAIL ($FAILED_REASON)"
    continue
  fi

  if [ "$ENABLE_FLASH_READBACK_VERIFY" = "1" ]; then
    BIN_SIZE="$(stat -c%s "$BIN_PATH")"
    # In sudo mode, previous readback may be root-owned under sticky /tmp.
    run_step "flash_readback_cleanup" "$FLASH_RM_CMD" || true
    if ! run_with_stlink_retry "flash_readback" "$FLASH_READ_CMD '$READBACK_PATH' 0x08000000 '$BIN_SIZE'"; then
      FAILED_STAGE="flash_readback"
      FAILED_REASON="$(last_reason)"
      if is_no_stlink_error; then
        FAILED_REASON="ST-Link not detected during readback (USB disconnected or in use by another app)"
      fi
      FAILED_TAIL="$(log_tail)"
      echo "$ATTEMPT_PREFIX | flash_verify=FAIL:readback | reason=$FAILED_REASON"
      append_report "- $ATTEMPT_PREFIX: flash_verify=FAIL:readback ($FAILED_REASON)"
      continue
    fi

    if [ "$USE_SUDO_FLASH" = "1" ]; then
      run_step "flash_readback_perms" "sudo chmod 644 '$READBACK_PATH'" || true
    fi

    if ! run_step "flash_compare" "cmp -n '$BIN_SIZE' -s '$BIN_PATH' '$READBACK_PATH'"; then
      FAILED_STAGE="flash_compare"
      FAILED_REASON="readback mismatch (flash content differs from built binary)"
      FAILED_TAIL="$(log_tail)"
      echo "$ATTEMPT_PREFIX | flash_verify=FAIL:compare | reason=$FAILED_REASON"
      append_report "- $ATTEMPT_PREFIX: flash_verify=FAIL:compare ($FAILED_REASON)"
      continue
    fi
  fi

  if ! run_step "uart_verify" "cd '$ROOT_DIR' && UART_PORT='$UART_PORT' UART_BAUD='$UART_BAUD' UART_TOKEN='$UART_TOKEN' UART_TIMEOUT='$UART_TIMEOUT' python3 test_runner.py"; then
    FAILED_STAGE="uart"
    FAILED_REASON="$(last_reason)"
    FAILED_TAIL="$(log_tail)"
    echo "$ATTEMPT_PREFIX | uart=FAIL | reason=$FAILED_REASON"
    append_report "- $ATTEMPT_PREFIX: uart=FAIL ($FAILED_REASON)"
    continue
  fi

  echo "$ATTEMPT_PREFIX | codex=OK build=OK flash=OK flash_verify=OK uart=OK"
  append_report "- $ATTEMPT_PREFIX: codex=OK build=OK flash=OK flash_verify=OK uart=OK"
  SUCCESS=1
  break
done

append_report ""
append_report "## Detailed Logs"
append_report "See: $VERBOSE_LOG"
append_report ""
append_report "### Last 200 lines"
append_report '```text'
tail -n 200 "$VERBOSE_LOG" >> "$REPORT_FILE"
append_report '```'

if [ "$SUCCESS" -eq 1 ]; then
  echo "SUCCESS | report=$REPORT_FILE"
  exit 0
fi

echo "FAILED | report=$REPORT_FILE"
exit 1
