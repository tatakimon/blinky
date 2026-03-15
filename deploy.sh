#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: ./deploy.sh \"Your command here\" [UART_TOKEN]"
  echo "Env options:"
  echo "  MAX_RETRIES=5 USE_SUDO_FLASH=0 ENABLE_FLASH_READBACK_VERIFY=1 FLASH_RETRIES=3 FLASH_RETRY_DELAY=3 UART_BAUD=115200 UART_TIMEOUT=8 UART_PORT=/dev/ttyACM0"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
TASK="$1"
UART_TOKEN="${2:-SoS}"
UART_TOKEN_SOURCE="cli-arg"
if [ $# -lt 2 ]; then
  UART_TOKEN_SOURCE="default"
fi
MAX_RETRIES="${MAX_RETRIES:-5}"
UART_BAUD="${UART_BAUD:-115200}"
UART_TIMEOUT="${UART_TIMEOUT:-8}"
UART_PORT_DISPLAY="${UART_PORT:-auto-detect}"

echo "Task: $TASK"
echo "UART token: $UART_TOKEN (source: $UART_TOKEN_SOURCE)"
echo "UART baud: $UART_BAUD"
echo "UART timeout: ${UART_TIMEOUT}s"
echo "UART port: $UART_PORT_DISPLAY"
echo "Max retries: $MAX_RETRIES"
echo "Flash readback verify: ${ENABLE_FLASH_READBACK_VERIFY:-1}"
echo "Flash retries: ${FLASH_RETRIES:-3} (delay ${FLASH_RETRY_DELAY:-3}s)"
if [ "$UART_TOKEN_SOURCE" = "default" ]; then
  echo "WARN: UART_TOKEN not provided; using default token '$UART_TOKEN'. Pass token explicitly for baseline runs."
fi

cd "$ROOT_DIR"
UART_TOKEN_SOURCE="$UART_TOKEN_SOURCE" ./autofix.sh "$TASK" "$UART_TOKEN"
