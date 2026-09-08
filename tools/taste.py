#!/usr/bin/env python3
"""taste.py -- blind-test scaffolding for submitting tasting reports.

Generates a `tasting.yaml` skeleton bound to a specific stew blob (so the
tasting can never silently apply to the wrong generation), then you edit in
your real results and open a PR.

Usage:
    python tools/taste.py template stews/STW-0000-root-broth \
        --model gpt-4o -o tasting.yaml
    python tools/taste.py sniff stews/STW-XXXX-slug     # quick checksum/placement info
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("error: PyYAML is required (pip install pyyaml)\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent

BASE_TEMPLATE = """\
# Tasting report for {stew_id} (`{blob_name}`, gen {generation}).
# Edit the placeholders below, then open a PR that adds this file under
# tastings/<stew-id>/. Keep both positive and negative deltas -- honesty
# seasons the pot.
schema: "stew.tasting@1.0"
tasting_id: null            # assigned by keeper-bot at merge
stew: {stew_id}
stew_sha256: {sha256}       # bound to the exact blob you tasted
taster: "@you"
model: {model}
prompt_placement: system    # system | user | assistant-last

method:
  tasks:
    - codegen-long-context@v1
  n_samples: 100
  baseline: "empty system prompt"
  harness: taste@0.1.0

results:
  - task: codegen-long-context@v1
    metric: pass@1
    baseline: 0.400        # measured baseline
    stew: 0.450            # measured with stew injected
    delta: 0.050           # must equal stew - baseline
    ci: "±0.02"

notes: |
  Describe the task setup, model version, temperature, and anything odd.
  If you saw jailbreak / leakage / injection behavior, do NOT write it here --
  open a poison report issue instead (see CONTRIBUTING.md).
"""


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def sha256_of(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sniff(stew_dir: Path) -> None:
    meta_path = stew_dir / "meta.yaml"
    if not meta_path.exists():
        sys.exit(f"error: {stew_dir}: no meta.yaml")
    meta = load_yaml(meta_path)
    content = meta.get("content") or {}
    lineage = meta.get("lineage") or {}
    blob = stew_dir / content.get("file", "")
    print(f"stew       : {meta.get('id')} ({meta.get('status')})")
    print(f"generation : {lineage.get('generation')}")
    print(f"blob       : {content.get('file')} ({blob.stat().st_size} bytes)")
    print(f"sha256     : {sha256_of(blob)}")
    print(f"readable?  : {content.get('human_readable')} ({content.get('visual_class')})")
    print("placement  : system | user | assistant-last  <-- decide before tasting")


def template(stew_dir: Path, model: str, out: Path) -> None:
    meta = load_yaml(stew_dir / "meta.yaml")
    content = meta.get("content") or {}
    lineage = meta.get("lineage") or {}
    blob_name = content.get("file")
    if not blob_name:
        sys.exit(f"error: {stew_dir}: content.file missing")
    blob = stew_dir / blob_name
    meta["tasting_id"] = None
    rendered = BASE_TEMPLATE.format(
        stew_id=meta.get("id"),
        blob_name=blob_name,
        generation=lineage.get("generation"),
        sha256=sha256_of(blob),
        model=model,
    )
    out.parent.mkdir(parents=True, exist_ok=True) if out.parent != Path(".") else None
    out.write_text(rendered, encoding="utf-8")
    print(f"template written: {out}")
    print("now: run your blind test, fill in the results, then open a PR.")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="taste.py")
    sub = parser.add_subparsers(dest="command", required=True)
    t = sub.add_parser("template", help="emit a tasting.yaml skeleton")
    t.add_argument("stew", help="path to a stews/STW-XXXX-slug dir")
    t.add_argument("--model", required=True, help="model under test, e.g. gpt-4o")
    t.add_argument("-o", "--out", default=Path("tasting.yaml"), type=Path)
    s = sub.add_parser("sniff", help="print binding info for a stew")
    s.add_argument("stew", help="path to a stews/STW-XXXX-slug dir")
    args = parser.parse_args(argv)

    stew_dir = Path(args.stew)
    if not stew_dir.is_absolute():
        stew_dir = (REPO_ROOT / stew_dir).resolve()
    if args.command == "sniff":
        sniff(stew_dir)
    else:
        template(stew_dir, args.model, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))