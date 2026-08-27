#!/usr/bin/env python3
"""Turn one Firecrawl scrape into a flat signal dict. Pure stdlib, no LLM.

This is the deterministic half of the skill: it measures, it does not judge.
Every field is either a fact from the page or an explicit `null` meaning
"could not determine" -- never a guess.
"""
import json, re, sys
from urllib.parse import urlparse

# Practice-management / booking platforms seen in the Canadian clinic market.
# janeapp is first because it is the ICP qualifier.
PLATFORMS = [
    "janeapp", "juvonno", "owlpractice", "clinicsense", "caserm",
    "mindbody", "cliniko", "fresha", "acuityscheduling", "calendly",
    "setmore", "square", "noterro", "practicebetter",
]
CMS_MARKERS = {
    "wordpress": ["wp-content", "wp-includes"],
    "wix": ["wix.com", "wixstatic"],
    "squarespace": ["squarespace"],
    "webflow": ["webflow"],
    "shopify": ["cdn.shopify"],
    "duda": ["dudamobile", "duda_website"],
    "godaddy": ["godaddysites"],
}
SERVICE_PAT = re.compile(r"/(services?|treatments?|what-we-(do|treat)|conditions?)(/|$|\?)", re.I)
STAFF_PAT = re.compile(r"/(team|our-team|staff|practitioners?|therapists?|about-us|about|meet)(/|$|\?)", re.I)
CA_POSTAL = re.compile(r"\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b")
PHONE = re.compile(r"(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")


def detect_platform(links, html):
    """Return (platform, evidence_url).

    A platform is only asserted when a resolvable URL is present. An earlier
    version fell back to a bare substring match and reported "square" for a
    clinic whose page merely contained that word -- no Square URL anywhere.
    Requiring a URL makes this signal high-confidence by construction, which is
    what lets the skill state it as fact rather than hedge.
    """
    hay = " ".join(links) + " " + html
    for p in PLATFORMS:
        m = re.search(r"https?://([a-z0-9-]+\.)?" + p + r"\.(com|ca|io)[^\s\"'<>]*", hay, re.I)
        if m:
            return p, m.group(0)[:200]
    return None, None


def main(raw_path, source_url):
    d = json.load(open(raw_path))
    md = d.get("markdown") or ""
    html = d.get("rawHtml") or ""
    links = [l if isinstance(l, str) else (l.get("url") or "") for l in (d.get("links") or [])]
    meta = d.get("metadata") or {}
    status = meta.get("statusCode")
    host = urlparse(source_url).netloc.lower().replace("www.", "")

    platform, evidence = detect_platform(links, html)
    internal = [l for l in links if host and host in urlparse(l).netloc.lower()]

    def distinct_paths(pattern):
        """Collapse to distinct URL *paths*.

        Anchor links (/services/#dry-needling) are the same page as /services/.
        Counting them separately would make a flat single-page site look like it
        has a dozen service pages -- inverting the signal we actually care about.
        """
        seen = {}
        for l in internal:
            path = urlparse(l).path.rstrip("/") or "/"
            if pattern.search(path):
                seen.setdefault(path, l)
        return [seen[k] for k in sorted(seen)]

    services = distinct_paths(SERVICE_PAT)
    staff = distinct_paths(STAFF_PAT)
    tel = [l for l in links if l.lower().startswith("tel:")]

    cms = None
    hl = html.lower()
    gen = meta.get("generator")
    gen_s = " ".join(gen) if isinstance(gen, list) else (gen or "")
    for name, marks in CMS_MARKERS.items():
        if any(m in hl for m in marks) or name in gen_s.lower():
            cms = name
            break

    # Sticky CTA: a fixed/sticky rule within 400 chars of a booking word.
    sticky = None
    if html:
        sticky = bool(re.search(
            r"position\s*:\s*(sticky|fixed)[^}]{0,400}?(book|appoint|schedul)"
            r"|(book|appoint|schedul)[^}]{0,400}?position\s*:\s*(sticky|fixed)", hl))

    out = {
        "url": source_url,
        "status_code": status,
        "fetch_ok": status == 200,
        "title": meta.get("title"),
        "booking_platform": platform,
        "booking_evidence": evidence,
        "is_janeapp": platform == "janeapp",
        "has_tel_link": bool(tel),
        # phone-only is only assertable when the fetch actually succeeded
        "phone_only_booking": (status == 200 and platform is None and bool(tel)) or None,
        "service_subpage_count": len(services),
        "service_subpages": services[:8],
        # "flat" == services exist but live on one page (or no service page at all)
        "flat_site": (status == 200 and len(services) <= 1) or None,
        "staff_page_count": len(staff),
        "staff_pages": staff[:5],
        "has_viewport_meta": bool(meta.get("viewport")),
        "cms": cms,
        "nap_phone_on_page": bool(PHONE.search(md)),
        "nap_postal_on_page": bool(CA_POSTAL.search(md)),
        "sticky_cta_hint": sticky,
        "html_bytes": len(html),
        "markdown_bytes": len(md),
        "internal_link_count": len(internal),
        "credits_used": meta.get("creditsUsed"),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
