"""Tests for 4x4x4 cube rotation using dynamic rotation system."""
import unittest

from cubing_algs.initial_state import get_initial_state
from cubing_algs.rotate_dynamic import rotate_move
from cubing_algs.vcube import VCube

# Solved 4x4x4 state: 96 facelets (6 faces * 16 facelets each)
# Face order: U, R, F, D, L, B
SOLVED_4X4X4 = get_initial_state(4)

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
        self.assertEqual(self.cube.center_index, 8)

    def test_orientation(self) -> None:
        """Test orientation."""
        with self.assertRaises(NotImplementedError):
            _ = self.cube.orientation


class Test4x4x4BasicMoves(unittest.TestCase):
    """Test basic face moves on 4x4x4 cube."""

    def test_solved_state(self) -> None:
        """Test that solved state is correctly defined."""
        # Verify length
        self.assertEqual(len(SOLVED_4X4X4), 96)

        # Verify each face has 16 facelets
        faces = ['U', 'R', 'F', 'D', 'L', 'B']
        for i, face in enumerate(faces):
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
