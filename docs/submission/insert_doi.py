#!/usr/bin/env python3
"""
insert_doi.py -- set the Zenodo DOI in the manuscript and cover letter.
Idempotent: re-running with a new DOI replaces the previous one.

Usage (from repo root):
    python docs/submission/insert_doi.py --concept 10.5281/zenodo.NNNNNNN [--version 10.5281/zenodo.21317617]

The CONCEPT DOI always resolves to the latest archived version and is what the
paper should cite; the VERSION DOI (optional) pins the exact snapshot described.
"""
import argparse, re, pathlib, sys

MS = pathlib.Path("docs/full_manuscript.md")
CL = pathlib.Path("docs/submission/cover_letter.md")

def build_sentence(concept, version):
    s = (f"The repository is archived at Zenodo under DOI {concept} (MIT licence), "
         f"a concept identifier that always resolves to the latest archived version")
    s += f"; the version described here is {version}. " if version else ". "
    return s + "It is mirrored at https://github.com/beebzy-droid/ipis-thesis-pyrolysis-epr."

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    ap.add_argument("--version", default=None)
    a = ap.parse_args()
    if not MS.exists():
        sys.exit("run from the repo root (docs/full_manuscript.md not found)")

    # --- manuscript: replace whatever archival sentence is currently there ---
    ms = MS.read_text(encoding="utf-8")
    pat = re.compile(r"The repository (?:is archived|will be archived)[^\n]*")
    if not pat.search(ms):
        sys.exit("archival sentence not found in the Data availability section")
    ms = pat.sub(build_sentence(a.concept, a.version), ms, count=1)
    MS.write_text(ms, encoding="utf-8")

    # --- cover letter ---
    cl = CL.read_text(encoding="utf-8")
    cl = re.sub(r"\(Zenodo, DOI: [^)]*\)|\(DOI to be inserted at acceptance\)",
                f"(Zenodo, DOI: {a.concept})", cl, count=1)
    CL.write_text(cl, encoding="utf-8")

    print(f"concept DOI set: {a.concept}" + (f" | version: {a.version}" if a.version else ""))
    print("next: pandoc docs/full_manuscript.md -o 01_manuscript_FINAL.docx")

if __name__ == "__main__":
    main()
