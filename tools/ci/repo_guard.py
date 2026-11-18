"""Fail CI if the tree holds files that must never be committed.

Blocks: .blend files and Blender backups, reference photos (refs/), renders and
exports folders, ortho/aerial/LiDAR imagery and rasters, likely secrets, and any
file at or over 95 MB (GitHub rejects files over 100 MB).
"""

import os
import re
import subprocess
import sys

MAX_BYTES = 95 * 1024 * 1024
WARN_BYTES = 50 * 1024 * 1024

BLOCKED_EXT = {
    ".blend",
    ".blend1",
    ".blend2",  # models go up as Release assets, not git
    ".tif",
    ".tiff",
    ".jp2",
    ".sid",
    ".ecw",
    ".img",  # ortho / DEM rasters
    ".las",
    ".laz",
    ".copc",  # LiDAR point clouds
    ".npz",
    ".npy",  # cached terrain grids from the box
    ".exr",
    ".hdr",  # renders / HDRIs (fetch CC0 HDRIs at build time instead)
    ".pem",
    ".key",
    ".p12",
}
BLOCKED_DIRS = {"refs", "renders", "exports", "backups"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
IMAGE_NAME = re.compile(r"ortho|naip|aerial|photo|mask|lidar|dsm|dtm|streetview", re.I)
SECRET = re.compile(
    r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|xox[abpr]-[A-Za-z0-9-]{10,}"
    r"|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
)
TEXT_EXT = {
    ".py",
    ".sh",
    ".js",
    ".mjs",
    ".json",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".html",
    ".css",
    ".txt",
    ".cfg",
    ".ini",
    ".env",
}


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True).stdout
    return [p for p in out.decode().split("\0") if p]


def main():
    problems, warnings = [], []
    for path in tracked_files():
        if not os.path.isfile(path):
            continue
        parts = path.split("/")
        name = parts[-1]
        ext = os.path.splitext(name)[1].lower()
        size = os.path.getsize(path)
        if ext in BLOCKED_EXT or re.search(r"\.blend\d*$", name):
            problems.append(f"{path}: blocked file type {ext or name}")
        if any(p in BLOCKED_DIRS for p in parts[:-1]):
            problems.append(f"{path}: inside a blocked folder (refs/renders/exports/backups)")
        if ext in IMAGE_EXT and IMAGE_NAME.search(name):
            problems.append(f"{path}: looks like reference photo or ortho/aerial imagery")
        if size >= MAX_BYTES:
            problems.append(f"{path}: {size / 1e6:.1f} MB is over the 95 MB limit")
        elif size >= WARN_BYTES:
            warnings.append(f"{path}: {size / 1e6:.1f} MB (over 50 MB)")
        if ext in TEXT_EXT and size < 5 * 1024 * 1024 and not path.startswith("vendor/"):
            with open(path, encoding="utf-8", errors="ignore") as fh:
                if SECRET.search(fh.read()):
                    problems.append(f"{path}: contains something that looks like a secret")
    for w in warnings:
        print(f"::warning::{w}")
    for p in problems:
        print(f"::error::{p}")
    print(f"repo-guard: {len(problems)} problem(s), {len(warnings)} warning(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
