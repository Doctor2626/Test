#!/usr/bin/env python3
"""Build the printable manual: ESC-Building-Manual.pdf with page numbers in the contents.

Usage: python3 manual/make_pdf.py "Issue 1 · Nov 2026"
Two passes: render, find the page each chapter starts on, write those numbers into
the printed contents, render again.
"""
import json, pathlib, re, subprocess, sys
from pypdf import PdfReader

root = pathlib.Path(__file__).parent
issue = sys.argv[1] if len(sys.argv) > 1 else "Draft"
out = root / "ESC-Building-Manual.pdf"
pages_file = root / ".pages.json"


def run(*args):
    subprocess.run(args, check=True)


def render():
    run(sys.executable, str(root / "build.py"), issue)
    run("node", str(root / "pdf.js"), str(out), issue)


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


# chapter anchors and titles, in order
targets = []
for f in sorted((root / "chapters").glob("[0-9][0-9]-*.html")):
    t = f.read_text(encoding="utf-8")
    sid = re.search(r'<section[^>]*\bid="([^"]+)"', t).group(1)
    title = re.sub(r"<[^>]+>", "", re.search(r"<h2[^>]*>(.*?)</h2>", t, re.S).group(1))
    targets.append((sid, norm(title.replace("&amp;", "&")), "in this chapter"))
targets += [("appendix-holds", "inspection holds", "appendix a"), ("appendix-defaults", "esc defaults", "appendix b")]

pages_file.write_text("{}")
render()
reader = PdfReader(str(out))
marks = {}
def walk(items):
    for x in items:
        if isinstance(x, list):
            walk(x)
        else:
            marks.setdefault(re.sub(r"[^a-z0-9]", "", x.title.lower()), reader.get_destination_page_number(x) + 1)
walk(reader.outline)
total = len(reader.pages)
found = {}
for sid, title, _ in targets:
    key = re.sub(r"[^a-z0-9]", "", title)
    if key in marks:
        found[sid] = marks[key]
missing = [s for s, _, _ in targets if s not in found]
pages_file.write_text(json.dumps(found))
render()
pages_file.unlink()
run(sys.executable, str(root / "build.py"), issue)  # leave the web build without page numbers
print(f"{out} · {total} pages · chapter pages {found}" + (f" · NOT FOUND: {missing}" if missing else ""))
