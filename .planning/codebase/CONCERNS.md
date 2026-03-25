# Concerns
## Authority Order
- In the trusted operational repo context, authority order is: `AGENTS.md`, `TODO.md`, `PROJECT_STATE.md`, `RUNBOOK.md`.
- Current phase, helper status, trusted baseline/LKG identity, token policy, and the next exact action must be taken from those root control files, not from this secondary codebase-map note.
- Current authoritative working repo context for this working copy is `/home/kerem/new_embedder_codex_app_gsd/blinky`.
- Earlier verified-host evidence from `~/stm32_sim_lab/blinky` remains historical audit lineage, not current repo authority for this working copy.
- If this file is read from another checkout such as `/home/kerem/copy/blinky`, treat that checkout as a non-authoritative analysis copy.


## Highest-Risk Concerns
- Repo-root ambiguity is a documentation risk unless docs distinguish the current authoritative working repo `/home/kerem/new_embedder_codex_app_gsd/blinky` from earlier historical evidence origin at `~/stm32_sim_lab/blinky` and from non-authoritative analysis copies such as `/home/kerem/copy/blinky`
- `tools/closed_loop_codex_verbose.py` is explicitly quarantined and currently fails `py_compile` with a `TabError` according to `TODO.md`, `PROJECT_STATE.md`, and `RUNBOOK.md`
- Layer A default-token behavior is aligned and proven for this working copy: `deploy.sh`, `autofix.sh`, and `test_runner.py` all use `STWINBX1_ON_LINE` as the current canonical baseline token path; `SoS` remains legacy historical context only
- Hardware success is host-specific and cannot be reproduced safely from a restricted agent session

## Repo Hygiene Issues
- The tree contains many `:Zone.Identifier` sidecar files, which add noise and can confuse file listings
- Generated build outputs such as `Dell_2_Steval/Debug/Dell_2_Steval.elf`, `.list`, and `.map` live alongside source
- Logs and attempt folders are extensive and committed in-tree, which raises the signal-to-noise ratio for discovery work
- There are duplicate orientation docs in `README.md` and `readme.md`

## Workflow Drift And Redundancy
- The trusted workflow is shell-based Layer A, but older or alternate flows remain in `tools/closed_loop_codex.py` and `tools/telegram_closed_loop_bot.py`
- `planning.md` and `BUILD_AGENT_TODO.md` describe a larger future system that is not yet the operational truth, so readers can confuse roadmap with implementation
- The hardcoded default bot root in `tools/telegram_closed_loop_bot.py` points to `/home/kerem/stm32_sim_lab/blinky`, which may drift from the current checkout location

## Dependency And Packaging Risks
- Python dependencies such as `pyserial` are used but not declared in a manifest
- Tool availability is assumed from the host shell, including `codex`, `arm-none-eabi-*`, and `st-flash`
- `.venv/` exists locally, but its contents are not a portable environment definition

## Firmware And Build Risks
- The enforced edit surface is intentionally tiny, which is good for safety but can make broader fixes awkward
- `Dell_2_Steval/Core/Src/main.c` includes both active firmware behavior and historical backup residue like `main.c.bak`
- The build directory is part of the working tree, so source-versus-output boundaries are blurred

## Testing And Evidence Risks
- There is no automated non-hardware regression suite
- Verification depends on USB visibility, UART access, serial permissions, and ST-LINK availability
- Because success claims are evidence-driven and host-specific, stale reports can be mistaken for current truth if control files are not kept current

## Recommended Follow-Up Areas
- Keep secondary descriptive docs aligned with the proven `STWINBX1_ON_LINE` default-token state and treat `SoS` as legacy historical context only
- Keep `tools/closed_loop_codex_verbose.py` documented as archival/non-primary unless a later controlled phase explicitly revives it
- Add a minimal dependency manifest for Python tooling
- Reduce repo noise from Windows metadata sidecars and committed transient artifacts
- Establish a clearer naming convention for promoted snapshots under `versions/`, which is already the next exact action in `TODO.md`
