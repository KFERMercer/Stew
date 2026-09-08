# 🍲 Stew

English | [中文](README.zh-CN.md)

> A perpetual stew, also known as forever soup, hunter's pot or hunter's stew, is a pot into which foodstuffs are placed and cooked, continuously. The pot is never or rarely emptied, and ingredients and liquid are replenished as necessary. Such foods can continue cooking for decades or longer if properly maintained. The concept is often a common element in descriptions of medieval inns. Foods prepared in a perpetual stew have been described as being flavourful due to the manner in which the ingredients blend together. Various ingredients can be used in a perpetual stew such as root vegetables, tubers (potatoes, yams, etc.) and various meats.

—— Wikipedia, [*Perpetual stew*](https://en.wikipedia.org/wiki/Perpetual_stew)

**Stew** is a repository dedicated to *AI stew*: prompt artifacts that started as ordinary instructions but, after **many rounds of context compression**, no longer look like anything human — sometimes indistinguishable from gibberish. Yet they share one property:

> **Inject this into the model, and it just performs better.**

That is the experiment. Repeated compression strips away task-irrelevant language and keeps only the patterns that genuinely resonate with a target model's token distribution. Once the "must be human-readable" constraint is dropped, evolutionary search can reach solutions human authors would never write.

This repository is the shared **pot** for such unreadable-but-effective artifacts: shareable, auditable, lineage-tracked. The stew itself may be opaque; everything around it must be crystal clear.

## Table of contents

- [🍲 Stew](#-stew)
  - [Table of contents](#table-of-contents)
  - [Why stews may work (even when garbled)](#why-stews-may-work-even-when-garbled)
  - [Design principles](#design-principles)
  - [Repository layout](#repository-layout)
  - [Data formats](#data-formats)
  - [State machine \& lifecycle](#state-machine--lifecycle)
  - [Community mechanics](#community-mechanics)
  - [Getting involved](#getting-involved)
  - [Command-line tools](#command-line-tools)
  - [Related Work](#related-work)
  - [License](#license)
  - [Inspiration](#inspiration)

## Why stews may work (even when garbled)

| Physical perpetual stew | AI stew in this pot |
|---|---|
| A pot that is never emptied | A prompt that is never "finalized", only iterated |
| Ingredients are continuously added and blended | Conversations, corrections, successes, failures are fed in |
| Ingredients fuse beyond recognition | Compression is irreversible: no single "ingredient" remains traceable |
| Flavor deepens; a new pot cannot replicate it | Gains from many generations are unreproducible by replaying the corpus |
| The pot has a history and a pedigree | Every generation's lineage is fully preserved |

Four non-exclusive mechanisms explain why a stew — which may look like gibberish after many compressions — can still outperform hand-written prompts:

1. **Information theory** — readability is human-centric redundancy. Repeated compression sheds syntax and semantics irrelevant to the target model's distribution, keeping only the highest-value triggers.
2. **Resonance tuning** — a compressed stew stops being an "instruction" and becomes a resonance profile for a specific model's latent space. It is **model-bound**: swap the model and it may do nothing — hence metadata must record the model.
3. **Search-space opening** — dropping the "human readable" constraint widens the search space enormously; evolutionary loops (compress ↔ evaluate) can reach solutions humans would never write.
4. **Emergence** — patterns that only appear after many generations cannot be explained by any single one, just as a stew's flavor cannot be inferred from any single day's ingredients.

In short, a stew is **carefully shaped entropy**, not random noise. Iterated compression and selection strip human-centric redundancy while retaining and densifying the token patterns that most reliably move the target model in the desired direction. What looks like gibberish to us is, to the model, a high-density, low-redundancy signal — the broth after impurities have been skimmed and the stock reduced to its essence.

The goal is blunt: **the stew must keep getting thicker.** The relationship between generations, compression rounds, and measured gains is the central statistical question this repository continuously produces.

## Design principles

Four letters to remember it — **ACID** (an homage, nothing to do with databases):

- **A — Appetizing (measurable)** — no one is ever asked to "read" garbled output to review it. Effectiveness is judged by blind tests; risk, by red-team probes. Measurement decides.
- **C — Culinary lineage (append-only)** — every compression generation is preserved as an immutable snapshot; multi-parent "hybrid" stews are first-class. The pot is never emptied.
- **I — Immutable pot** — stew blobs are append-only (`stew.gen-NNN.txt`); statuses may change, blobs never do. Retire, never delete; quarantine and seal for poison.
- **D — Documented residue (transparent metadata)** — the blob may be opaque, but everything around it — lineage, evaluations, compliance, tastings — must be fully readable and auditable.

## Repository layout

```
stew/
├── README.md                  # English doorway
├── README.zh-CN.md            # Chinese doorway
├── LICENSE                    # MIT license
├── AGENTS.md                  # Orientation for AI coding agents
├── SKILL.md                   # Agent skill guide: search / use / contribute
├── TODO.md                    # Roadmap (MCP server, agent-app plugins)
├── CONTRIBUTING.md            # Community submission mechanics
├── GOVERNANCE.md              # Keeper powers, state machine, adjudication
├── CONVENTIONS.md             # IDs, naming, directories, commits
├── schema/                    # JSON Schema contracts
│   ├── metadata.schema.json
│   ├── tasting.schema.json
│   └── proposal.schema.json
├── registry.yaml              # Full-pot index (bot summary + curated)
├── stews/                     # Merged stews, one directory each
│   └── STW-0000-root-broth/   # Example: the seed of the pot (generation 0)
│       ├── meta.yaml          # Editable metadata (the ONLY mutable file)
│       └── stew.gen-000.txt   # Immutable blob snapshot
├── proposals/                 # PR staging area for community submissions
├── tastings/                  # Independent blind-test reports (anyone)
├── logs/                      # Cooker compression logs (reproducibility)
└── tools/                     # validate.py · cook.py · taste.py · summarize.py
```

Core invariants: **blobs are immutable** (`stew.gen-NNN.txt` is append-only; `meta.yaml`'s `content.file` points at the current generation), **lineage is append-only** (multi-parent DAG supported), **content-addressed** (every `sha256` is CI-enforced).

## Data formats

The blob may be anything unreadable; **metadata must be YAML** — human-readable, diff-friendly — governed by contracts in `schema/*.json`.

- **`meta.yaml`** (a stew's identity card): status, content (bytes / sha256 / readability labels), lineage (generation, parents, root-seed provenance), benchmarks (bot-maintained), safety, legal, community.
- **`tasting.yaml`** (blind-test report): must **bind** `stew_sha256`, `model`, and `prompt_placement` — a tasting without these is meaningless for unreadable prompts; deltas honest in both directions.
- **`proposal.yaml`** (submission): `kind` ∈ {new-stew, new-generation, hybrid}, `method` (protocol `cook-v1`, compressor, dataset), `reproducibility`.

## State machine & lifecycle

```
                  submit PR               merge
  (new stew) ──────────► seed ─────────► simmering
                                             │  maturity criteria met
                                             ▼
  failed / superseded ◄── retired      mature
  poison report ──► quarantined ──► resolved (cleared) / sealed (2/3 vote)
```

- **Simmering**: ≥30 days minimum; open to tasting and forking.
- **Maturity** (all required): ≥7 independent tastings from ≥5 distinct tasters, ≥2 model families, significant positive delta on canonical task suites, no unresolved safety flags.
- **Retired ≠ deleted**: superseded stews are archived; ancestor snapshots stay in the pot forever.
- **Sealed**: the heaviest tool for confirmed poison — removed from the index, unreferenceable, but the blob stays in git history as evidence.

Full permission matrix and adjudication: [GOVERNANCE.md](GOVERNANCE.md).

## Community mechanics

| Role | Can do |
|---|---|
| **Cook** | anyone: submit a new stew / new generation / hybrid |
| **Taster** | anyone: run blind tests and submit `tasting.yaml` |
| **Keeper** (≥3 humans) | merge proposals, assign STW-IDs, adjudicate seals; structural change needs 2/3 |
| **Keeper Bot** | CI: validation, registry summary, state promotion, poison screening |

Submissions are PR-driven: put `stew.txt + proposal.yaml + self-tasting.yaml` in `proposals/<username>-<slug>/` and open a PR. CI gates machine-checks (schema, hashes, token budget, poison screen, dedupe); Keepers gate human-checks (source legitimacy, privacy compliance, metadata honesty). **Nobody reads the blob in review** — that's what blind tests are for.

Details: [CONTRIBUTING.md](CONTRIBUTING.md).

## Getting involved

- **Taste (easiest)** — pick a simmering or mature stew, run a blind test, submit a tasting per [CONTRIBUTING.md](CONTRIBUTING.md).
- **Fork** — take a stew as parent, run `cook-v1` protocol a few more generations, submit a new-generation proposal.
- **New pot** — bring your own seed broth or compress the root seed.
- **Report poison** — saw jailbreak / leakage / injection? Open a poison-report issue; Keepers can quarantine immediately.

Remember: **you never need to read the blob — only measure it.**

## Command-line tools

```bash
# Validate the whole pot (CI runs this too)
python tools/validate.py all

# Generate a local tasting-report skeleton (then edit and submit)
python tools/taste.py template stews/STW-0000-root-broth --model gpt-4o -o tasting.yaml

# Rebuild the full-pot index (checksums + summary)
python tools/summarize.py registry
```

See [AGENTS.md](AGENTS.md) and each tool's `--help` for more.

## Related Work

| # | Paper | Notes |
|---|---|---|
| 1 | [Prompt Compression for Large Language Models: A Survey](https://aclanthology.org/2025.naacl-long.368/) | Taxonomy of hard vs. soft compression that Stew inherits; frames Stew as *hard-filtering + evolutionary search* with content-addressed governance. |
| 2 | [Compressing Prompts for Accelerated Inference of Large Language Models](https://aclanthology.org/2023.emnlp-main.825/) (LLMLingua) | Hard-prompt filtering with a small LM estimating token perplexity/self-information;Stew's `cook-v1` demo compressor is the same family, but Stew drops readability and adds blind tasting. |
| 3 | [Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression](https://aclanthology.org/2024.findings-acl.57/) (LLMLingua-2) | Distillation-trained classifier for token keep/drop; shows task-agnostic hard compression can be learned — a drop-in `STEW_COMPRESSOR_CMD`. |
| 4 | [Learning to Compress Prompts with Gist Tokens](https://openreview.net/forum?id=2DtxPCL3T5) (GIST) | Soft-prompt: compresses a prompt into `\<gist\>` tokens; *gibberish yet effective* — the direct precedent for Stew's "resonance profile" claim and model-bound `tasting.yaml`. |
| 5 | [Generalized Prompt Compression for Large Language Models](https://arxiv.org/abs/2408.03094) (500xCompressor) | Encoder-decoder that compresses prompts into KV-memories up to 480× (500× name); proves extreme soft-compression is viable and must be evaluated by measurement, not reading — Stew's `A` principle. |
| 6 | [Optimizing generative AI by backpropagating language model feedback](https://www.nature.com/articles/s41586-025-08661-4) / [Automatic “Differentiation” via Text](https://arxiv.org/abs/2406.07496) (TextGrad) | Textual Gradient Descent (`TGD`): `loss.backward()` via LLM feedback; gives Stew a principled optimizer for the `compress ↔ evaluate` loop beyond demo truncation. |

## License

[MIT](https://github.com/KFERMercer/Stew/blob/main/LICENSE) (maintained on the remote repository). The pot serves everyone; everyone feeds the pot. A curator's name is ladled onto the lineage head and travels with it forever.

## Inspiration

The core idea for this repository is from [@joelhooks' post on X](https://x.com/joelhooks/status/2097173680795046087).
