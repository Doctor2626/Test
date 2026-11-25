#!/usr/bin/env python3
"""Assemble manual/chapters/*.html into manual/index.html using manual/template.html."""
import html, pathlib, re, sys

root = pathlib.Path(__file__).parent
issue = sys.argv[1] if len(sys.argv) > 1 else "Draft"
files = sorted((root / "chapters").glob("[0-9][0-9]-*.html"))
toc, bodies, figs = [], [], 0
for f in files:
    text = f.read_text(encoding="utf-8").strip()
    sid = re.search(r'<section[^>]*\bid="([^"]+)"', text)
    h2 = re.search(r"<h2[^>]*>(.*?)</h2>", text, re.S)
    if not sid or not h2:
        sys.exit(f"{f.name}: missing section id or h2")
    title = re.sub(r"<[^>]+>", "", h2.group(1)).strip()
    num = f.name[:2]
    toc.append(f'        <li><a href="#{sid.group(1)}"><span class="n">{num}</span><span>{title}</span></a></li>')
    bodies.append(text)
    figs += len(re.findall(r'<figure class="diagram"', text))

out = (root / "template.html").read_text(encoding="utf-8")
out = (out.replace("{{TOC}}", "\n".join(toc))
          .replace("{{CHAPTERS}}", "\n".join(bodies))
          .replace("{{CHAPTER_COUNT}}", str(len(files)))
          .replace("{{FIG_COUNT}}", str(figs))
          .replace("{{ISSUE}}", html.escape(issue)))
(root / "index.html").write_text(out, encoding="utf-8")
print(f"{len(files)} chapters, {figs} figures, {len(out)//1024} KB -> {root/'index.html'}")
