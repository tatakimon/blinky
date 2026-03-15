# Lessons Learned

1. Keep one workflow path: use `deploy.sh` -> `autofix.sh` -> `test_runner.py`; avoid parallel orchestration.
2. Treat build success and runtime success as separate checks; UART token verification is mandatory evidence.
3. Keep STM32 edits inside `USER CODE` blocks only unless explicitly approved otherwise.
4. Always preserve and reference concrete artifacts (`logs/closed_loop_report_*.md`, `verbose.log`) before claiming success.
5. Track token/port/baud explicitly every run; token mismatch can invalidate otherwise correct firmware behavior.
6. Keep `TODO.md` and `PROJECT_STATE.md` current after meaningful work to make handoff/restart safe.
7. Do a hardware visibility preflight (`/dev/serial/by-id`, `/dev/ttyACM*`) before baseline runs to avoid non-actionable loop attempts.
8. Document token precedence explicitly (CLI arg -> orchestrator env -> verifier) so fallback defaults cannot silently change verification intent.
9. Device visibility alone is not enough: treat `Permission denied` and `Found 0 stlink programmers` as separate host-access blockers that must be fixed before token conclusions.
10. If `sudo -n` is blocked by `no new privileges`, do not assume elevated probes are possible in-session; move validation to an unrestricted host shell.
