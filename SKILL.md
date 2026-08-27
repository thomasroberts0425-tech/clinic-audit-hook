---
name: clinic-audit-hook
description: Audit a clinic or local healthcare website against ICP signals and draft a personalized outreach opener. Use when given a physiotherapy, chiropractic, RMT/massage, dental, rehab, or wellness clinic URL and asked to audit it, check outreach fit, find the hook, assess it as a lead, identify its booking system, or write a first-touch opener. Triggers on "audit this clinic", "is this a good lead", "what's wrong with this clinic's site", "do they use Jane App", "write me an opener for this clinic", or a bare clinic URL pasted with intent to reach out.
allowed-tools:
  - Bash(*/clinic-audit-hook/scripts/collect.sh *)
  - Bash(python3 */clinic-audit-hook/scripts/extract_signals.py *)
  - Bash(firecrawl *)
---

# Clinic Audit → Outreach Hook

Turn one clinic URL into an evidence-backed signal table and a single-paragraph
outreach opener.

This is the judgment layer for leads that warrant a personal approach. Bulk enrichment
and tiering happen upstream; this runs on the ones worth a human call.

## Before you start

The input URL is assumed **already review-qualified** (4.5+ stars, 100+ reviews) by the
upstream pipeline or a manual check. This skill audits the website. It does not qualify
the lead. If you do not know the review status, say so in the output.

## Workflow

### 1. Collect

```bash
~/.claude/skills/clinic-audit-hook/scripts/collect.sh "<clinic-url>"
```

Writes to `./.audit/` in the current directory. If the skill is installed elsewhere,
use the path it actually lives at — the scripts are self-contained and run from any cwd.

One Firecrawl call, then a pure-stdlib extractor. Deterministic -- no model in this path,
so the same URL yields the same signals every run.

**Check `fetch_ok` first.** If `status_code` is not 200, stop. A blocked or errored fetch
produces a page with no booking links, no forms, and no content -- which looks exactly
like a maximally weak website. Reporting that as an audit finding is the single worst
failure mode available here. Say the fetch failed and stop.

### 2. Read the signals against the rubric

Read `references/icp-rubric.md`. For each signal, note whether it fired and at what
confidence. **Do not restate signals as findings without checking confidence** -- the
rubric marks which ones can be stated as fact.

### 3. Pick exactly one hook

Use the hook priority list in the rubric. Take the first that fires. Resist the urge to
mention the others; one specific finding outperforms three.

If nothing above Medium confidence fires, the answer is "skip this lead" -- see the
closing section of `references/voice.md`.

### 4. Write

Read `references/voice.md` and follow it. The register is **customer-curious, not
consultant-declarative** -- you went looking for something on their site and could not
find it, and you are asking about it. You are not presenting an audit.

Output in this order:

**Signal table** -- every signal, whether it fired, the evidence, and the confidence.
This is the audit, and it is what makes the message checkable.

**The hook** -- which signal you chose and why it beat the others. One or two sentences.

**The observation** -- one or two sentences that fill the `[PERSONALIZED OBSERVATION]`
slot in the existing cold email template. This is the load-bearing output.

**The full email** -- first person, from Thomas, built around that observation.
**50-80 words. A short question as the subject line, under 60 characters. One CTA, and
it asks for interest, never for time** ("Is that something you've already looked at?" --
not "worth a quick call?"). Leave `[credibility line]` as a placeholder rather than
inventing a track record.

These constraints come from the data in `references/voice.md`, not from taste. The
interest-CTA rule is the highest-leverage one: Gong found it the best-performing CTA for
cold email across 304,174 messages, and asking for time upfront costs replies.

## Rules

- **Never assert a signal the collector did not return.** If `booking_platform` is null,
  they have no detectable booking platform -- not "they use phone booking". The
  difference matters.
- **Never invent a number.** No load times, no traffic estimates, no revenue figures.
  `html_bytes` is a page-weight proxy, not a load time; do not convert one to the other.
- **A null is not a negative.** `sticky_cta_hint: null` means unknown, not absent.
- **Say when you are guessing.** "Dated frontend" is your read of the page. Label it.
- **Never invent a track record.** No claimed clients, results, or experience. Leave
  `[credibility line]` for Thomas to fill. A fabricated reference collapses the moment
  they ask a follow-up question.
- **Vary the opening line.** If several clinics in a row get the same sentence skeleton,
  the skeleton is the tell and the personalisation is worthless. Rotate the entry point.
- **Never close by asking for time.** No "quick call", no "20 minutes", no calendar link
  on a first touch. Ask whether the thing you found is on their radar. The meeting is
  asked for on the reply.
- Decline rather than manufacture. A skipped lead costs nothing; a bad first touch
  burns the only first impression that clinic will give.
