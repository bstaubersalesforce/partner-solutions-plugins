# Slack-insights smoke test

A scenario-level smoke test for the Slack-insights flow (`refs/slack-insights.md`).
Distinct from `tests/validate_skill.py`, which checks **structural invariants** of the
skill's files. This test walks **mocked channel + message data** through the flow and
verifies the produced output obeys the ref's rules.

> **All data here is FABRICATED.** Channel names, authors, and messages are invented for
> testing. Nothing is real Slack content. There is still no live Slack MCP tool, so this
> does not exercise the actual `list channels` / `read history` round-trip or live
> extraction judgment — only the flow logic and output shape.

## Files

| File | Role |
|---|---|
| `mock_channels.json` | 9 fabricated channels engineered to test discovery ranking, the Low-drop (incl. two false positives), and the >6 Medium+High cap. |
| `mock_messages.json` | 11 fabricated messages covering all 7 extraction buckets, noise (banter/scheduling), sentiment-only, and one planted Slack-vs-POV conflict. |
| `produced_output.json` | What the flow should produce from those fixtures (ranked shortlist + AskUserQuestion split, extracted facts, dropped noise, surfaced conflict, narrative, Stage 3 pruning, provenance). |
| `validate_smoke.py` | Independent validator — re-derives expectations from the fixtures, so the producer can't assert its own success. |

## Run

```bash
python3 tests/slack-smoke/validate_smoke.py
```

Exit 0 = all 34 checks pass.

## What it covers

Discovery ranking & tiers · Low-drop · >6 cap + honest disclosure · the 4-option-per-question
`AskUserQuestion` split · all 7 buckets · no-hallucination (every fact traces to a real message) ·
attribution fidelity · noise rejection · conflict surfaced (both sides, not overwritten) ·
Slack confidence tier never hardens · sentiment narrative placement/label/basis ·
Stage 3 pruning (suppress / narrow / convert-to-conflict, made visible) · provenance entry.

## Not covered (live shakedown, pending a connected Slack MCP tool)

The real MCP round-trip and the model's real-time extraction judgment against actual
channel history. Update the fixtures or add live cases once a Slack tool is connected.
