"""Build viewer/stars.json, the stars the viewer draws in the night sky.

Reads the Yale Bright Star Catalogue, 5th revised edition (Hoffleit and Warren 1991, public
domain; CDS catalogue V/50, mirrored by the Harvard-Smithsonian Center for Astrophysics), and
keeps every star brighter than magnitude --limit with its J2000 position, visual magnitude
and B-V colour index. The viewer turns the sky for the instant shown (viewer/sky-math.js).
Standard library only.

Usage:
    python3 tools/sky/build_stars.py --cache /some/dir/outside/the/repo
    python3 tools/sky/build_stars.py --catalogue /path/to/bsc5.dat.gz
"""

from __future__ import annotations

import argparse
import gzip
import json
import urllib.request
from pathlib import Path

URL = "http://tdc-www.harvard.edu/catalogs/bsc5.dat.gz"
OUT = Path(__file__).resolve().parents[2] / "viewer" / "stars.json"
SOURCE = (
    "Yale Bright Star Catalogue, 5th revised edition (Hoffleit and Warren 1991), "
    "CDS V/50, public domain"
)


def parse_line(line: str) -> tuple[float, float, float, float] | None:
    """(ra, dec, vmag, b_v) in degrees and magnitudes from one fixed-width catalogue line.

    Returns None for the few entries with no J2000 position (novae and non-stellar objects
    that were dropped from the catalogue) or no magnitude. A missing B-V counts as 0.6 (sun-like).
    """
    if len(line) < 107 or not line[75:77].strip() or not line[102:107].strip():
        return None
    ra = (int(line[75:77]) + int(line[77:79]) / 60 + float(line[79:83]) / 3600) * 15
    dec = int(line[84:86]) + int(line[86:88]) / 60 + int(line[88:90]) / 3600
    if line[83] == "-":
        dec = -dec
    vmag = float(line[102:107])
    bv_text = line[109:114].strip()
    b_v = float(bv_text) if bv_text else 0.6
    return ra, dec, vmag, b_v


def build(text: str, limit: float) -> list[list[float]]:
    """Stars brighter than `limit`, brightest first: [ra, dec, vmag, b_v], rounded."""
    stars = []
    for line in text.splitlines():
        star = parse_line(line)
        if star and star[2] < limit:
            ra, dec, vmag, b_v = star
            stars.append([round(ra, 3), round(dec, 3), round(vmag, 2), round(b_v, 2)])
    stars.sort(key=lambda s: s[2])
    return stars


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--catalogue", type=Path, help="bsc5.dat or bsc5.dat.gz already downloaded")
    ap.add_argument("--cache", type=Path, help="folder outside the repository to download into")
    ap.add_argument("--limit", type=float, default=4.5, help="faintest magnitude kept (4.5)")
    args = ap.parse_args()
    path = args.catalogue
    if path is None:
        if args.cache is None:
            ap.error("give --catalogue or --cache")
        args.cache.mkdir(parents=True, exist_ok=True)
        path = args.cache / "bsc5.dat.gz"
        if not path.exists():
            urllib.request.urlretrieve(URL, path)
    raw = path.read_bytes()
    text = (gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw).decode("latin-1")
    stars = build(text, args.limit)
    doc = {
        "source": SOURCE,
        "epoch": "J2000",
        "limit": args.limit,
        "fields": ["ra_deg", "dec_deg", "vmag", "b_v"],
        "stars": stars,
    }
    OUT.write_text(json.dumps(doc, separators=(",", ":")) + "\n")
    print(f"{len(stars)} stars brighter than {args.limit} -> {OUT}")


if __name__ == "__main__":
    main()
