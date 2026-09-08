# SKILL.md

> Skill guide for AI agents (and humans who think in automation) on how to
> **search**, **use**, and **contribute** to the Stew pot.

The pot holds *AI stew*: prompt artifacts that are unreadable but measured.
You will never be asked to understand a blob — only to find it, verify it,
inject it, measure it, or volunteer one.

## 1. Searching the pot

The index of everything is `registry.yaml` (`stews` list + `summary` block);
`stews/` holds the actual pots.

| Need | Command |
|---|---|
| Whole-pot table (id, slug, status, generation, curator) | `python tools/summarize.py stats` |
| Integrity check before trusting anything | `python tools/validate.py all` |
| Single pot's binding info (blob, sha256, readability) | `python tools/taste.py sniff stews/<ID-slug>` |
| Rebuild `registry.yaml` after a merge | `python tools/summarize.py registry` |
| One pot's current generation file | `cat stews/<ID-slug>/<content.file from meta.yaml>` |

Picking criteria, best first:

1. `status: mature` — has met the community maturity bar.
2. `benchmarks` — prefer pots with **positive delta** on the task suite you
   care about. Read `meta.yaml`; never trust a blob without its numbers.
3. `tags` — match your domain (e.g. `codegen`, `long-context`).
4. `content.human_readable: false` — expected for real stew; do not reject a
   pot for being gibberish.

## 2. Using a stew

1. **Verify identity** — the blob you ladle must match `meta.yaml`:
   ```
   registry digest  = stews/<ID>/stew.gen-NNN.txt
   sha256sum stews/<ID>/stew.gen-NNN.txt  # compare with content.sha256
   ```
2. **Inject at the right placement** — `meta.yaml`/tastings record
   `prompt_placement`: `system`, `user`, or `assistant-last`. System is the
   safe default; swap if a tasting shows better elsewhere.
3. **Bind model** — stews are model-bound. A pot benchmarked on `claude-3.5`
   may be inert on `gpt-4o`. Re-measure before relying on it.
4. **Measure, don't trust** — run the same task with and without the stew and
   record the delta. Honest deltas (even negative) are contributions.
5. **Safety stop** — if you observe jailbreak, leakage, or injection
   behavior, stop immediately and open a poison-report issue (IMMEDIATE
   quarantine is the point). See [CONTRIBUTING.md](CONTRIBUTING.md).

## 3. Contributing (three paths)

### 3a. Taste (anyone, fastest)

```bash
python tools/taste.py template stews/<ID-slug> --model <model> -o tasting.yaml
# fill in method/results/notes honestly, then:
python tools/validate.py tasting tasting.yaml
```
Submit under `tastings/<ID>/`. The report must bind `stew_sha256`, `model`,
and `prompt_placement`.

### 3b. Fork & cook (new generation)

```bash
# dry-run first (default demo compressor, writes nothing)
python tools/cook.py run --parent stews/<ID-slug> --rounds 3 --dry-run

# real compression once STEW_COMPRESSOR_CMD is wired (external LLM command)
STEW_COMPRESSOR_CMD="your-llm-compress" python tools/cook.py run \
  --parent stews/<ID-slug> --rounds 3
```
Then file `proposals/<user>-<slug>/` with `proposal.yaml`
(`kind: new-generation`), `stew.txt`, `self-tasting.yaml`, and `logs/`.

### 3c. New pot / hybrid

Same PR shape (`kind: new-stew` or `kind: hybrid`); a hybrid declares every
parent in `lineage.parents`.

## 4. Non-negotiable rules for agents

- **Never** edit a `stew.gen-NNN.txt` blob or a merged `meta.yaml`. A new
  generation is a new file, not an edit.
- **Never** hand-edit `benchmarks` or `registry.yaml`'s `summary` — run
  `python tools/summarize.py registry`.
- **Never** invent an `STW-`/`TST-` ID; assign at merge only.
- **Never** delete; the pot's vocabulary is *retire*, *quarantine*, *seal*.
- **Always** close with `python tools/validate.py all` and no diff on
  `registry.yaml`.

## 5. File map for skill authors

| File | Purpose |
|---|---|
| `AGENTS.md` | Engineering contract & invariants (read first) |
| `schema/*.json` | Authoritative contracts for all YAML metadata |
| `CONTRIBUTING.md` | PR mechanics, gates, commit format |
| `GOVERNANCE.md` | Keeper powers, state machine, sealing |
| `CONVENTIONS.md` | IDs, naming, directory, snapshot rules |
| `TODO.md` | Roadmap (MCP server, agent-app plugins) |