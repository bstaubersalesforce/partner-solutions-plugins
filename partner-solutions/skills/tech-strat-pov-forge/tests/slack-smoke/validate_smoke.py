#!/usr/bin/env python3
"""
Smoke-test validator for the Slack-insights flow (refs/slack-insights.md).
Checks the produced output against the mock fixtures + the ref's rules.
Independent of the producer: it re-derives expectations from the fixtures.
Exit 0 = all pass.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
def load(n): return json.load(open(os.path.join(HERE, n)))

chans = load("mock_channels.json")
msgs  = load("mock_messages.json")
out   = load("produced_output.json")

RESULTS = []
def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))

# ---- 1. Discovery ranking matches expected tiers per fixture --------------
exp_tier = {c["name"]: c["expected_tier"] for c in chans["channels"]}
ranked = {r["name"]: r["tier"] for r in out["stage1_discovery"]["ranked_candidates"]}
dropped = set(out["stage1_discovery"]["dropped_low"])
# every Low must be dropped, never ranked
lows = [n for n,t in exp_tier.items() if t == "Low"]
check("All Low-confidence channels dropped (noise channels excluded)",
      all(n in dropped for n in lows) and not any(ranked.get(n) for n in lows),
      f"lows={lows} dropped={sorted(dropped)}")
# every Medium/High appears in ranked with the right tier
mh = {n:t for n,t in exp_tier.items() if t in ("High","Medium")}
tier_ok = all(ranked.get(n) == t for n,t in mh.items())
check("Every Medium/High channel ranked with correct tier", tier_ok,
      f"expected={mh} got={ranked}")

# ---- 2. The >6 cap + disclosure -------------------------------------------
mh_count = len(mh)
shown = out["stage1_discovery"]["shortlist_shown"]
check("Medium+High count computed correctly", out["stage1_discovery"]["medium_high_count"] == mh_count,
      f"claimed={out['stage1_discovery']['medium_high_count']} actual={mh_count}")
check("Shortlist capped at 6 when >6 candidates", len(shown) == 6 and mh_count > 6,
      f"shown={len(shown)} mh={mh_count}")
check("Truncation disclosed honestly", f"top 6 of {mh_count}" in out["stage1_discovery"]["disclosure"],
      out["stage1_discovery"]["disclosure"])
# shown must be the 6 highest-priority (all 4 High + 2 Medium), no Low
check("Shortlist contains no dropped Low channel", not (set(shown) & dropped))
check("Shortlist is High-first (all 4 High included)",
      all(n in shown for n,t in mh.items() if t=="High"))

# ---- 3. AskUserQuestion 4-option cap honored ------------------------------
auq = out["stage1_discovery"]["askuserquestion_render"]
opt_counts = [len(q["options"]) for q in auq["questions"]]
check("No AskUserQuestion question exceeds 4 options", all(c <= 4 for c in opt_counts), f"counts={opt_counts}")
check("Split renders all 6 shortlisted channels", sum(opt_counts) == len(shown), f"rendered={sum(opt_counts)} shown={len(shown)}")

# ---- 4. Extraction: every fact traces to a real message (no hallucination)-
msg_by_id = {m["id"]: m for m in msgs["messages"]}
facts = out["extracted_facts"]
all_trace = all(f["source_id"] in msg_by_id for f in facts)
check("Every extracted fact traces to a real mock message", all_trace,
      f"ids={[f['source_id'] for f in facts]}")
# attribution must match the source message author+date
attr_ok = all(f["attribution"] == f"@{msg_by_id[f['source_id']]['author']}, {msg_by_id[f['source_id']]['date']}"
              for f in facts if f["source_id"] in msg_by_id)
check("Attribution (@author, date) matches the source message", attr_ok)
# bucket must match the message's intended bucket
bucket_ok = all(f["bucket"] == msg_by_id[f["source_id"]]["signal_bucket"] for f in facts if f["source_id"] in msg_by_id)
check("Each fact's bucket matches its source message's signal", bucket_ok)

# ---- 5. All 7 buckets present exactly once --------------------------------
SEVEN = {"exec_sponsor","pilot","commercial_model","stakeholder_needs","blocker","proof_point","timeline"}
got_buckets = [f["bucket"] for f in facts]
check("All 7 extraction buckets represented", set(got_buckets) == SEVEN,
      f"got={sorted(set(got_buckets))}")
check("No bucket duplicated (one fact per signal here)", len(got_buckets) == len(set(got_buckets)))

# ---- 6. Confidence tier on every Slack fact -------------------------------
check("Every Slack fact carries the [from internal Slack — confirm] tier",
      all(f["confidence"] == "[from internal Slack — confirm]" for f in facts))

# ---- 7. Noise dropped, never extracted ------------------------------------
noise_ids = {m["id"] for m in msgs["messages"] if m["signal_bucket"] == "NOISE"}
sentiment_ids = {m["id"] for m in msgs["messages"] if m["signal_bucket"] == "SENTIMENT_ONLY"}
extracted_ids = {f["source_id"] for f in facts}
check("All NOISE messages dropped (none extracted as facts)", not (noise_ids & extracted_ids),
      f"noise={noise_ids} extracted={extracted_ids}")
check("dropped_as_noise lists exactly the noise messages", set(out["dropped_as_noise"]) == noise_ids,
      f"claimed={out['dropped_as_noise']} actual={sorted(noise_ids)}")
check("SENTIMENT_ONLY messages not extracted as discrete facts", not (sentiment_ids & extracted_ids))

# ---- 8. Conflict surfaced, not silently overwritten -----------------------
conflicts = out["conflicts_surfaced"]
conflict_msgs = [m for m in msgs["messages"] if m.get("conflict_with_pov")]
check("The planted POV conflict is surfaced", len(conflicts) >= 1 and len(conflict_msgs) == 1)
if conflicts:
    c = conflicts[0]
    check("Conflict shows BOTH pov_says and slack_says (no silent overwrite)",
          bool(c.get("pov_says")) and bool(c.get("slack_says")))
    check("Conflict routed to a Stage 3 question", bool(c.get("stage3_question")))
# the conflicting commercial_model fact must still carry the Slack tier (not promoted/overwritten)
cm = [f for f in facts if f["bucket"]=="commercial_model"][0]
check("Conflicting Slack fact stays at Slack tier (did not harden/overwrite POV)",
      cm["confidence"] == "[from internal Slack — confirm]" and cm.get("conflict") is True)

# ---- 9. Narrative: placement, label, basis --------------------------------
nar = out["channel_narrative"]
check("Narrative placed in Confidence & Assumptions", nar["placement"] == "Confidence & Assumptions")
check("Narrative carries the sentiment label", nar["label"] == "[internal Slack sentiment — not partner-confirmed]")
check("Narrative is basis-attributed (message count + channels)", "synthesized from" in nar["basis"])
check("Narrative reflects both momentum and the blocker (balanced read)",
      any(w in nar["text"].lower() for w in ("accelerat","momentum","energized")) and "block" in nar["text"].lower())

# ---- 10. Stage 3 pruning against the real POV gaps ------------------------
pr = out["stage3_pruning"]
check("Pruning suppressed at least the exec-sponsor and pilot gaps",
      any("sponsor" in s["gap"].lower() for s in pr["suppressed"]) and
      any("pilot" in s["gap"].lower() or "design partner" in s["gap"].lower() for s in pr["suppressed"]))
check("A partially-answered gap was narrowed (not suppressed)", len(pr["narrowed"]) >= 1)
check("The commercial-model conflict became a Stage 3 question", len(pr["converted_to_conflict"]) >= 1)
check("Pruning is made visible to the user", bool(pr.get("visible_note")))

# ---- 11. Provenance entry completeness ------------------------------------
prov = out["research_provenance_entry"]
check("Provenance records channels read with tiers", all("—" in c for c in prov["channels_read"]))
check("Provenance records the 90-day window", prov["window_days"] == 90)
check("Provenance logs facts by bucket for all 7", set(prov["facts_by_bucket"].keys()) == SEVEN)
check("Provenance discloses discovery truncation", "top 6 of 7" in prov["discovery_disclosure"])

# ---- report ----------------------------------------------------------------
width = max(len(n) for n,_,_ in RESULTS)
passed = sum(1 for _,ok,_ in RESULTS if ok)
print(f"\nSlack-insights smoke test — {len(RESULTS)} checks\n" + "="*(width+14))
for name, ok, detail in RESULTS:
    tag = "PASS " if ok else "FAIL "
    line = f"{tag} {name.ljust(width)}"
    if not ok and detail: line += f"  → {detail}"
    print(line)
print("="*(width+14))
print(f"{passed}/{len(RESULTS)} passed\n")
sys.exit(0 if passed == len(RESULTS) else 1)
