#!/usr/bin/env python3
"""cook.py -- execute the cook-v1 compression protocol.

The proliferation of an AI stew is driven by compression rounds. Each round:

    1. sample K conversations: model + parent stew + task corpus -> outputs
    2. distill: compress(parent + successes + failures) -> candidate generation
    3. blind test: candidate vs parent on a held-out task suite
    4. accept if delta > 0 (or non-worse); otherwise discard the round

This module ships a pluggable, dependency-light skeleton. The default
"compressor" is a pure-Python, deterministic demonstration heuristic so the
pipeline can run end-to-end without an LLM API key. Wire REAL compressors by
setting STEW_COMPRESSOR_CMD (an external command reading the draft from
stdin and writing the compressed candidate to stdout).

Usage:
    python tools/cook.py --parent stews/STW-0000-root-broth --rounds 3 --dry-run
    python tools/cook.py stats stews/STW-0000-root-broth
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("error: PyYAML is required (pip install pyyaml)\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
PROTOCOL = "cook-v1"
DEFAULT_ROUNDS = 1


class StewError(Exception):
    pass


def load_meta(stew_dir: Path) -> dict:
    meta_path = stew_dir / "meta.yaml"
    if not meta_path.exists():
        raise StewError(f"{stew_dir}: no meta.yaml")
    with meta_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def current_blob(stew_dir: Path) -> Path:
    meta = load_meta(stew_dir)
    name = (meta.get("content") or {}).get("file")
    if not name:
        raise StewError(f"{stew_dir}: content.file missing")
    blob = stew_dir / name
    if not blob.exists():
        raise StewError(f"{stew_dir}: content.file {name!r} missing")
    return blob


def stats(stew_dir: Path) -> dict:
    blob = current_blob(stew_dir)
    meta = load_meta(stew_dir)
    return {
        "id": meta.get("id"),
        "slug": meta.get("slug"),
        "generation": (meta.get("lineage") or {}).get("generation"),
        "bytes": blob.stat().st_size,
        "lines": len(blob.read_text(encoding="utf-8").splitlines()),
        "snapshots": sorted(p.name for p in stew_dir.glob("stew.gen-*.txt")),
    }


def _default_compressor(draft: str) -> str:
    """Deterministic demo compressor: strip empty lines and collapse whitespace.

    This exists so the pipeline is runnable offline. It deliberately does NOT
    produce gibberish or improve quality. Replace it with a real LLM-backed
    compressor for actual use.
    """
    lines = []
    for raw in draft.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def _external_compressor(draft: str, cmd: str) -> str:
    proc = subprocess.run(
        cmd, shell=True, input=draft, capture_output=True, text=True, timeout=600
    )
    if proc.returncode != 0:
        raise StewError(f"STEW_COMPRESSOR_CMD failed: {proc.stderr[:400]}")
    return proc.stdout
def compress(draft: str, dry_run: bool) -> str:
    cmd = os.environ.get("STEW_COMPRESSOR_CMD") if not dry_run else None
    if cmd:
        return _external_compressor(draft, cmd)
    return _default_compressor(draft)


def run_cook(parent_dir: Path, rounds: int, dry_run: bool) -> Path:
    if not parent_dir.exists():
        raise StewError(f"{parent_dir}: does not exist")
    meta = load_meta(parent_dir)
    parent_id = meta.get("id")
    if not parent_id:
        raise StewError(f"{parent_dir}: meta.yaml missing id")
    if meta.get("status") not in ("seed", "simmering", "mature"):
        raise StewError(f"{parent_id}: cannot cook from status {meta.get('status')!r}")

    gen = (meta.get("lineage") or {}).get("generation", 0)
    draft = current_blob(parent_dir).read_text(encoding="utf-8")
    compressor_kind = "external" if os.environ.get("STEW_COMPRESSOR_CMD") else "demo"

    for i in range(1, rounds + 1):
        candidate = compress(draft, dry_run)
        out_name = f"stew.gen-{gen + i:03d}.txt"
        out_path = parent_dir / out_name
        if dry_run:
            print(
                f"[cook-v1] round {i}/{rounds} -> {out_name} "
                f"({len(candidate)} chars, {compressor_kind} compressor)"
            )
        else:
            if out_path.exists():
                raise StewError(f"{out_path} already exists; append-only rule")
            out_path.write_text(candidate + "\n", encoding="utf-8")
            print(f"[cook-v1] wrote {out_path}")
        draft = candidate  # next round distills the candidate

    print(
        f"[cook-v1] complete: {rounds} distilled round(s) from {parent_id} "
        f"(gen {gen} -> gen {gen + rounds})"
    )
    if dry_run:
        print(
            "[cook-v1] dry-run: no files written. Drop --dry-run AFTER wiring a real "
            "compressor; then file a proposal with logs/."
        )
    return parent_dir


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="cook.py", description=PROTOCOL + " protocol runner")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run compression rounds on a stew")
    run.add_argument("--parent", required=True, help="path to a stews/STW-XXXX-slug dir")
    run.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    run.add_argument("--dry-run", action="store_true", help="compute only, write nothing")
    st = sub.add_parser("stats", help="show quick stats for a stew")
    st.add_argument("stew", help="path to a stews/STW-XXXX-slug dir")
    args = parser.parse_args(argv)

    if args.command == "stats":
        print(json.dumps(stats(Path(args.stew)), indent=2, ensure_ascii=False))
        return 0
    run_cook(Path(args.parent), args.rounds, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))