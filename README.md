# urlclean

**Strip tracking parameters from links.** One Python file, no dependencies, never fetches
the URL — it only reads text and prints.

```
removed 2: utm_source, fbclid
https://shop.example/item?id=42
```

## Quick start

```bash
python urlclean.py "https://shop.example/item?utm_source=mail&id=42&fbclid=xyz"
echo "https://x.com/a?igshid=1" | python urlclean.py
python urlclean.py --list "https://x.com/a?utm_medium=cpc&id=2"   # say what was removed
python urlclean.py --keep utm_source "https://x.com/a?utm_source=brand&id=2"
```

## What it removes

Around 70 parameters in five groups: campaign tags (`utm_*`), ad click identifiers
(`fbclid`, `gclid`, `msclkid`, `ttclid`, `li_fat_id`…), social and referral tags (`igshid`,
`si`, `ref`, `mc_cid`), marketing automation (`__hssc`, `_hsenc`, `mkt_tok`, `wt.mc_id`),
and assorted analytics (`spm`, `oly_enc_id`, `s_kwcid`).

Everything else is kept, in its original order. Unknown keys are never removed — the tool
would rather leave a tracker than break a working link.

## Behaviour worth knowing

- **No scheme? It adds `https://`.** A bare `example.com/p` becomes a clickable link rather
  than a string your chat app has to guess at.
- **Unparseable input comes back unchanged**, with an empty removal list. No mangling.
- **Fragments survive.** `#section` is preserved.
- **`--keep` wins** over the blocklist, for the rare campaign link you actually want intact.
- **`--list` writes to stderr**, so stdout stays a clean, pipeable URL.

## Tests

```bash
python tests/test_urlclean.py      # 12 tests
```

UTM stripping, real parameters preserved, scheme insertion, fragments, the `--keep`
override, extra blocked keys, unparseable input, and the CLI paths.

## Licence

MIT with Commons Clause. Copyright (c) 2026 Siddhant Neekhra. See [LICENSE.md](LICENSE.md).
