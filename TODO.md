# TODO

Roadmap for Stew. Nothing here is sacred order — pick a lane and send a PR
(see [CONTRIBUTING.md](CONTRIBUTING.md)). Items are tracked inline; move the
checkbox when the change lands and `tools/validate.py all` passes.

## 1. Agent-app plugins / adapters

Thin wrappers so mainstream agent runtimes can consume and contribute stews
inside their own UI.

- [ ] **OpenCode** — with compressed prompt extraction
- [ ] **GitHub Copilot** — with compressed prompt extraction
- [ ] **Cursor** — with compressed prompt extraction
- [ ] **Claude Code** — with compressed prompt extraction
- [ ] **OpenAI Codex** — with compressed prompt extraction
- [ ] Extraction support in every adapter: expose `extract` via native UI/command (reuses `tools/extract.py` core from `## 3`), auto-fills `proposal.yaml#method.extracted_from`, includes `--redact` sanitization and `sha256` binding
- [ ] Adapter contract: all adapters share one protocol (search → verify →
      fetch → measure → report → extract); only the surface differs.

## 2. MCP server (agents first-class)

Give agents native, tool-call access to the pot instead of shelling out to
CLI scripts.

- [ ] Build an MCP server (SDK: `mcp` Python, stdio transport) serving the
      pot as resources and tools, e.g.:
  - `stew_search(filter: status|tags|min_delta|task)` → list matching pots
    from `registry.yaml` + `meta.yaml`
  - `stew_get(stew_id, generation?)` → current blob + sha256 + placement
    hints (never an unverified byte)
  - `stew_taste(stew_id, model, placement)` → tasting skeleton bound to the
    exact blob (`tools/taste.py template` under the hood)
  - `stew_propose(...)` → stages `proposals/<user>-<slug>/` for a PR
  - `stew_poison(stew_id, behavior)` → creates a poison-report issue
- [ ] Verification path: tool output must never skip `sha256` verification;
      agents get the blob **and** its digest.
- [ ] Config: `STEW_MCP_TOKEN_LIMIT`, model bindings, default placement.
- [ ] Tests: run all tools through the server in CI (extension of
      `.github/workflows/validate-proposal.yml`).

## 3. Agent Compressed Prompt Extraction (Extract)

Extract the final compressed prompt from mainstream agent runtimes and convert it into a stew candidate, closing the loop: use → extract → contribute. Also exposed through `## 1` plugins and `## 2` MCP server.

- [ ] Extractor placeholder `tools/extract.py`: `extract <source> --from <agent> --out proposals/<user>-<slug>/stew.txt` + `extract sniff` pre-check + `extract template` to scaffold `proposal.yaml` (agent-agnostic; supports all adapters in `## 1`)
- [ ] Adapter layer `tools/extractors/*.py` with unified `detect()/extract()` interface (one module per agent, no priority ordering)
- [ ] Provenance & compliance: `proposal.yaml#method.extracted_from: {agent, version, session_ref, extracted_at}`, append `extracted via extract-v1` to `lineage.root_seed.provenance_note`, require manual confirmation of `legal.privacy_screened`, support `--redact` sanitization
- [ ] MCP integration (reserved): `stew_extract(source, from)` (depends on `## 2. MCP server`), output bound via `sha256`
- [ ] Validation (reserved): future `tools/validate.py proposal` check for `extracted_from`; no validation changes in placeholder phase

## Backlog / ideas

- [ ] Real compressor integration for `cook-v1`: `cook.py` currently ships a
      deterministic *demo* compressor; wire an LLM-backed one +
      benchmark harness so `--dry-run` numbers are honest.
- [ ] Tasting leaderboard: `tools/summarize.py` gains a `tasters` subcommand
      (effective tasting counts → community voting weight).
- [ ] Sealed-stew vault: `stews/sealed/` convention + `validate.py` grant for
      index absence (already modeled; needs exec tooling).
- [ ] `AGENTS.md`/`SKILL.md` → GitHub Actions bot that answers "which stew
      should I use?" from `registry.yaml`.

## Done

- [x] Repo skeleton, schemas, `validate.py` / `taste.py` / `cook.py` /
      `summarize.py`, seed pot `STW-0000`, CI workflow, poison-report
      template.