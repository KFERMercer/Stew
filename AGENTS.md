# AGENTS.md

> Orientation file for AI coding agents (and humans who like precision). Read
> this before touching the repository. The human-facing doorway is
> [README.zh-CN.md](README.zh-CN.md) (Chinese); this file is the canonical
> engineering contract. License: [MIT](https://github.com/KFERMercer/Stew/blob/main/LICENSE) (remote).

## Mission

**Stew** is a shared pot for *AI stew*: prompt artifacts that have been
compressed over many generations until they are no longer human-readable —
sometimes indistinguishable from gibberish — yet measurably improve model
performance.

Our core hypothesis is that repeated context compression strips away
human-centrically redundant syntax and semantics, leaving only the patterns
that genuinely resonate with a target model's token distribution. Once the
"must be human-readable" constraint is dropped, evolutionary search can find
solutions human authors would never write.

The pot is never emptied. Nothing is deleted; everything is either simmering,
retired, or sealed.

## Design principles (ACID)

| Letter | Word | Rule |
|---|---|---|
| **A** | **A**ppetizing | Effectiveness is measured, never read. No reviewer is ever asked to "read" a garbled stew; benchmarks speak, red-team probes speak. |
| **C** | **C**ulinary lineage | Lineage is append-only. Full ancestry is preserved; multi-parent "hybrid" stews are first-class. |
| **I** | **I**mmutable pot | Stew blobs are immutable (`stew.gen-NNN.txt`); statuses may change, blobs never do. Retire, never delete; quarantine and seal for poison. |
| **D** | **D**ocumented residue | The blob may be opaque; its metadata must be fully transparent, readable, auditable. |

## Repository layout

```
stew/
├── README.md                  # English doorway
├── README.zh-CN.md            # Chinese doorway
├── LICENSE                    # MIT license
├── AGENTS.md                  # This file
├── SKILL.md                   # Skill guide: search / use / contribute stew for agents
├── TODO.md                    # Roadmap: MCP server, agent-app plugins
├── CONTRIBUTING.md            # Community submission mechanics
├── GOVERNANCE.md              # Keeper powers, state machine, adjudication
├── CONVENTIONS.md             # IDs, naming, directories, commits
├── schema/                    # JSON Schema contracts (metadata/tasting/proposal)
├── registry.yaml              # Full-pot index (bot-summary + curated)
├── stews/                     # Merged stews, one directory each
│   └── STW-0000-root-broth/
│       ├── meta.yaml            # Editable metadata (only mutable file)
│       └── stew.gen-000.txt     # Immutable snapshot of the current generation
├── proposals/                 # PR staging area for community submissions
├── tastings/                  # Independent blind-test reports (anyone)
├── logs/                      # Cooker compression logs (reproducibility)
└── tools/                     # validate.py · cook.py · taste.py · summarize.py
```

Invariants enforced by the tooling:

1. **Blob immutability** — content files are append-only; `meta.yaml`'s
   `content.file` pointer moves forward, blobs never change.
2. **Lineage append-only** — a new generation adds snapshots; it never
   rewrites history.
3. **Content addressing** — every snapshot has a `sha256` recorded in
   metadata and verified by CI.
4. **Registry consistency** — `registry.yaml` must match the `stews/`
   directory, verified by `tools/validate.py all`.

## Data formats

All metadata is **YAML**, human-readable and diff-friendly. Authority rests
in `schema/*.json`; `tools/validate.py` embeds equivalent structural checks
so validation works without extra dependencies.

- **`meta.yaml`** (per-stew identity card): `status`, `content`
  (bytes/sha256/human_readable/visual_class), `lineage` (generation, parents,
  root_seed provenance), `benchmarks` (bot-maintained, do **not** hand-edit),
  `safety`, `legal`, `community`.
- **`tasting.yaml`** (blind-test report): must **bind** all three of
  `stew_sha256`, `model`, and `prompt_placement`. A tasting without these is
  meaningless for unreadable prompts.
- **`proposal.yaml`** (submission): `kind` ∈ {`new-stew`, `new-generation`,
  `hybrid`}, `method` (protocol `cook-v1`, compressor version, dataset),
  `reproducibility`.

## State machine

```
 (new) --PR--> seed --merge--> simmering
                               simmering --(maturity criteria met)--> mature
   mature / simmering --(superseded / failed)--> retired
   any --(poison report)--> quarantined --(cleared)--> resolved
   quarantined --(adjudicated / 2-3 vote)--> sealed
```

Statuses: `seed | simmering | mature | retired | quarantined | sealed`.
Maturity (all required): ≥7 independent tastings from ≥5 distinct tasters,
≥2 model families, significant positive delta on canonical task suites, no
unresolved safety flags. Sealing removes a stew from the registry index and
blocks future references; the blob remains in git history as evidence.

## Workflows & commands

```bash
# Validate the whole pot (this is what CI runs)
python tools/validate.py all

# Validate a single proposal directory
python tools/validate.py proposal proposals/<user>-<slug>

# Recompute root-seed checksum before filing a proposal
python tools/summarize.py sha256 stews/STW-0000-root-broth/stew.gen-000.txt

# Generate a tasting-report skeleton (edit it, then submit)
python tools/taste.py template stews/STW-0000-root-broth --model gpt-4o -o tasting.yaml

# Rebuild the registry summary block from stews/ metadata
python tools/summarize.py registry
```

## Conventions for AI agents

- **Language**: all code, schemas, metadata, and engineering docs in English.
  The only Chinese document is `README.zh-CN.md`.
- **IDs**: merged stews get `STW-` + zero-padded number (e.g. `STW-0042`);
  reviewed tastings get `TST-` + number. Never invent an ID yourself.
- **Never** modify a `stew.gen-NNN.txt` blob or an existing `meta.yaml`
  once merged. New generations, not edits.
- **Never** hand-edit the `benchmarks` block or `registry.yaml`'s
  `summary` — regenerate with `summarize.py`.
- **State transitions** are performed by Keeper Bot in CI or by Keeper
  humans; record every transition in `state_history` with `at/from/to/by/ref`.
- **Commit messages**: `<scope>: <imperative summary>` — e.g.
  `proposals: add STW-0002 candidate broth`, `schema: tighten token_estimate`.

## Definition of done for changes

A change is done when `python tools/validate.py all` passes,
`tools/summarize.py registry` produces no diff on `registry.yaml`,
and no English file was renamed or degraded to Chinese (and vice versa).
