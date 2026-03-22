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

print(f'Cube size: {args.cube_size}')
if args.algorithm:
    print(f'Algorithm: {args.algorithm}')

axis_groups = [
    [
        ('yx-35', 'Y Axis + X-35', 'y{angle}x-35'),
    ],
    [
        ('x', 'X Axis', 'x{angle}'),
        ('y', 'Y Axis', 'y{angle}'),
        ('z', 'Z Axis', 'z{angle}'),
    ],
    [
        ('xy', 'X + Y', 'x{angle}y{angle}'),
        ('xz', 'X + Z', 'x{angle}z{angle}'),
        ('yx', 'Y + X', 'y{angle}x{angle}'),
        ('yz', 'Y + Z', 'y{angle}z{angle}'),
        ('zx', 'Z + X', 'z{angle}x{angle}'),
        ('zy', 'Z + Y', 'z{angle}y{angle}'),
    ],
    [
        ('xyz', 'X + Y + Z', 'x{angle}y{angle}z{angle}'),
        ('xzy', 'X + Z + Y', 'x{angle}z{angle}y{angle}'),
        ('yxz', 'Y + X + Z', 'y{angle}x{angle}z{angle}'),
        ('yzx', 'Y + Z + X', 'y{angle}z{angle}x{angle}'),
        ('zxy', 'Z + X + Y', 'z{angle}x{angle}y{angle}'),
        ('zyx', 'Z + Y + X', 'z{angle}y{angle}x{angle}'),
    ],
]

cube_info = f'{args.cube_size}x{args.cube_size}x{args.cube_size}'
if args.algorithm:
    cube_info_title = f'{cube_info} - {args.algorithm}'
    cube_info_html = f'{cube_info} - <code>{args.algorithm}</code>'
else:
    cube_info_title = cube_info
    cube_info_html = cube_info

html_parts: list[str] = []
html_parts.append("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Cube Rotations - CUBE_INFO_PLACEHOLDER</title>
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
  .frame svg { display: block; border-radius: 12px;
               background: linear-gradient(135deg, #3b2667,
                                           #1a1a2e 50%, #1f4068);
               box-shadow: 0 4px 20px rgba(0,0,0,0.5),
                           inset 0 1px 0 rgba(255,255,255,0.08); }
  .controls { margin: 20px 0; display: flex; gap: 16px;
              align-items: center; }
  button { padding: 6px 16px; cursor: pointer; font-size: 14px;
           background: #333; color: #eee; border: 1px solid #555;
           border-radius: 4px; }
  button:hover { background: #444; }
  input[type=range] { width: 300px; }
  input[type=number] { width: 60px; background: #333; color: #eee;
                       border: 1px solid #555; border-radius: 4px;
                       padding: 4px 8px; font-size: 14px; }
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
  .info { font-size: 16px; color: #aaa; margin: 0 0 8px; }
  .info code { color: #ddd; background: #333; padding: 2px 6px;
               border-radius: 3px; }
</style>
</head>
<body>
<div id="loading">
  <div class="spinner"></div>
  <p>Loading cube frames&hellip;</p>
</div>
<div id="content">
<h1>Cube Rotation - All Axes</h1>
<p class="info">CUBE_INFO_HTML_PLACEHOLDER</p>
<div class="controls">
  <label>Angle</label>
  <input type="range" id="angle-slider" min="0" max="359" value="45">
  <input type="number" id="angle-input" min="0" max="359" value="45">
</div>
<div class="controls">
  <label>Speed</label>
  <input type="range" id="speed" min="1" max="100" value="50">
  <span id="speed-val">50 ms</span>
</div>
<div class="controls">
  <button id="play-btn">⏵︎ Play</button>
</div>
<div class="cubes">
""")

for group_idx, group in enumerate(axis_groups):
    if group_idx > 0:
        html_parts.append('</div>\n<div class="cubes">\n')
    for axis_id, label, rotation_fmt in group:
        print(f'Generating {label}...')
        html_parts.append(
            f'<div class="axis-group" data-axis="{axis_id}">\n'
            f'  <h2>{label}</h2>\n',
        )
        for angle in range(360):
            rotation = rotation_fmt.format(angle=angle)
            svg = render_cube(cube, size=200, rotation=rotation)
            # Prefix gradient IDs to avoid collisions between frames
            prefix = f'{axis_id}{angle}-'
            assert svg is not None  # noqa: S101
            svg = svg.replace('id="g-', f'id="{prefix}g-')
            svg = svg.replace('url(#g-', f'url(#{prefix}g-')
            active = ' active' if angle == 45 else ''
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
let current = 45;
let playing = false;
let interval;

const angleSlider = document.getElementById('angle-slider');
const angleInput = document.getElementById('angle-input');

function goTo(angle) {
  groups.forEach(g => {
    const frames = g.querySelectorAll('.frame');
    frames[current].classList.remove('active');
    frames[angle].classList.add('active');
  });
  current = angle;
  angleSlider.value = angle;
  angleInput.value = angle;
}

function step() {
  goTo((current + 1) % 360);
}

function pause() {
  playing = false;
  clearInterval(interval);
  document.getElementById('play-btn').textContent = '⏵︎ Play';
}

function startInterval() {
  const ms = parseInt(document.getElementById('speed').value);
  clearInterval(interval);
  interval = setInterval(step, ms);
}

document.getElementById('loading').remove();
document.getElementById('content').classList.add('ready');

document.getElementById('play-btn').addEventListener('click', () => {
  playing = !playing;
  document.getElementById('play-btn').textContent = (
    playing ? '⏸︎ Pause' : '⏵︎ Play'
  );
  if (playing) startInterval(); else clearInterval(interval);
});

const speedSlider = document.getElementById('speed');
speedSlider.addEventListener('input', () => {
  document.getElementById('speed-val').textContent = speedSlider.value + ' ms';
  if (playing) startInterval();
});

angleSlider.addEventListener('input', () => {
  pause();
  goTo(parseInt(angleSlider.value));
});

angleInput.addEventListener('input', () => {
  const val = parseInt(angleInput.value);
  if (val >= 0 && val <= 359) {
    pause();
    goTo(val);
  }
});
</script>
</body>
</html>
""")

filename = f'rotate_all_axes_{args.cube_size}x{args.cube_size}x{args.cube_size}'
if args.algorithm:
    safe_alg = args.algorithm.replace(' ', '_').replace("'", '-')
    filename += f'_{safe_alg}'
filename += '.html'
out = Path(__file__).parent.parent / filename
html = ''.join(html_parts)
html = html.replace('CUBE_INFO_PLACEHOLDER', cube_info_title)
html = html.replace('CUBE_INFO_HTML_PLACEHOLDER', cube_info_html)
out.write_text(html)
print(f'Saved {out}')
