#!/usr/bin/env python3
"""
urlclean - strip tracking parameters from links.

Usage:
    python urlclean.py "https://shop.com/item?utm_source=mail&id=5&fbclid=abc"
    echo "https://x.com/a?igshid=1" | python urlclean.py
    python urlclean.py --list "https://x.com/a?utm_medium=cpc&gclid=z&id=2"

Dry by nature: it only reads text and prints. It never fetches the URL.

Stdlib only.
"""

import argparse
import sys

APP = "urlclean"
VERSION = "1.0"

# Query keys that exist to track you, not to serve the page.
TRACKING = {
    # campaign tagging
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_name", "utm_cid", "utm_reader", "utm_social", "utm_brand",
    # ad click identifiers
    "fbclid", "gclid", "dclid", "gclsrc", "wbraid", "gbraid", "msclkid",
    "yclid", "twclid", "ttclid", "li_fat_id", "rdt_cid", "epik", "irclickid",
    # social and referral
    "igshid", "igsh", "si", "ref", "ref_src", "ref_url", "referrer",
    "mc_cid", "mc_eid", "mkt_tok", "_ga", "_gl", "vero_id", "vero_conv",
    # marketing automation and analytics
    "__hssc", "__hstc", "__hssrc", "_hsenc", "_hsmi", "hsctatracking",
    "wt.mc_id", "pk_campaign", "pk_kwd", "piwik_campaign", "at_medium",
    "at_campaign", "cmpid", "campaign_id", "sc_channel", "sc_campaign",
    # misc
    "spm", "scm", "oly_enc_id", "oly_anon_id", "s_kwcid", "trk", "trkcampaign",
    "gclid_", "fb_action_ids", "fb_action_types", "fb_source", "share_id",
}


def clean(url, extra=None, keep=None):
    """
    Return (cleaned_url, removed_keys). Unknown or unparseable input comes back
    unchanged with an empty list, rather than being mangled.
    """
    from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

    text = (url or "").strip()
    if not text:
        return "", []

    added_scheme = False
    if not text.lower().startswith(("http://", "https://")):
        text = "https://" + text
        added_scheme = True

    try:
        parts = urlsplit(text)
    except ValueError:
        return url, []

    blocked = set(TRACKING)
    if extra:
        blocked |= {k.lower() for k in extra}
    allowed = {k.lower() for k in (keep or [])}

    pairs = parse_qsl(parts.query, keep_blank_values=True)
    kept, removed = [], []
    for key, value in pairs:
        lower = key.lower()
        if lower in allowed:
            kept.append((key, value))
        elif lower in blocked:
            removed.append(key)
        else:
            kept.append((key, value))

    query = urlencode(kept, doseq=True)
    result = urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))
    return result, removed


def main(argv=None):
    p = argparse.ArgumentParser(prog=APP, description="Remove tracking parameters from URLs.")
    p.add_argument("urls", nargs="*", help="URLs to clean; omit to read stdin, one per line")
    p.add_argument("--list", action="store_true", dest="show_list",
                   help="also show which parameters were removed")
    p.add_argument("--keep", action="append", default=[],
                   help="a parameter to keep even though it looks like tracking (repeatable)")
    p.add_argument("--version", action="version", version=f"{APP} {VERSION}")
    args = p.parse_args(argv)

    urls = args.urls or [line for line in (l.strip() for l in sys.stdin) if line]
    if not urls:
        p.print_help()
        return 2

    for url in urls:
        cleaned, removed = clean(url, keep=args.keep)
        print(cleaned)
        if args.show_list:
            if removed:
                print(f"  removed {len(removed)}: {', '.join(removed)}", file=sys.stderr)
            else:
                print("  removed 0: this link carries no known tracking parameters",
                      file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
