# Governance

How the pot is kept, by whom, and under what rules.

## Principles

1. **No deletion.** Retiring, quarantining, and sealing are the only terminal
   states. Git history is the ledger.
2. **Measurement over reading.** Nobody is required to read a garbled blob;
   blind tests and red-team probes are the court of appeal.
3. **Consent of keepers.** Structural change requires a 2/3 Keeper vote.

## Keepers

- At least **3 Keepers** must be active for structural decisions.
- Keeper duties: merge proposals, assign `STW-`/`TST-` IDs, promote states,
  adjudicate poison reports and seals.
- Keepers are individuals, not organizations; membership is recorded in the
  GitHub team and pasted into `state_history` refs of their actions.

## State machine

```
 (new) --PR--> seed --merge--> simmering
                               simmering --(maturity criteria)--> mature
   mature / simmering --(superseded / failed)--> retired
   any --(poison report)--> quarantined --(cleared)--> resolved
   quarantined --(adjudicated)--> sealed
```

| State | Meaning | Allowed by |
|---|---|---|
| `seed` | Merged, awaiting simmer assignment | Keeper Bot |
| `simmering` | ≥30 days minimum; open to tasting & forking | Keeper Bot |
| `mature` | Maturity criteria met (below) | Keeper Bot after Keeper vote |
| `retired` | Superseded or below baseline; archived, never deleted | Keeper vote |
| `quarantined` | Poison report active; frozen immediately | Any Keeper (instant) |
| `sealed` | Removed from index, unreferenceable; blob kept for evidence | 2/3 Keeper vote |

Every transition appends to `state_history`:

```yaml
state_history:
  - {at: 2026-09-08T22:00:00Z, from: seed, to: simmering, by: keeper-bot, ref: pr-42}
```

## Maturity criteria (all required)

1. ≥7 independent tastings,
2. contributed by ≥5 distinct tasters,
3. covering ≥2 model families,
4. with a significant positive delta on the canonical task suites
   (`core-v1` family),
5. and no unresolved safety flags.

## Poison reports

- Any Taster may open a poison report issue for observed jailbreak,
  leakage, or injection behavior.
- A Keeper may immediately set `status: quarantined`. While quarantined the
  stew no longer appears in the registry and may not be forked.
- Adjudication within 14 days: clear (`resolved` → back to prior state) or
  confirm (`sealed`, 2/3 vote).

## Sealing

The heaviest tool, used only for confirmed poison:

1. Keeper motion + 2/3 vote;
2. Keeper Bot moves the directory to `stews/sealed/`, sets `status: sealed`,
   removes the entry from `registry.yaml`;
3. The blob stays in git history forever as evidence.

## Registry integrity

`registry.yaml` is the index of the pot. Its `summary` block is regenerated
by `tools/summarize.py registry`; the `stews` list is verified by
`tools/validate.py all`. Never edit the `summary` block by hand.