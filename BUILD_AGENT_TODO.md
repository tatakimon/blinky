# BUILD_AGENT_TODO

Roadmap for Layer B only (future outer autonomous firmware-agent system).

## Core control plane
- [ ] Define persistent state model (task state, run history, evidence pointers).
- [ ] Define trusted baseline / LKG lifecycle (create, verify, freeze, restore, promote).
- [ ] Define isolated workspace/worktree flow for safe edits and diff capture.
- [ ] Define TaskSpec generation contract from user intent + constraints.

## Safety and execution gates
- [ ] Add explicit approval gate before any flash/program step.
- [ ] Add structured diagnostics and failure memory across attempts/sessions.
- [ ] Define commit/tag/promote flow for verified baselines.

## Interfaces
- [ ] Build messaging adapter with Telegram first.
- [ ] Keep adapter interface extensible for additional channels later.

## Integration boundary with Layer A
- [ ] Treat `deploy.sh` as current execution entrypoint.
- [ ] Keep `autofix.sh` and `test_runner.py` as inner-loop primitives unless explicitly replaced in a future migration step.
- [ ] Define when/how Layer B calls Layer A without changing Layer A behavior.
