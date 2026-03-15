

This repo has two concerns.
First, it stabilizes the current STM32 closed-loop firmware workflow already present in the repository.
Second, it serves as the foundation for a larger autonomous firmware agent that will eventually accept user requests, create isolated workspaces, apply guarded edits, build, flash, verify on hardware, and promote verified versions as the new trusted baseline.





# STM32U585 Closed-Loop Firmware Agent Lab

This repository is a controlled firmware-agent workspace for the **STWIN.box / STM32U585AI**.

The goal is to make firmware iteration safer, more reproducible, and easier to resume across sessions by combining:

- a constrained firmware editing workflow
- a repeatable build/flash/verify loop
- UART-based runtime verification
- persistent state files for continuity when chat context is lost

## Big Picture

Instead of treating firmware changes as isolated edits, this repo treats them as a closed loop:

1. define the current task clearly
2. constrain what may be changed
3. build the firmware
4. flash the board
5. verify real runtime behavior over UART
6. record the result
7. leave the repo in a state where the next session can continue safely

This is meant to reduce common failure modes such as:

- editing the wrong files
- breaking generated STM32Cube structure
- assuming build success means runtime success
- losing continuity between agent sessions
- not knowing what the next exact step should be

## Current Active Workflow

The current workflow is centered around:

- `deploy.sh` — main operator entrypoint
- `autofix.sh` — retry/orchestration loop
- `test_runner.py` — UART/runtime verification tool

Supporting structure:

- `Dell_2_Steval/` — active STM32 project
- `logs/` — reports and run artifacts
- `versions/` — historical baselines / snapshots
- `tools/` — helper or legacy scripts
- `AGENTS.md` — agent operating rules
- `TODO.md` — current task and next exact action
- `PROJECT_STATE.md` — verified state, risks, and current phase
- `LESSONS.md` — short reusable lessons learned
- `RUNBOOK.md` — operator-facing workflow guide
- `planning.md` — broader project plan

## Design Principles

### 1. Minimal-change discipline
Prefer improving the current workflow over replacing it.

### 2. Protect STM32 generated structure
Do not modify generated STM32 code outside `/* USER CODE BEGIN ... */` / `/* USER CODE END ... */` blocks unless explicitly required.

### 3. Runtime truth over compile-only confidence
A successful build is not enough. Runtime verification via UART is part of the baseline.

### 4. Continuation after context loss
Every meaningful session should leave behind enough state so a future agent can resume safely.

### 5. Evidence-first workflow
Logs, reports, and explicit pass/fail reasons matter more than optimistic assumptions.

## What This Repo Is For

This repo is for:

- stabilizing a firmware-agent development loop
- testing safe, minimal firmware modifications
- making hardware verification reproducible
- preserving operational continuity across agent sessions

This repo is not for:

- uncontrolled broad refactors
- parallel orchestration experiments during baseline stabilization
- arbitrary edits to generated STM32 project structure

## Current Phase

The project starts from **baseline stabilization**:

- align state/control files
- confirm the real operator flow
- verify the baseline with one fresh run
- only then improve scripts or add new firmware features

## Workflow Diagram

```mermaid
flowchart TD
    A[Operator gives task] --> B[Read state files first]
    B --> B1[TODO.md]
    B --> B2[PROJECT_STATE.md]
    B --> B3[LESSONS.md]
    B --> B4[planning.md]
    B --> B5[AGENTS.md]

    B5 --> C[deploy.sh]
    C --> D[autofix.sh retry loop]

    D --> E[Codex applies minimal patch]
    E --> F[Build / link / objcopy]
    F --> G[Flash with st-flash]
    G --> H[Optional flash readback verify]
    H --> I[test_runner.py UART verification]

    I --> J{Result}
    J -->|PASS| K[Write logs and report]
    J -->|FAIL| L[Capture failure reason]

    K --> M[Update TODO.md]
    K --> N[Update PROJECT_STATE.md]
    L --> M
    L --> N

    N --> O[Next Exact Action for next session]