#!/usr/bin/env python3
"""Build client-guide/ESC-Renovation-Guide.pdf with page-numbered contents.
Usage: python3 client-guide/make_pdf.py "Edition 1 · Nov 2026"
"""
import json, pathlib, re, subprocess, sys
from pypdf import PdfReader
root = pathlib.Path(__file__).parent
issue = sys.argv[1] if len(sys.argv) > 1 else "Draft"
out = root / "ESC-Renovation-Guide.pdf"
pj = root / ".pages.json"
def render():
    subprocess.run([sys.executable, str(root / "build.py"), issue], check=True)
    subprocess.run(["node", str(root.parent / "manual" / "pdf.js"), str(out), issue, str(root / "index.html"), "ESC-GUIDE-01 Your Renovation"], check=True)
body = (root / "body.html").read_text(encoding="utf-8")
targets = [(m.group(1), re.sub(r"[^a-z0-9]", "", re.sub(r"<[^>]+>|&amp;", "", m.group(2)).lower()))
           for m in re.finditer(r'<section class="chapter" id="([^"]+)">.*?<h2>(.*?)</h2>', body, re.S)]
pj.write_text("{}"); render()
r = PdfReader(str(out)); marks = {}
def walk(items):
    for x in items:
        if isinstance(x, list): walk(x)
        else: marks.setdefault(re.sub(r"[^a-z0-9]", "", x.title.lower()), r.get_destination_page_number(x) + 1)
walk(r.outline)
found = {sid: marks[k] for sid, k in targets if k in marks}
pj.write_text(json.dumps(found)); render(); pj.unlink()
subprocess.run([sys.executable, str(root / "build.py"), issue], check=True)
print(out, len(r.pages), "pages", found, "missing:", [s for s, _ in targets if s not in found])
