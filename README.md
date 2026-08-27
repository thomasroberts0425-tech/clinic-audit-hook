# clinic-audit-hook

A Claude Code skill. Give it a clinic URL; it audits the site against a fixed ICP rubric
and drafts one outreach opener naming a specific, evidenced problem.

```bash
./scripts/collect.sh "https://example-clinic.com/"
```

## Why this exists as a skill and not a script

It sits alongside an existing Python/Supabase outreach pipeline that handles volume:
Google Maps ingestion, enrichment, lead scoring, tiered email generation, sending. That
pipeline works and is not replaced here.

What it does not do is judgment. Its website analysis is substring matching over a plain
HTTP fetch:

```python
"has_booking_keywords": any(x in html for x in ["book", "appointment", "schedule"]),
```

That tells you the word "book" appears somewhere. It cannot tell a Jane App clinic from
a phone-only clinic with a "Book by phone" heading — and that distinction is the entire
ICP qualifier.

So the split is deliberate:

| | Pipeline | This skill |
|---|---|---|
| Volume | thousands | one at a time |
| Output | tiered email batches | one audited opener |
| Booking detection | keyword presence | platform + evidence URL |
| Judgment signals | none | flat site structure, NAP, bios, design |
| Blocked fetches | scored as weak sites | detected and refused |

The skill runs on Tier 1 leads — the ones already routed to personal outreach.

## Architecture

`scripts/` is deterministic and has no model in it. `SKILL.md` and `references/` are the
judgment layer. That boundary is the point: the script measures, the skill decides, and
the signal table makes the decision checkable.

```
SKILL.md                  workflow + rules
references/icp-rubric.md  signals, thresholds, hook priority
references/voice.md       output rules, worked good/bad openers
scripts/collect.sh        one Firecrawl call
scripts/extract_signals.py  raw scrape -> flat signal dict
examples/                 real runs
```

## Validation

Ground truth came from Google Maps `bookingLinks` on 50 real clinic records — booking
platform known independently of the website. The audit only ever sees the clinic's own
site.

| Clinic | Truth | Plain HTTP fetch | This skill | Evidence found |
|---|---|---|---|---|
| bodyforma.ca | Jane App | found | **Jane App** | `bodyforma.janeapp.com` |
| northcarept.com | Jane App | **403 blocked** | **Jane App** | `northcarept.janeapp.com` |
| healthone.ca | Jane App | found | **Jane App** | `healthone.janeapp.com` |
| thephysioapproach.com | Jane App | **403 blocked** | **Jane App** | `thephysioapproach.janeapp.com` |
| denisonrehab.com | none | **403 blocked** | none | — |
| kindcureclinic.com | none | found | none | — |

6/6, no false positives. Every detected subdomain matches the independent ground truth.

## Two findings from building this

**1. The blocker was bot-blocking, not JavaScript.** The working assumption was that Jane
App widgets were JS-injected and invisible to a non-rendering fetch. They are not — where
a plain fetch got real HTML it found `janeapp` fine. The failure mode is 403s. Across 40
real clinic sites, **7 returned non-200 to a default `python-requests` user-agent**, plus
one connection error: roughly 1 in 5.

**2. That silently corrupts lead scoring.** `requests.get()` does not raise on 403 — it
returns the block page. An analyzer with only a try/except and no status check parses
"403 - Forbidden" and records every signal as absent: no booking system, no contact form,
no CMS. Because gap-based scoring awards points for absent signals, a blocked clinic
scores as a *maximally weak website* and is promoted up the outreach tiers. It gets
contacted precisely because the fetch failed.

Verified directly: on a 403 body, `book`/`appointment`/`schedule` are all absent, `<form>`
absent, `wp-content` absent — an all-gaps record indistinguishable from a genuinely bad site.

Fix in the pipeline is small: check `status_code` before parsing, and treat a non-200 as
unknown rather than absent.

## Requirements

Firecrawl CLI on PATH with an API key. Python 3, stdlib only. One credit per audit.

## Scope

Audits one already-review-qualified URL. No batch processing, no CRM writes, no email
sending, no review checking — the 4.5★/100+ gate is upstream and this tool cannot see it.
