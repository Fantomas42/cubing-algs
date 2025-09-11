import unittest

from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies
from cubing_algs.masks import F2L_MASK
from cubing_algs.vcube import VCube


class CubiesToFaceletsTestCase(unittest.TestCase):

    def test_cubies_to_facelets_solved(self):
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0, 0, 0, 0, 0, 0, 0, 0]
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        so = [0, 1, 2, 3, 4, 5]
        facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

        self.assertEqual(
            cubies_to_facelets(
                cp, co,
                ep, eo,
                so,
            ),
            facelets,
        )

    def test_cubies_to_facelets_solved_oriented(self):
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0, 0, 0, 0, 0, 0, 0, 0]
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        so = [3, 4, 2, 0, 1, 5]
        facelets = (
            'DDDDDDDDD'
            'LLLLLLLLL'
            'FFFFFFFFF'
            'UUUUUUUUU'
            'RRRRRRRRR'
            'BBBBBBBBB'
        )

        self.assertEqual(
            cubies_to_facelets(
                cp, co,
                ep, eo,
                so,
            ),
            facelets,
        )

    def test_cubies_to_facelets(self):
        cp = [0, 5, 2, 1, 7, 4, 6, 3]
        co = [1, 2, 0, 2, 1, 1, 0, 2]
        ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
        eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
        so = [0, 1, 2, 3, 4, 5]
        facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

        self.assertEqual(
            cubies_to_facelets(
                cp, co,
                ep, eo,
                so,
            ),
            facelets,
        )

    def test_cubies_to_facelets_oriented(self):
        cp = [4, 0, 1, 3, 7, 5, 6, 2]
        co = [2, 0, 0, 1, 1, 0, 0, 2]
        ep = [8, 0, 1, 2, 11, 5, 6, 7, 4, 9, 10, 3]
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        so = [2, 1, 3, 5, 4, 0]
        facelets = 'FFRFFDFFDRRURRURRURRBDDBDDBBBUBBUBBLDDDLLLLLLFLLFUUFUU'

        self.assertEqual(
            cubies_to_facelets(
                cp, co,
                ep, eo,
                so,
            ),
            facelets,
        )


class FaceletsToCubiesTestCase(unittest.TestCase):

    def test_facelets_to_cubies_solved(self):
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0, 0, 0, 0, 0, 0, 0, 0]
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        so = [0, 1, 2, 3, 4, 5]
        facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

        self.assertEqual(
            facelets_to_cubies(facelets),
            (
                cp, co,
                ep, eo,
                so,
            ),
        )

    def test_facelets_to_cubies(self):
        cp = [0, 5, 2, 1, 7, 4, 6, 3]
        co = [1, 2, 0, 2, 1, 1, 0, 2]
        ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
        eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
        so = [0, 1, 2, 3, 4, 5]
        facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

        self.assertEqual(
            facelets_to_cubies(facelets),
            (
                cp, co,
                ep, eo,
                so,
            ),
        )

    def test_facelets_to_cubies_oriented(self):
        cp = [4, 0, 1, 3, 7, 5, 6, 2]
        co = [2, 0, 0, 1, 1, 0, 0, 2]
        ep = [8, 0, 1, 2, 11, 5, 6, 7, 4, 9, 10, 3]
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        so = [2, 1, 3, 5, 4, 0]
        facelets = 'FFRFFDFFDRRURRURRURRBDDBDDBBBUBBUBBLDDDLLLLLLFLLFUUFUU'

        self.assertEqual(
            facelets_to_cubies(facelets),
            (
                cp, co,
                ep, eo,
                so,
            ),
        )


class CubiesToFaceletsCustomStateTestCase(unittest.TestCase):
    """Tests for the custom_state parameter in cubies_to_facelets function."""

    def test_custom_state_basic_functionality(self):
        """Test that custom_state parameter works with basic cube states."""
        # Solved state
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0, 0, 0, 0, 0, 0, 0, 0]
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        so = [0, 1, 2, 3, 4, 5]

        # Custom state with different pattern
        # (54 chars, each face has its color)
        custom_state = 'LLLLLLLLLFFFFFFFFFUUUUUUUUURRRRRRRRRBBBBBBBBBDDDDDDDDD'

        result = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=custom_state,
        )

        # Should return the custom state since cube is solved
        self.assertEqual(result, custom_state)

    def test_custom_state_vs_standard_solved(self):
        """Test that scheme=None behaves same as no scheme for solved cube."""
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0, 0, 0, 0, 0, 0, 0, 0]
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        so = [0, 1, 2, 3, 4, 5]

        result_standard = cubies_to_facelets(cp, co, ep, eo, so)
        result_custom_none = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=None,
        )

        self.assertEqual(result_standard, result_custom_none)

    def test_custom_state_with_moves_r_turn(self):
        """Test that moves applied to scheme produce correct transformations."""
        # Create a custom pattern with unique centers (54 chars)
        custom_state = 'UUURUUUUURRRURURRRFFFFFFFFFDDDLDDDDDLLLBLLLLLBBBFBBBBB'

        # Apply R move to the custom state using VCube
        cube = VCube(custom_state, check=False)
        cube.rotate('R')
        expected_after_r = cube.state

        # Get cubie representation of R move applied to solved cube
        solved_cube = VCube()
        solved_cube.rotate('R')
        cp, co, ep, eo, so = solved_cube.to_cubies

        # Apply same transformation to custom state
        result = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=custom_state,
        )

        self.assertEqual(result, expected_after_r)

    def test_custom_state_with_moves_f_turn(self):
        """Test F move on custom state."""
        # Use a pattern with clear face identification
        custom_state = (
            'UUUUUUUUU'
            'RRRRRRRRR'
            'FFFFFFFFF'
            'DDDDDDDDD'
            'LLLLLLLLL'
            'BBBBBBBBB'
        )

        # Apply F move to custom state using VCube
        cube = VCube(custom_state, check=False)
        cube.rotate('F')
        expected_after_f = cube.state

        # Get cubie representation of F move applied to solved cube
        solved_cube = VCube()
        solved_cube.rotate('F')
        cp, co, ep, eo, so = solved_cube.to_cubies

        # Apply same transformation to custom state
        result = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=custom_state,
        )

        self.assertEqual(result, expected_after_f)

    def test_custom_state_with_move_sequence(self):
        """Test that a sequence of moves on scheme produces correct result."""
        # Use pattern for easy tracking with valid cube characters (54 chars)
        custom_state = 'UUURUUUUURRRURURRRFFFFFFFFFDDDLDDDDDLLLBLLLLLBBBFBBBBB'
        move_sequence = "R U R' U'"

        # Apply moves to custom state using VCube
        cube = VCube(custom_state, check=False)
        cube.rotate(move_sequence)
        expected_result = cube.state

        # Get cubie representation after applying moves to solved cube
        solved_cube = VCube()
        solved_cube.rotate(move_sequence)
        cp, co, ep, eo, so = solved_cube.to_cubies

        # Apply same transformation to custom state using cubies_to_facelets
        result = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=custom_state,
        )

        self.assertEqual(result, expected_result)

    def test_custom_state_mask_with_move_sequence(self):
        """Test that a sequence of moves on scheme produces correct result."""
        # Use mask for easy tracking with valid cube characters (54 chars)
        custom_state = F2L_MASK
        move_sequence = "R U R' U'"

        # Apply moves to custom state using VCube
        cube = VCube(custom_state, check=False)
        cube.rotate(move_sequence)
        expected_result = cube.state

        # Get cubie representation after applying moves to solved cube
        solved_cube = VCube()
        solved_cube.rotate(move_sequence)
        cp, co, ep, eo, so = solved_cube.to_cubies

        # Apply same transformation to custom state using cubies_to_facelets
        result = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=custom_state,
        )

        self.assertEqual(result, expected_result)

    def test_custom_state_with_complex_algorithm(self):
        """Test custom_state with a more complex algorithm."""
        # Create a distinctive pattern with valid cube characters (54 chars)
        custom_state = 'UUURUUUUURRRURURRRFFFFFFFFFDDDLDDDDDLLLBLLLLLBBBFBBBBB'

        # Apply Sune algorithm: R U R' U R U2 R'
        algorithm = "R U R' U R U2 R'"

        # Apply algorithm to custom state using VCube
        cube = VCube(custom_state, check=False)
        cube.rotate(algorithm)
        expected_result = cube.state

        # Get cubie representation after applying algorithm to solved cube
        solved_cube = VCube()
        solved_cube.rotate(algorithm)
        cp, co, ep, eo, so = solved_cube.to_cubies

        # Apply same transformation to custom state
        result = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=custom_state,
        )

        self.assertEqual(result, expected_result)

    def test_custom_state_inverse_consistency(self):
        """
        Test that applying moves and their inverse
        returns to original scheme.
        """
        custom_state = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

        # Apply R and then R'
        cube = VCube()
        cube.rotate("R R'")  # Should return to solved
        cp, co, ep, eo, so = cube.to_cubies

        # Should get back the original custom state
        result = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=custom_state,
        )
        self.assertEqual(result, custom_state)

        # Test with sequence that returns to solved
        cube = VCube()
        cube.rotate('R R R R')  # Four R moves return to solved
        cp, co, ep, eo, so = cube.to_cubies

        result = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=custom_state,
        )
        self.assertEqual(result, custom_state)

    def test_custom_state_scrambled_to_scrambled(self):
        """Test transforming one custom state to another through moves."""
        # Start with one custom pattern (valid cube characters, 54 chars)
        scheme = 'UUURUUUUURRRURURRRFFFFFFFFFDDDLDDDDDLLLBLLLLLBBBFBBBBB'

        # Apply some moves to get the transformation
        cube = VCube()
        cube.rotate('R U F')
        cp, co, ep, eo, so = cube.to_cubies

        # Apply this transformation to our custom state
        result = cubies_to_facelets(
            cp, co, ep, eo, so,
            scheme=scheme,
        )

        # Verify by applying same moves to VCube with scheme
        verification_cube = VCube(scheme, check=False)
        verification_cube.rotate('R U F')
        expected = verification_cube.state

        self.assertEqual(result, expected)
