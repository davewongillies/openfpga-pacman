#!/usr/bin/env python3
"""Verify each mra/*.mra assembles byte-for-byte to the .rom the core expects.

Cross-checks the shipped .mra recipes against tools/build_roms.py (the canonical
layout the data_loader streams). For every mra/<name>.mra it reads the index-0
part list, assembles it from the MAME zips, and compares to build_roms.py's
output for the game of the same <name>. Exits non-zero on any mismatch.

Usage:  python3 tools/verify_mra.py [--zipdir DIR]   (default zipdir: ~/Downloads)
"""
import argparse, hashlib, os, re, sys, zipfile
import build_roms

MRA_DIR = os.path.join(os.path.dirname(__file__), "..", "mra")


def parse_mra(path):
    """Return (zip_names[list], [part_name,...]) from the index-0 <rom> block."""
    xml = open(path, encoding="utf-8").read()
    m = re.search(r'<rom index="0"[^>]*zip="([^"]+)"[^>]*>(.*?)</rom>', xml, re.S)
    if not m:
        raise ValueError(f"{path}: no index-0 rom block")
    zips = m.group(1).split("|")
    parts = re.findall(r'name="([^"]+)"', m.group(2))
    return zips, parts


def assemble_from_mra(zips, parts, zipdir):
    members = {}   # name -> bytes, searched across the | zip list
    for zn in zips:
        zp = os.path.join(zipdir, zn)
        if os.path.exists(zp):
            with zipfile.ZipFile(zp) as z:
                for n in z.namelist():
                    members.setdefault(os.path.basename(n), z.read(n))
    blob = bytearray()
    for p in parts:
        if p not in members:
            raise FileNotFoundError(f"part {p} not in {zips}")
        blob += members[p]
    return bytes(blob)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zipdir", default=os.path.expanduser("~/Downloads"))
    a = ap.parse_args()
    fails = 0
    for fn in sorted(os.listdir(MRA_DIR)):
        if not fn.endswith(".mra"):
            continue
        game = fn[:-4]                              # "Pac-Man.mra" -> "Pac-Man"
        spec = build_roms.GAMES.get(game)
        if not spec:
            print(f"  ?? {fn}: no build_roms entry named {game!r}")
            fails += 1
            continue
        ref = assemble_from_mra([spec["zip"]],
                                [p for p, _ in spec["parts"]], a.zipdir)   # build_roms layout
        zips, parts = parse_mra(os.path.join(MRA_DIR, fn))
        got = assemble_from_mra(zips, parts, a.zipdir)
        if got == ref:
            print(f"  ok {fn:28s} {len(got)}B  md5={hashlib.md5(got).hexdigest()}")
        else:
            print(f"  !! {fn:28s} MISMATCH vs build_roms ({len(got)}B vs {len(ref)}B)")
            fails += 1
    print(f"{'ALL MATCH' if not fails else f'{fails} MISMATCH'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
