#!/usr/bin/env python3
"""Assemble manual/chapters/*.html into manual/index.html (ESC house style).

Usage: python3 manual/build.py "Issue 1 · Nov 2026"
Adds part dividers, per-chapter contents, heading anchors, the ESC logo,
and two appendices collected from the chapters: inspection holds and ESC defaults.
"""
import base64, html, json, pathlib, re, sys

root = pathlib.Path(__file__).parent
issue = sys.argv[1] if len(sys.argv) > 1 else "Draft"
# optional page numbers for the printed contents: manual/.pages.json {anchor_id: page}
pages = json.loads((root / ".pages.json").read_text()) if (root / ".pages.json").exists() else {}

PARTS = [
    ("I", "Before the build", "Contract to mobilization: sequence, permits, site setup and neighbors.", ["01"]),
    ("II", "Structure", "Taking the house down to what stays, then the ground, the footings and the frame.", ["02", "03", "04"]),
    ("III", "Envelope", "Roof, walls, windows and insulation: keeping water out and heat in.", ["05"]),
    ("IV", "Mechanical systems", "Plumbing, HVAC and electrical, from rough-in to trim.", ["06", "07", "08"]),
    ("V", "Finishes", "Walls, tile, millwork, cabinets, stairs and floors.", ["09", "10", "11"]),
]


def data_uri(name):
    return "data:image/png;base64," + base64.b64encode((root / "assets" / name).read_bytes()).decode()


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


chapters = {}
for f in sorted((root / "chapters").glob("[0-9][0-9]-*.html")):
    num = f.name[:2]
    text = f.read_text(encoding="utf-8").strip()
    sid = re.search(r'<section[^>]*\bid="([^"]+)"', text).group(1)
    title = strip(re.search(r"<h2[^>]*>(.*?)</h2>", text, re.S).group(1))

    # anchors on h3s + in-chapter contents
    heads = []
    def add_id(m, sid=sid, heads=heads):
        i = len(heads) + 1
        hid = f"{sid}-s{i}"
        heads.append((hid, strip(m.group(2))))
        return f'<h3{m.group(1)} id="{hid}">{m.group(2)}</h3>'
    text = re.sub(r"<h3([^>]*)>(.*?)</h3>", add_id, text, flags=re.S)

    # big chapter numeral in the header; contents list after it
    text = text.replace('<header class="ch-head">', f'<header class="ch-head"><span class="ch-num" aria-hidden="true">{num}</span>', 1)
    toc_items = "".join(f'<li><a href="#{h}">{html.escape(t)}</a></li>' for h, t in heads)
    text = text.replace("</header>", f'</header>\n<nav class="in-chapter" aria-label="In this chapter"><p class="label">In this chapter</p><ol>{toc_items}</ol></nav>', 1)

    # collect holds and defaults, each with the section it sits in
    def section_at(pos):
        last = None
        for m in re.finditer(r'<h3[^>]*id="([^"]+)"[^>]*>(.*?)</h3>', text[:pos], re.S):
            last = (m.group(1), strip(m.group(2)))
        return last or (sid, title)
    holds = []
    for m in re.finditer(r'<aside class="callout hold">(.*?)</aside>', text, re.S):
        body = re.sub(r'<p class="callout-label">.*?</p>', "", m.group(1), flags=re.S)
        holds.append((section_at(m.start()), strip(body)))
    picks = []
    for m in re.finditer(r'<p class="pick">(.*?)</p>', text, re.S):
        body = re.sub(r"^\s*<strong>[^<]*</strong>\s*", "", m.group(1))
        picks.append((section_at(m.start()), strip(body)))

    chapters[num] = dict(sid=sid, title=title, text=text, holds=holds, picks=picks,
                         figs=len(re.findall(r'<figure class="diagram"', text)))

# body, part by part
body, toc, ptoc = [], [], []
for pn, pname, pdesc, nums in PARTS:
    nums = [n for n in nums if n in chapters]
    if not nums:
        continue
    pid = f"part-{pn.lower()}"
    body.append(f'<div class="part-divider" id="{pid}"><span class="pn">{pn}</span><div><p class="label">Part {pn}</p><h2>{pname}</h2><p>{pdesc}</p></div></div>')
    toc.append(f'      <p class="part">Part {pn} · {pname}</p>\n      <ol>')
    ptoc.append(f'<p class="pt-part">Part {pn} · {pname}</p><ol>')
    for n in nums:
        c = chapters[n]
        body.append(c["text"])
        toc.append(f'        <li><a href="#{c["sid"]}"><span class="n">{n}</span><span>{html.escape(c["title"])}</span></a></li>')
        ptoc.append(f'<li><span class="n">{n}</span><span class="t">{html.escape(c["title"])}</span><span class="pg">{pages.get(c["sid"], "")}</span></li>')
    toc.append("      </ol>")
    ptoc.append("</ol>")


def appendix(aid, letter, title, intro, key, col):
    rows = []
    for n, c in chapters.items():
        for (hid, htitle), txt in c[key]:
            rows.append(f'<tr><td><a href="#{hid}">{n}</a></td><td>{html.escape(htitle)}</td><td>{html.escape(txt)}</td></tr>')
    return (f'<section class="appendix" id="{aid}"><header class="ch-head"><span class="ch-num" aria-hidden="true">{letter}</span>'
            f'<p class="eyebrow">Appendix {letter} · Quick reference</p><h2>{title}</h2><p class="lede">{intro}</p></header>'
            f'<div class="table-wrap"><table class="specs"><thead><tr><th>Ch.</th><th>Section</th><th>{col}</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></section>'), len(rows)

a_html, a_n = appendix("appendix-holds", "A", "Inspection holds",
    "Every hold point in the manual, in build order. Nothing gets covered, poured or closed up until the hold is signed off. Chapter numbers link back to the section.",
    "holds", "Hold")
b_html, b_n = appendix("appendix-defaults", "B", "ESC defaults",
    "The method we choose by default for each decision in the manual, and when we switch. Use it to brief subs and clients; read the chapter for the alternatives.",
    "picks", "ESC default")
body.append('<div class="part-divider" id="part-ref"><span class="pn">R</span><div><p class="label">Reference</p><h2>Appendices</h2><p>Holds and defaults collected from every chapter.</p></div></div>')
body += [a_html, b_html]
toc.append('      <p class="part">Reference</p>\n      <ol>')
toc.append(f'        <li><a href="#appendix-holds"><span class="n">A</span><span>Inspection holds ({a_n})</span></a></li>')
toc.append(f'        <li><a href="#appendix-defaults"><span class="n">B</span><span>ESC defaults ({b_n})</span></a></li>')
toc.append("      </ol>")
ptoc.append('<p class="pt-part">Reference</p><ol>'
            f'<li><span class="n">A</span><span class="t">Inspection holds</span><span class="pg">{pages.get("appendix-holds", "")}</span></li>'
            f'<li><span class="n">B</span><span class="t">ESC defaults</span><span class="pg">{pages.get("appendix-defaults", "")}</span></li></ol>')
print_toc = '<section class="print-toc" aria-hidden="true"><h2>Contents</h2>' + "".join(ptoc) + '</section>'

figs = sum(c["figs"] for c in chapters.values())
out = (root / "template.html").read_text(encoding="utf-8")
for k, v in {
    "{{TOC}}": "\n".join(toc), "{{PRINT_TOC}}": print_toc, "{{BODY}}": "\n".join(body),
    "{{CHAPTER_COUNT}}": str(len(chapters)), "{{PART_COUNT}}": str(len(PARTS)), "{{FIG_COUNT}}": str(figs),
    "{{ISSUE}}": html.escape(issue),
    "{{LOGO_FULL}}": data_uri("esc-logo-full.png"), "{{LOGO_FULL_REV}}": data_uri("esc-logo-full-reverse.png"),
    "{{LOGO_MARK}}": data_uri("esc-mark.png"), "{{LOGO_MARK_REV}}": data_uri("esc-mark-reverse.png"),
}.items():
    out = out.replace(k, v)
(root / "index.html").write_text(out, encoding="utf-8")
print(f"{len(chapters)} chapters, {figs} figures, {a_n} holds, {b_n} defaults, {len(out)//1024} KB")
