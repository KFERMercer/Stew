#!/usr/bin/env python3
"""validate.py -- structural and integrity checks for the Stew pot.

Usage:
    python tools/validate.py all
    python tools/validate.py registry
    python tools/validate.py stew stews/STW-0000-root-broth
    python tools/validate.py proposal proposals/<user>-<slug>
    python tools/validate.py tasting tastings/STW-0000/tst-....yaml

Built-in structural checks make validation work with only `pyyaml` installed.
If `jsonschema` is available, the schema contracts under schema/ are also
applied for full conformance.

Exit code is 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("error: PyYAML is required (pip install pyyaml)\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schema"

STATUSES = {"seed", "simmering", "mature", "retired", "quarantined", "sealed"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GEN_RE = re.compile(r"^stew\.gen-(\d{3})\.txt$")

MAX_STEW_TOKENS = 64000


class Issues:
    """Collects (severity, message) pairs; helper for reporting."""

    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []

    def error(self, msg: str) -> None:
        self.items.append(("error", msg))

    def warn(self, msg: str) -> None:
        self.items.append(("warn", msg))

    def ok(self) -> bool:
        return not any(sev == "error" for sev, _ in self.items)

    def render(self) -> str:
        if not self.items:
            return "OK (no issues)"
        lines = []
        for sev, msg in self.items:
            lines.append(f"[{sev.upper():5}] {msg}")
        return "\n".join(lines)


def sha256_of(path: Path) -> str:
    """Return the lowercase hex sha256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict:
    """Load a YAML document; raise ValueError on parse errors."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {path}: {exc}") from exc


def try_load_schema(name: str):
    """Best-effort JSON Schema load; returns None when jsonschema is absent."""
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        return None
    path = SCHEMA_DIR / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def validate_against_schema(schema, instance, issues: Issues, label: str) -> None:
    """Apply JSON Schema when available; never fail on tooling absence."""
    if schema is None:
        return
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        location = ".".join(str(p) for p in err.path) or "<root>"
        issues.error(f"{label}: schema violation at {location}: {err.message}")
# ---------------------------------------------------------------------------
# Stew directory checks
# ---------------------------------------------------------------------------


def validate_stew_dir(stew_dir: Path, issues: Issues) -> None:
    """Validate one stews/<ID-slug>/ directory against metadata + invariants."""
    meta_path = stew_dir / "meta.yaml"
    if not meta_path.exists():
        issues.error(f"{stew_dir}: missing meta.yaml")
        return
    meta = load_yaml(meta_path)

    schema = try_load_schema("metadata.schema.json")
    validate_against_schema(schema, meta, issues, str(stew_dir))

    stew_id = meta.get("id", "?")
    label = f"{stew_id} ({stew_dir.name})"

    # -- status --
    status = meta.get("status")
    if status not in STATUSES:
        issues.error(f"{label}: unknown status {status!r}")

    # -- state_history --
    history = meta.get("state_history") or []
    if not history:
        issues.error(f"{label}: state_history must have at least one entry")
    last_to = None
    for entry in history:
        if "to" in entry:
            last_to = entry["to"]
    if last_to is not None and last_to != status:
        issues.error(
            f"{label}: state_history last 'to' ({last_to!r}) != status ({status!r})"
        )

    # -- content: immutable blob --
    content = meta.get("content") or {}
    blob_name = content.get("file")
    if not blob_name:
        issues.error(f"{label}: content.file is missing")
        return
    blob = stew_dir / blob_name
    if not blob.exists():
        issues.error(f"{label}: content.file {blob_name!r} does not exist")
        return
    recorded = content.get("sha256")
    actual = sha256_of(blob)
    if recorded != actual:
        issues.error(
            f"{label}: sha256 mismatch for {blob_name} "
            f"(recorded {recorded}, actual {actual})"
        )
    reported_bytes = content.get("bytes")
    if reported_bytes is not None and reported_bytes != blob.stat().st_size:
        issues.error(
            f"{label}: byte count mismatch ({reported_bytes} != {blob.stat().st_size})"
        )

    # -- lineage: append-only generation counters --
    lineage = meta.get("lineage") or {}
    snapshots = sorted(
        (GEN_RE.match(p.name) for p in stew_dir.glob("stew.gen-*.txt")),
        key=lambda m: int(m.group(1)),
    )
    gen_count = len(snapshots)
    declared_gen = lineage.get("generation")
    if declared_gen is None or declared_gen != gen_count - 1:
        issues.error(
            f"{label}: lineage.generation {declared_gen} != snapshot count - 1 "
            f"({gen_count - 1}); append-only rule violated or counter stale"
        )
    expected_names = [f"stew.gen-{i:03d}.txt" for i in range(gen_count)]
    actual_names = sorted(p.name for p in stew_dir.glob("stew.gen-*.txt"))
    if actual_names != expected_names:
        issues.error(f"{label}: snapshot names must be contiguous: {actual_names}")

    # -- root seed provenance (generations > 0 need parents) --
    if declared_gen and declared_gen > 0:
        parents = lineage.get("parents") or []
        if not parents:
            issues.error(
                f"{label}: generations > 0 must declare lineage.parents; "
                "hybrids list every parent"
            )
        root_seed = lineage.get("root_seed") or {}
        if not root_seed.get("source_type") or not root_seed.get("provenance_note"):
            issues.error(f"{label}: root_seed provenance must be documented")

    # -- safety screen sanity against status --
    safety = meta.get("safety") or {}
    screen = safety.get("screen")
    if status == "sealed" and screen != "sealed":
        issues.error(f"{label}: status is sealed but safety.screen is not")
def validate_registry(issues: Issues) -> None:
    """Verify registry.yaml matches the stews/ directory (by id + sha256)."""
    registry_path = REPO_ROOT / "registry.yaml"
    if not registry_path.exists():
        issues.error("registry.yaml is missing")
        return
    registry = load_yaml(registry_path)

    stew_path = REPO_ROOT / "stews"
    if not stew_path.exists():
        issues.error("stews/ directory is missing")
        return

    actual = {}
    for stew_dir in sorted(p for p in stew_path.iterdir() if p.is_dir()):
        meta_path = stew_dir / "meta.yaml"
        if not meta_path.exists():
            continue
        meta = load_yaml(meta_path)
        actual[meta.get("id")] = {
            "slug": meta.get("slug"),
            "status": meta.get("status"),
            "path": str(stew_dir.relative_to(REPO_ROOT)),
            "content_sha256": (meta.get("content") or {}).get("sha256"),
            "generation": (meta.get("lineage") or {}).get("generation"),
        }

    indexed = {}
    for entry in registry.get("stews", []):
        indexed[entry.get("id")] = entry

    for stew_id, meta in sorted(actual.items()):
        entry = indexed.get(stew_id)
        if entry is None:
            status_of = actual.get(stew_id, {}).get("status")
            if status_of != "sealed":
                issues.error(
                    f"registry: {stew_id} present in stews/ but missing from registry.yaml"
                )
            continue
        for key in ("slug", "status", "path", "content_sha256", "generation"):
            if entry.get(key) != meta.get(key):
                issues.error(
                    f"registry: {stew_id} {key} mismatch "
                    f"(registry {entry.get(key)!r} != meta {meta.get(key)!r})"
                )
    for stew_id, entry in sorted(indexed.items()):
        if stew_id not in actual:
            issues.error(f"registry: {stew_id} indexed but stews/ directory missing")
# ---------------------------------------------------------------------------
# Proposal & tasting checks
# ---------------------------------------------------------------------------


def validate_proposal_dir(prop_dir: Path, issues: Issues) -> None:
    """Validate a proposals/<user>-<slug>/ submission."""
    prop_yaml = prop_dir / "proposal.yaml"
    if not prop_yaml.exists():
        issues.error(f"{prop_dir}: missing proposal.yaml")
        return
    proposal = load_yaml(prop_yaml)
    schema = try_load_schema("proposal.schema.json")
    validate_against_schema(schema, proposal, issues, str(prop_dir))

    # token budget guard (DoS protection)
    stew_attachment = proposal.get("attachments", {}).get("stew")
    if stew_attachment:
        blob = prop_dir / stew_attachment
        if blob.exists() and blob.stat().st_size > MAX_STEW_TOKENS * 4:
            issues.error(
                f"{prop_dir}: {stew_attachment} exceeds the {MAX_STEW_TOKENS}-token "
                "budget guard (bytes-based heuristic)"
            )

    self_tasting = proposal.get("attachments", {}).get("self_tasting")
    if self_tasting:
        tasting_path = prop_dir / self_tasting
        if not tasting_path.exists():
            issues.error(f"{prop_dir}: attachment {self_tasting!r} missing")
        else:
            validate_tasting_file(tasting_path, issues)

    logs = proposal.get("attachments", {}).get("logs")
    if proposal.get("method", {}).get("reproducibility") and not logs:
        issues.error(f"{prop_dir}: method.reproducibility is true but no logs attached")

    # new-generation / hybrid proposals must reference a known parent stew
    kind = proposal.get("kind")
    if kind in ("new-generation", "hybrid"):
        issues.warn(
            f"{prop_dir}: verify lineage.parents references a merged STW-ID "
            "during Keeper review"
        )


def validate_tasting_file(path: Path, issues: Issues) -> None:
    """Validate a single tasting report with binding checks."""
    if not path.exists():
        issues.error(f"{path}: missing")
        return
    tasting = load_yaml(path)
    schema = try_load_schema("tasting.schema.json")
    validate_against_schema(schema, tasting, issues, str(path))

    label = str(path)
    sha = tasting.get("stew_sha256")
    if sha and SHA256_RE.match(sha) is None:
        issues.error(f"{label}: stew_sha256 is not a 64-char hex digest")
    if tasting.get("tasting_id") is None:
        issues.warn(f"{label}: tasting_id not yet assigned (expected for proposals)")

    # consistency: each result row must match its declared baseline/stew columns
    for row in tasting.get("results", []):
        if row.get("delta") is not None and (
            row.get("baseline") is not None and row.get("stew") is not None
        ):
            expect = round(row["stew"] - row["baseline"], 6)
            if row["delta"] is not None and round(row["delta"], 6) != expect:
                issues.error(
                    f"{label}: delta {row.get('delta')} != stew - baseline ({expect}) "
                    f"for task {row.get('task')!r}"
                )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="validate.py",
        description="Structural and integrity checks for the Stew pot.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        help="all | registry | stew | proposal | tasting",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="path relative to repo root (for stew|proposal|tasting)",
    )
    args = parser.parse_args(argv)

    issues = Issues()
    target = args.target

    if target == "all":
        validate_registry(issues)
        for stew_dir in sorted(p for p in (REPO_ROOT / "stews").iterdir() if p.is_dir()):
            validate_stew_dir(stew_dir, issues)
        prop_root = REPO_ROOT / "proposals"
        if prop_root.exists():
            for prop_dir in sorted(p for p in prop_root.iterdir() if p.is_dir()):
                validate_proposal_dir(prop_dir, issues)
        tasting_root = REPO_ROOT / "tastings"
        if tasting_root.exists():
            for tasting_path in sorted(p for p in tasting_root.rglob("*.yaml")):
                validate_tasting_file(tasting_path, issues)
    elif target == "registry":
        validate_registry(issues)
    else:
        # allow both `validate.py stew dir` and `validate.py "stew dir"`
        if args.path is None and " " in target:
            target, args.path = target.split(" ", 1)
        if target == "stew" and args.path:
            validate_stew_dir(REPO_ROOT / args.path, issues)
        elif target == "proposal" and args.path:
            validate_proposal_dir(REPO_ROOT / args.path, issues)
        elif target == "tasting" and args.path:
            validate_tasting_file(REPO_ROOT / args.path, issues)
        else:
            parser.error(f"unknown target {target!r}")

    print(issues.render())
    return 0 if issues.ok() else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))