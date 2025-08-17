# Cubing Algs

Python module providing tools for cubing algorithm manipulations.

## Installation

```bash
pip install cubing-algs
```

## Features

- Parse and validate Rubik's cube algorithm notation
- Transform algorithms (mirror, compress, rotate, etc.)
- Calculate metrics (HTM, QTM, STM, ETM, QSTM)
- Support for wide moves, slice moves, and rotations
- Big cubes notation support
- SiGN notation support

## Basic Usage

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves
from cubing_algs.transform.size import expand_moves

algo = parse_moves("F R U2 F'")
print(algo.transform(mirror_moves, expand_moves))
# F U U R' F'
```

## Parsing

Parse a string of moves into an `Algorithm` object:

```python
from cubing_algs.parsing import parse_moves

# Basic parsing
algo = parse_moves("R U R' U'")

# Parsing multiple formats
algo = parse_moves("R U R` U`")       # Backtick notation
algo = parse_moves("R:U:R':U'")       # With colons
algo = parse_moves("R(U)R'[U']")      # With brackets/parentheses
algo = parse_moves("3Rw 3-4u' 2R2")   # For big cubes

# Parse CFOP style (removes starting/ending U/y rotations)
from cubing_algs.parsing import parse_moves_cfop
algo = parse_moves_cfop("y U R U R' U'")  # Will remove the initial y
```

## Transformations

Apply various transformations to algorithms:

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves
from cubing_algs.transform.size import compress_moves
from cubing_algs.transform.size import expand_moves
from cubing_algs.transform.sign import sign_moves
from cubing_algs.transform.sign import unsign_moves
from cubing_algs.transform.rotation import remove_final_rotations
from cubing_algs.transform.slice import reslice_moves
from cubing_algs.transform.slice import unslice_wide_moves
from cubing_algs.transform.fat import refat_moves
from cubing_algs.transform.fat import unfat_rotation_moves
from cubing_algs.transform.symmetry import (
    symmetry_m_moves,
    symmetry_s_moves,
    symmetry_e_moves,
    symmetry_c_moves
)
from cubing_algs.transform.offset import (
    offset_x_moves,
    offset_y_moves,
    offset_z_moves
)
from cubing_algs.transform.degrip import (
    degrip_x_moves,
    degrip_y_moves,
    degrip_z_moves,
    degrip_full_moves
)

algo = parse_moves("R U R' U'")

# Mirror an algorithm
mirrored = algo.transform(mirror_moves)  # U' R U' R'

# Compression/Expansion
compressed = algo.transform(compress_moves)  # Optimize with cancellations
expanded = algo.transform(expand_moves)  # Convert double moves to single pairs

# SiGN notation
sign = algo.transform(sign_moves)  # Convert to r, u, f notation
standard = algo.transform(unsign_moves)  # Convert to Rw, Uw, Fw notation

# Remove final rotations
clean = algo.transform(remove_final_rotations)  # Remove trailing x, y, z moves

# Slice moves
wide = algo.transform(unslice_wide_moves)  # M -> r' R, S -> f F', E -> u' U
resliced = algo.transform(reslice_moves)  # L' R -> M x, etc.

# Fat moves
rotation = algo.transform(unfat_rotation_moves)  # f r u -> B z L x D y
refated = algo.transform(refat_moves)  # L x -> r, etc.

# Symmetry
m_sym = algo.transform(symmetry_m_moves)  # M-slice symmetry (L<->R)
s_sym = algo.transform(symmetry_s_moves)  # S-slice symmetry (F<->B)
e_sym = algo.transform(symmetry_e_moves)  # E-slice symmetry (U<->D)
c_sym = algo.transform(symmetry_c_moves)  # Combined M and S symmetry

# Offset (change viewpoint)
x_offset = algo.transform(offset_x_moves)  # As if rotated with x
y_offset = algo.transform(offset_y_moves)  # As if rotated with y
z_offset = algo.transform(offset_z_moves)  # As if rotated with z

# Degrip (move rotations to the end)
x_degrip = algo.transform(degrip_x_moves)  # Move x rotations to the end
y_degrip = algo.transform(degrip_y_moves)  # Move y rotations to the end
z_degrip = algo.transform(degrip_z_moves)  # Move z rotations to the end
full_degrip = algo.transform(degrip_full_moves)  # Move all rotations to the end
```

## Metrics

Compute algorithm metrics:

```python
from cubing_algs.parsing import parse_moves

algo = parse_moves("R U R' U' R' F R2 U' R' U' R U R' F'")

# Access metrics
print(algo.metrics)
# {
#   'rotations': 0,
#   'outer_moves': 14,
#   'inner_moves': 0,
#   'htm': 14,
#   'qtm': 16,
#   'stm': 14,
#   'etm': 14,
#   'qstm': 16,
#   'generators': ['R', 'U', 'F']
# }

# Individual metrics
print(f"HTM: {algo.metrics['htm']}")
print(f"QTM: {algo.metrics['qtm']}")
print(f"STM: {algo.metrics['stm']}")
print(f"ETM: {algo.metrics['etm']}")
print(f"QSTM: {algo.metrics['qstm']}")
print(f"Generators: {', '.join(algo.metrics['generators'])}")
```

## Move Object

The `Move` class represents a single move:

```python
from cubing_algs.move import Move

move = Move("R")
move2 = Move("R2")
move3 = Move("R'")
wide = Move("Rw")
wide_sign = Move("r")
rotation = Move("x")

# Properties
print(move.base_move)  # R
print(move.modifier)   # ''

# Checking move type
print(move.is_rotation_move)   # False
print(move.is_outer_move)      # True
print(move.is_inner_move)      # False
print(move.is_wide_move)       # False

# Checking modifiers
print(move.is_clockwise)         # True
print(move.is_counter_clockwise) # False
print(move.is_double)            # False

# Transformations
print(move.inverted)   # R'
print(move.doubled)    # R2
print(wide.to_sign)    # r
print(wide_sign.to_standard)  # Rw
```

## Optimization Functions

The module provides several optimization functions to simplify algorithms:

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.optimize import (
    optimize_repeat_three_moves,
    optimize_do_undo_moves,
    optimize_double_moves,
    optimize_triple_moves
)

algo = parse_moves("R R R")
optimized1 = algo.transform(optimize_repeat_three_moves)  # R'

algo = parse_moves("R R'")
optimized2 = algo.transform(optimize_do_undo_moves)  # (empty)

algo = parse_moves("R R")
optimized3 = algo.transform(optimize_double_moves)  # R2

algo = parse_moves("R R2")
optimized4 = algo.transform(optimize_triple_moves)  # R'
```

## Chaining Transformations

Multiple transformations can be chained together:

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves
from cubing_algs.transform.size import compress_moves
from cubing_algs.transform.symmetry import symmetry_m_moves

algo = parse_moves("R U R' U' R' F R F'")
result = algo.transform(mirror_moves, compress_moves, symmetry_m_moves)

# Same as:
# result = algo.transform(mirror_moves)
# result = result.transform(compress_moves)
# result = result.transform(symmetry_m_moves)
```

## Transform until fixed point

Chained transformations can be run until a fixed point:

```python
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves

algo = parse_moves("R R F F' R2 U F2")
result = algo.transform(optimize_do_undo_moves, optimize_double_moves)
# R2 R2 U F2

algo = parse_moves("R R F F' R2 U F2")
result = algo.transform(optimize_do_undo_moves, optimize_double_moves, to_fixpoint=True)
# U F2
```

## Understanding Metrics

The module calculates the following metrics:

- **HTM (Half Turn Metric)**: Counts quarter turns as 1, half turns as 1
- **QTM (Quarter Turn Metric)**: Counts quarter turns as 1, half turns as 2
- **STM (Slice Turn Metric)**: Counts both face turns and slice moves as 1
- **ETM (Execution Turn Metric)**: Counts all moves including rotations
- **QSTM (Quarter Slice Turn Metric)**: Counts quarter turns as 1, slice quarter turns as 1, half turns as 2

## Examples

### Generating a mirror of an OLL algorithm

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves

oll = parse_moves("r U R' U' r' F R F'")
oll_mirror = oll.transform(mirror_moves)
print(oll_mirror)  # F' R' F r U R U' r'
```

### Converting a wide move algorithm to SiGN notation

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.sign import sign_moves

algo = parse_moves("Rw U R' U' Rw' F R F'")
sign = algo.transform(sign_moves)
print(sign)  # r U R' U' r' F R F'
```

### Finding the shortest form of an algorithm

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.size import compress_moves

algo = parse_moves("R U U U R' R R F F' F F")
compressed = algo.transform(compress_moves)
print(compressed)  # R U' R2 F2
```

### Changing the viewpoint of an algorithm

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.offset import offset_y_moves

algo = parse_moves("R U R' U'")
y_rotated = algo.transform(offset_y_moves)
print(y_rotated)  # F R F' R'
```

### De-gripping a fingertrick sequence

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.degrip import degrip_y_moves

algo = parse_moves("y F R U R' U' F'")
degripped = algo.transform(degrip_y_moves)
print(degripped)  # R F R F' R' y
```
