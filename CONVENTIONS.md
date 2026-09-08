# Conventions

Format and naming rules. Schema files under `schema/` are authoritative for
data; this document governs everything else.

## Language

- Code, schemas, metadata, commit messages: **English**.
- Documentation: **English**, except `README.zh-CN.md` — the sole Chinese
  doorway.
- Stew blob bodies have **no language rule**: they may be any bytes.

## Identifiers

| Entity | Pattern | Issued by |
|---|---|---|
| Stew | `STW-` + 4 digits, zero-padded (`STW-0042`) | Keeper Bot at merge |
| Tasting | `TST-` + 4 digits, zero-padded (`TST-0007`) | Keeper Bot at merge |
| Generation | `gen-NNN`, zero-padded from 000 | Author (append-only) |
| Proposal dir | `<github-username>-<slug>` | Author |

IDs are immutable once assigned. Slug may be chosen by the cook (e.g.
`STW-0001-deepdish`), directory name mirrors it: `STW-0001-deepdish`.

## Stew directory layout

```
stews/<ID-slug>/
├── meta.yaml            # editable metadata (the ONLY editable file)
├── stew.gen-000.txt     # oldest snapshot
├── stew.gen-001.txt     # ...
└── ...                  # up to stew.gen-NNN.txt = current generation
```

`meta.yaml#content.file` points at the current generation and is the only
place that changes between generations. Historical blobs are never touched.

## Snapshot rules

- Files are named `stew.gen-NNN.txt`; the three-digit counter is
  append-only (`gen-000`, `gen-001`, …).
- Every snapshot's `sha256` appears in `meta.yaml` and is recomputed by CI.
- `lineage.generation` equals `number_of_snapshots - 1`, multi-parent
  hybrids include every parent in `lineage.parents`.

## status values

`seed | simmering | mature | retired | quarantined | sealed`

## Token budget

- Proposal `stew.txt` must be ≤64,000 tokens to avoid DoS-y submissions
  (configurable in `.github/workflows/validate-proposal.yml`).

## Metadata field etiquette

| Field | Who may write |
|---|---|
| Everything in `meta.yaml` except `benchmarks` | Curator (via proposal) |
| `benchmarks` block | Keeper Bot only (`summarize.py`) |
| `registry.yaml` `summary` | Keeper Bot only |
| `registry.yaml` `stews` list | Keeper Bot, verified by `validate.py` |

## Git practices

- Branch per proposal: `stew/<username>/<slug>` or `tasting/<username>/<tst-slug>`.
- Commit subject: `<scope>: <imperative summary>`.
- Squash-friendly: one logical change per commit; PRs are merged with a
  dedicated Keeper Bot commit that assigns the ID.

## Validation entrypoint

```bash
python tools/validate.py all
```

Must pass before merge and before any "definition of done" is claimed
(see [AGENTS.md](AGENTS.md)).