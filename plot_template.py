"""
Matplotlib configuration templates matching two LaTeX targets:

- report : \\documentclass[a4paper, 12pt]{report} + \\usepackage[margin=2.5cm]{geometry}
- beamer : \\documentclass[aspectratio=169]{beamer}   (16:9 widescreen, not 4:3)

Usage:
    from plot_template import configure_report, configure_beamer, backToDefaultMatplotlib

    configure_report(width="full")   # figure spanning the full report textwidth
    configure_report(width="half")   # two side-by-side figures at report font size
    configure_beamer(width="full")   # full-slide figure, 16:9
    configure_beamer(width="half")   # two side-by-side figures on a slide

    ... plt.plot(...) ...
    backToDefaultMatplotlib()        # reset rcParams when done
"""

import matplotlib.pyplot as plt
import scienceplots  # noqa: F401 - side effect: registers the "science" style

PT_TO_IN = 1 / 72.27

# --- measured constants -----------------------------------------------------
# These come from actually compiling the target documents and reading
# \the\textwidth / \the\textheight from the log - not guessed. If you change
# margins, font size, or beamer theme, remeasure with the snippet below.
#
#   \typeout{TEXTWIDTH-PT=\the\textwidth}
#   \typeout{TEXTHEIGHT-PT=\the\textheight}
#
# Report: \documentclass[a4paper, 12pt]{report} + \usepackage[margin=2.5cm]{geometry}
REPORT_TEXTWIDTH_PT = 455.24411

# Beamer: \documentclass[aspectratio=169]{beamer}, plain theme (no navigation
# chrome). A theme with a title bar / footline eats into \textheight - if you
# use one, remeasure inside an actual \frame and pass textheight_pt=... below.
BEAMER_TEXTWIDTH_PT = 398.3386
BEAMER_TEXTHEIGHT_PT = 252.0748

REPORT_BASE_FONT_SIZE = 12  # \normalsize of the 12pt report class
BEAMER_BASE_FONT_SIZE = 11  # beamer's default base font size

_WIDTH_PRESETS = {"full": 1.0, "half": 0.48}


def _resolve_width_fraction(width):
    if isinstance(width, str):
        try:
            return _WIDTH_PRESETS[width]
        except KeyError:
            raise ValueError(f"width must be 'full', 'half', or a float, got {width!r}")
    return float(width)


def _apply_font_rcparams(base_font_size, font_family):
    plt.style.use(["science"])

    normal = base_font_size
    small = normal - 2
    plt.rcParams.update({
        "font.size": normal,
        "axes.titlesize": normal,
        "axes.labelsize": normal,
        "legend.fontsize": small,
        "xtick.labelsize": normal,
        "ytick.labelsize": normal,
        "figure.constrained_layout.use": True,
        "lines.linewidth": 1.0,
        "axes.linewidth": 0.6,
        "legend.frameon": True,
        "legend.edgecolor": "black",
        "legend.framealpha": 1.0,
        "patch.linewidth": 0.5,
    })
    # "science" already gives serif + usetex + amsmath/amssymb, which renders
    # as Computer Modern by default - only beamer's sans-serif needs an override.
    if font_family == "sans-serif":
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": ["Computer Modern Sans Serif"],
            # Matches beamer's default sans-serif math style.
            "text.latex.preamble": r"\usepackage{sansmath}\sansmath",
        })


def configure_report(width="full", aspect_ratio=1.6, bigger_font_by=0, textwidth_pt=None):
    """
    Configure Matplotlib to match \\documentclass[a4paper, 12pt]{report}.

    width: "full" (\\textwidth), "half" (two figures side by side, 0.48\\textwidth),
           or a float fraction of \\textwidth (e.g. 0.3 for a third).
    aspect_ratio: fig_width / fig_height (default 1.6, close to the golden ratio).
    textwidth_pt: override REPORT_TEXTWIDTH_PT if your margins differ.
    """
    textwidth_pt = textwidth_pt or REPORT_TEXTWIDTH_PT
    fraction = _resolve_width_fraction(width)
    fig_width = textwidth_pt * PT_TO_IN * fraction
    fig_height = fig_width / aspect_ratio

    base_font_size = REPORT_BASE_FONT_SIZE + bigger_font_by
    _apply_font_rcparams(base_font_size, "serif")
    plt.rcParams.update({"figure.figsize": (fig_width, fig_height)})
    print(f"Plot configured for report ({width}): {fig_width:.2f}\"x{fig_height:.2f}\" at {base_font_size}pt.")


def configure_beamer(width="full", caption_spacer=0.72, aspect_ratio=None,
                      bigger_font_by=0, textwidth_pt=None, textheight_pt=None):
    """
    Configure Matplotlib to match \\documentclass[aspectratio=169]{beamer} (16:9).

    width: "full" (\\textwidth), "half" (two figures side by side, 0.48\\textwidth),
           or a float fraction of \\textwidth.
    caption_spacer: fraction of \\textheight given to the plot, leaving room
                     below it for a caption (and above for the frame title).
                     Ignored if aspect_ratio is given.
    aspect_ratio: fig_width / fig_height; overrides caption_spacer-based height.
    textwidth_pt / textheight_pt: override the measured beamer constants if
                     you use a theme with different margins.
    """
    textwidth_pt = textwidth_pt or BEAMER_TEXTWIDTH_PT
    textheight_pt = textheight_pt or BEAMER_TEXTHEIGHT_PT
    fraction = _resolve_width_fraction(width)
    fig_width = textwidth_pt * PT_TO_IN * fraction

    if aspect_ratio is not None:
        fig_height = fig_width / aspect_ratio
    else:
        fig_height = textheight_pt * PT_TO_IN * caption_spacer

    base_font_size = BEAMER_BASE_FONT_SIZE + bigger_font_by
    _apply_font_rcparams(base_font_size, "sans-serif")
    plt.rcParams.update({"figure.figsize": (fig_width, fig_height)})
    print(f"Plot configured for beamer 16:9 ({width}): {fig_width:.2f}\"x{fig_height:.2f}\" at {base_font_size}pt.")


def backToDefaultMatplotlib():
    plt.rcdefaults()


# --- optional: full LaTeX pgf export (publication-quality, no dvipng) -------
# Use once a plot is final and ready for the actual report/beamer, instead of
# the usetex rcParams set by configure_report/configure_beamer above.
#
# import matplotlib as mpl
# mpl.use("pgf")
# plt.rcParams.update({
#     "pgf.texsystem": "pdflatex",
#     "pgf.rcfonts": False,   # don't let matplotlib override fonts from rcParams
# })
# ... then call configure_report(...) or configure_beamer(...) as usual, and
# plt.savefig("figure.pgf") to \input{figure.pgf} directly in LaTeX.
