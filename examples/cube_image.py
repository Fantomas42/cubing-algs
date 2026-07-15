"""
Generate an SVG image of the cube.

Supports configurable rotation and algorithm.
"""
import argparse
from pathlib import Path

from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    'algorithm',
    nargs='?',
    default='',
    help='Algorithm to apply before rendering (e.g. "R U R\' U\'")',
)
parser.add_argument(
    '-r', '--rotation',
    default='y45x-35',
    help='Camera rotation string (default: y45x-34)',
)
parser.add_argument(
    '-s', '--image-size',
    type=int,
    default=200,
    help='Image size in pixels (default: 200)',
)
parser.add_argument(
    '-n', '--cube-size',
    type=int,
    default=3,
    help='Cube size: 2 for 2x2, 3 for 3x3, etc. (default: 3)',
)
parser.add_argument(
    '-l', '--layout',
    choices=['', 'top'],
    default='',
    help='Rendering mode: 3d perspective or top face plan view (default: 3d)',
)
parser.add_argument(
    '-o', '--output',
    help='Output file path (default: cube.svg in current directory)',
)
args = parser.parse_args()

cube = VCube(size=args.cube_size)
if args.algorithm:
    cube.rotate(parse_moves(args.algorithm, trust_input=False))

svg = cube.image(
    image_size=args.image_size,
    rotation=args.rotation,
    layout=args.layout,
)

out = Path(args.output) if args.output else Path('cube.svg')
out.write_text(svg)
print(f'Saved {out}')
