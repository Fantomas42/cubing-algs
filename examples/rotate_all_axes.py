"""Generate an HTML file showing the cube rotating on X, Y, and Z axes."""
# ruff: noqa: T201
import argparse
from pathlib import Path

from cubing_algs.display.image import render_cube
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    'algorithm',
    nargs='?',
    default='',
    help='Algorithm to apply before rendering',
)
parser.add_argument(
    '--cube-size',
    type=int,
    default=3,
    help='Cube size (2 for 2x2, 3 for 3x3, etc.)',
)
args = parser.parse_args()

cube = VCube(size=args.cube_size)
if args.algorithm:
    cube.rotate(parse_moves(args.algorithm, trust_input=False))

print(f'Algorithm: {args.algorithm}, Cube size: {args.cube_size}')

axes = [
    ('x', 'X Axis', 'x{angle}'),
    ('y', 'Y Axis', 'y{angle}'),
    ('z', 'Z Axis', 'z{angle}'),
    ('xyz', 'X + Y + Z', 'x{angle}y{angle}z{angle}'),
]

html_parts: list[str] = []
html_parts.append("""\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Cube Rotations - All Axes</title>
<style>
  body { background: #1a1a1a; color: #eee; font-family: sans-serif;
         display: flex; flex-direction: column; align-items: center;
         margin: 20px; }
  .cubes { display: flex; gap: 40px; flex-wrap: wrap;
           justify-content: center; }
  .axis-group { text-align: center; }
  .axis-group h2 { margin-bottom: 8px; }
  .angle { font-size: 14px; color: #aaa; margin-top: 4px;
           font-variant-numeric: tabular-nums; }
  .frame { display: none; }
  .frame.active { display: block; }
  .controls { margin: 20px 0; display: flex; gap: 16px;
              align-items: center; }
  button { padding: 6px 16px; cursor: pointer; font-size: 14px;
           background: #333; color: #eee; border: 1px solid #555;
           border-radius: 4px; }
  button:hover { background: #444; }
  input[type=range] { width: 300px; }
  #loading { position: fixed; inset: 0; background: #1a1a1a;
             display: flex; flex-direction: column; align-items: center;
             justify-content: center; z-index: 100; }
  #loading .spinner { width: 48px; height: 48px;
             border: 4px solid #444; border-top-color: #eee;
             border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  #loading p { margin-top: 16px; font-size: 18px; color: #aaa; }
  #content { visibility: hidden; display: flex; flex-direction: column;
             align-items: center; width: 100%; }
  #content.ready { visibility: visible; }
</style>
</head>
<body>
<div id="loading">
  <div class="spinner"></div>
  <p>Loading cube frames&hellip;</p>
</div>
<div id="content">
<h1>Cube Rotation &mdash; All Axes</h1>
<div class="controls">
  <button id="play-btn">Pause</button>
  <input type="range" id="speed" min="1" max="100" value="50">
  <span id="speed-val">50 ms</span>
</div>
<div class="cubes">
""")

for axis_id, label, rotation_fmt in axes:
    print(f'Generating {label}...')
    html_parts.append(
        f'<div class="axis-group" data-axis="{axis_id}">\n'
        f'  <h2>{label}</h2>\n'
        f'  <div class="angle" data-angle-display>0°</div>\n',
    )
    for angle in range(360):
        rotation = rotation_fmt.format(angle=angle)
        svg = render_cube(cube, size=200, rotation=rotation)
        # Prefix gradient IDs to avoid collisions between frames
        prefix = f'{axis_id}{angle}-'
        assert svg is not None  # noqa: S101
        svg = svg.replace('id="g-', f'id="{prefix}g-')
        svg = svg.replace('url(#g-', f'url(#{prefix}g-')
        active = ' active' if angle == 0 else ''
        html_parts.append(
            f'  <div class="frame{active}" data-angle="{angle}">'
            f'{svg}</div>\n',
        )
    html_parts.append('</div>\n')

html_parts.append("""\
</div>
</div>
<script>
const groups = document.querySelectorAll('.axis-group');
let current = 0;
let playing = true;
let interval;

function step() {
  groups.forEach(g => {
    const frames = g.querySelectorAll('.frame');
    frames[current].classList.remove('active');
  });
  current = (current + 1) % 360;
  groups.forEach(g => {
    const frames = g.querySelectorAll('.frame');
    frames[current].classList.add('active');
    g.querySelector('[data-angle-display]').textContent = current + '°';
  });
}

function startInterval() {
  const ms = parseInt(document.getElementById('speed').value);
  clearInterval(interval);
  interval = setInterval(step, ms);
}

document.getElementById('loading').remove();
document.getElementById('content').classList.add('ready');
startInterval();

document.getElementById('play-btn').addEventListener('click', () => {
  playing = !playing;
  document.getElementById('play-btn').textContent = playing ? 'Pause' : 'Play';
  if (playing) startInterval(); else clearInterval(interval);
});

const speedSlider = document.getElementById('speed');
speedSlider.addEventListener('input', () => {
  document.getElementById('speed-val').textContent = speedSlider.value + ' ms';
  if (playing) startInterval();
});
</script>
</body>
</html>
""")

out = Path(__file__).parent.parent / 'rotate_all_axes.html'
out.write_text(''.join(html_parts))
print(f'Saved {out}')
