#!/usr/bin/env python3
import sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
VERS = ROOT / "versions"

def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""

def extract_hyp_change(txt: str):
    hyp = ""
    chg = ""
    for line in txt.splitlines():
        if line.startswith("HYPOTHESIS:") and not hyp:
            hyp = line[len("HYPOTHESIS:"):].strip()
        if line.startswith("CHANGE:") and not chg:
            chg = line[len("CHANGE:"):].strip()
        if hyp and chg:
            break
    return hyp, chg

def changed_files_from_diff(diff_txt: str):
    files = []
    # supports diff -ruN output or unified diff headers
    for line in diff_txt.splitlines():
        if line.startswith("--- "):
            f = line[4:].strip().split("\t")[0]
            if f and f != "/dev/null":
                files.append(f)
    # normalize to just filenames
    norm = []
    for f in files:
        # diff may include pre/ post path
        norm.append(f.split("/")[-1])
    return sorted(set(norm))

def plus_minus(diff_txt: str):
    plus = minus = 0
    for line in diff_txt.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("+"):
            plus += 1
        elif line.startswith("-"):
            minus += 1
    return plus, minus

def main():
    if len(sys.argv) < 2:
        print("Usage: tools/attempt_summary.py <attempt_number>")
        sys.exit(2)

    n = int(sys.argv[1])
    att = LOGS / f"attempt_{n:02d}"
    ver = read_text(att / "verify.txt")
    diff_txt = read_text(att / "diff.patch")
    codex_txt = read_text(att / "codex_reply.txt") or read_text(att / "codex_stdout.txt")

    hyp, chg = extract_hyp_change(codex_txt)
    files = changed_files_from_diff(diff_txt)
    plus, minus = plus_minus(diff_txt)

    print(f"=== Attempt {n:02d} summary ===")
    if hyp: print(f"HYPOTHESIS: {hyp}")
    if chg: print(f"CHANGE:     {chg}")
    if files: print(f"FILES:      {', '.join(files)}")
    if diff_txt: print(f"DIFF:       +{plus} / -{minus} lines")
    print()

    if ver:
        print("[verify excerpt]")
        print("\n".join(ver.splitlines()[:25]))
        print()

    if diff_txt:
        print("[diff excerpt]")
        print("\n".join(diff_txt.splitlines()[:80]))

if __name__ == "__main__":
    main()
