import unittest

from cubing_algs.constants import INITIAL_STATE
from cubing_algs.facelets import _CORNER_LOOKUP
from cubing_algs.facelets import _EDGE_LOOKUP
from cubing_algs.facelets import _cache
from cubing_algs.facelets import clear_cache
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import disable_cache
from cubing_algs.facelets import enable_cache
from cubing_algs.facelets import facelets_to_cubies
from cubing_algs.facelets import get_cache_info
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


class TestFaceletsOptimizationCoverage(unittest.TestCase):
    """
    Test cases to achieve complete coverage
    of the optimized facelets module.
    """

    @staticmethod
    def setUp():
        clear_cache()
        enable_cache()

    @staticmethod
    def tearDown():
        clear_cache()
        enable_cache()

    def test_cache_management_functions(self):
        """Test all cache management utility functions."""
        # Test initial state
        info = get_cache_info()
        self.assertEqual(info['facelets_cached'], 0)
        self.assertEqual(info['cubies_cached'], 0)
        self.assertEqual(info['max_size'], 512)
        self.assertTrue(info['enabled'])

        # Add some items to cache
        facelets_to_cubies(INITIAL_STATE)
        cubies_to_facelets(
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5],
        )

        info = get_cache_info()
        self.assertGreater(info['facelets_cached'], 0)
        self.assertGreater(info['cubies_cached'], 0)

        # Test cache clearing
        clear_cache()
        info = get_cache_info()
        self.assertEqual(info['facelets_cached'], 0)
        self.assertEqual(info['cubies_cached'], 0)

        # Test cache disable/enable
        disable_cache()
        info = get_cache_info()
        self.assertFalse(info['enabled'])

        # Operations should not be cached when disabled
        facelets_to_cubies(INITIAL_STATE)
        info = get_cache_info()
        self.assertEqual(info['facelets_cached'], 0)

        enable_cache()
        info = get_cache_info()
        self.assertTrue(info['enabled'])

    def test_cache_eviction_facelets(self):
        """
        Test cache eviction when max size is reached for facelets cache.
        """
        # Set a small cache size
        original_max_size = _cache.max_size
        _cache.max_size = 2

        try:
            # Fill cache beyond max size using valid states
            cube = VCube()

            states = [INITIAL_STATE]

            # Generate valid states
            moves = ['R', 'U', 'F']
            for move in moves:
                cube.rotate(move)
                states.append(cube.state)

            for state in states:
                facelets_to_cubies(state)

            # Check that cache size is limited
            info = get_cache_info()
            self.assertLessEqual(info['facelets_cached'], 2)

        finally:
            _cache.max_size = original_max_size

    def test_cache_eviction_cubies(self):
        """Test cache eviction when max size is reached for cubies cache."""
        # Set a small cache size
        original_max_size = _cache.max_size
        _cache.max_size = 2

        try:
            # Fill cache beyond max size
            cubies_states = [
                (
                    [0, 1, 2, 3, 4, 5, 6, 7],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 2, 3, 4, 5],
                ),
                (
                    [0, 1, 2, 3, 4, 5, 6, 7],
                    [1, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 2, 3, 4, 5],
                ),
                (
                    [0, 1, 2, 3, 4, 5, 6, 7],
                    [2, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 2, 3, 4, 5],
                ),
            ]

            for cubies_state in cubies_states:
                cubies_to_facelets(*cubies_state)

            # Check that cache size is limited
            info = get_cache_info()
            self.assertLessEqual(info['cubies_cached'], 2)

        finally:
            _cache.max_size = original_max_size

    def test_corner_fallback_logic(self):
        """Test fallback logic for invalid corner states."""
        # Save original lookup
        original_lookup = _CORNER_LOOKUP.copy()

        try:
            # Clear the lookup to force fallback
            _CORNER_LOOKUP.clear()

            # Now all corner lookups will fail and use fallback
            result = facelets_to_cubies(INITIAL_STATE)

            # Should still work with fallback logic
            self.assertEqual(len(result), 5)
            self.assertEqual(len(result[0]), 8)  # cp
            self.assertEqual(len(result[1]), 8)  # co

        finally:
            # Restore original lookup
            _CORNER_LOOKUP.clear()
            _CORNER_LOOKUP.update(original_lookup)

    def test_edge_fallback_logic(self):
        """Test fallback logic for invalid edge states."""
        # Save original lookup
        original_lookup = _EDGE_LOOKUP.copy()

        try:
            # Clear the lookup to force fallback
            _EDGE_LOOKUP.clear()

            # Now all edge lookups will fail and use fallback
            result = facelets_to_cubies(INITIAL_STATE)

            # Should still work with fallback logic
            self.assertEqual(len(result), 5)
            self.assertEqual(len(result[2]), 12)  # ep
            self.assertEqual(len(result[3]), 12)  # eo

        finally:
            # Restore original lookup
            _EDGE_LOOKUP.clear()
            _EDGE_LOOKUP.update(original_lookup)

    def test_edge_fallback_flipped_orientation(self):
        """Test fallback logic for flipped edge orientation case."""
        # Create a cube with a flipped edge
        cube = VCube()
        cube.rotate('F')  # This creates a flipped edge

        # Save original lookup
        original_lookup = _EDGE_LOOKUP.copy()

        try:
            # Clear the lookup to force fallback
            _EDGE_LOOKUP.clear()

            # This should use fallback and hit the flipped edge case
            result = facelets_to_cubies(cube.state)

            # Should still work with fallback logic
            self.assertEqual(len(result), 5)
            self.assertEqual(len(result[2]), 12)  # ep
            self.assertEqual(len(result[3]), 12)  # eo

            # Check that at least one edge has orientation 1 (flipped)
            self.assertTrue(any(eo == 1 for eo in result[3]))

        finally:
            # Restore original lookup
            _EDGE_LOOKUP.clear()
            _EDGE_LOOKUP.update(original_lookup)

    def test_cache_hit_paths(self):
        """Test cache hit paths explicitly."""
        # Clear cache first
        clear_cache()

        info = get_cache_info()
        self.assertEqual(info['cubies_cached'], 0)
        self.assertEqual(info['facelets_cached'], 0)

        # First call - cache miss
        result1 = facelets_to_cubies(INITIAL_STATE)
        info = get_cache_info()
        self.assertEqual(info['facelets_cached'], 1)

        # Second call - cache hit
        result2 = facelets_to_cubies(INITIAL_STATE)
        self.assertEqual(result1, result2)

        info = get_cache_info()
        self.assertEqual(info['facelets_cached'], 1)

        # Test cubies_to_facelets cache hit
        cubies_args = (
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5],
        )

        # First call - cache miss
        result1 = cubies_to_facelets(*cubies_args)
        info = get_cache_info()
        self.assertEqual(info['cubies_cached'], 1)

        # Second call - cache hit
        result2 = cubies_to_facelets(*cubies_args)
        self.assertEqual(result1, result2)

        info = get_cache_info()
        self.assertEqual(info['cubies_cached'], 1)

    def test_cubies_to_facelets_with_scheme(self):
        """Test cubies_to_facelets with custom scheme parameter."""
        cubies_args = (
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5],
        )

        # Test with None scheme (default path)
        result1 = cubies_to_facelets(*cubies_args, scheme=None)

        # Test with custom scheme
        custom_scheme = 'W' * 54  # All white
        result2 = cubies_to_facelets(*cubies_args, scheme=custom_scheme)

        # Results should be different
        self.assertNotEqual(result1, result2)

    def test_cache_disabled_paths(self):
        """
        Test that cache operations work correctly when caching is disabled.
        """
        disable_cache()

        # Operations should not use cache
        result1 = facelets_to_cubies(INITIAL_STATE)
        result2 = facelets_to_cubies(INITIAL_STATE)

        # Results should be identical but cache should remain empty
        self.assertEqual(result1, result2)
        info = get_cache_info()
        self.assertEqual(info['facelets_cached'], 0)
        self.assertFalse(info['enabled'])

        # Test cubies_to_facelets
        cubies_args = (
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5],
        )

        result1 = cubies_to_facelets(*cubies_args)
        result2 = cubies_to_facelets(*cubies_args)

        self.assertEqual(result1, result2)
        info = get_cache_info()
        self.assertEqual(info['cubies_cached'], 0)

    def test_corner_orientation_modulo(self):
        """Test corner orientation modulo operation in fallback logic."""
        # Create a state that will trigger the fallback logic
        # and test the ori % 3 operation
        invalid_state = list(INITIAL_STATE)

        # Create an invalid corner configuration
        invalid_state[8] = 'U'
        invalid_state[9] = 'U'  # Same color, will trigger fallback
        invalid_state[20] = 'F'

        invalid_state_str = ''.join(invalid_state)

        result = facelets_to_cubies(invalid_state_str)
        # The result should have valid corner orientations (0, 1, or 2)
        for co in result[1]:  # Corner orientations
            self.assertIn(co, [0, 1, 2])
