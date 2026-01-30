"""Type definitions for the cubing-algs library."""
import re
from typing import Literal

# Piece type for corners and edges
type PieceType = Literal['corner', 'edge']

# Cubie arrays - permutation and orientation
type Permutation = list[int]
type Orientation = list[int]

# Cube cubies tuple (cp, co, ep, eo)
type CubeCubies = tuple[Permutation, Orientation, Permutation, Orientation]

# Regex pattern type
type RegexPattern = re.Pattern[str]
