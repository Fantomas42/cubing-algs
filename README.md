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
- Display and tracks facelets on 3x3x3 cube
- Commutator and conjugate notation support
- Pattern library with classic cube patterns
- Scramble generation for various cube sizes
- Virtual cube simulation and state tracking

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

## Commutators and Conjugates

The module supports advanced notation for commutators and conjugates:

```python
from cubing_algs.parsing import parse_moves

# Commutator notation [A, B] = A B A' B'
algo = parse_moves("[R, U]")  # Expands to: R U R' U'

# Conjugate notation [A: B] = A B A'
algo = parse_moves("[R: U]")  # Expands to: R U R'

# Nested commutators and conjugates
algo = parse_moves("[R, [U, D]]")  # Nested commutator
algo = parse_moves("[R: [U, D]]")  # Conjugate with commutator

# Complex examples
algo = parse_moves("[R U: F]")     # R U F U' R'
algo = parse_moves("[R, U D']")    # R U D' R' D U'
```

**Supported notation:**
- `[A, B]` - Commutator: expands to `A B A' B'`
- `[A: B]` - Conjugate: expands to `A B A'`
- Nested brackets are fully supported
- Can be mixed with regular move notation

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

## Cube Patterns

Access a library of classic cube patterns:

```python
from cubing_algs.patterns import get_pattern, PATTERNS

# Get a specific pattern
superflip = get_pattern('Superflip')
print(superflip)  # U R2 F B R B2 R U2 L B2 R U' D' R2 F R' L B2 U2 F2

checkerboard = get_pattern('EasyCheckerboard')
print(checkerboard)  # U2 D2 R2 L2 F2 B2

# List all available patterns
print(list(PATTERNS.keys()))

# Some popular patterns
cube_in_cube = get_pattern('CubeInTheCube')
anaconda = get_pattern('Anaconda')
wire = get_pattern('Wire')
tetris = get_pattern('Tetris')
```

**Available patterns include:**
- `Superflip` - All edges flipped
- `EasyCheckerboard` - Classic checkerboard pattern
- `CubeInTheCube` - Cube within a cube effect
- `Tetris` - Tetris-like pattern
- `Wire` - Wire frame effect
- `Anaconda`, `Python`, `GreenMamba`, `BlackMamba` - Snake patterns
- `Cross`, `Plus`, `Minus` - Cross patterns
- And many more! (70+ patterns total)

## Scramble Generation

Generate scrambles for various cube sizes with advanced customization options:

```python
from cubing_algs.scrambler import scramble, scramble_easy_cross, build_cube_move_set

# Generate scramble for 3x3x3 cube (default 25 moves)
scramble_3x3 = scramble(3)
print(scramble_3x3)

# Generate scramble for 4x4x4 cube (includes wide moves)
scramble_4x4 = scramble(4)
print(scramble_4x4)  # Example: Rw U 2R D' Fw2 R' Uw F2 ...

# Generate scramble for 6x6x6 cube (includes multi-layer moves)
scramble_6x6 = scramble(6)
print(scramble_6x6)  # Example: 3Rw 2F' 4Uw2 3Fw R 2Bw' ...

# Generate scramble with specific number of moves
custom_scramble = scramble(3, iterations=20)
print(f"Custom 20-move scramble: {custom_scramble}")

# Generate easy cross scramble (only F, R, B, L moves - 10 moves)
easy_scramble = scramble_easy_cross()
print(f"Easy cross scramble: {easy_scramble}")  # Example: F R B' L F' R2 B L' F R

# Build custom move set for specific cube size
move_set_3x3 = build_cube_move_set(3)
print(f"3x3 moves: {move_set_3x3[:12]}")  # ['R', "R'", 'R2', 'U', "U'", 'U2', ...]

move_set_4x4 = build_cube_move_set(4)
print(f"4x4 additional moves: {[m for m in move_set_4x4 if 'w' in m][:9]}")  # ['Rw', "Rw'", 'Rw2', ...]

move_set_6x6 = build_cube_move_set(6)
multi_layer = [m for m in move_set_6x6 if any(c.isdigit() for c in m)]
print(f"6x6 multi-layer moves: {multi_layer[:12]}")  # ['2R', "2R'", '2R2', '3R', ...]
```

**Scramble Features:**
- **Cube sizes**: Supports 2x2x2 through 7x7x7+ cubes
- **Automatic move count**: Based on cube size (configurable ranges)
  - 2x2x2: 9-11 moves
  - 3x3x3: 20-25 moves
  - 4x4x4: 40-45 moves
  - 5x5x5+: 60-70 moves
- **Smart move validation**: Prevents consecutive moves on same face or opposite faces
- **Big cube support**:
  - Wide moves (Rw, Uw, etc.) for 4x4x4+
  - Multi-layer moves (2R, 3Rw, etc.) for 6x6x6+
- **Easy cross scrambles**: Only F, R, B, L moves for beginners
- **Customizable iterations**: Override default move counts

**Move Set Generation:**
The `build_cube_move_set()` function creates appropriate move sets:
- **3x3x3**: Basic face turns (R, U, F, etc.) with modifiers (', 2)
- **4x4x4+**: Adds wide moves (Rw, Uw, Fw, etc.)
- **6x6x6+**: Adds numbered layer moves (2R, 3R, 2Rw, 3Rw, etc.)

**Validation Logic:**
- No consecutive moves on the same face (R R' is invalid)
- No consecutive moves on opposite faces (R L is invalid)
- Ensures natural, realistic scramble sequences

## Virtual Cube Simulation

Track cube state and visualize the cube:

```python
from cubing_algs.vcube import VCube
from cubing_algs.parsing import parse_moves

# Create a new solved cube
cube = VCube()
print(cube.is_solved)  # True

# Apply moves
cube.rotate("R U R' U'")
print(cube.is_solved)  # False

# Apply algorithm object
algo = parse_moves("F R U R' U' F'")
cube.rotate(algo)

# Display the cube (ASCII art)
cube.show()

# Get cube state as facelets string
print(cube.state)  # 54-character string representing all facelets

# Get move history
print(cube.history)  # List of all moves applied

# Create cube from specific state
custom_cube = VCube("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")

# Work with cube coordinates (corner/edge positions and orientations)
cp, co, ep, eo, so = cube.to_cubies
new_cube = VCube.from_cubies(cp, co, ep, eo, so)

# Get individual faces
u_face = cube.get_face('U')  # Get U face facelets
center_piece = cube.get_face_center_indexes()  # Get all face centers
```

**VCube features:**
- Full 3x3x3 cube state tracking
- ASCII art display with multiple orientations
- Move history tracking
- Conversion between facelets and cubie coordinates
- Integrity checking to ensure valid cube states
- Support for creating cubes from custom states

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
from cubing_algs.vcube import VCube

oll = parse_moves("F U F' R' F R U' R' F' R")  # 14 Anti-Gun
oll_mirror = oll.transform(mirror_moves)
print(oll_mirror)  # R' F R U R' F' R F U' F'

cube = VCube()
cube.rotate('z2')
cube.rotate(oll)
cube.show('oll')  # Display OLL pattern
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

### Working with commutators and patterns

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.patterns import get_pattern
from cubing_algs.vcube import VCube

# Parse and expand a commutator
comm = parse_moves("[R, U]")  # R U R' U'

# Apply a pattern to a virtual cube
cube = VCube()
pattern = get_pattern('Superflip')
cube.rotate(pattern)
cube.show()  # Display the superflip pattern

# Generate and apply a scramble
from cubing_algs.scrambler import scramble
scramble_algo = scramble(3, 25)
cube = VCube()
cube.rotate(scramble_algo)
print(f"Scrambled with: {scramble_algo}")
```

### Advanced scramble generation and testing

```python
from cubing_algs.scrambler import scramble, scramble_easy_cross, build_cube_move_set
from cubing_algs.vcube import VCube

# Test different scramble types
cube = VCube()

# Standard 3x3x3 scramble
standard_scramble = scramble(3)
cube.rotate(standard_scramble)
print(f"Standard scramble ({standard_scramble.metrics['htm']} HTM): {standard_scramble}")

# Easy cross scramble for beginners
cube = VCube()
easy_scramble = scramble_easy_cross()
cube.rotate(easy_scramble)
print(f"Easy cross scramble: {easy_scramble}")
cube.show(orientation='DF')  # Visual check of scrambled state with DF orientation

# Big cube scramble with specific length
big_cube_scramble = scramble(5, iterations=50)
print(f"5x5x5 scramble (50 moves): {big_cube_scramble}")

# Analyze move distribution
move_set = build_cube_move_set(4)
face_moves = [m for m in move_set if not 'w' in m]
wide_moves = [m for m in move_set if 'w' in m]
print(f"4x4x4 face moves: {len(face_moves)}")  # 18 moves (6 faces × 3 modifiers)
print(f"4x4x4 wide moves: {len(wide_moves)}")  # 18 moves (6 faces × 3 modifiers)
```

### Advanced algorithm development workflow

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves
from cubing_algs.transform.symmetry import symmetry_m_moves
from cubing_algs.vcube import VCube
from cubing_algs.scrambler import scramble

# Start with a commutator
base_alg = parse_moves("[R U R', D]")  # R U R' D R U' R' D'

# Generate variations
mirrored = base_alg.transform(mirror_moves)
m_symmetric = base_alg.transform(symmetry_m_moves)

# Test on virtual cube
cube = VCube()
cube.rotate(base_alg)
print(f"Original: {base_alg} ({base_alg.metrics['htm']} HTM)")
print(f"Mirrored: {mirrored} ({mirrored.metrics['htm']} HTM)")
print(f"Is solved after: {cube.is_solved}")

# Test algorithm on scrambled cube
test_cube = VCube()
test_scramble = scramble(3, 15)
test_cube.rotate(test_scramble)
print(f"Applied scramble: {test_scramble}")

# Apply algorithm and check result
test_cube.rotate(base_alg)
print(f"Cube state after algorithm: {test_cube.state[:9]}...")  # First 9 facelets

# Create conjugate setup
setup = parse_moves("R U")
full_alg = parse_moves(f"[{setup}: {base_alg}]")
print(f"With setup: {full_alg}")
```
