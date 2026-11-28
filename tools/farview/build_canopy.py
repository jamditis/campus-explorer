"""Build viewer/canopy.webp and viewer/canopy.json: tree canopy cover over the far view.

Reads the USFS Tree Canopy Cover (NLCD), percent canopy per 30 m cell, public domain, from the
MRLC GeoServer (WCS 1.0.0, EPSG:3857), and resamples it onto a 60 m grid in the model's own frame
(Blender x east, y grid north, metres from the EPSG:6527 origin, as in viewer/geo.js) so the viewer
can look it up from world x and z. One 8-bit channel, 0 to 100 % as 0 to 255, greyscale WebP.

The viewer puts tree cover where it really is on the far ground and sinks far houses into it
(docs/VIEWER.md "Far view"). Nothing here is imagery: canopy cover is a modelled percentage.

Usage (Python with numpy, pyproj, Pillow and tifffile; downloads stay outside the repository):
    python3 tools/farview/build_canopy.py --cache /some/dir/outside/the/repo
"""

from __future__ import annotations

import argparse
import io
import json
import urllib.request
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image
from pyproj import Transformer

# WCS 1.0.0: the server's 2.0.1 GetCoverage fails on this coverage's time axis
WCS = "https://www.mrlc.gov/geoserver/wcs"
COVERAGE = "mrlc_NLCD-Tree-Canopy_conus_year_data:NLCD-Tree-Canopy_conus_year_data"
NATIVE = 38.0  # the coverage's cell in EPSG:3857 units (30 m on the ground at this latitude)
ROOT = Path(__file__).resolve().parents[2]
E0, N0, FT = 575880.0, 738340.0, 1200 / 3937  # model origin (EPSG:6527 ftUS) and ftUS -> m
# the box the far view needs (Blender m): the campus, the ridges round it, east past Manhattan
X0, X1, Y0, Y1 = -10000.0, 21980.0, -20000.0, 10000.0  # whole 60 m cells
CELL = 60.0  # the near view has real trees; past 1 km a 60 m cell is a few pixels


def fetch(cache: Path, year: int, box3857: tuple[float, float, float, float]) -> Path:
    """GeoTIFF of the canopy coverage over box3857 for `year`, cached."""
    path = cache / f"canopy_{year}_{'_'.join(str(round(v)) for v in box3857)}.tif"
    if path.exists():
        return path
    x0, y0, x1, y1 = box3857
    w, h = round((x1 - x0) / NATIVE), round((y1 - y0) / NATIVE)
    url = (
        f"{WCS}?service=WCS&version=1.0.0&request=GetCoverage&coverage={COVERAGE}&crs=EPSG:3857"
        f"&bbox={x0},{y0},{x1},{y1}&width={w}&height={h}&format=GeoTIFF&time={year}-01-01T00:00:00.000Z"
    )
    with urllib.request.urlopen(url, timeout=300) as r:
        data = r.read()
    if data[:2] not in (b"II", b"MM"):
        raise SystemExit(f"not a TIFF from the WCS: {data[:300]!r}")
    path.write_bytes(data)
    return path


def grid(raster: np.ndarray, box3857: tuple[float, float, float, float]) -> np.ndarray:
    """Canopy percent on the model-frame grid (rows from north Y1 to south Y0), bilinear."""
    to_ll = Transformer.from_crs("EPSG:6527", "EPSG:3857", always_xy=True)
    xs = np.arange(X0 + CELL / 2, X1, CELL)
    ys = np.arange(Y1 - CELL / 2, Y0, -CELL)
    gx, gy = np.meshgrid(xs, ys)
    mx, my = to_ll.transform(E0 + gx / FT, N0 + gy / FT)
    x0, y0, x1, y1 = box3857
    h, w = raster.shape
    # pixel centres: column c at x0 + (c + 0.5) * dx, row r at y1 - (r + 0.5) * dy
    fc = (mx - x0) / (x1 - x0) * w - 0.5
    fr = (y1 - my) / (y1 - y0) * h - 0.5
    c0 = np.clip(np.floor(fc).astype(int), 0, w - 2)
    r0 = np.clip(np.floor(fr).astype(int), 0, h - 2)
    tc, tr = np.clip(fc - c0, 0, 1), np.clip(fr - r0, 0, 1)
    v = raster.astype(np.float32)
    v[v > 100] = 0  # no-data (255) and water
    top = v[r0, c0] * (1 - tc) + v[r0, c0 + 1] * tc
    bottom = v[r0 + 1, c0] * (1 - tc) + v[r0 + 1, c0 + 1] * tc
    return top * (1 - tr) + bottom * tr


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cache", type=Path, required=True, help="folder outside the repository")
    ap.add_argument("--year", type=int, default=2023, help="canopy year (2023)")
    args = ap.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    to_m = Transformer.from_crs("EPSG:6527", "EPSG:3857", always_xy=True)
    corners = [to_m.transform(E0 + x / FT, N0 + y / FT) for x in (X0, X1) for y in (Y0, Y1)]
    pad = 300.0
    box = (
        min(c[0] for c in corners) - pad,
        min(c[1] for c in corners) - pad,
        max(c[0] for c in corners) + pad,
        max(c[1] for c in corners) + pad,
    )
    raster = tifffile.imread(fetch(args.cache, args.year, box))
    if raster.ndim == 3:
        raster = raster[..., 0]
    pct = grid(raster, box)
    img = Image.fromarray(np.clip(np.rint(pct * 2.55), 0, 255).astype(np.uint8), "L")
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=80, method=6)
    (ROOT / "viewer" / "canopy.webp").write_bytes(buf.getvalue())
    meta = {
        "source": "USFS Tree Canopy Cover (NLCD), via MRLC; public domain",
        "year": args.year,
        "frame": "Blender metres from the EPSG:6527 origin; x east, y grid north",
        "box": [X0, Y0, X1, Y1],
        "cell": CELL,
        "size": [img.width, img.height],
        "rows": "north to south",
        "value": "canopy percent * 2.55",
        "mean_percent": round(float(pct.mean()), 1),
    }
    (ROOT / "viewer" / "canopy.json").write_text(json.dumps(meta, indent=1) + "\n")
    size = len(buf.getvalue())
    print(f"{img.width} x {img.height}, mean canopy {pct.mean():.1f} %, {size} bytes")


if __name__ == "__main__":
    main()
