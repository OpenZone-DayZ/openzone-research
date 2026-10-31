#!/usr/bin/env python3
"""Rebuild every font of fonts.json into OpenZone_Research/gui/fonts.

    python source/fonts/build_fonts.py              build, remove ozl_* files no longer listed
    python source/fonts/build_fonts.py --check      build in memory, compare with the files on disk
    python source/fonts/build_fonts.py --preview D  also write atlas and sample PNGs into D

Next to the fonts it writes OFL.txt: the copyright lines of every bundled typeface and the
SIL Open Font License once, so the licence travels inside the pbo with the fonts.

The build stops with a non-zero exit when a font would lack a required character (every
Ukrainian letter, the Latin I, the UI punctuation -- fontbuild.REQUIRED) or when an output
name carries a Reserved Font Name of its face's OFL.txt. A Cyrillic І or і drawn with the
Latin letter is allowed and printed as a WARNING.

Needs Python 3.10+ and Pillow. Paths come from this file's own place in the repository,
nothing machine-specific. The output is deterministic: an unchanged manifest and unchanged
TTFs give byte-identical files, so `--check` doubles as the "are the fonts up to date" test.
"""
import argparse
import json
import os
import re
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import fontbuild  # noqa: E402
from fontkit import sfnt  # noqa: E402

LICENCE_NOTE = (
    "The fonts in this folder (ozl_*.fnt with their ozl_*.edds atlases) are bitmap renderings\n"
    "of the typefaces below, made by source/fonts/build_fonts.py of the OpenZone Research\n"
    "repository. They are Modified Versions under the SIL Open Font License 1.1 and do not use\n"
    "any Reserved Font Name. The original TTF files are in that repository, source/fonts/.\n")
LICENCE_START = "This Font Software is licensed"
RFN = re.compile(r'Reserved Font Names?((?:\s*(?:,|and)?\s*"[^"]+")+)')


def face_path(face):
    """A manifest face: a path below this folder (an absolute path works too)."""
    return os.path.normpath(os.path.join(HERE, face))


def read_licence(face):
    """(copyright lines, licence text, Reserved Font Names) of the OFL.txt beside a face."""
    with open(os.path.join(os.path.dirname(face_path(face)), "OFL.txt"), encoding="utf-8-sig") as fh:
        text = fh.read().replace("\r\n", "\n")
    head, rest = text.split(LICENCE_START, 1)
    m = RFN.search(head)
    reserved = re.findall(r'"([^"]+)"', m.group(1)) if m else []
    return head.strip(), LICENCE_START + rest, reserved


def licence_text(manifest):
    """OFL.txt of the output folder: every face's copyright lines, then the licence once."""
    faces = {}
    for o in manifest["outputs"]:
        faces.setdefault(o["face"], []).append(o["name"])
    parts, body = [LICENCE_NOTE], None
    for face in sorted(faces):
        head, licence, _ = read_licence(face)
        if body is None:
            body = licence
        family = sfnt.names(face_path(face)).get(1, face)
        parts.append("%s -- %s\n%s\n" % (", ".join(sorted(faces[face])), family, head))
    return "\n".join(parts) + "\n" + body.rstrip() + "\n"


def squash(name):
    return re.sub(r"[^0-9a-z]", "", name.lower())


def load_manifest(path):
    with open(path, encoding="utf-8") as fh:
        m = json.load(fh)
    names = [o["name"] for o in m["outputs"]]
    if len(set(names)) != len(names):
        raise SystemExit("fonts.json: duplicate output names")
    for o in m["outputs"]:
        if not o["name"].endswith(str(o["cell"])):
            raise SystemExit("fonts.json: %s must end with its cell height %d" % (o["name"], o["cell"]))
        if o.get("kind", "bitmap") not in ("bitmap", "sdf"):
            raise SystemExit("fonts.json: %s: kind is bitmap or sdf" % o["name"])
        # a converted font is a Modified Version under the OFL: no Reserved Font Name in it
        for rfn in read_licence(o["face"])[2]:
            if squash(rfn) in squash(o["name"]):
                raise SystemExit("fonts.json: %s carries the Reserved Font Name %r of %s" % (
                    o["name"], rfn, o["face"]))
    return m


def build_one(o, charsets):
    stem = o["name"][: -len(str(o["cell"]))]
    make = fontbuild.build_sdf if o.get("kind", "bitmap") == "sdf" else fontbuild.build
    return make(face_path(o["face"]), stem, o["cell"],
                charset=charsets.get(o["charset"], o["charset"]), wght=o.get("wght"))


def same_file(a, b):
    if not os.path.isfile(b):
        return False
    x, y = open(a, "rb").read(), open(b, "rb").read()
    if a.endswith(".txt"):          # a checkout may turn the licence's LF into CRLF
        x, y = x.replace(b"\r\n", b"\n"), y.replace(b"\r\n", b"\n")
    return x == y


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=os.path.join(HERE, "fonts.json"))
    ap.add_argument("--check", action="store_true", help="compare with the committed files, write nothing")
    ap.add_argument("--preview", default="", help="folder for atlas and sample PNGs")
    args = ap.parse_args(argv)

    m = load_manifest(args.manifest)
    out_dir = os.path.join(REPO, *m["output"].split("/"))
    # build everything first: a font that fails leaves the folder exactly as it was
    built, failed = [], []
    for o in m["outputs"]:
        try:
            built.append(build_one(o, m["charsets"]))
        except SystemExit as e:             # a required character is missing: report, go on
            failed.append(o["name"])
            print("FAILED %s: %s" % (o["name"], e))
    if failed:
        print("BUILD FAILED: %s; nothing was written" % ", ".join(failed))
        return 2
    work = tempfile.mkdtemp(prefix="ozl_fonts_") if args.check else out_dir
    written, total = [], 0
    for b in built:
        for w in b.warnings:
            print("WARNING %s: %s" % (b.name, w))
        fnt_path, edds_path = fontbuild.write(b, work)
        written += [fnt_path, edds_path]
        size = os.path.getsize(fnt_path) + os.path.getsize(edds_path)
        total += size
        if args.preview:
            fontbuild.preview(b, fnt_path, args.preview)
        print(fontbuild.describe(b) + "  [%d KB]" % (size // 1024))
    lic = os.path.join(work, "OFL.txt")
    with open(lic, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(licence_text(m))
    written.append(lic)

    listed = {os.path.basename(p) for p in written}
    extra = sorted(f for f in os.listdir(out_dir) if f.startswith("ozl_") and f.endswith((".fnt", ".edds"))
                   and f not in listed) if os.path.isdir(out_dir) else []
    if args.check:
        stale = [os.path.basename(p) for p in written
                 if not same_file(p, os.path.join(out_dir, os.path.basename(p)))]
        for p in written:
            os.remove(p)
        os.rmdir(work)
        if stale or extra:
            print("OUT OF DATE: %s" % " ".join(stale + ["(not listed) " + e for e in extra]))
            return 1
        print("up to date: %d fonts and OFL.txt, %d KB" % (len(m["outputs"]), total // 1024))
        return 0
    for f in extra:
        os.remove(os.path.join(out_dir, f))
        print("removed", f)
    print("%d fonts (%d files) and OFL.txt, %d KB in %s" % (len(m["outputs"]), 2 * len(m["outputs"]),
                                                          total // 1024, m["output"]))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
