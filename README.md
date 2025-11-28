# Cubing Algs

Python module providing comprehensive tools for Rubik's cube algorithm manipulation, analysis, and simulation.

## Installation

```bash
pip install cubing-algs
```

## Features

- **Dual Representation System**: Work with both facelet (visual) and cubie (mathematical) representations
- **Algorithm Analysis**: Comprehensive metrics, impact analysis, ergonomics, and structure detection
- **Powerful Transformations**: Mirror, rotate, compress, and compose algorithms with a clean pipeline API
- **Virtual Cube Simulation**: Full 3x3x3 cube state tracking with orientation support
- **Advanced Notation**: Commutators `[A, B]`, conjugates `[A: B]`, wide moves, slice moves, rotations
- **Pattern Library**: 70+ classic cube patterns (Superflip, Checkerboard, etc.)
- **Scramble Generation**: Smart scrambles for 2x2x2 through 7x7x7+ cubes
- **Big Cube Support**: Multi-layer notation for larger cubes
- **Performance Optimized**: C extension for move execution, LRU caching for conversions

## Quick Start

```python
from cubing_algs import Algorithm, VCube

# Parse a classic algorithm
sexy_move = Algorithm.parse_moves("R U R' U'")

# Analyze it
print(f"Moves: {sexy_move.metrics.htm} HTM")        # 4 HTM
print(f"Pattern: {sexy_move.structure.compressed}") # [R, U] (commutator)
print(f"Cycles: {sexy_move.cycles}")                # 6 (repeats 6 times to solve)
print(f"Comfort: {sexy_move.ergonomics.comfort_rating}")  # Execution difficulty

# Test on virtual cube
cube = VCube()
cube.rotate(sexy_move)
cube.show()  # Display the result
print(f"Solved: {cube.is_solved}")  # False
```

## Core Concepts

### Dual Representation System

This library uses two complementary representations of cube state:

**Facelet Representation** (54-character string):
- Visual representation of all 54 stickers on the cube
- Format: `UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB`
- Position 0-53 represent: U face (0-8), R face (9-17), F (18-26), D (27-35), L (36-44), B (45-53)
- Based on the **Kociemba facelet format**, widely used in cube solving algorithms
- Used for visualization, display, and move execution (via optimized C extension)

**Cubie Representation** (permutation + orientation arrays):
```python
cp = [0,1,2,3,4,5,6,7]           # Corner Permutation (8 corners)
co = [0,0,0,0,0,0,0,0]           # Corner Orientation (0, 1, or 2)
ep = [0,1,2,3,4,5,6,7,8,9,10,11] # Edge Permutation (12 edges)
eo = [0,0,0,0,0,0,0,0,0,0,0,0]   # Edge Orientation (0 or 1)
so = [0,1,2,3,4,5]               # Spatial Orientation (6 centers)
```
- Mathematical representation for analysis and group theory operations
- Used for integrity checking and advanced analysis

Both representations can be converted bidirectionally with caching for performance.

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

Apply various transformations to algorithms using the transform pipeline:

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves
from cubing_algs.transform.size import compress_moves, expand_moves
from cubing_algs.transform.symmetry import symmetry_m_moves

algo = parse_moves("R U R' U'")

# Mirror an algorithm
mirrored = algo.transform(mirror_moves)  # L' U' L U

# Compression (optimize with cancellations)
compressed = parse_moves("R R U U U").transform(compress_moves)  # R2 U'

# Expansion (convert double moves to single pairs)
expanded = parse_moves("R2 U'").transform(expand_moves)  # R R U'

# Chain multiple transformations
result = algo.transform(mirror_moves, compress_moves, symmetry_m_moves)

# Transform until fixed point (apply repeatedly until stable)
messy = parse_moves("R R F F' R2 U F2")
clean = messy.transform(compress_moves, to_fixpoint=True)  # U F2
```

### Available Transformations

**Basic transformations:**
- `mirror_moves` - Mirror across M plane (R ↔ L)
- `compress_moves` - Optimize with move cancellations (R R → R2, R R' → ∅)
- `expand_moves` - Convert double moves to pairs (R2 → R R)

**Notation conversions:**
- `sign_moves` - Convert to SiGN notation (Rw → r)
- `unsign_moves` - Convert to standard notation (r → Rw)
- `translate_moves` - Translate between notation systems
- `translate_pov_moves` - Translate point-of-view notation

**Rotations:**
- `remove_rotations` - Remove all rotation moves
- `remove_starting_rotations` - Remove leading rotation moves
- `remove_ending_rotations` - Remove trailing rotation moves
- `compress_ending_rotations` - Compress rotations at end (x x → x2)
- `unwide_rotation_moves` - Expand wide moves (r → R M' x)
- `rewide_moves` - Combine to wide moves (R M' x → r)

**Slice moves:**
- `unslice_wide_moves` - Expand slice moves (M → r' R)
- `unslice_rotation_moves` - Expand slice to rotation moves
- `reslice_moves` - Combine to slice moves (L' R → M x)
- `reslice_m_moves`, `reslice_s_moves`, `reslice_e_moves` - Reslice specific axes

**Symmetries:**
- `symmetry_m_moves` - M-slice symmetry (L ↔ R)
- `symmetry_s_moves` - S-slice symmetry (F ↔ B)
- `symmetry_e_moves` - E-slice symmetry (U ↔ D)
- `symmetry_c_moves` - Combined M and S symmetry

**Viewpoint/Offset:**
- `offset_x_moves`, `offset_y_moves`, `offset_z_moves` - Change viewpoint (90° rotation)
- `offset_x2_moves`, `offset_y2_moves`, `offset_z2_moves` - Change viewpoint (180° rotation)
- `offset_xprime_moves`, `offset_yprime_moves`, `offset_zprime_moves` - Change viewpoint (-90° rotation)

**Degrip (move rotations to end):**
- `degrip_x_moves`, `degrip_y_moves`, `degrip_z_moves` - Move specific axis rotations to end
- `degrip_full_moves` - Move all rotations to the end

**AUF (Adjust U Face):**
- `remove_auf_moves` - Remove AUF moves from algorithm

**Timing:**
- `untime_moves` - Remove timing notation (@200ms, etc.)
- `pause_moves` - Add pause moves
- `unpause_moves` - Remove pause moves (.)

**Trimming:**
- `trim_moves` - Remove setup and undo moves

**Optimization:**
- `optimize_repeat_three_moves` - R R R → R'
- `optimize_do_undo_moves` - R R' → (empty)
- `optimize_double_moves` - R R → R2
- `optimize_triple_moves` - R R2 → R'

See the [Transformations section](#transformations) for import examples.

## Metrics

Compute algorithm metrics:

```python
from cubing_algs.parsing import parse_moves

algo = parse_moves("R U R' U' R' F R2 U' R' U' R U R' F'")  # T-Perm

# Access metrics
print(algo.metrics._asdict())
# {
#   'pauses': 0,
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
print(f"HTM: {algo.metrics.htm}")   # 14
print(f"QTM: {algo.metrics.qtm}")   # 16
print(f"Generators: {', '.join(algo.metrics.generators)}")  # R, U, F
```

**Metric definitions:**
- **HTM (Half Turn Metric)**: Counts quarter turns as 1, half turns as 1 (also known as OBTM - Outer Block Turn Metric)
- **QTM (Quarter Turn Metric)**: Counts quarter turns as 1, half turns as 2 (also known as OBQTM - Outer Block Quantum Turn Metric)
- **STM (Slice Turn Metric)**: Counts both face turns and slice moves as 1 (also known as BTM/RBTM - Block/Range Block Turn Metric)
- **ETM (Execution Turn Metric)**: Counts all moves including rotations
- **RTM (Rotation Turn Metric)**: Counts only rotation moves (x, y, z)
- **QSTM (Quarter Slice Turn Metric)**: Counts quarter turns as 1, slice quarter turns as 1, half turns as 2 (also known as BQTM - Block Quarter Turn Metric)

**Metric aliases:**
The `MetricsData` object also provides these property aliases for convenience:
- `obtm` → `htm`
- `obqtm` → `qtm`
- `btm` / `rbtm` → `stm`
- `bqtm` → `qstm`

## Algorithm Analysis

Beyond basic metrics, algorithms provide comprehensive analysis capabilities:

```python
from cubing_algs.parsing import parse_moves

algo = parse_moves("R U R' U'")

# Structure analysis - detect commutators and conjugates
print(algo.structure.compressed)         # "[R, U]" (commutator notation)
print(algo.structure.commutator_count)   # 1
print(algo.structure.conjugate_count)    # 0
print(algo.structure.total_structures)   # 1
print(algo.structure.max_nesting_depth)  # 1

# Impact analysis - spatial effects on cube
print(algo.impacts.affected_facelet_count)  # Number of facelets that change position
print(algo.impacts.average_distance)        # Average movement distance
print(algo.impacts.total_displacement)      # Total displacement of all facelets
print(algo.impacts.max_distance)            # Maximum distance any facelet moves

# Ergonomics analysis - execution comfort
print(algo.ergonomics.comfort_rating)       # Overall execution difficulty (0-10)
print(algo.ergonomics.estimated_time_ms)    # Estimated execution time
print(algo.ergonomics.regrip_count)         # Number of regrips needed
print(algo.ergonomics.finger_usage)         # Which fingers are used

# Cycle analysis
print(algo.cycles)  # 6 - How many repetitions return to solved state

# Minimum cube size
print(algo.min_cube_size)  # 2 - Minimum cube size to execute this algorithm
```

**Analysis use cases:**
- **Structure detection**: Automatically identify commutator/conjugate patterns
- **Impact analysis**: Understand which pieces are affected by an algorithm
- **Ergonomics**: Evaluate execution difficulty and fingertrick requirements
- **Algorithm comparison**: Compare different algorithms for the same case

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
from cubing_algs import VCube
from cubing_algs.parsing import parse_moves

# Create a new solved cube
cube = VCube()
print(cube.is_solved)  # True
print(cube.orientation)  # "UF" - default orientation

# Apply moves
cube.rotate("R U R' U'")
print(cube.is_solved)  # False

# Apply algorithm object
algo = parse_moves("F R U R' U' F'")
cube.rotate(algo)

# Display the cube (ASCII art with colors)
cube.show()

# Display with different options
cube.show(orientation='UB')        # View from different angle
cube.show(mode='oll')              # OLL pattern visualization
cube.show(palette='colorblind')    # Colorblind-friendly colors
cube.show(mask='F2L')              # Highlight specific pieces

# Get cube state
print(cube.state)       # 54-character facelet string
print(cube.orientation) # Current orientation (e.g., "UF")
print(cube.history)     # List of all moves applied

# Orientation features
oriented = cube.oriented_copy('UB')  # Create copy with U top, B front
print(oriented.orientation)  # "UB"

moves = cube.compute_orientation_moves('DR')  # Calculate moves to get D top, R front
print(moves)  # e.g., "x2 y"

# Create cube from specific state
custom_cube = VCube("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")

# Work with cubie representation (mathematical)
cp, co, ep, eo, so = cube.to_cubies  # Convert to cubie format
new_cube = VCube.from_cubies(cp, co, ep, eo, so)  # Create from cubies

# Get individual faces
u_face = cube.get_face('U')  # Get U face facelets (9 characters)
```

**VCube features:**
- Full 3x3x3 cube state tracking with dual representation
- ASCII art display with colors, multiple orientations, and visual modes
- Move history tracking
- Orientation management (get current, create oriented copies, compute orientation moves)
- Conversion between facelets and cubie coordinates
- Integrity checking to ensure valid cube states
- Support for creating cubes from custom states

**Default orientation:**
The default orientation is **'UF'**, following the **WCA (World Cube Association) standard**:
- **U (Up/Top) face**: White color
- **F (Front) face**: Green color
- **R (Right) face**: Red color
- **D (Down/Bottom) face**: Yellow color (opposite White)
- **L (Left) face**: Orange color (opposite Red)
- **B (Back) face**: Blue color (opposite Green)

This standard orientation is used consistently across the library for cube initialization, display, and algorithm application.

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

## Performance

The library is optimized for performance:

- **C Extension**: Move execution uses an optimized C extension (`cubing_algs.extensions.rotate`) compiled with `-O3` optimization
- **LRU Caching**: Facelet ↔ cubie conversion uses LRU caching (512 entries) for repeated operations
- **Lazy Evaluation**: Algorithm transforms are composable and don't execute until needed
- **Lightweight State**: Virtual cube state is a simple 54-character string with minimal overhead
- **Cached Properties**: Algorithm analysis properties (metrics, impacts, etc.) are computed once and cached

**Performance characteristics:**
- Move execution: ~1-2 microseconds per move (C extension)
- Facelet/cubie conversion: ~10-20 microseconds uncached, ~0.1 microseconds cached
- Algorithm parsing: ~50-100 microseconds for typical algorithms

## Examples

### Generating a mirror of an OLL algorithm

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves
from cubing_algs import VCube

oll = parse_moves("F U F' R' F R U' R' F' R")  # OLL 14 Anti-Gun
oll_mirror = oll.transform(mirror_moves)
print(oll_mirror)  # R' F R U R' F' R F U' F'

cube = VCube()
cube.rotate('z2')
cube.rotate(oll)
cube.show(mode='oll')  # Display OLL pattern
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
from cubing_algs import VCube

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
from cubing_algs import VCube

# Test different scramble types
cube = VCube()

# Standard 3x3x3 scramble
standard_scramble = scramble(3)
cube.rotate(standard_scramble)
print(f"Standard scramble ({standard_scramble.metrics.htm} HTM): {standard_scramble}")

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
from cubing_algs import VCube
from cubing_algs.scrambler import scramble

# Start with a commutator
base_alg = parse_moves("[R U R', D]")  # R U R' D R U' R' D'

# Generate variations
mirrored = base_alg.transform(mirror_moves)
m_symmetric = base_alg.transform(symmetry_m_moves)

# Analyze algorithms
print(f"Original: {base_alg} ({base_alg.metrics.htm} HTM)")
print(f"Comfort: {base_alg.ergonomics.comfort_rating}/10")
print(f"Affected pieces: {base_alg.impacts.affected_facelet_count}")
print(f"Mirrored: {mirrored} ({mirrored.metrics.htm} HTM)")

# Test on virtual cube
cube = VCube()
cube.rotate(base_alg)
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

## Development

This library is designed for both end-users and developers:

**For users:**
- Comprehensive API with intuitive design
- Full type hints for IDE support
- Extensive examples and documentation

**For developers:**
- Comprehensive test suite with pytest
- C extension source in `cubing_algs/extensions/rotate.c`
- Full type hints and docstrings throughout the codebase

**Development commands:**
```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest cubing_algs

# Type checking
mypy --strict cubing_algs

# Linting
ruff check cubing_algs
```
