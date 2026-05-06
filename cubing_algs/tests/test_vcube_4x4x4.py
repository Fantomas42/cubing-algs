"""Tests for 4x4x4 cube rotation using dynamic rotation system."""
import unittest

from cubing_algs.constants import FACE_ORDER
from cubing_algs.exceptions import NotSupportedCubeSizeError
from cubing_algs.extensions.rotate_dynamic import rotate_move
from cubing_algs.solved_state import get_solved_facelets
from cubing_algs.solved_state import get_unique_facelets
from cubing_algs.vcube import VCube

# Solved 4x4x4 state: 96 facelets (6 faces * 16 facelets each)
# Face order: U, R, F, D, L, B
SOLVED_4X4X4 = get_solved_facelets(4)
UNIQUE_4X4X4 = get_unique_facelets(4)

# Expected states after moves (generated from magiccube)
EXPECTED_4X4X4_R = (
    'UUUFUUUFUUUFUUUFRRRRRRRRRRRRRRRRFFFDFFFDFFFDFFFD'
    'DDDBDDDBDDDBDDDBLLLLLLLLLLLLLLLLUBBBUBBBUBBBUBBB'
)
EXPECTED_4X4X4_RPRIME = (
    'UUUBUUUBUUUBUUUBRRRRRRRRRRRRRRRRFFFUFFFUFFFUFFFUD'
    'DDFDDDFDDDFDDDFLLLLLLLLLLLLLLLLDBBBDBBBDBBBDBBB'
)
EXPECTED_4X4X4_R2 = (
    'UUUDUUUDUUUDUUUDRRRRRRRRRRRRRRRRFFFBFFFBFFFBFFFBD'
    'DDUDDDUDDDUDDDULLLLLLLLLLLLLLLLFBBBFBBBFBBBFBBB'
)
EXPECTED_4X4X4_U = (
    'UUUUUUUUUUUUUUUUBBBBRRRRRRRRRRRRRRRRFFFFFFFFFFFFD'
    'DDDDDDDDDDDDDDDFFFFLLLLLLLLLLLLLLLLBBBBBBBBBBBB'
)
EXPECTED_4X4X4_F = (
    'UUUUUUUUUUUULLLLURRRURRRURRRURRRFFFFFFFFFFFFFFFF'
    'RRRRDDDDDDDDDDDDLLLDLLLDLLLDLLLDBBBBBBBBBBBBBBBB'
)
EXPECTED_4X4X4_x = (
    'FFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRDDDDDDDDDDDDDDDDB'
    'BBBBBBBBBBBBBBBLLLLLLLLLLLLLLLLUUUUUUUUUUUUUUUU'
)
EXPECTED_4X4X4_y = (
    'UUUUUUUUUUUUUUUUBBBBBBBBBBBBBBBBRRRRRRRRRRRRRRR'
    'RDDDDDDDDDDDDDDDDFFFFFFFFFFFFFFFFLLLLLLLLLLLLLLLL'
)
EXPECTED_4X4X4_z = (
    'LLLLLLLLLLLLLLLLUUUUUUUUUUUUUUUUFFFFFFFFFFFFFFFF'
    'RRRRRRRRRRRRRRRRDDDDDDDDDDDDDDDDBBBBBBBBBBBBBBBB'
)
EXPECTED_4X4X4_Rw = (
    'UUFFUUFFUUFFUUFFRRRRRRRRRRRRRRRRFFDDFFDDFFDDFFDD'
    'DDBBDDBBDDBBDDBBLLLLLLLLLLLLLLLLUUBBUUBBUUBBUUBB'
)
EXPECTED_4X4X4_2R = (
    'UUFUUUFUUUFUUUFURRRRRRRRRRRRRRRRFFDFFFDFFFDFFFDF'
    'DDBDDDBDDDBDDDBDLLLLLLLLLLLLLLLLBUBBBUBBBUBBBUBB'
)


class Test4x4x4VCube(unittest.TestCase):
    """Test VCube implementation for 4x4x4."""

    def setUp(self) -> None:
        """Set up required components."""
        self.cube = VCube(size=4)

    def test_has_fixed_centers(self) -> None:
        """Check has_fixed_centers property."""
        self.assertFalse(self.cube.has_fixed_centers)

    def test_center_index(self) -> None:
        """Test the value of center index."""
        self.assertEqual(self.cube.center_index, 5)

    def test_orientation(self) -> None:
        """Test orientation."""
        self.assertEqual(
            self.cube.orientation, 'UF',
        )

        self.cube.rotate('z2')

        self.assertEqual(
            self.cube.orientation, 'DF',
        )

    def test_cubies(self) -> None:
        """Test cubies."""
        with self.assertRaises(NotSupportedCubeSizeError):
            _ = self.cube.cubies

    def test_check_integrity(self) -> None:
        """Test check_integrity on a 4x4x4 cube."""
        self.assertTrue(self.cube.check_integrity())

    def test_to_algorithm(self) -> None:
        """Test to_algorithm raises on non-3x3x3 cubes."""
        other = VCube(size=4)
        with self.assertRaises(NotSupportedCubeSizeError):
            self.cube.to_algorithm(other)


class Test4x4x4ScrambledVCube(unittest.TestCase):
    """Test VCube implementation for 4x4x4."""

    def test_scrambled_oriented_copy_issue_01(self) -> None:
        """Test issue with scrambled center."""
        cube = VCube(size=4)
        cube.rotate(
            "U B2 2U2 L B2 L Uw B2 U' B' 2R2 "
            "U F2 2D2 Rw2 B' 2L' 2U2 F' Rw' U' "
            "B' D R2 F' 2D2 B L' Fw2 R2 U' Fw "
            "Uw' L2 D F' L' F2 Rw2 U' L U L2 "
            "D2 2L2 B2 R",
        )

        for orientation in ('DF', 'UF'):
            with self.subTest(orientation=orientation):
                self.assertIsInstance(
                    cube.oriented_copy(orientation),
                    VCube,
                )

    def test_scrambled_oriented_copy_issue_02(self) -> None:
        """Test issue with scrambled center."""
        cube = VCube(size=4)
        cube.rotate(
            "F2 U2 F2 2L' D2 R' Dw' 2R' Fw2 "
            "2L' 2U2 R' Dw2 2R F2 U' B' 2L2 "
            "Dw2 2R2 Fw' R' D2 L F U' B' Lw2 "
            "2U2 2L2 Fw U2 B2 U2 B2 L2 F Lw' "
            "D2 L2 B2 2L' B' R2 B' D' R2 2D2",
        )

        for orientation in ('DF', 'UF'):
            with self.subTest(orientation=orientation):
                self.assertIsInstance(
                    cube.oriented_copy(orientation),
                    VCube,
                )


class Test4x4x4BasicMoves(unittest.TestCase):
    """Test basic face moves on 4x4x4 cube."""

    def test_solved_state(self) -> None:
        """Test that solved state is correctly defined."""
        # Verify length
        self.assertEqual(len(SOLVED_4X4X4), 96)

        # Verify each face has 16 facelets
        for i, face in enumerate(FACE_ORDER):
            start = i * 16
            end = start + 16
            face_colors = SOLVED_4X4X4[start:end]
            self.assertEqual(face_colors, face * 16)

    def test_r_move(self) -> None:
        """Test R move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, 'R', size=4)
        self.assertEqual(result, EXPECTED_4X4X4_R, 'R move state mismatch')
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_r_prime_move(self) -> None:
        """Test R' move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, "R'", size=4)
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_r_r_prime_cancel(self) -> None:
        """Test that R R' returns to solved state."""
        after_r = rotate_move(SOLVED_4X4X4, 'R', size=4)
        after_r_prime = rotate_move(after_r, "R'", size=4)
        self.assertEqual(after_r_prime, SOLVED_4X4X4)

    def test_r2_move(self) -> None:
        """Test R2 move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, 'R2', size=4)
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_r_four_times(self) -> None:
        """Test that R applied 4 times returns to solved state."""
        state = SOLVED_4X4X4
        for _ in range(4):
            state = rotate_move(state, 'R', size=4)
        self.assertEqual(state, SOLVED_4X4X4)

    def test_u_move(self) -> None:
        """Test U move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, 'U', size=4)
        self.assertEqual(result, EXPECTED_4X4X4_U, 'U move state mismatch')
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_u_four_times(self) -> None:
        """Test that U applied 4 times returns to solved state."""
        state = SOLVED_4X4X4
        for _ in range(4):
            state = rotate_move(state, 'U', size=4)
        self.assertEqual(state, SOLVED_4X4X4)

    def test_f_move(self) -> None:
        """Test F move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, 'F', size=4)
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_f_four_times(self) -> None:
        """Test that F applied 4 times returns to solved state."""
        state = SOLVED_4X4X4
        for _ in range(4):
            state = rotate_move(state, 'F', size=4)
        self.assertEqual(state, SOLVED_4X4X4)

    def test_all_basic_moves(self) -> None:
        """Test that all basic moves work and are invertible."""
        moves = ['R', 'L', 'U', 'D', 'F', 'B']

        for move in moves:
            # Test move changes state
            result = rotate_move(SOLVED_4X4X4, move, size=4)
            self.assertNotEqual(
                result, SOLVED_4X4X4, f'{move} should change state',
            )

            # Test inverse returns to solved
            inverse = move + "'"
            back = rotate_move(result, inverse, size=4)
            self.assertEqual(
                back, SOLVED_4X4X4,
                f'{move} followed by {inverse} should return to solved',
            )

            # Test 4 repetitions return to solved
            state = SOLVED_4X4X4
            for _ in range(4):
                state = rotate_move(state, move, size=4)
            self.assertEqual(
                state, SOLVED_4X4X4,
                f'{move} applied 4 times should return to solved',
            )


class Test4x4x4Rotations(unittest.TestCase):
    """Test cube rotation moves (x, y, z) on 4x4x4."""

    def test_x_rotation(self) -> None:
        """Test x rotation on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, 'x', size=4)
        self.assertEqual(result, EXPECTED_4X4X4_x, 'x rotation state mismatch')
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_x_four_times(self) -> None:
        """Test that x applied 4 times returns to solved state."""
        state = SOLVED_4X4X4
        for _ in range(4):
            state = rotate_move(state, 'x', size=4)
        self.assertEqual(state, SOLVED_4X4X4)

    def test_y_rotation(self) -> None:
        """Test y rotation on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, 'y', size=4)
        self.assertEqual(result, EXPECTED_4X4X4_y, 'y rotation state mismatch')
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_y_four_times(self) -> None:
        """Test that y applied 4 times returns to solved state."""
        state = SOLVED_4X4X4
        for _ in range(4):
            state = rotate_move(state, 'y', size=4)
        self.assertEqual(state, SOLVED_4X4X4)

    def test_z_rotation(self) -> None:
        """Test z rotation on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, 'z', size=4)
        self.assertEqual(result, EXPECTED_4X4X4_z, 'z rotation state mismatch')
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_z_four_times(self) -> None:
        """Test that z applied 4 times returns to solved state."""
        state = SOLVED_4X4X4
        for _ in range(4):
            state = rotate_move(state, 'z', size=4)
        self.assertEqual(state, SOLVED_4X4X4)

    def test_rotation_inverses(self) -> None:
        """Test that rotation moves are invertible."""
        rotations = ['x', 'y', 'z']

        for rotation in rotations:
            result = rotate_move(SOLVED_4X4X4, rotation, size=4)
            inverse = rotation + "'"
            back = rotate_move(result, inverse, size=4)
            self.assertEqual(
                back, SOLVED_4X4X4,
                f'{rotation} followed by {inverse} should return to solved',
            )


class Test4x4x4Sequences(unittest.TestCase):
    """Test move sequences on 4x4x4."""

    def test_double_moves(self) -> None:
        """Test that double moves work correctly."""
        # R2 should equal R R
        r_r = rotate_move(SOLVED_4X4X4, 'R', size=4)
        r_r = rotate_move(r_r, 'R', size=4)

        r2 = rotate_move(SOLVED_4X4X4, 'R2', size=4)

        self.assertEqual(r_r, r2)

    def test_commutator_sequence(self) -> None:
        """Test a commutator sequence on 4x4x4."""
        state = SOLVED_4X4X4
        state = rotate_move(state, 'R', size=4)
        state = rotate_move(state, 'U', size=4)
        state = rotate_move(state, "R'", size=4)
        state = rotate_move(state, "U'", size=4)

        # This sequence should change the cube
        self.assertNotEqual(state, SOLVED_4X4X4)

    def test_mixed_sequence(self) -> None:
        """Test a mixed sequence with multiple move types."""
        state = SOLVED_4X4X4
        moves = ['R', "U'", 'F2', "L'", 'D', "B'"]

        for move in moves:
            state = rotate_move(state, move, size=4)

        # Should be scrambled
        self.assertNotEqual(state, SOLVED_4X4X4)

        # Apply inverse sequence to return to solved
        for move in reversed(moves):
            if "'" in move:
                inverse_move = move.replace("'", '')
            elif '2' in move:
                inverse_move = move  # Double moves are self-inverse
            else:
                inverse_move = move + "'"

            state = rotate_move(state, inverse_move, size=4)

        # Should be back to solved
        self.assertEqual(state, SOLVED_4X4X4)


class Test4x4x4StateLength(unittest.TestCase):
    """Test state length consistency."""

    def test_state_length_preserved(self) -> None:
        """Test that state length remains 96 after moves."""
        state = SOLVED_4X4X4
        moves = ['R', 'U', 'F', 'L', 'D', 'B', 'x', 'y', 'z']

        for move in moves:
            state = rotate_move(state, move, size=4)
            self.assertEqual(
                len(state), 96,
                f'State length should be 96 after {move}',
            )


class Test4x4x4WideMoves(unittest.TestCase):
    """Test wide moves on 4x4x4 cube."""

    def test_rw_move(self) -> None:
        """Test Rw (right wide) move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, 'Rw', size=4)
        self.assertEqual(result, EXPECTED_4X4X4_Rw, 'Rw move state mismatch')
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_rw_inverse(self) -> None:
        """Test Rw Rw' returns to solved state."""
        after_rw = rotate_move(SOLVED_4X4X4, 'Rw', size=4)
        after_rw_prime = rotate_move(after_rw, "Rw'", size=4)
        self.assertEqual(after_rw_prime, SOLVED_4X4X4)

    def test_rw_four_times(self) -> None:
        """Test that Rw applied 4 times returns to solved state."""
        state = SOLVED_4X4X4
        for _ in range(4):
            state = rotate_move(state, 'Rw', size=4)
        self.assertEqual(state, SOLVED_4X4X4)

    def test_all_wide_moves(self) -> None:
        """Test that all wide moves work and are invertible."""
        wide_moves = ['Rw', 'Lw', 'Uw', 'Dw', 'Fw', 'Bw']

        for move in wide_moves:
            # Test move changes state
            result = rotate_move(SOLVED_4X4X4, move, size=4)
            self.assertNotEqual(
                result, SOLVED_4X4X4,
                f'{move} should change state',
            )

            # Test inverse returns to solved
            inverse = move + "'"
            back = rotate_move(result, inverse, size=4)
            self.assertEqual(
                back, SOLVED_4X4X4,
                f'{move} followed by {inverse} should return to solved',
            )

            # Test 4 repetitions return to solved
            state = SOLVED_4X4X4
            for _ in range(4):
                state = rotate_move(state, move, size=4)
            self.assertEqual(
                state, SOLVED_4X4X4,
                f'{move} applied 4 times should return to solved',
            )

    def test_3rw_move(self) -> None:
        """Test 3Rw (3-layer wide) move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, '3Rw', size=4)
        self.assertNotEqual(result, SOLVED_4X4X4)

        # Test inverse
        inverse = rotate_move(result, "3Rw'", size=4)
        self.assertEqual(inverse, SOLVED_4X4X4)


class Test4x4x4LayeredMoves(unittest.TestCase):
    """Test layered moves on 4x4x4 cube."""

    def test_2r_move(self) -> None:
        """Test 2R (second layer) move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, '2R', size=4)
        self.assertEqual(result, EXPECTED_4X4X4_2R, '2R move state mismatch')
        self.assertNotEqual(result, SOLVED_4X4X4)

    def test_2r_inverse(self) -> None:
        """Test 2R 2R' returns to solved state."""
        after_2r = rotate_move(SOLVED_4X4X4, '2R', size=4)
        after_2r_prime = rotate_move(after_2r, "2R'", size=4)
        self.assertEqual(after_2r_prime, SOLVED_4X4X4)

    def test_2r_four_times(self) -> None:
        """Test that 2R applied 4 times returns to solved state."""
        state = SOLVED_4X4X4
        for _ in range(4):
            state = rotate_move(state, '2R', size=4)
        self.assertEqual(state, SOLVED_4X4X4)

    def test_all_second_layer_moves(self) -> None:
        """Test that all second layer moves work and are invertible."""
        layer_moves = ['2R', '2L', '2U', '2D', '2F', '2B']

        for move in layer_moves:
            # Test move changes state
            result = rotate_move(SOLVED_4X4X4, move, size=4)
            self.assertNotEqual(
                result, SOLVED_4X4X4,
                f'{move} should change state',
            )

            # Test inverse returns to solved
            inverse = move + "'"
            back = rotate_move(result, inverse, size=4)
            self.assertEqual(
                back, SOLVED_4X4X4,
                f'{move} followed by {inverse} should return to solved',
            )

    def test_layered_vs_basic(self) -> None:
        """Test that layered moves differ from basic moves."""
        r_result = rotate_move(SOLVED_4X4X4, 'R', size=4)
        two_r_result = rotate_move(SOLVED_4X4X4, '2R', size=4)

        # They should be different because they affect different layers
        self.assertNotEqual(r_result, two_r_result)

    def test_3r_move(self) -> None:
        """Test 3R (third layer) move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, '3R', size=4)
        self.assertNotEqual(result, SOLVED_4X4X4)

        # Test inverse
        inverse = rotate_move(result, "3R'", size=4)
        self.assertEqual(inverse, SOLVED_4X4X4)


class Test4x4x4WideAndLayered(unittest.TestCase):
    """Test combinations of wide and layered moves."""

    def test_2rw_move(self) -> None:
        """Test 2Rw (2-layer wide) move on 4x4x4."""
        result = rotate_move(SOLVED_4X4X4, '2Rw', size=4)
        self.assertNotEqual(result, SOLVED_4X4X4)

        # 2Rw should equal Rw (both affect outer 2 layers)
        rw_result = rotate_move(SOLVED_4X4X4, 'Rw', size=4)
        self.assertEqual(result, rw_result)

    def test_double_wide_moves(self) -> None:
        """Test double wide moves."""
        # Rw2 should equal Rw Rw
        rw_rw = rotate_move(SOLVED_4X4X4, 'Rw', size=4)
        rw_rw = rotate_move(rw_rw, 'Rw', size=4)

        rw2 = rotate_move(SOLVED_4X4X4, 'Rw2', size=4)
        self.assertEqual(rw_rw, rw2)


class Test4x4x4SiGNNotation(unittest.TestCase):
    """Test SiGN notation (lowercase) for wide moves on 4x4x4."""

    def test_lowercase_r_equals_rw(self) -> None:
        """Test that lowercase 'r' is equivalent to 'Rw'."""
        result_r = rotate_move(SOLVED_4X4X4, 'r', size=4)
        result_rw = rotate_move(SOLVED_4X4X4, 'Rw', size=4)
        self.assertEqual(result_r, result_rw, 'r should equal Rw')

    def test_lowercase_u_equals_uw(self) -> None:
        """Test that lowercase 'u' is equivalent to 'Uw'."""
        result_u = rotate_move(SOLVED_4X4X4, 'u', size=4)
        result_uw = rotate_move(SOLVED_4X4X4, 'Uw', size=4)
        self.assertEqual(result_u, result_uw, 'u should equal Uw')

    def test_lowercase_f_equals_fw(self) -> None:
        """Test that lowercase 'f' is equivalent to 'Fw'."""
        result_f = rotate_move(SOLVED_4X4X4, 'f', size=4)
        result_fw = rotate_move(SOLVED_4X4X4, 'Fw', size=4)
        self.assertEqual(result_f, result_fw, 'f should equal Fw')

    def test_all_lowercase_wide_moves(self) -> None:
        """Test that all lowercase moves are equivalent to wide moves."""
        lowercase_moves = ['r', 'l', 'u', 'd', 'f', 'b']
        uppercase_moves = ['Rw', 'Lw', 'Uw', 'Dw', 'Fw', 'Bw']

        for lower, upper in zip(lowercase_moves, uppercase_moves, strict=True):
            with self.subTest(move=lower):
                result_lower = rotate_move(SOLVED_4X4X4, lower, size=4)
                result_upper = rotate_move(SOLVED_4X4X4, upper, size=4)
                self.assertEqual(
                    result_lower, result_upper,
                    f'{lower} should equal {upper}',
                )

    def test_lowercase_with_prime(self) -> None:
        """Test lowercase moves with prime notation."""
        result_r_prime = rotate_move(SOLVED_4X4X4, "r'", size=4)
        result_rw_prime = rotate_move(SOLVED_4X4X4, "Rw'", size=4)
        self.assertEqual(result_r_prime, result_rw_prime, "r' should equal Rw'")

    def test_lowercase_with_double(self) -> None:
        """Test lowercase moves with double notation."""
        result_r2 = rotate_move(SOLVED_4X4X4, 'r2', size=4)
        result_rw2 = rotate_move(SOLVED_4X4X4, 'Rw2', size=4)
        self.assertEqual(result_r2, result_rw2, 'r2 should equal Rw2')

    def test_lowercase_sequence(self) -> None:
        """Test a sequence using lowercase notation."""
        # r U r' U' should work like Rw U Rw' U'
        cube = VCube(size=4)
        cube.rotate("r U r' U'")
        self.assertFalse(cube.is_solved)

        # Apply inverse to return to solved
        cube.rotate("U r U' r'")
        self.assertTrue(cube.is_solved)


class Test4x4x4VCubeCustomFacelets(unittest.TestCase):
    """Test VCube implementation for 4x4x4 with custom facelets."""

    def setUp(self) -> None:
        """Set up required components."""
        self.state = get_unique_facelets(4)
        self.cube = VCube(initial=self.state, size=4, check=False)

    def test_rotate(self) -> None:
        """Test rotate."""
        self.cube.rotate('F R U')

        self.assertNotEqual(
            self.cube.state,
            self.state,
        )


class Test4x4x4VCubeCheckCustomState(unittest.TestCase):
    """Test VCube implementation for 4x4x4 with scrambled facelets."""

    def setUp(self) -> None:
        """Set up required components."""
        self.state = EXPECTED_4X4X4_R
        self.cube = VCube(initial=self.state, size=4, check=True)

    def test_rotate(self) -> None:
        """Test rotate."""
        self.cube.rotate('F R U')

        self.assertNotEqual(
            self.cube.state,
            self.state,
        )


class Test4x4x4MoveConsistency(unittest.TestCase):
    """
    Test that 180° and CCW move codes match applying the CW move repeatedly.

    Uses unique facelets so every position has a distinct value — the solved
    state's symmetry can hide index-pair swaps across face positions.
    """

    @staticmethod
    def apply(state: str, move: str) -> str:
        """
        Apply move.

        Returns:
           State once move applied.

        """
        return rotate_move(state, move, size=4)

    @staticmethod
    def apply_n(state: str, move: str, n: int) -> str:
        """
        Apply N moves.

        Returns:
           State once move applied.

        """
        for _ in range(n):
            state = rotate_move(state, move, size=4)
        return state

    def test_all_180_moves_equal_cw_twice(self) -> None:
        """Every X2 direct code must equal X applied twice, for all faces."""
        for move in ['U', 'R', 'F', 'D', 'L', 'B']:
            with self.subTest(move=move):
                self.assertEqual(
                    self.apply(UNIQUE_4X4X4, move + '2'),
                    self.apply_n(UNIQUE_4X4X4, move, 2),
                )

    def test_all_180_moves_equal_ccw_twice(self) -> None:
        """Every X2 direct code must equal X' applied twice, for all faces."""
        for move in ['U', 'R', 'F', 'D', 'L', 'B']:
            with self.subTest(move=move):
                self.assertEqual(
                    self.apply(UNIQUE_4X4X4, move + '2'),
                    self.apply_n(UNIQUE_4X4X4, move + "'", 2),
                )

    def test_all_ccw_moves_equal_cw_three_times(self) -> None:
        """Every X' direct code must equal X applied three times."""
        for move in ['U', 'R', 'F', 'D', 'L', 'B']:
            with self.subTest(move=move):
                self.assertEqual(
                    self.apply(UNIQUE_4X4X4, move + "'"),
                    self.apply_n(UNIQUE_4X4X4, move, 3),
                )
