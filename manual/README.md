# ESC Building Manual

House reference for how Emory Street Construction builds: one chapter per trade, from preconstruction and demolition through footings, framing, envelope, mechanicals, drywall, tile and millwork. Each chapter compares the different ways to do the work, gives the ESC default, and includes section/plan/elevation drawings as inline SVG.

- `chapters/NN-slug.html` — chapter source (HTML fragments; edit these)
- `template.html` — page shell in ESC house style (logo, green/gold palette, Georgia + Arial)
- `assets/` — ESC logo and mark, standard and reverse (dark-mode) versions
- `build.py` — assembles `index.html`, groups chapters into five parts, and builds the inspection-hold and ESC-default appendices: `python3 manual/build.py "Issue 1 · Nov 2026"`
- `index.html` — built manual (open in a browser)
