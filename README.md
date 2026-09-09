# Cubing Algs

<p align="center">
  <picture>
    <source srcset="https://raw.githubusercontent.com/Fantomas42/cubing-algs/develop/.github/assets/banner.svg" type="image/svg+xml">
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Fantomas42/cubing-algs/develop/.github/assets/banner-dark.png">
    <img src="https://raw.githubusercontent.com/Fantomas42/cubing-algs/develop/.github/assets/banner-light.png" alt="cubing-algs - Rubik's cube algorithm manipulation, analysis &amp; simulation" width="600">
  </picture>
</p>

Python module providing comprehensive tools for Rubik's cube algorithm manipulation, analysis, and simulation.

## Installation

```bash
pip install cubing-algs

# With the GPU rendering backend: PNG, GIF and interactive window
pip install cubing-algs[opengl]
```

## Features

- **Dual Representation System**: Work with both facelet (visual) and cubie (mathematical) representations
- **Algorithm Analysis**: Comprehensive metrics, impact analysis, ergonomics, and structure detection
- **Powerful Transformations**: Invert, rotate, compress, and compose algorithms with a clean pipeline API
- **Virtual Cube Simulation**: Full 3x3x3 cube state tracking with orientation support
- **Advanced Notation**: Commutators `[A, B]`, conjugates `[A: B]`, wide moves, slice moves, rotations
- **Rendering**: ASCII/ANSI nets in the terminal, SVG images, and optional GPU rendering to PNG, GIF or an interactive window
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

# Parse last layer style (removes starting/ending U and y moves)
from cubing_algs.parsing import parse_moves_last_layer
algo = parse_moves_last_layer("y U R U R' U R U2 R'")  # Removes the leading y and U
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
from cubing_algs.transform.invert import invert_moves
from cubing_algs.transform.size import compress_moves, expand_moves
from cubing_algs.transform.symmetry import symmetry_m_moves

algo = parse_moves("R U R' U'")

# Invert an algorithm
inverse = algo.transform(invert_moves)  # U R U' R'

# Compression (optimize with cancellations)
compressed = parse_moves("R R U U U").transform(compress_moves)  # R2 U'

# Expansion (convert double moves to single pairs)
expanded = parse_moves("R2 U'").transform(expand_moves)  # R R U'

# Chain multiple transformations
result = algo.transform(invert_moves, compress_moves, symmetry_m_moves)

# Transform until fixed point (apply repeatedly until stable)
messy = parse_moves("R R F F' R2 U F2")
clean = messy.transform(compress_moves, to_fixpoint=True)  # U F2
```

### Available Transformations

**Basic transformations:**
- `invert_moves` - Invert moves
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
impacts = algo.impacts()
print(impacts.facelets_mobilized_count)     # Number of facelets that change position
print(impacts.facelets_scrambled_percent)   # Fraction of movable facelets displaced
print(impacts.facelets_face_mobility)       # Impact breakdown by face

# Impact analysis on larger cubes
impacts_5x5 = algo.impacts(size=5)
print(impacts_5x5.facelets_mobilized_count)  # Facelets affected on 5x5x5

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

The `cubing_algs.scrambler` module provides comprehensive scramble generation:
- **NxN scrambles** for cubes of any size (2x2x2 to NxNxN)
- **Step-based scrambles** for speedcubing practice (PLL, OLL, F2L, ZBLL, etc.)
- **Piece-level constraints** for fine-grained control over cube state
- **Practice scrambles** for cross, x-cross, and F2L training

### Basic NxN Scrambles

```python
from cubing_algs.scrambler import scramble

# Generate scramble for 3x3x3 cube (default 25-30 moves)
scramble_3x3 = scramble(3)
print(scramble_3x3)

# Generate scramble for 4x4x4 cube (includes wide moves)
scramble_4x4 = scramble(4)
print(scramble_4x4)  # Example: Rw U R D' Fw2 R' Uw F2 ...

# Generate scramble for 6x6x6 cube (includes multi-layer moves)
scramble_6x6 = scramble(6)
print(scramble_6x6)  # Example: 3Rw F' 3Uw2 Fw R Bw' ...

# Generate scramble with specific number of moves
custom_scramble = scramble(3, iterations=20)
print(f"Custom 20-move scramble: {custom_scramble}")

# Include inner layer moves (e.g., 2R, 3R for big cubes)
inner_scramble = scramble(5, inner_layers=True)

# Left-handed optimized scramble (excludes D, R, B instead of D, L, B)
lh_scramble = scramble(4, right_handed=False)
```

### Step-Based Scrambles

Generate scrambles for specific speedcubing steps. The cube state is constructed
mathematically (not by applying random moves), ensuring a valid partial-solve state:

```python
from cubing_algs.scrambler import scramble_step

# Last Layer steps
pll_scramble = scramble_step("PLL")          # Only U layer permuted
oll_scramble = scramble_step("OLL")          # U layer permuted + oriented
zbll_scramble = scramble_step("ZBLL")        # Corners oriented, all U pieces permuted

# With random AUF (Adjust U Face)
pll_with_auf = scramble_step("PLL", include_auf=True)

# F2L variants
f2l_scramble = scramble_step("F2L")          # First two layers scrambled
zzf2l_scramble = scramble_step("ZZF2L")      # ZZ method F2L

# Roux method
cmll_scramble = scramble_step("CMLL")        # Roux CMLL step
sb_scramble = scramble_step("SB")            # Roux Second Block

# Last Slot variants
ls_scramble = scramble_step("LS")            # Last Slot
wv_scramble = scramble_step("WV")            # Winter Variation
```

**Supported steps:**
- **Last Layer**: LL, OLL, PLL, CLL, OLLCP, COLL, ZBLL, 2GLL, OCLL, ELL, EPLL, CPLL, ZZLL
- **F2L variants**: F2L, ZZF2L, ZZRB, PETRUSF2L
- **Last Slot**: LS, ELS, ZZLS, TSLE, CLS, CPLS, EJLS, EJF2L, TTLL, WV, SV, VLS, VHLS
- **Roux method**: CMLL, CMLLEO, SB
- **Petrus method**: PETRUS2X2X3, PETRUSEO

### OCLL Case Scrambles

Generate scrambles for specific OCLL (Orientation of Corners of Last Layer) cases:

```python
from cubing_algs.scrambler import scramble_ocll_case

sune_scramble = scramble_ocll_case("Sune")
antisune_scramble = scramble_ocll_case("AntiSune")
h_scramble = scramble_ocll_case("H")
pi_scramble = scramble_ocll_case("Pi")
```

**Valid cases:** T, U, L, H, Pi, Sune, AntiSune, Solved

### Cross and X-Cross Practice

```python
from cubing_algs.scrambler import scramble_easy_cross, scramble_x_cross

# Easy cross scramble - returns (scramble, solution) tuple
scramble_alg, solution = scramble_easy_cross()
print(f"Scramble: {scramble_alg}")
print(f"Solution: {solution}")

# Adjust difficulty: 'easy' (3 moves), 'normal' (5 moves), 'hard' (7 moves)
easy_scramble, easy_solution = scramble_easy_cross(difficulty='easy')
hard_scramble, hard_solution = scramble_easy_cross(difficulty='hard')

# X-cross scramble - cross + one F2L slot preserved
x_cross_scramble, x_cross_solution = scramble_x_cross(slots=['FR'])

# XX-cross - cross + two F2L slots preserved
xx_scramble, xx_solution = scramble_x_cross(slots=['FR', 'FL'])

# Valid slots: FR, FL, BR, BL
```

### F2L Slot Practice

```python
from cubing_algs.scrambler import scramble_f2l

# Scramble a single F2L slot (cross solved, one slot scrambled)
f2l_scramble = scramble_f2l(slots=['FR'])

# Scramble multiple F2L slots
multi_slot = scramble_f2l(slots=['FR', 'BL'])
```

### Piece-Level Constraints

For maximum control over cube state, specify exactly which pieces should be
solved, oriented, scrambled, or disoriented:

```python
from cubing_algs.scrambler import scramble_with_piece_constraints

# PLL-like state: all pieces oriented, only permutation scrambled
pll_state = scramble_with_piece_constraints(
    orient_corners_spec="all",
    orient_edges_spec="all",
)

# F2L solved, last layer scrambled
f2l_solved = scramble_with_piece_constraints(
    solve_corners="D",
    solve_edges="D E",
    buffer_corners="U",
    buffer_edges="U",
)

# ZBLL-like: last layer corners oriented, permutation scrambled
zbll_state = scramble_with_piece_constraints(
    orient_corners_spec="U",
    orient_edges_spec="U",
)

# Specific pieces scrambled
specific = scramble_with_piece_constraints(
    solve_corners="URF UBR",    # Keep these corners solved
    derange_edges="UF UR",      # Ensure these edges are NOT solved
    disorient_corners_spec="U", # U-layer corners must be misoriented
)
```

**Piece specification formats:**
- `"all"` or `""`: All pieces of that type
- `"U"`, `"D"`, `"R"`, `"L"`, `"F"`, `"B"`: All pieces on that layer
- `"URF UBR"`: Specific pieces by name (space-separated)
- `"U DFR"`: Mix of layer and specific pieces

### Scramble Features

- **Cube sizes**: Supports 2x2x2 through 7x7x7+ cubes
- **Automatic move count**: Based on cube size (configurable ranges)
  - 2x2x2: 9-11 moves
  - 3x3x3: 25-30 moves
  - 4x4x4: 45-50 moves
  - 5x5x5: 60 moves
  - 6x6x6: 80 moves
  - 7x7x7: 100 moves
- **Smart move validation**: Prevents consecutive moves on same face or opposite faces
- **Big cube support**:
  - Wide moves (Rw, Uw, etc.) for 4x4x4+
  - Multi-layer moves (3Rw, etc.) for 6x6x6+
  - Optional inner layer moves (2R, 3R, etc.)
- **Handedness**: Right-handed (default) or left-handed move set optimization
- **Reproducible scrambles**: Pass a `Random` instance for deterministic results
- **Physical constraints**: Step-based scrambles maintain valid cube states
  (sum(co) % 3 == 0, sum(eo) % 2 == 0, matching permutation parity)

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
cp, co, ep, eo, so = cube.cubies  # Convert to cubie format
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

## Image Rendering

Generate SVG images of cube states using the `render_cube` function or the `.image()` method available on both `VCube` and `Algorithm` objects:

```python
from cubing_algs import VCube
from cubing_algs.parsing import parse_moves
from cubing_algs.display.image import render_cube

# Render a cube state as SVG
cube = VCube()
cube.rotate("R U R' U'")
svg = cube.image()  # Returns SVG string

# Render an algorithm's effect directly
algo = parse_moves("R U R' U' R' F R2 U' R' U' R U R' F'")
svg = algo.image()  # Applies to solved cube and renders

# Using render_cube directly
svg = render_cube(cube, size=300)
```

### Views

Two rendering modes are available:

```python
# 3D perspective view (default)
svg_3d = cube.image(view='3d')

# Flat top-face view with adjacent strips from F, R, B, L faces
svg_top = cube.image(view='top')
```

### Customization

```python
# Custom image size (pixels)
svg = cube.image(size=400)

# Custom rotation angle for 3D view (axis-angle format)
svg = cube.image(rotation='y45x-34')   # Default angle
svg = cube.image(rotation='y-30')      # Different angle
svg = cube.image(rotation='y90x-20')   # Multiple rotations

# Camera distance (larger = flatter, smaller = more depth)
svg = cube.image(distance=20.0)

# Custom cube body color (supports alpha: #rrggbbaa)
svg = cube.image(cube_color='#222222')
svg = cube.image(cube_color='#11111180')  # Semi-transparent

# Color palettes
svg = cube.image(palette_name='default')
svg = cube.image(palette_name='colorblind')
svg = cube.image(palette_name='neon')

# Algorithm with explicit cube size
algo = parse_moves("R U R'")
svg = algo.image(cube_size=2)  # Render on a 2x2x2
```

**Available palettes:** `default`, `rgb`, `vibrant`, `neon`, `metal`, `pastel`, `retro`, `minecraft`, `colorblind`, `dracula`, `alucard`, `solarized-dark`, `solarized-light`, `halloween`, `galaxy`, `vampire`, `ghoul`, `goblin`, `void`, `cyberpunk`, `synthwave`, `matrix`, `sunset`, `ocean`, `forest`, `fire`, `ice`, `white`, `black`, `red`, `green`, `blue`

### Saving to File

```python
# Save as SVG
with open('cube.svg', 'w') as f:
    f.write(cube.image(size=400))

# Embed in HTML
html = f'<html><body>{cube.image()}</body></html>'
with open('cube.html', 'w') as f:
    f.write(html)
```

## GPU Rendering

Beside the SVG backend, cubes can be drawn in 3D on the GPU: a PNG without any
screen, an animated GIF of an algorithm, or an interactive window. It ships in
the `opengl` extra, and nothing of it is imported until it is used:

```bash
pip install cubing-algs[opengl]
```

The framing, the palettes, the display modes and the masks are the ones of
`.image()`: the same cube comes out the same way in both backends, lit as a
solid rather than drawn flat. Cubes of any size are supported, from 2x2x2 up.

```python
from cubing_algs import VCube
from cubing_algs.parsing import parse_moves

cube = VCube()
cube.rotate("R U R' U'")

# A PNG, headless: no display server, no window
png = cube.render(image_size=512, mode='oll')
with open('cube.png', 'wb') as f:
    f.write(png)

# An animated GIF of an algorithm being played
cube.animate("R U R' U'", 'sexy.gif')

# An interactive window
cube.view()
```

`Algorithm` offers the same three, applying itself to a cube first, exactly as
`.image()` and `.show()` do:

```python
algo = parse_moves("R U R2 U' R' U' R U R'")

algo.render()                 # PNG of the state it leads to
algo.animate('pll.gif')       # GIF of it playing on a solved cube
algo.view(5)                  # window, on a 5x5x5 this time
```

A GIF needs Pillow; without it, the animation comes out as numbered PNG frames
the encoder of your choice can assemble.

A **timed algorithm plays at the speed it was made**: each move lasts until the
next timestamp is due, and the cube stands still through the gaps, so a recorded
solve keeps its recognition pauses.

```python
# The animation lasts 1.5 s, the last move waiting its turn
parse_moves('R@0 U@120 F@240 R@1500').animate('solve.gif')
```

A written pause `.` holds the cube still for a second, so a hesitation is seen
rather than skipped. A timestamp saying a longer rest wins over it.

### Viewer Shortcuts

```
cubing-algs viewer
  Drag             Orbit the cube
  Ctrl Drag        Carry the window across the screen
  Wheel            Zoom in and out
  R U F L D B      Turn a face
  M E S            Turn a slice
  X Y Z            Turn the whole cube
  Shift            Primes a face turn as in R'
  Ctrl             Doubles a face turn as in R2
  Alt              Widen a face turn, as in Rw
  Space            Frame the cube again
  Backspace        Put the cube back as it was
  Tab              Open the cube up, and put it back together
  F2               Show the X/Y/Z axes, red green blue
  F3               Monitor the rendering performance
  F4               Print a performance report
  F5               Turn the vsync on and off
  F12              Write a screenshot
  Esc, Q           Close the window
```

`F3` writes what the rendering costs in the title of the window - frame rate,
processor time, GPU time - and `F4` prints the whole of it to the terminal:
where a frame goes, what is left of the budget the screen leaves, and what that
frame had to draw. A frame rate held by the vsync is the refresh rate of the
screen and nothing else, so `F5` frees the frames from it when the question is
what the machine truly holds.

```
cubing-algs debug - 240 frames over 2.4 s, 0 dropped
  frame      10.02 ms   min   9.81   p95  10.42   max  22.40
  advance     0.41 ms   min   0.30   p95   0.62   max   1.90
  draw        1.32 ms   min   1.10   p95   1.71   max   3.40
  swap        8.21 ms   min   7.60   p95   8.80   max   9.10   vsync on
  gpu         0.72 ms   min   0.61   p95   0.94   max   1.60
  headroom  83%   budget 10.00 ms (100 Hz screen)
  scene     26 instances, 1456 triangles, 2.5 KiB
  target    720x720, 8 samples, 2 draw calls
  context   Mesa Intel(R) Iris(R) Xe Graphics - 4.6
```

For what `.view()` does not expose - a lighting of its own, the duration of a
move, or an orientation pushed from outside - build the viewer directly. It is
a dataclass, and its state can be reached while it runs:

```python
from cubing_algs.display.gl import OrientationTracker, Quat, Viewer

# This sensor's own axis convention - the driver decoding its raw
# bytes is the one that knows this value.
basis = Quat(w=0.7071067811865476, x=-0.7071067811865476, y=0.0, z=0.0)
tracker = OrientationTracker(basis=basis)
viewer = Viewer(cube, mode='f2l', debug=True, orientation=tracker)

tracker.update(w, x, y, z)    # raw quaternion of a bluetooth cube
viewer.push("R U R'")         # queue moves to be played
viewer.run()
```

`push()` is safe to call from a producer thread, and dates what it is handed:
the cube then turns at the cadence of whoever is pushing, a single move behind
it, rather than at a beat of its own. A producer stamping its moves - `R@100` -
is honored as well, so a solve is replayed at its true speed whether it is
pushed live or handed over whole.

The window itself belongs to `GlfwHost`, which `run()` builds behind the
scenes. Reaching for it directly is how a cube is laid on the desktop - no
background, no decoration, floating above everything:

```python
from cubing_algs.display.gl.host import GlfwHost

GlfwHost(viewer, transparent=True).run()
```

A compositor is free to refuse, and says so in a logged line rather than by
drawing something unexpected. A transparent visual and a multisampled window
being mutually exclusive on some drivers, the cube is then antialiased offscreen
and copied to the window; `msaa=False` draws straight into it instead. A window
with no decoration has no bar to grab, so `Ctrl` and the left button carry it
across the screen - a gesture a decorated window answers too.

`examples/gl_transparent_window.py` plays an algorithm in such a window, and is
written as a subclass overriding `frame()` alone.

A window can also be taken off the screen without being given back. `hide()`
and `show()` are what a process opening a window for somebody else needs - a
tray, a launcher, a window glanced at between two other things - and
`visible=False` opens one already hidden. Nothing is released, and the loop
goes on turning behind it: the moves that arrive are played, a tracker
following a sensor catches up, and what is shown again is the cube as it now
stands rather than a hiding replayed in front of whoever asked for it back. The
keys closing a window go through the `on_close()` seam, so a host driven from
outside is free to put its window away where the loop would have ended.

### Command Line

```bash
# Write a PNG of a cube, or of a case, on any cube size
python -m cubing_algs apply "R U R' U'" --mode=oll --render cube.png --image-size 512
python -m cubing_algs apply "Rw U Rw' U'" --size 5 --render nxn.png
python -m cubing_algs case OLL 27 --render oll27.png --palette pastel

# Animate an algorithm, on any cube size
python -m cubing_algs animate "R U R' U'" --out sexy.gif
python -m cubing_algs animate "Rw U 3Rw' M2 x" --size 5 --out nxn.gif
python -m cubing_algs case OLL 27 --animate oll27.gif   # the case being solved

# Open an interactive window
python -m cubing_algs apply "R U R' U'" --mode=oll --view
```

`--image-size` counts pixels, where `--size` counts the cubies of an edge.

### Diagnosing the Backend

```bash
python -m cubing_algs.display.gl.doctor
```

Reports the contexts that can be created on this machine, what they support,
and writes a gradient PNG proving the pipeline works end to end.

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

**Performance characteristics:**
- Move execution: ~1-2 microseconds per move (C extension)
- Facelet/cubie conversion: ~10-20 microseconds uncached, ~0.1 microseconds cached
- Algorithm parsing: ~50-100 microseconds for typical algorithms

## Examples

### Generating the inverse of an OLL algorithm

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.invert import invert_moves
from cubing_algs import VCube

oll = parse_moves("F U F' R' F R U' R' F' R")  # OLL 14 Anti-Gun
oll_invert = oll.transform(invert_moves)
print(oll_invert)  # R' F R U R' F' R F U' F'

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
scramble_algo = scramble(3, iterations=25)
cube = VCube()
cube.rotate(scramble_algo)
print(f"Scrambled with: {scramble_algo}")
```

### Step-based scramble practice

```python
from cubing_algs.scrambler import scramble_step, scramble_easy_cross, scramble_f2l
from cubing_algs import VCube

# Practice PLL recognition
cube = VCube()
pll_scramble = scramble_step("PLL")
cube.rotate(pll_scramble)
cube.show(mode='oll')  # Visualize - all pieces oriented, only permutation scrambled

# Practice cross building with solution
scramble_alg, solution = scramble_easy_cross(difficulty='normal')
cube = VCube()
cube.rotate(scramble_alg)
print(f"Scramble: {scramble_alg}")
print(f"Solution: {solution}")

# Practice a specific F2L slot
f2l_scramble = scramble_f2l(slots=['FR'])
cube = VCube()
cube.rotate(f2l_scramble)
cube.show()  # Cross solved, FR slot scrambled
```

### Advanced algorithm development workflow

```python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.invert import invert_moves
from cubing_algs.transform.symmetry import symmetry_m_moves
from cubing_algs import VCube
from cubing_algs.scrambler import scramble

# Start with a commutator
base_alg = parse_moves("[R U R', D]")  # R U R' D R U' R' D'

# Generate variations
inverse = base_alg.transform(invert_moves)
m_symmetric = base_alg.transform(symmetry_m_moves)

# Analyze algorithms
print(f"Original: {base_alg} ({base_alg.metrics.htm} HTM)")
print(f"Comfort: {base_alg.ergonomics.comfort_rating}/10")
print(f"Affected pieces: {base_alg.impacts().facelets_mobilized_count}")
print(f"Inverse: {inverse} ({inverse.metrics.htm} HTM)")

# Test on virtual cube
cube = VCube()
cube.rotate(base_alg)
print(f"Is solved after: {cube.is_solved}")

# Test algorithm on scrambled cube
test_cube = VCube()
test_scramble = scramble(3, iterations=15)
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
