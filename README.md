# plot_template

![version](https://img.shields.io/badge/version-0.1.0-blue)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![matplotlib](https://img.shields.io/badge/matplotlib-required-blue)

Matplotlib configuration helpers that make your figures match the typography
and page geometry of two common LaTeX targets:

- **report** — `\documentclass[a4paper, 12pt]{report}` with
  `\usepackage[margin=2.5cm]{geometry}`
- **beamer** — `\documentclass[aspectratio=169]{beamer}` (16:9 widescreen)

Figures come out sized (in inches) and font-scaled so that when you
`\includegraphics` them at full width, text in the plot matches the
surrounding document's font size exactly — no more tiny/huge axis labels.

## Requirements

- `matplotlib`
- [`scienceplots`](https://github.com/garrett361/SciencePlots) (provides the
  `"science"` style used under the hood)
- A working LaTeX installation (the styles use `usetex=True` for Computer
  Modern fonts and proper math rendering)

```bash
pip install matplotlib scienceplots
```

## Installation (importable from anywhere)

This repo is set up as an installable package ([pyproject.toml](pyproject.toml)),
so you can install it once into a virtualenv and then `import plot_template`
from any project using that venv — no `sys.path` hacks or copying the file
around needed.

```bash
python3 -m venv .venv
source .venv/bin/activate          # or .venv\Scripts\activate on Windows
pip install -e /path/to/plot_template
```

`-e` (editable) means edits to `plot_template.py` take effect immediately
without reinstalling — useful while you're still tweaking the measured
constants. Drop `-e` for a normal, frozen install.

To make it available in every venv you create (instead of one at a time),
publish it somewhere pip can reach (e.g. a private Git repo) and install via:

```bash
pip install git+https://github.com/LucienLD/plot_template.git
```

then repeat the `pip install` step in each new venv.

## Quick start

```python
from plot_template import configure_report, configure_beamer, backToDefaultMatplotlib
import matplotlib.pyplot as plt

configure_report(width="full")   # size/fonts for a report-class document

plt.plot(x, y)
plt.savefig("figure.pdf")

backToDefaultMatplotlib()        # reset rcParams back to matplotlib defaults
```

Import the two `configure_*` functions for whichever document you're
targeting, call one before plotting, and call `backToDefaultMatplotlib()`
when you're done (e.g. before making a plot for a different target, or at
the end of a script/notebook cell).

## Functions

### `configure_report(width="full", aspect_ratio=1.6, bigger_font_by=0, textwidth_pt=None)`

Matches `\documentclass[a4paper, 12pt]{report}` + `margin=2.5cm` geometry.

- `width`: `"full"` (spans `\textwidth`), `"half"` (for two side-by-side
  figures, `0.48\textwidth`), or any float fraction of `\textwidth` (e.g.
  `0.3`).
- `aspect_ratio`: `fig_width / fig_height` (default `1.6`, close to the
  golden ratio).
- `bigger_font_by`: add this many points to the base 12pt font (e.g. `2` for
  a slightly larger caption font).
- `textwidth_pt`: override the measured textwidth if your margins differ
  from the default (see [Remeasuring](#remeasuring-for-a-different-layout)).

### `configure_beamer(width="full", caption_spacer=0.72, aspect_ratio=None, bigger_font_by=0, textwidth_pt=None, textheight_pt=None)`

Matches `\documentclass[aspectratio=169]{beamer}` with a plain theme (no
navigation chrome).

- `width`: same semantics as `configure_report`.
- `caption_spacer`: fraction of `\textheight` given to the plot, leaving
  room below for a caption and above for the frame title. Ignored if
  `aspect_ratio` is given.
- `aspect_ratio`: overrides `caption_spacer`-based height with a fixed
  `fig_width / fig_height`.
- `bigger_font_by`: add this many points to the base 11pt beamer font.
- `textwidth_pt` / `textheight_pt`: override the measured beamer constants
  (see below).

### `backToDefaultMatplotlib()`

Resets `matplotlib.rcParams` to their defaults via `plt.rcdefaults()`. Call
this between switching targets, or at the end of your plotting code.

## Examples

```python
# Two figures side by side in a report, slightly bigger font for readability
configure_report(width="half", bigger_font_by=1)
plt.plot(x, y)
plt.savefig("fig_left.pdf")

# Full-slide beamer figure with a fixed 4:3-ish aspect ratio instead of the
# caption-aware default height
configure_beamer(width="full", aspect_ratio=1.33)
plt.plot(x, y)
plt.savefig("slide_fig.pdf")
```

Then in LaTeX:

```latex
\includegraphics[width=\textwidth]{fig_left.pdf}
```

## Remeasuring for a different layout

The default constants (`REPORT_TEXTWIDTH_PT`, `BEAMER_TEXTWIDTH_PT`,
`BEAMER_TEXTHEIGHT_PT` in [plot_template.py](plot_template.py)) were obtained
by actually compiling the target documents, not guessed. If you change
margins, font size, or beamer theme, remeasure by adding this to your `.tex`
file (inside a `\frame` for beamer, to account for the title bar):

```latex
\typeout{TEXTWIDTH-PT=\the\textwidth}
\typeout{TEXTHEIGHT-PT=\the\textheight}
```

Then read the values (in pt) from the compile log and either update the
constants in `plot_template.py`, or pass them directly:

```python
configure_report(textwidth_pt=345.0)
configure_beamer(textwidth_pt=307.28987, textheight_pt=230.2318)
```

## Publication-quality export (optional)

Once a plot is final, you can skip matplotlib's `usetex` rendering and
export directly to a `.pgf` file for `\input` in LaTeX — see the commented
snippet at the bottom of [plot_template.py](plot_template.py):

```python
import matplotlib as mpl
mpl.use("pgf")
plt.rcParams.update({
    "pgf.texsystem": "pdflatex",
    "pgf.rcfonts": False,
})
configure_report(width="full")
plt.plot(x, y)
plt.savefig("figure.pgf")
```

Then in LaTeX: `\input{figure.pgf}`.