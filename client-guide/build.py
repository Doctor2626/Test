#!/usr/bin/env python3
"""Build client-guide/index.html from body.html + template.html (ESC house style).
Usage: python3 client-guide/build.py "Edition 1 · Nov 2026"
"""
import base64, html, json, pathlib, re, sys
root = pathlib.Path(__file__).parent
assets = root.parent / "manual" / "assets"
issue = sys.argv[1] if len(sys.argv) > 1 else "Draft"
pages = json.loads((root / ".pages.json").read_text()) if (root / ".pages.json").exists() else {}
body = (root / "body.html").read_text(encoding="utf-8")
def strip(s): return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
toc, ptoc = [], []
for m in re.finditer(r'<section class="chapter" id="([^"]+)">.*?<span class="ch-num"[^>]*>(\d+)</span>.*?<h2>(.*?)</h2>', body, re.S):
    sid, n, title = m.group(1), m.group(2), strip(m.group(3))
    toc.append(f'        <li><a href="#{sid}"><span class="n">{n}</span><span>{html.escape(title)}</span></a></li>')
    ptoc.append(f'<li><span class="n">{n}</span><span class="t">{html.escape(title)}</span><span class="pg">{pages.get(sid, "")}</span></li>')
print_toc = '<section class="print-toc" aria-hidden="true"><h2>Contents</h2><ol>' + "".join(ptoc) + "</ol></section>"
def uri(n): return "data:image/png;base64," + base64.b64encode((assets / n).read_bytes()).decode()
out = (root / "template.html").read_text(encoding="utf-8")
for k, v in {"{{TOC}}": "\n".join(toc), "{{PRINT_TOC}}": print_toc, "{{BODY}}": body, "{{ISSUE}}": html.escape(issue),
             "{{LOGO_FULL}}": uri("esc-logo-full.png"), "{{LOGO_FULL_REV}}": uri("esc-logo-full-reverse.png"),
             "{{LOGO_MARK}}": uri("esc-mark.png"), "{{LOGO_MARK_REV}}": uri("esc-mark-reverse.png")}.items():
    out = out.replace(k, v)
(root / "index.html").write_text(out, encoding="utf-8")
print(f"{len(toc)} sections, {len(re.findall('figure class=.diagram', body))} figures, {len(out)//1024} KB")
