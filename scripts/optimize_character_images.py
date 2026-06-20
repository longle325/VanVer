#!/usr/bin/env python3
"""Re-encode character webp images for the web.

The source portraits ship at ~500KB each (q~88 equivalent) which is far heavier
than needed for the sizes they render at. This re-encodes them in place at their
native resolution with a leaner quality setting, so dimensions are unchanged
(no upscaling/blurriness on the Discover hero) but byte size drops ~40-50%.

Run from repo root:  python3 scripts/optimize_character_images.py
Requires Pillow with webp support (pip install pillow).
"""
from __future__ import annotations

import glob
import io
import os
import sys

from PIL import Image

QUALITY = 72
METHOD = 6  # slowest/best webp encoder effort
SRC_GLOB = "frontend/public/characters/*.webp"

# Re-encoding a lossy WebP always shrinks it a little, so a naive "smaller wins"
# rule degrades quality on every rerun. Only rewrite when the win is large —
# i.e. the file is still an un-optimized original. Once optimized, re-encoding
# saves only a few percent, falls below this floor, and is skipped (idempotent).
MIN_SAVINGS_RATIO = 0.15


def main() -> int:
    paths = sorted(glob.glob(SRC_GLOB))
    if not paths:
        print(f"No images matched {SRC_GLOB} (run from repo root?)", file=sys.stderr)
        return 1

    before_total = after_total = 0
    rewritten = skipped = 0

    for path in paths:
        before = os.path.getsize(path)
        before_total += before

        im = Image.open(path)
        # No alpha is used by any character image; flatten to RGB for smaller output.
        im = im.convert("RGB")

        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=QUALITY, method=METHOD)
        data = buf.getvalue()

        # Only overwrite when the win is large enough to be a fresh original;
        # small wins mean it's already optimized, so skip to stay idempotent.
        if len(data) <= before * (1 - MIN_SAVINGS_RATIO):
            with open(path, "wb") as fh:
                fh.write(data)
            after_total += len(data)
            rewritten += 1
        else:
            after_total += before
            skipped += 1

    mb = 1024 * 1024
    print(f"images:    {len(paths)} (rewritten {rewritten}, skipped {skipped})")
    print(f"before:    {before_total / mb:.1f} MB")
    print(f"after:     {after_total / mb:.1f} MB")
    print(f"savings:   {(before_total - after_total) / mb:.1f} MB "
          f"({(1 - after_total / before_total) * 100:.0f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
