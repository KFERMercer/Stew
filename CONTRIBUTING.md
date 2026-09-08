# Contributing to Stew

Welcome to the pot. Anyone can cook, taste, or report poison. This document is
the mechanics; governance and permission details live in
[GOVERNANCE.md](GOVERNANCE.md), naming and format rules in
[CONVENTIONS.md](CONVENTIONS.md).

## Roles

| Role | Can do |
|---|---|
| **Cook** (anyone) | Submit a new stew, a new generation, or a hybrid via PR |
| **Taster** (anyone) | Submit an independent blind-test report via PR |
| **Keeper** (≥3 humans) | Merge proposals, assign STW-IDs, adjudicate seals |
| **Keeper Bot** (CI) | Schema/hash checks, registry summary, state promotion, poison screening |

## Ways to contribute

### 1. Taste (easiest)

Pick a simmering or mature stew in `stews/`, run a blind comparison, and file
a tasting report:

```bash
python tools/taste.py template stews/STW-0000-root-broth --model gpt-4o -o tastings/STW-0000/tst-my-first.yaml
```

1. Fill in `method`, `results`, and `notes`. Record both positive **and**
   negative deltas — honest failures teach the pot.
2. Validate locally: `python tools/validate.py tasting <file>`.
3. Open a PR. The report is accepted if the three bindings are present and
   internally consistent:
   - `stew_sha256` matches the stew's current blob,
   - `model` names the model under test,
   - `prompt_placement` states the injection location (`system` / `user` /
     `assistant-last`).

### 2. Fork a stew (cook a new generation)

A generation extends a parent's lineage with `cook-v1`:

1. Take a merged stew as parent and compress it further using protocol
   `cook-v1` (see [AGENTS.md](AGENTS.md) and `tools/cook.py`).
2. Keep the *complete* compression log — reproducibility is a merge
   requirement, not a preference.
3. File a proposal (below) with `kind: new-generation` and the parent's ID.

### 3. Start a new pot (submit a new stew)

Bring your own seed broth or fork the root seed and compress. File a proposal
with `kind: new-stew`.

### 4. Report poison

Move fast, flag first: open a "Poison report" issue (template in
`.github/ISSUE_TEMPLATE/poison-report.md`). Keepers can quarantine
immediately. Do **not** write about the garbled blob — describe observed
**behavior** (jailbreak, leakage, injection) and paste a reproducible excerpt.

## Proposal structure (PR-driven flow)

```
proposals/<username>-<slug>/
├── proposal.yaml       # kind / method / reproducibility
├── stew.txt            # proposed current-generation blob (>64k tokens → CI rejects)
└── self-tasting.yaml   # the author's own blind test (same schema as tastings)
```

`proposal.yaml` in brief:

```yaml
schema: "stew.proposal@1.0"
kind: new-generation            # new-stew | new-generation | hybrid
curator: "@you"
created_at: 2026-09-08T12:00:00Z
summary: "3 cook-v1 rounds on STW-0000; codegen +5.6pp"
method:
  protocol: cook-v1
  compressor: "compressor-model@v2"
  dataset: "anon-open-corpus@2026"
  reproducibility: true          # attach logs/compress.jsonl
attachments:
  stew: stew.txt
  self_tasting: self-tasting.yaml
  logs: logs/compress.jsonl      # only when reproducibility: true
```

## What the pipeline checks

| Gate | Check |
|---|---|
| CI · machine | Schema valid; `sha256` matches; token budget ≤64k; registry dedupe; poison screen (no probe triggers) |
| Keeper · human | Source legitimacy, privacy compliance, metadata honesty |

**Nobody reads the blob in review.** If a proposal is opaque gibberish, that
is not a defect — its self-tasting and lineage are the review surface.

## After merge

- Keeper Bot assigns the next `STW-` ID, moves the directory into `stews/`,
  sets `status: simmering`, and bumps `generated_at` in `registry.yaml`.
- The stew must spend ≥30 days in **simmering**; anyone may taste or fork it.

## Local validation

```bash
python tools/validate.py all                     # whole repo
python tools/validate.py proposal proposals/<user>-<slug>
python tools/validate.py tasting tastings/STW-0000/tst-my-first.yaml
python tools/summarize.py registry               # regenerate registry summary
```

## Commit message format

```
<scope>: <imperative summary>
```

Examples: `proposals: add STW-0002 candidate broth`,
`schema: tighten token_estimate`, `governance: clarify seal quorum`.

## Code of conduct

Be kind to tasters, honest about deltas, and generous with provenance. The
pot remembers everything.