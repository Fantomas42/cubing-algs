"""Tests for 2x2x2 cube rotation using dynamic rotation system."""
import unittest

from cubing_algs.initial_state import get_initial_state
from cubing_algs.rotate_dynamic import rotate_move
from cubing_algs.vcube import VCube

# Solved 2x2x2 state: 24 facelets (6 faces * 4 facelets each)
# Face order: U, R, F, D, L, B
SOLVED_2X2X2 = get_initial_state(2)

# Expected states after moves
EXPECTED_2X2X2_R = 'UFUFRRRRFDFDDBDBLLLLUBUB'
EXPECTED_2X2X2_RPRIME = 'UBUBRRRRFUFUDFDFLLLLDBDB'
EXPECTED_2X2X2_R2 = 'UDUDRRRRFBFBDUDULLLLFBFB'
EXPECTED_2X2X2_U = 'UUUUBBRRRRFFDDDDFFLLLLBB'
EXPECTED_2X2X2_F = 'UULLURURFFFFRRDDLDLDBBBB'
EXPECTED_2X2X2_x = 'FFFFRRRRDDDDBBBBLLLLUUUU'
EXPECTED_2X2X2_y = 'UUUUBBBBRRRRDDDDFFFFLLLL'
EXPECTED_2X2X2_z = 'LLLLUUUUFFFFRRRRDDDDBBBB'


class Test2x2x2VCube(unittest.TestCase):
    """Test VCube implementation for 2x2x2."""

    def setUp(self) -> None:
        """Set up required components."""
        self.cube = VCube(size=2)

    def test_has_fixed_centers(self) -> None:
        """Check has_fixed_centers property."""
        self.assertFalse(self.cube.has_fixed_centers)


class Test2x2x2BasicMoves(unittest.TestCase):
    """Test basic face moves on 2x2x2 cube."""

    def test_solved_state(self) -> None:
        """Test that solved state is correctly defined."""
        # Verify length
        self.assertEqual(len(SOLVED_2X2X2), 24)

        # Verify each face has 4 facelets
        faces = ['U', 'R', 'F', 'D', 'L', 'B']
        for i, face in enumerate(faces):
            start = i * 4
            end = start + 4
            face_colors = SOLVED_2X2X2[start:end]
            self.assertEqual(face_colors, face * 4)

    def test_r_move(self) -> None:
        """Test R move on 2x2x2."""
        result = rotate_move(SOLVED_2X2X2, 'R', size=2)
        self.assertEqual(result, EXPECTED_2X2X2_R, 'R move state mismatch')
        self.assertNotEqual(result, SOLVED_2X2X2)

    def test_r_prime_move(self) -> None:
        """Test R' move on 2x2x2."""
        result = rotate_move(SOLVED_2X2X2, "R'", size=2)
        self.assertEqual(
            result, EXPECTED_2X2X2_RPRIME, "R' move state mismatch",
        )
        self.assertNotEqual(result, SOLVED_2X2X2)

    def test_r_r_prime_cancel(self) -> None:
        """Test that R R' returns to solved state."""
        after_r = rotate_move(SOLVED_2X2X2, 'R', size=2)
        after_r_prime = rotate_move(after_r, "R'", size=2)
        self.assertEqual(after_r_prime, SOLVED_2X2X2)

    def test_r2_move(self) -> None:
        """Test R2 move on 2x2x2."""
        result = rotate_move(SOLVED_2X2X2, 'R2', size=2)
        self.assertEqual(result, EXPECTED_2X2X2_R2, 'R2 move state mismatch')
        self.assertNotEqual(result, SOLVED_2X2X2)

    def test_r_four_times(self) -> None:
        """Test that R applied 4 times returns to solved state."""
        state = SOLVED_2X2X2
        for _ in range(4):
            state = rotate_move(state, 'R', size=2)
        self.assertEqual(state, SOLVED_2X2X2)

    def test_u_move(self) -> None:
        """Test U move on 2x2x2."""
        result = rotate_move(SOLVED_2X2X2, 'U', size=2)
        self.assertEqual(result, EXPECTED_2X2X2_U, 'U move state mismatch')
        self.assertNotEqual(result, SOLVED_2X2X2)

    def test_u_four_times(self) -> None:
        """Test that U applied 4 times returns to solved state."""
        state = SOLVED_2X2X2
        for _ in range(4):
            state = rotate_move(state, 'U', size=2)
        self.assertEqual(state, SOLVED_2X2X2)

    def test_f_move(self) -> None:
        """Test F move on 2x2x2."""
        result = rotate_move(SOLVED_2X2X2, 'F', size=2)
        self.assertEqual(result, EXPECTED_2X2X2_F, 'F move state mismatch')
        self.assertNotEqual(result, SOLVED_2X2X2)

    def test_f_four_times(self) -> None:
        """Test that F applied 4 times returns to solved state."""
        state = SOLVED_2X2X2
        for _ in range(4):
            state = rotate_move(state, 'F', size=2)
        self.assertEqual(state, SOLVED_2X2X2)

    def test_all_basic_moves(self) -> None:
        """Test that all basic moves work and are invertible."""
        moves = ['R', 'L', 'U', 'D', 'F', 'B']

        for move in moves:
            # Test move changes state
            result = rotate_move(SOLVED_2X2X2, move, size=2)
            self.assertNotEqual(
                result, SOLVED_2X2X2, f'{move} should change state',
            )

            # Test inverse returns to solved
            inverse = move + "'"
            back = rotate_move(result, inverse, size=2)
            self.assertEqual(
                back, SOLVED_2X2X2,
                f'{move} followed by {inverse} should return to solved',
            )

            # Test 4 repetitions return to solved
            state = SOLVED_2X2X2
            for _ in range(4):
                state = rotate_move(state, move, size=2)
            self.assertEqual(
                state, SOLVED_2X2X2,
                f'{move} applied 4 times should return to solved',
            )


class Test2x2x2Rotations(unittest.TestCase):
    """Test cube rotation moves (x, y, z) on 2x2x2."""

    def test_x_rotation(self) -> None:
        """Test x rotation on 2x2x2."""
        result = rotate_move(SOLVED_2X2X2, 'x', size=2)
        self.assertEqual(result, EXPECTED_2X2X2_x, 'x rotation state mismatch')
        self.assertNotEqual(result, SOLVED_2X2X2)

    def test_x_four_times(self) -> None:
        """Test that x applied 4 times returns to solved state."""
        state = SOLVED_2X2X2
        for _ in range(4):
            state = rotate_move(state, 'x', size=2)
        self.assertEqual(state, SOLVED_2X2X2)

    def test_y_rotation(self) -> None:
        """Test y rotation on 2x2x2."""
        result = rotate_move(SOLVED_2X2X2, 'y', size=2)
        self.assertEqual(result, EXPECTED_2X2X2_y, 'y rotation state mismatch')
        self.assertNotEqual(result, SOLVED_2X2X2)

    def test_y_four_times(self) -> None:
        """Test that y applied 4 times returns to solved state."""
        state = SOLVED_2X2X2
        for _ in range(4):
            state = rotate_move(state, 'y', size=2)
        self.assertEqual(state, SOLVED_2X2X2)

    def test_z_rotation(self) -> None:
        """Test z rotation on 2x2x2."""
        result = rotate_move(SOLVED_2X2X2, 'z', size=2)
        self.assertEqual(result, EXPECTED_2X2X2_z, 'z rotation state mismatch')
        self.assertNotEqual(result, SOLVED_2X2X2)

    def test_z_four_times(self) -> None:
        """Test that z applied 4 times returns to solved state."""
        state = SOLVED_2X2X2
        for _ in range(4):
            state = rotate_move(state, 'z', size=2)
        self.assertEqual(state, SOLVED_2X2X2)

    def test_rotation_inverses(self) -> None:
        """Test that rotation moves are invertible."""
        rotations = ['x', 'y', 'z']

        for rotation in rotations:
            result = rotate_move(SOLVED_2X2X2, rotation, size=2)
            inverse = rotation + "'"
            back = rotate_move(result, inverse, size=2)
            self.assertEqual(
                back, SOLVED_2X2X2,
                f'{rotation} followed by {inverse} should return to solved',
            )


class Test2x2x2Sequences(unittest.TestCase):
    """Test move sequences on 2x2x2."""

    def test_commutator_r_u(self) -> None:
        """Test R U R' U' sequence (not quite a commutator on 2x2x2)."""
        state = SOLVED_2X2X2
        state = rotate_move(state, 'R', size=2)
        state = rotate_move(state, 'U', size=2)
        state = rotate_move(state, "R'", size=2)
        state = rotate_move(state, "U'", size=2)

        # This sequence should change the cube
        self.assertNotEqual(state, SOLVED_2X2X2)

        # Repeating should eventually return to solved
        # (Actually, for 2x2x2, this is a corner 3-cycle with order 6)
        for _ in range(5):
            state = rotate_move(state, 'R', size=2)
            state = rotate_move(state, 'U', size=2)
            state = rotate_move(state, "R'", size=2)
            state = rotate_move(state, "U'", size=2)

        self.assertEqual(state, SOLVED_2X2X2)
