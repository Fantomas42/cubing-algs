"""
Generate a stickering demo gallery, mirroring cubing.js' cube3d-stickering.

For every display mode declared in ``cubing_algs.display.mode.MODE_CONFIGS``
(plus the bare ``full`` render), apply a representative algorithm and render
the cube with ``VCube.image()``. The SVGs are laid out in an HTML grid so the
result can be opened side by side with cubing.js' own stickering demo to
compare renders and complete or correct the masks/modes.

Algorithms are borrowed from cubing.js' ``stickering-demo-algs.ts`` whenever a
cubing_algs mode maps onto one of its stickerings, so matching cases line up.
"""
# ruff: noqa: T201
import argparse
from pathlib import Path
from urllib.parse import quote_plus

from cubing_algs.display.mode import MODE_CONFIGS
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.invert import invert_moves
from cubing_algs.vcube import VCube

# Generic scramble for whole-cube render styles (no stage-specific mask).
RENDER_STYLE_ALG = "B' U' B2 U' B2 U F2 U' B2 L2 U R2 U2 R' F2 U2 B U' R2 F D2"

# Per-mode illustrative algorithm and the cubing.js stickering it echoes,
# grouped by demo section for layout control in the HTML gallery.
# (group title, [(mode, algorithm, cubing.js counterpart), ...])
DEMOS: list[tuple[str, list[tuple[str, str, str]]]] = [
    ('Cross', [
        ('cross-top', "y2 (y' R)5 D", '(no direct eq)'),
        ('cross-bottom', "(y' R)5 D", 'Cross'),
    ]),
    ('F2L', [
        ('f2l', "R2' u R2 u' R2'", 'F2L'),
        ('af2l', "R2' u R2 u' R2'", 'F2L'),
        ('f2l+cll', "R U R' U' R U R' U R U' R'", 'CLS'),
        ('f2l+ell', "M U' M' U2 M U' M'", 'ELL'),
    ]),
    ('Last Layer', [
        ('ll', "R' F R F2' U F R U R' F' U' F", 'LL'),
        ('oll', "r U R' U R U2 r'", 'OLL'),
        ('pll', "R U R' U' R' F R2 U' R' U' R U R' F'", 'PLL'),
    ]),
    ('Edge Orientation', [
        ('eo', "B U B' D F R' L D'", 'EO'),
        ('eo-cross', "B U B' D F R' L D'", 'EOcross'),
        ('eo-line', "B U B' D F R' L D'", 'EOline'),
        ('eo-slice', "B U B' D F R' L D'", '(no cubing.js eq)'),
        ('eo-edge', "B U B' D F R' L D'", '(no cubing.js eq)'),
    ]),
    ('Roux', [
        ('cmll', "F R U R' U' F'", 'CMLL'),
        ('lse', "U M2' U' M2'", 'L6E'),
        ('l6eo', "U M2' U' M2'", 'L6EO'),
        ('l10p', "U M2' U' M2'", 'L10P'),
    ]),
    ('Render Styles', [
        ('visible', RENDER_STYLE_ALG, '(render style)'),
        ('dimmed', RENDER_STYLE_ALG, '(render style)'),
        ('masked', RENDER_STYLE_ALG, '(render style)'),
        ('hidden', RENDER_STYLE_ALG, '(render style)'),
        ('oriented', RENDER_STYLE_ALG, '(render style)'),
    ]),
]


PAGE_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>cubing_algs stickering demo</title>
<style>
body {{ background: #f5f5f7; color: #222; font-family: sans-serif;
       padding: 2rem 3rem; margin: 0; }}
h1 {{ margin-top: 0; }}
.group {{ margin-bottom: 3rem; }}
.group-title {{ border-bottom: 1px solid #ccc; padding-bottom: .5rem; }}
.content {{ display: flex; flex-wrap: wrap; gap: 1.5rem; }}
.case {{ background: #fff; border: 1px solid #ddd; border-radius: 8px;
        padding: 1rem; width: 220px; text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, .08);
        transition: transform .15s ease, box-shadow .15s ease; }}
.case:hover {{ transform: translateY(-4px);
             box-shadow: 0 6px 12px rgba(0, 0, 0, .15); }}
.case h3 {{ margin: 0 0 .4rem; font-size: 1.3rem; text-transform: uppercase; }}
.counterpart {{ color: #666; font-size: 1rem; margin-bottom: .75rem; }}
.cube svg {{ width: 100%; height: auto; }}
.algo {{ margin: .75rem 0 0; padding: .5rem .6rem .3rem .6rem;
        background: #2d2d2d; border-radius: 4px;
        font-family: 'Courier New', monospace; font-size: .9rem;
        line-height: 1.4; letter-spacing: .02em; text-align: left;
        color: #eee; cursor: pointer;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.algo.expanded {{ white-space: normal; overflow: visible;
                 text-overflow: clip; word-break: break-word; }}
.tt-link {{ display: inline-block; margin-top: .5rem; font-size: .85rem;
           color: #0a58ca; text-decoration: none; }}
.tt-link:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>cubing_algs stickering modes</h1>
{groups}
</body>
61;7600;1c/html>
"""

GROUP_TEMPLATE = """\
<section class="group">
<h2 class="group-title">{title}</h2>
<div class="content">
{cases}
</div>
</section>
"""


def build_demo(image_size: int, rotation: str, term_timer_url: str) -> str:
    """
    Render every demo case and assemble them into an HTML gallery.

    Args:
        image_size: Output dimension in pixels for each cube SVG.
        rotation: Camera rotation string for the 3D views.
        term_timer_url: Base URL of the term-timer render server, used to
            build a per-case link reproducing the same cube state.

    Returns:
        A complete HTML document as a string.

    """
    known_modes = set(MODE_CONFIGS)
    groups: list[str] = []

    for title, demos in DEMOS:
        cases: list[str] = []

        for mode, alg, counterpart in demos:
            if mode not in known_modes:
                print(f'Skipping unknown mode: { mode }')
                continue

            setup = invert_moves(parse_moves(alg, trust_input=False))

            cube = VCube()
            cube.rotate('z2')
            cube.rotate(setup)

            svg = cube.image(
                mode=mode,
                image_size=image_size,
                rotation=rotation,
                layout='mirror',
            )

            render_alg = quote_plus(f'z2 { setup }')
            link = (
                f'{ term_timer_url }/cube/render/'
                f'?algorithm={ render_alg }&amp;m={ mode }&amp;o=UF'
            )

            cases.append(
                '<div class="case">'
                f'<h3>{ mode }</h3>'
                f'<div class="counterpart">cubing.js: { counterpart }</div>'
                f'<div class="cube">{ svg }</div>'
                '<pre class="algo" '
                'onclick="this.classList.toggle(\'expanded\')">'
                f'{ alg }</pre>'
                f'<a class="tt-link" href="{ link }" '
                'target="_blank" rel="noopener">debug in term-timer ↗</a>'
                '</div>',
            )

        groups.append(
            GROUP_TEMPLATE.format(title=title, cases=''.join(cases)),
        )

    return PAGE_TEMPLATE.format(groups=''.join(groups))


def main() -> None:
    """Parse arguments and write the stickering demo gallery to disk."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-s', '--image-size',
        type=int,
        default=160,
        help='Image size in pixels for each cube (default: 160)',
    )
    parser.add_argument(
        '-r', '--rotation',
        default='y45x-35',
        help='Camera rotation for the 3D views (default: y45x-35)',
    )
    parser.add_argument(
        '-o', '--output',
        default='stickering_demo.html',
        help='Output HTML file path (default: stickering_demo.html)',
    )
    parser.add_argument(
        '-t', '--term-timer-url',
        default='http://localhost:8333',
        help='Base URL of the term-timer render server '
             '(default: http://localhost:8333)',
    )
    args = parser.parse_args()

    html = build_demo(args.image_size, args.rotation, args.term_timer_url)

    case_count = sum(len(demos) for _, demos in DEMOS)

    out = Path(args.output)
    out.write_text(html, encoding='utf-8')
    print(f'Saved { out } ({ case_count } cases)')


if __name__ == '__main__':
    main()
