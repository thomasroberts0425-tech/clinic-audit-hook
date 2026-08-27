# ICP Rubric

Signals, thresholds, and the reasoning behind each. Ported from field notes so this
repo stands alone -- no vault, no database.

## Upstream gate (NOT checked here)

**4.5+ stars with 100+ Google reviews.** This is the hard qualifier and it lives on
Google Business Profile, not on the clinic's own site. A URL-in tool structurally
cannot see it. It is checked upstream (Apify -> Google Maps ingestion, or a 3-5 minute
manual check) before a URL ever reaches this skill.

If you do not know whether the clinic passed this gate, **say so** rather than implying
the audit qualified them. The audit measures the website. It does not qualify the lead.

## Signals

Confidence is load-bearing. State high-confidence signals as fact. Hedge medium ones.
Never lead a hook with a low-confidence or judgment signal.

| Signal | Field | Confidence | Why it matters |
|---|---|---|---|
| Jane App installed | `is_janeapp` | **High** | The ICP qualifier. Jane App means they already pay for booking software -- digitally ready, budget-aware, past the "do we need this" conversation. Best possible lead. |
| Other booking platform | `booking_platform` | **High** | Juvonno, Cliniko, Mindbody, Fresha, Owl, ClinicSense. Same signal as Jane App: they buy software. |
| Booking route | `booking_route` | **High** | How a patient actually books: `platform` (Jane App etc.), `booking_page` (their own), `contact_form` (Book button opens a contact form -- a callback request, not booking), `phone_only` (no booking affordance at all). Three earlier attempts at this signal were wrong in ways that would have burned leads. Never say "phone-only" unless the route says so. |
| Flat service structure | `flat_site` | **High** | One services page (or anchors on the homepage) instead of per-service URLs. Directly costs local search. The single most reliable SEO hook. |
| Missing staff bios | `staff_page_count` | Medium | Bios add unique content and E-E-A-T, and rank for "[treatment] [city] [therapist]". |
| NAP incomplete | `nap_phone_on_page`, `nap_postal_on_page` | **High** | Name/address/phone must be on the landing page and consistent everywhere. Missing = direct local-ranking damage. |
| No responsive viewport | `has_viewport_meta` | **High** | Rare, and damning when true. Local clinic traffic is mobile-dominant. |
| No sticky booking CTA | `sticky_cta_hint` | **Low** | Heuristic over CSS. Treat as a prompt to look, never as a stated fact. |
| Page weight | `html_bytes` | **Low** | Crude proxy. Do not quote a load time you did not measure. |
| Dated frontend | -- | **Judgment** | Your read of the rendered page. Legitimate, but label it as opinion. |

## Already covered upstream

SSL, contact form, CMS, and analytics detection exist in the enrichment pipeline. They
are collected here for context but are not hooks -- do not build an opener around them.

## Hook priority

Rank candidate hooks in this order and take the first that fires:

1. **Jane App + flat services** -- they invested in booking but search can't find the
   services. The strongest opener in the set: praises a real decision, names a real gap.
2. **Jane App + missing NAP** -- same shape, local-ranking flavour.
3. **`contact_form` or `phone_only` route** -- a patient cannot actually book. High pain,
   and now high confidence. Say what is literally true: a Book button that opens a
   contact form is a callback request, not booking.
4. **Flat services** alone.
5. **Missing staff bios** alone.
6. **Nothing fired** -- recommend skipping. See voice.md.
