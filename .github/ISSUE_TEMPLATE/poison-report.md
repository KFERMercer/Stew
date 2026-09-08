---
name: Poison report (毒汤报告)
about: Report observed jailbreak, leakage, or injection behavior from a stew blob.
title: "[poison] <STW-XXXX> <short behavior summary>"
labels: poison
assignees: ""
---

> Poison reports are about **behavior**, not about the blob being unreadable.
> Gibberish is not poison. If you can't reproduce a harmful behavior, ask in
> Discussions instead.

## Stew

- Stew ID: `STW-XXXX`
- Blob sha256: `...`
- Model & version under test:
- Prompt placement: `system` / `user` / `assistant-last`

## Observed behavior

<!-- What did the model DO that is harmful? Include a short verbatim excerpt. -->

## Reproducer

1. Load model:
2. Inject stew at `<placement>`:
3. Prompt / trigger:
4. Result:

## Severity

- [ ] jailbreak (safety bypass)
- [ ] information leakage (PII / training-data exposure)
- [ ] prompt injection (attacker-controlled output)
- [ ] other: <!-- describe -->

## Impact on the pot

Recommended action: `quarantined` (instant, by any Keeper) / `sealed` (2/3 vote)