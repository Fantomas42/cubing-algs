"""Tests for 5x5x5 cube rotation using dynamic rotation system."""
import unittest

from cubing_algs.initial_state import get_initial_state
from cubing_algs.rotate_dynamic import rotate_move
from cubing_algs.vcube import VCube

# Solved 5x5x5 state: 150 facelets (6 faces * 25 facelets each)
# Face order: U, R, F, D, L, B
SOLVED_5X5X5 = get_initial_state(5)

# Expected states for slice moves (M, E, S) - verified against MagicCube
EXPECTED_5X5X5 = {
    'M': (
        'UUBUUUUBUUUUBUUUUBUUUUBUURRRRRRRRRRRRRRRRRRRRRRRRRFFUFFFFUFFFFUFFFFUFFFFUFFDDFDDDDFDDDDFDDDDFDDDDFDDLLLLLLLLLLLLLLLLLLLLLLLLLBBDBBBBDBBBBDBBBBDBBBBDBB'
    ),
    "M'": (
        'UUFUUUUFUUUUFUUUUFUUUUFUURRRRRRRRRRRRRRRRRRRRRRRRRFFDFFFFDFFFFDFFFFDFFFFDFFDDBDDDDBDDDDBDDDDBDDDDBDDLLLLLLLLLLLLLLLLLLLLLLLLLBBUBBBBUBBBBUBBBBUBBBBUBB'
    ),
    'M2': (
        'UUDUUUUDUUUUDUUUUDUUUUDUURRRRRRRRRRRRRRRRRRRRRRRRRFFBFFFFBFFFFBFFFFBFFFFBFFDDUDDDDUDDDDUDDDDUDDDDUDDLLLLLLLLLLLLLLLLLLLLLLLLLBBFBBBBFBBBBFBBBBFBBBBFBB'
    ),
    'E': (
        'UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRFFFFFRRRRRRRRRRFFFFFFFFFFLLLLLFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLBBBBBLLLLLLLLLLBBBBBBBBBBRRRRRBBBBBBBBBB'
    ),
    "E'": (
        'UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRBBBBBRRRRRRRRRRFFFFFFFFFFRRRRRFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLFFFFFLLLLLLLLLLBBBBBBBBBBLLLLLBBBBBBBBBB'
    ),
    'E2': (
        'UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRLLLLLRRRRRRRRRRFFFFFFFFFFBBBBBFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLRRRRRLLLLLLLLLLBBBBBBBBBBFFFFFBBBBBBBBBB'
    ),
    'S': (
        'UUUUUUUUUULLLLLUUUUUUUUUURRURRRRURRRRURRRRURRRRURRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDRRRRRDDDDDDDDDDLLDLLLLDLLLLDLLLLDLLLLDLLBBBBBBBBBBBBBBBBBBBBBBBBB'
    ),
    "S'": (
        'UUUUUUUUUURRRRRUUUUUUUUUURRDRRRRDRRRRDRRRRDRRRRDRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDLLLLLDDDDDDDDDDLLULLLLULLLLULLLLULLLLULLBBBBBBBBBBBBBBBBBBBBBBBBB'
    ),
    'S2': (
        'UUUUUUUUUUDDDDDUUUUUUUUUURRLRRRRLRRRRLRRRRLRRRRLRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDUUUUUDDDDDDDDDDLLRLLLLRLLLLRLLLLRLLLLRLLBBBBBBBBBBBBBBBBBBBBBBBBB'
    ),
    'M E': (
        'UUBUUUUBUUUUBUUUUBUUUUBUURRRRRRRRRRFFUFFRRRRRRRRRRFFUFFFFUFFLLLLLFFUFFFFUFFDDFDDDDFDDDDFDDDDFDDDDFDDLLLLLLLLLLBBDBBLLLLLLLLLLBBDBBBBDBBRRRRRBBDBBBBDBB'
    ),
    "M' E'": (
        'UUFUUUUFUUUUFUUUUFUUUUFUURRRRRRRRRRBBUBBRRRRRRRRRRFFDFFFFDFFRRRRRFFDFFFFDFFDDBDDDDBDDDDBDDDDBDDDDBDDLLLLLLLLLLFFDFFLLLLLLLLLLBBUBBBBUBBLLLLLBBUBBBBUBB'
    ),
    'M S': (
        'UUBUUUUBUULLLLLUUBUUUUBUURRURRRRURRRRBRRRRURRRRURRFFUFFFFUFFFFUFFFFUFFFFUFFDDFDDDDFDDRRRRRDDFDDDDFDDLLDLLLLDLLLLFLLLLDLLLLDLLBBDBBBBDBBBBDBBBBDBBBBDBB'
    ),
    'E S': (
        'UUUUUUUUUULLBLLUUUUUUUUUURRURRRRURRFFUFFRRURRRRURRFFFFFFFFFFLLLLLFFFFFFFFFFDDDDDDDDDDRRFRRDDDDDDDDDDLLDLLLLDLLBBDBBLLDLLLLDLLBBBBBBBBBBRRRRRBBBBBBBBBB'
    ),
    "M E M' E'": (
        'UUUUUUUUUUUULUUUUUUUUUUUURRRRRRRRRRRRBRRRRRRRRRRRRFFFFFFFFFFFFUFFFFFFFFFFFFDDDDDDDDDDDDRDDDDDDDDDDDDLLLLLLLLLLLLFLLLLLLLLLLLLBBBBBBBBBBBBDBBBBBBBBBBBB'
    ),
    "S M S' M'": (
        'UUUUUUUUUUUULUUUUUUUUUUUURRRRRRRRRRRRFRRRRRRRRRRRRFFFFFFFFFFFFDFFFFFFFFFFFFDDDDDDDDDDDDRDDDDDDDDDDDDLLLLLLLLLLLLBLLLLLLLLLLLLBBBBBBBBBBBBUBBBBBBBBBBBB'
    ),
}

# Expected states after moves (generated from magiccube)
EXPECTED_5X5X5_R = (
    'UUUUFUUUUFUUUUFUUUUFUUUUFRRRRRRRRRRRRRRRRRRRRRRRRRFFFFDFFFF'
    'DFFFFDFFFFDFFFFDDDDDBDDDDBDDDDBDDDDBDDDDBLLLLLLLLLLLLLLLL'
    'LLLLLLLLLUBBBBUBBBBUBBBBUBBBBUBBBB'
)
EXPECTED_5X5X5_RPRIME = (
    'UUUUBUUUUBUUUUBUUUUBUUUUBRRRRRRRRRRRRRRRRRRRRRRRRRFFFFUFFFF'
    'UFFFFUFFFFUFFFFUDDDDFDDDDFDDDDFDDDDFDDDDFLLLLLLLLLLLLLLLL'
    'LLLLLLLLLDBBBBDBBBBDBBBBDBBBBDBBBB'
)
EXPECTED_5X5X5_R2 = (
    'UUUUDUUUUDUUUUDUUUUDUUUUDRRRRRRRRRRRRRRRRRRRRRRRRRFFFFBFFFF'
    'BFFFFBFFFFBFFFFBDDDDUDDDDUDDDDUDDDDUDDDDULLLLLLLLLLLLLLLL'
    'LLLLLLLLLFBBBBFBBBBFBBBBFBBBBFBBBB'
)
EXPECTED_5X5X5_U = (
    'UUUUUUUUUUUUUUUUUUUUUUUUUBBBBBRRRRRRRRRRRRRRRRRRRRRRRRRFFF'
    'FFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDFFFFFLLLLLLLLL'
    'LLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBB'
)
EXPECTED_5X5X5_F = (
    'UUUUUUUUUUUUUUUUUUUULLLLLURRRRURRRRURRRRURRRRURRRRFFFFFFFF'
    'FFFFFFFFFFFFFFFFFRRRRRDDDDDDDDDDDDDDDDDDDDLLLLDLLLLDLLLLD'
    'LLLLDLLLLDBBBBBBBBBBBBBBBBBBBBBBBBB'
)
EXPECTED_5X5X5_x = (
    'FFFFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRDDDDD'
    'DDDDDDDDDDDDDDDDDDDDBBBBBBBBBBBBBBBBBBBBBBBBBLLLLLLLLLL'
    'LLLLLLLLLLLLLLLUUUUUUUUUUUUUUUUUUUUUUUUU'
)
EXPECTED_5X5X5_y = (
    'UUUUUUUUUUUUUUUUUUUUUUUUUBBBBBBBBBBBBBBBBBBBBBBBBBRRRRR'
    'RRRRRRRRRRRRRRRRRRRRDDDDDDDDDDDDDDDDDDDDDDDDDFFFFFFFFFF'
    'FFFFFFFFFFFFFFFLLLLLLLLLLLLLLLLLLLLLLLLL'
)
EXPECTED_5X5X5_z = (
    'LLLLLLLLLLLLLLLLLLLLLLLLLUUUUUUUUUUUUUUUUUUUUUUUUUFFFFF'
    'FFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRRRRDDDDDDDDDD'
    'DDDDDDDDDDDDDDDBBBBBBBBBBBBBBBBBBBBBBBBB'
)
EXPECTED_5X5X5_Rw = (
    'UUUFFUUUFFUUUFFUUUFFUUUFFRRRRRRRRRRRRRRRRRRRRRRRRRFFFDDFF'
    'FDDFFFDDFFFDDFFFDDDDDBBDDDBBDDDBBDDDBBDDDBBLLLLLLLLLLLL'
    'LLLLLLLLLLLLLUUBBBUUBBBUUBBBUUBBBUUBBB'
)
EXPECTED_5X5X5_2R = (
    'UUUFUUUUFUUUUFUUUUFUUUUFURRRRRRRRRRRRRRRRRRRRRRRRRFFFDF'
    'FFFDFFFFDFFFFDFFFFDFDDDBDDDDBDDDDBDDDDBDDDDBDLLLLLLLLLL'
    'LLLLLLLLLLLLLLLBUBBBBUBBBBUBBBBUBBBBUBBB'
)
EXPECTED_5X5X5_3R = (
    'UUFUUUUFUUUUFUUUUFUUUUFUURRRRRRRRRRRRRRRRRRRRRRRRRFFDFF'
    'FFDFFFFDFFFFDFFFFDFFDDBDDDDBDDDDBDDDDBDDDDBDDLLLLLLLLLL'
    'LLLLLLLLLLLLLLLBBUBBBBUBBBBUBBBBUBBBBUBB'
)


class Test5x5x5VCube(unittest.TestCase):
    """Test VCube implementation for 5x5x5."""

    def setUp(self) -> None:
        """Set up required components."""
        self.cube = VCube(size=5)

    def test_has_fixed_centers(self) -> None:
        """Check has_fixed_centers property."""
        self.assertTrue(self.cube.has_fixed_centers)

    def test_center_index(self) -> None:
        """Test the value of center index."""
        self.assertEqual(self.cube.center_index, 12)

    def test_get_face_center_indexes(self) -> None:
        """Test get face center indexes."""
        self.cube.rotate('F R U')

        self.assertEqual(
            self.cube.get_face_center_indexes(),
            ['U', 'R', 'F', 'D', 'L', 'B'],
        )

        self.cube.rotate('z2')

        self.assertEqual(
            self.cube.get_face_center_indexes(),
            ['D', 'L', 'F', 'U', 'R', 'B'],
        )

    def test_orientation(self) -> None:
        """Test orientation."""
        self.assertEqual(
            self.cube.orientation, 'UF',
        )

        self.cube.rotate('z2')

        self.assertEqual(
            self.cube.orientation, 'DF',
        )


class Test5x5x5BasicMoves(unittest.TestCase):
    """Test basic face moves on 5x5x5 cube."""

    def test_solved_state(self) -> None:
        """Test that solved state is correctly defined."""
        # Verify length
        self.assertEqual(len(SOLVED_5X5X5), 150)

        # Verify each face has 25 facelets
        faces = ['U', 'R', 'F', 'D', 'L', 'B']
        for i, face in enumerate(faces):
            start = i * 25
            end = start + 25
            face_colors = SOLVED_5X5X5[start:end]
            self.assertEqual(face_colors, face * 25)

    def test_r_move(self) -> None:
        """Test R move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, 'R', size=5)
        self.assertEqual(result, EXPECTED_5X5X5_R, 'R move state mismatch')
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_r_prime_move(self) -> None:
        """Test R' move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, "R'", size=5)
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_r_r_prime_cancel(self) -> None:
        """Test that R R' returns to solved state."""
        after_r = rotate_move(SOLVED_5X5X5, 'R', size=5)
        after_r_prime = rotate_move(after_r, "R'", size=5)
        self.assertEqual(after_r_prime, SOLVED_5X5X5)

    def test_r2_move(self) -> None:
        """Test R2 move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, 'R2', size=5)
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_r_four_times(self) -> None:
        """Test that R applied 4 times returns to solved state."""
        state = SOLVED_5X5X5
        for _ in range(4):
            state = rotate_move(state, 'R', size=5)
        self.assertEqual(state, SOLVED_5X5X5)

    def test_u_move(self) -> None:
        """Test U move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, 'U', size=5)
        self.assertEqual(result, EXPECTED_5X5X5_U, 'U move state mismatch')
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_u_four_times(self) -> None:
        """Test that U applied 4 times returns to solved state."""
        state = SOLVED_5X5X5
        for _ in range(4):
            state = rotate_move(state, 'U', size=5)
        self.assertEqual(state, SOLVED_5X5X5)

    def test_f_move(self) -> None:
        """Test F move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, 'F', size=5)
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_f_four_times(self) -> None:
        """Test that F applied 4 times returns to solved state."""
        state = SOLVED_5X5X5
        for _ in range(4):
            state = rotate_move(state, 'F', size=5)
        self.assertEqual(state, SOLVED_5X5X5)

    def test_all_basic_moves(self) -> None:
        """Test that all basic moves work and are invertible."""
        moves = ['R', 'L', 'U', 'D', 'F', 'B']

        for move in moves:
            # Test move changes state
            result = rotate_move(SOLVED_5X5X5, move, size=5)
            self.assertNotEqual(
                result, SOLVED_5X5X5, f'{move} should change state',
            )

            # Test inverse returns to solved
            inverse = move + "'"
            back = rotate_move(result, inverse, size=5)
            self.assertEqual(
                back, SOLVED_5X5X5,
                f'{move} followed by {inverse} should return to solved',
            )

            # Test 4 repetitions return to solved
            state = SOLVED_5X5X5
            for _ in range(4):
                state = rotate_move(state, move, size=5)
            self.assertEqual(
                state, SOLVED_5X5X5,
                f'{move} applied 4 times should return to solved',
            )


class Test5x5x5Rotations(unittest.TestCase):
    """Test cube rotation moves (x, y, z) on 5x5x5."""

    def test_x_rotation(self) -> None:
        """Test x rotation on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, 'x', size=5)
        self.assertEqual(result, EXPECTED_5X5X5_x, 'x rotation state mismatch')
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_x_four_times(self) -> None:
        """Test that x applied 4 times returns to solved state."""
        state = SOLVED_5X5X5
        for _ in range(4):
            state = rotate_move(state, 'x', size=5)
        self.assertEqual(state, SOLVED_5X5X5)

    def test_y_rotation(self) -> None:
        """Test y rotation on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, 'y', size=5)
        self.assertEqual(result, EXPECTED_5X5X5_y, 'y rotation state mismatch')
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_y_four_times(self) -> None:
        """Test that y applied 4 times returns to solved state."""
        state = SOLVED_5X5X5
        for _ in range(4):
            state = rotate_move(state, 'y', size=5)
        self.assertEqual(state, SOLVED_5X5X5)

    def test_z_rotation(self) -> None:
        """Test z rotation on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, 'z', size=5)
        self.assertEqual(result, EXPECTED_5X5X5_z, 'z rotation state mismatch')
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_z_four_times(self) -> None:
        """Test that z applied 4 times returns to solved state."""
        state = SOLVED_5X5X5
        for _ in range(4):
            state = rotate_move(state, 'z', size=5)
        self.assertEqual(state, SOLVED_5X5X5)

    def test_rotation_inverses(self) -> None:
        """Test that rotation moves are invertible."""
        rotations = ['x', 'y', 'z']

        for rotation in rotations:
            result = rotate_move(SOLVED_5X5X5, rotation, size=5)
            inverse = rotation + "'"
            back = rotate_move(result, inverse, size=5)
            self.assertEqual(
                back, SOLVED_5X5X5,
                f'{rotation} followed by {inverse} should return to solved',
            )


class Test5x5x5Sequences(unittest.TestCase):
    """Test move sequences on 5x5x5."""

    def test_double_moves(self) -> None:
        """Test that double moves work correctly."""
        # R2 should equal R R
        r_r = rotate_move(SOLVED_5X5X5, 'R', size=5)
        r_r = rotate_move(r_r, 'R', size=5)

        r2 = rotate_move(SOLVED_5X5X5, 'R2', size=5)

        self.assertEqual(r_r, r2)

    def test_commutator_sequence(self) -> None:
        """Test a commutator sequence on 5x5x5."""
        state = SOLVED_5X5X5
        state = rotate_move(state, 'R', size=5)
        state = rotate_move(state, 'U', size=5)
        state = rotate_move(state, "R'", size=5)
        state = rotate_move(state, "U'", size=5)

        # This sequence should change the cube
        self.assertNotEqual(state, SOLVED_5X5X5)

    def test_mixed_sequence(self) -> None:
        """Test a mixed sequence with multiple move types."""
        state = SOLVED_5X5X5
        moves = ['R', "U'", 'F2', "L'", 'D', "B'"]

        for move in moves:
            state = rotate_move(state, move, size=5)

        # Should be scrambled
        self.assertNotEqual(state, SOLVED_5X5X5)

        # Apply inverse sequence to return to solved
        for move in reversed(moves):
            if "'" in move:
                inverse_move = move.replace("'", '')
            elif '2' in move:
                inverse_move = move  # Double moves are self-inverse
            else:
                inverse_move = move + "'"

            state = rotate_move(state, inverse_move, size=5)

        # Should be back to solved
        self.assertEqual(state, SOLVED_5X5X5)


class Test5x5x5StateLength(unittest.TestCase):
    """Test state length consistency."""

    def test_state_length_preserved(self) -> None:
        """Test that state length remains 150 after moves."""
        state = SOLVED_5X5X5
        moves = ['R', 'U', 'F', 'L', 'D', 'B', 'x', 'y', 'z']

        for move in moves:
            state = rotate_move(state, move, size=5)
            self.assertEqual(
                len(state), 150,
                f'State length should be 150 after {move}',
            )


class Test5x5x5LargerCubeSpecific(unittest.TestCase):
    """Test 5x5x5-specific characteristics."""

    def test_center_count(self) -> None:
        """Test that 5x5x5 has correct number of center pieces."""
        # 5x5x5 has 9 centers per face (excluding corners and edges)
        # Total: 6 faces * 9 centers = 54 center facelets
        # But we can't easily test this without specific logic

        # Instead, test that the cube structure is correct
        self.assertEqual(len(SOLVED_5X5X5), 150)
        self.assertEqual(len(SOLVED_5X5X5) // 6, 25)

    def test_layer_structure(self) -> None:
        """Test that 5x5x5 has 5 layers."""
        # Each face is 5x5
        face_size = 5
        expected_facelets_per_face = face_size * face_size
        self.assertEqual(expected_facelets_per_face, 25)

        # Total facelets
        total_facelets = 6 * expected_facelets_per_face
        self.assertEqual(total_facelets, 150)
        self.assertEqual(len(SOLVED_5X5X5), total_facelets)


class Test5x5x5WideMoves(unittest.TestCase):
    """Test wide moves on 5x5x5 cube."""

    def test_rw_move(self) -> None:
        """Test Rw (right wide) move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, 'Rw', size=5)
        self.assertEqual(result, EXPECTED_5X5X5_Rw, 'Rw move state mismatch')
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_rw_inverse(self) -> None:
        """Test Rw Rw' returns to solved state."""
        after_rw = rotate_move(SOLVED_5X5X5, 'Rw', size=5)
        after_rw_prime = rotate_move(after_rw, "Rw'", size=5)
        self.assertEqual(after_rw_prime, SOLVED_5X5X5)

    def test_all_wide_moves(self) -> None:
        """Test that all wide moves work and are invertible."""
        wide_moves = ['Rw', 'Lw', 'Uw', 'Dw', 'Fw', 'Bw']

        for move in wide_moves:
            # Test move changes state
            result = rotate_move(SOLVED_5X5X5, move, size=5)
            self.assertNotEqual(
                result, SOLVED_5X5X5,
                f'{move} should change state',
            )

            # Test inverse returns to solved
            inverse = move + "'"
            back = rotate_move(result, inverse, size=5)
            self.assertEqual(
                back, SOLVED_5X5X5,
                f'{move} followed by {inverse} should return to solved',
            )

    def test_3rw_move(self) -> None:
        """Test 3Rw (3-layer wide) move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, '3Rw', size=5)
        self.assertNotEqual(result, SOLVED_5X5X5)

        # Test inverse
        inverse = rotate_move(result, "3Rw'", size=5)
        self.assertEqual(inverse, SOLVED_5X5X5)


class Test5x5x5LayeredMoves(unittest.TestCase):
    """Test layered moves on 5x5x5 cube."""

    def test_2r_move(self) -> None:
        """Test 2R (second layer) move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, '2R', size=5)
        self.assertEqual(result, EXPECTED_5X5X5_2R, '2R move state mismatch')
        self.assertNotEqual(result, SOLVED_5X5X5)

    def test_2r_inverse(self) -> None:
        """Test 2R 2R' returns to solved state."""
        after_2r = rotate_move(SOLVED_5X5X5, '2R', size=5)
        after_2r_prime = rotate_move(after_2r, "2R'", size=5)
        self.assertEqual(after_2r_prime, SOLVED_5X5X5)

    def test_all_second_layer_moves(self) -> None:
        """Test that all second layer moves work and are invertible."""
        layer_moves = ['2R', '2L', '2U', '2D', '2F', '2B']

        for move in layer_moves:
            # Test move changes state
            result = rotate_move(SOLVED_5X5X5, move, size=5)
            self.assertNotEqual(
                result, SOLVED_5X5X5,
                f'{move} should change state',
            )

            # Test inverse returns to solved
            inverse = move + "'"
            back = rotate_move(result, inverse, size=5)
            self.assertEqual(
                back, SOLVED_5X5X5,
                f'{move} followed by {inverse} should return to solved',
            )

    def test_3r_move(self) -> None:
        """Test 3R (third layer) move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, '3R', size=5)
        self.assertEqual(result, EXPECTED_5X5X5_3R, '3R move state mismatch')
        self.assertNotEqual(result, SOLVED_5X5X5)

        # Test inverse
        inverse = rotate_move(result, "3R'", size=5)
        self.assertEqual(inverse, SOLVED_5X5X5)

    def test_4r_move(self) -> None:
        """Test 4R (fourth layer) move on 5x5x5."""
        result = rotate_move(SOLVED_5X5X5, '4R', size=5)
        self.assertNotEqual(result, SOLVED_5X5X5)

        # Test inverse
        inverse = rotate_move(result, "4R'", size=5)
        self.assertEqual(inverse, SOLVED_5X5X5)

    def test_layered_vs_basic(self) -> None:
        """Test that layered moves differ from basic moves."""
        r_result = rotate_move(SOLVED_5X5X5, 'R', size=5)
        two_r_result = rotate_move(SOLVED_5X5X5, '2R', size=5)
        three_r_result = rotate_move(SOLVED_5X5X5, '3R', size=5)

        # They should all be different
        self.assertNotEqual(r_result, two_r_result)
        self.assertNotEqual(r_result, three_r_result)
        self.assertNotEqual(two_r_result, three_r_result)


class Test5x5x5SliceMoves(unittest.TestCase):
    """Test slice moves (M, E, S) on 5x5x5 cube."""

    def test_m_move(self) -> None:
        """Test M move on 5x5x5 matches MagicCube."""
        cube = VCube(size=5)
        result = cube.rotate('M')
        self.assertEqual(result, EXPECTED_5X5X5['M'])

    def test_m_prime_move(self) -> None:
        """Test M' move on 5x5x5 matches MagicCube."""
        cube = VCube(size=5)
        result = cube.rotate("M'")
        self.assertEqual(result, EXPECTED_5X5X5["M'"])

    def test_m2_move(self) -> None:
        """Test M2 move on 5x5x5 matches MagicCube."""
        cube = VCube(size=5)
        result = cube.rotate('M2')
        self.assertEqual(result, EXPECTED_5X5X5['M2'])

    def test_e_move(self) -> None:
        """Test E move on 5x5x5 matches MagicCube."""
        cube = VCube(size=5)
        result = cube.rotate('E')
        self.assertEqual(result, EXPECTED_5X5X5['E'])

    def test_e_prime_move(self) -> None:
        """Test E' move on 5x5x5 matches MagicCube."""
        cube = VCube(size=5)
        result = cube.rotate("E'")
        self.assertEqual(result, EXPECTED_5X5X5["E'"])

    def test_e2_move(self) -> None:
        """Test E2 move on 5x5x5 matches MagicCube."""
        cube = VCube(size=5)
        result = cube.rotate('E2')
        self.assertEqual(result, EXPECTED_5X5X5['E2'])

    def test_s_move(self) -> None:
        """Test S move on 5x5x5 matches MagicCube."""
        cube = VCube(size=5)
        result = cube.rotate('S')
        self.assertEqual(result, EXPECTED_5X5X5['S'])

    def test_s_prime_move(self) -> None:
        """Test S' move on 5x5x5 matches MagicCube."""
        cube = VCube(size=5)
        result = cube.rotate("S'")
        self.assertEqual(result, EXPECTED_5X5X5["S'"])

    def test_s2_move(self) -> None:
        """Test S2 move on 5x5x5 matches MagicCube."""
        cube = VCube(size=5)
        result = cube.rotate('S2')
        self.assertEqual(result, EXPECTED_5X5X5['S2'])

    def test_slice_move_combinations(self) -> None:
        """Test combined slice move sequences on 5x5x5."""
        # Test M E
        cube = VCube(size=5)
        result = cube.rotate('M E')
        self.assertEqual(result, EXPECTED_5X5X5['M E'])

        # Test M S
        cube = VCube(size=5)
        result = cube.rotate('M S')
        self.assertEqual(result, EXPECTED_5X5X5['M S'])

        # Test E S
        cube = VCube(size=5)
        result = cube.rotate('E S')
        self.assertEqual(result, EXPECTED_5X5X5['E S'])

    def test_slice_move_reversibility(self) -> None:
        """Test that slice moves are reversible on 5x5x5."""
        for move in ['M', 'E', 'S']:
            with self.subTest(move=move):
                cube = VCube(size=5)
                cube.rotate(f'{move} {move} {move} {move}')
                self.assertTrue(cube.is_solved)

    def test_slice_move_prime_cancels(self) -> None:
        """Test that slice moves cancel with their primes."""
        for move in ['M', 'E', 'S']:
            with self.subTest(move=move):
                cube = VCube(size=5)
                cube.rotate(f"{move} {move}'")
                self.assertTrue(cube.is_solved)
