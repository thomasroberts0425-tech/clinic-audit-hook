# Example: NorthCare Physiotherapy

Real run. Ground truth confirmed independently — this clinic's Google Maps booking link
is `northcarept.janeapp.com`, which the audit found from the website alone.

Upstream qualification: 5.0 stars, 59 reviews. Passes the rating gate; **below the
100-review threshold**, so this is a borderline lead on volume.

```bash
./scripts/collect.sh "https://northcarept.com/"
```

## Signal table

| Signal | Fired | Evidence | Confidence |
|---|---|---|---|
| Jane App installed | **yes** | `https://northcarept.janeapp.com/` | High |
| Flat service structure | **yes** | 1 distinct service path (`/services/`, rest are anchors) | High |
| NAP on landing page | no gap | phone + postal code both present | High |
| Staff bios | partial | 1 page (`/about/`), no per-practitioner URLs | Medium |
| Responsive viewport | no gap | viewport meta present | High |
| Sticky booking CTA | not detected | no fixed/sticky rule near a booking word | **Low — heuristic** |
| Phone-only booking | n/a | platform found, so not phone-only | — |
| Review gate | — | checked upstream, not by this skill | — |

Collected in 1 Firecrawl credit. CMS: WordPress.

## Hook

**Jane App + flat services** — priority 1. They already pay for booking software, so the
"do you need online booking" conversation is finished. The gap is upstream of booking:
six treatments live on one `/services` page as anchor links, so there is no rankable URL
for any individual service.

Chosen over the staff-bio gap because it is High confidence and has a clearer cost.

## Observation

Fills the `[PERSONALIZED OBSERVATION]` slot in the cold email template:

> Someone asked me who does shockwave in North York — you do, but I only found that out
> by scrolling your services page.

## Email

54 words. Question subject, 15 characters. Ask is for interest, not time.

> **Subject:** shockwave page?
>
> Hi — someone asked me last week who does shockwave in North York. You do it, but I only
> found that out by scrolling your services page. There's no page for it on its own.
>
> Probably why you don't turn up for "shockwave therapy North York."
>
> Already on your radar, or worth a look?
>
> — Thomas

Built to the constraints in `references/voice.md`: interest CTA rather than a time
request (Gong, 304K emails), 50-80 words (Hunter, 34M cold emails), question subject
under 60 characters (Belkins, 5.5M emails), problem stated before explanation.

No credibility line — at 54 words there was no room for one that was both true and short.

## Note

`sticky_cta_hint: false` is a Low-confidence heuristic over CSS text and is deliberately
absent from the opener. It is a prompt to look at the page, not a finding to assert.
