# ruff: noqa: S311
"""Tests for step-based scramble generation."""
import unittest
from random import Random

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.exceptions import InvalidStepError
from cubing_algs.integrity import compute_parity
from cubing_algs.scrambler.steps import SUPPORTED_STEPS
from cubing_algs.scrambler.steps import generate_step_state
from cubing_algs.scrambler.steps import scramble_easy_cross
from cubing_algs.scrambler.steps import scramble_ocll_case
from cubing_algs.scrambler.steps import scramble_step
from cubing_algs.scrambler.steps import scramble_with_piece_constraints
from cubing_algs.vcube import VCube


class TestGenerateStepState(unittest.TestCase):
    """Tests for generate_step_state function."""

    def test_all_supported_steps_generate(self) -> None:
        """Test that all supported steps generate valid states."""
        rng = Random(42)
        for step in SUPPORTED_STEPS:
            cp, co, ep, eo = generate_step_state(step, rng)

            # Check basic validity
            self.assertEqual(len(cp), 8)
            self.assertEqual(len(co), 8)
            self.assertEqual(len(ep), 12)
            self.assertEqual(len(eo), 12)

            # Check orientation constraints
            self.assertEqual(sum(co) % 3, 0, f'Step {step}: sum(co) % 3 != 0')
            self.assertEqual(sum(eo) % 2, 0, f'Step {step}: sum(eo) % 2 != 0')

            # Check parity constraint
            self.assertEqual(
                compute_parity(cp),
                compute_parity(ep),
                f'Step {step}: parity mismatch',
            )

    def test_invalid_step_raises(self) -> None:
        """Test that invalid step name raises error."""
        with self.assertRaises(InvalidStepError):
            generate_step_state('INVALID_STEP', Random(42))

    def test_pll_only_permutation(self) -> None:
        """Test that PLL only permutes U layer."""
        _cp, co, _ep, eo = generate_step_state('PLL', Random(42))

        # All orientations should be solved
        self.assertEqual(co, SOLVED_CO)
        self.assertEqual(eo, SOLVED_EO)

    def test_oll_has_orientation(self) -> None:
        """Test that OLL has some orientation on U layer."""
        rng = Random(42)
        has_corner_orientation = False
        has_edge_orientation = False

        # Try multiple times to ensure randomness
        for _ in range(10):
            _cp, co, _ep, eo = generate_step_state('OLL', rng)

            # Check if U corners have orientation
            u_corners = [0, 1, 2, 3]
            if any(co[i] != 0 for i in u_corners):
                has_corner_orientation = True

            # Check if U edges have orientation
            u_edges = [0, 1, 2, 3]
            if any(eo[i] != 0 for i in u_edges):
                has_edge_orientation = True

        # At least one trial should have orientation
        self.assertTrue(has_corner_orientation or has_edge_orientation)

    def test_f2l_permutes_all_corners(self) -> None:
        """Test that F2L permutes all corners."""
        cp, _co, _ep, _eo = generate_step_state('F2L', Random(42))

        # All corners should potentially be permuted
        # Just check valid permutation
        self.assertEqual(set(cp), set(SOLVED_CP))

    def test_deterministic_with_seed(self) -> None:
        """Test that same seed produces same result."""
        cp1, co1, ep1, eo1 = generate_step_state('PLL', Random(42))
        cp2, co2, ep2, eo2 = generate_step_state('PLL', Random(42))

        self.assertEqual(cp1, cp2)
        self.assertEqual(co1, co2)
        self.assertEqual(ep1, ep2)
        self.assertEqual(eo1, eo2)

    def test_default_rng_when_none(self) -> None:
        """Test that default RNG is used when None is passed."""
        cp, co, ep, eo = generate_step_state('PLL', None)

        # Should generate valid state
        self.assertEqual(len(cp), 8)
        self.assertEqual(len(co), 8)
        self.assertEqual(len(ep), 12)
        self.assertEqual(len(eo), 12)

    def test_ejls_dfr_corner_disorientation(self) -> None:
        """Test EJLS and EJF2L steps ensure DFR corner is disoriented."""
        # Test many seeds to ensure DFR is always disoriented
        # Note: The code always enters the if co[4] == 0 branch because
        # random_corner_orientation(U_CORNERS) doesn't touch co[4]
        for seed in range(100):
            for step in ['EJLS', 'EJF2L']:
                rng = Random(seed)
                _cp, co, _ep, _eo = generate_step_state(step, rng)

                # DFR is corner index 4, should be disoriented
                self.assertNotEqual(
                    co[4], 0,
                    f'{step}: DFR should be disoriented (seed {seed})',
                )

                # Orientation sum constraint should hold
                self.assertEqual(
                    sum(co) % 3, 0,
                    f'{step}: Orientation constraint failed (seed {seed})',
                )


class TestScrambleStep(unittest.TestCase):
    """Tests for scramble_step function."""

    def test_all_steps_with_kociemba(self) -> None:
        """Test all step types with kociemba installed."""
        rng = Random(42)
        for step in SUPPORTED_STEPS:
            scramble = scramble_step(step, rng, include_auf=False)

            # Should return an Algorithm
            self.assertIsInstance(scramble, Algorithm)

    def test_invalid_step_raises(self) -> None:
        """Test that invalid step raises error."""
        with self.assertRaises(InvalidStepError):
            scramble_step('INVALID', Random(42))

    def test_scramble_produces_correct_state(self) -> None:
        """Test that scramble produces expected step state."""
        rng = Random(42)
        scramble = scramble_step('PLL', rng, include_auf=False)

        # Apply scramble to solved cube
        cube = VCube()
        cube.rotate(str(scramble))

        # Check that only U layer is permuted (no orientation)
        _cp, co, _ep, eo, _ = cube.to_cubies

        # All orientations should be 0
        self.assertEqual(co, SOLVED_CO)
        self.assertEqual(eo, SOLVED_EO)

    def test_with_auf(self) -> None:
        """Test scramble with AUF enabled."""
        scramble_with = scramble_step('PLL', Random(42), include_auf=True)
        scramble_without = scramble_step('PLL', Random(42), include_auf=False)

        # Different RNG seeds, so might be same or different
        # Just verify both work
        self.assertIsInstance(scramble_with, Algorithm)
        self.assertIsInstance(scramble_without, Algorithm)

    def test_deterministic_with_seed(self) -> None:
        """Test that same seed produces same scramble."""
        scramble1 = scramble_step('PLL', Random(42), include_auf=False)
        scramble2 = scramble_step('PLL', Random(42), include_auf=False)

        self.assertEqual(str(scramble1), str(scramble2))

    def test_default_rng_when_none(self) -> None:
        """Test that default RNG is used when None is passed."""
        scramble = scramble_step('PLL', None, include_auf=False)

        # Should return valid Algorithm
        self.assertIsInstance(scramble, Algorithm)


class TestScrambleOCLLCase(unittest.TestCase):
    """Tests for scramble_ocll_case function."""

    def test_all_ocll_cases(self) -> None:
        """Test all OCLL case types."""
        cases = ['T', 'U', 'L', 'H', 'Pi', 'Sune', 'AntiSune', 'Solved']
        rng = Random(42)

        for case in cases:
            scramble = scramble_ocll_case(case, rng)

            # Should return an Algorithm
            self.assertIsInstance(scramble, Algorithm)

    def test_invalid_case_raises(self) -> None:
        """Test that invalid case raises error."""
        with self.assertRaises(InvalidStepError):
            scramble_ocll_case('INVALID', Random(42))

    def test_case_insensitive(self) -> None:
        """Test that case names are case-insensitive."""
        # These should all work
        self.assertEqual(
            scramble_ocll_case('T', Random(42)),
            scramble_ocll_case('t', Random(42)),
        )
        self.assertEqual(
            scramble_ocll_case('sune', Random(42)),
            scramble_ocll_case('SUNE', Random(42)),
        )

    def test_solved_case(self) -> None:
        """Test that solved case returns valid scramble."""
        scramble = scramble_ocll_case('Solved', Random(42))

        # Apply to cube
        cube = VCube()
        cube.rotate(str(scramble))

        # U corners should be oriented
        _cp, co, _ep, _eo, _ = cube.to_cubies
        u_corners = [0, 1, 2, 3]

        # All U corners should be oriented
        self.assertTrue(all(co[i] == 0 for i in u_corners))

    def test_deterministic_with_seed(self) -> None:
        """Test that same seed produces same scramble."""
        scramble1 = scramble_ocll_case('T', Random(42))
        scramble2 = scramble_ocll_case('T', Random(42))

        self.assertEqual(str(scramble1), str(scramble2))

    def test_default_rng_when_none(self) -> None:
        """Test that default RNG is used when None is passed."""
        scramble = scramble_ocll_case('T', None)

        # Should return valid Algorithm
        self.assertIsInstance(scramble, Algorithm)


class TestSupportedSteps(unittest.TestCase):
    """Tests for SUPPORTED_STEPS constant."""

    def test_has_last_layer_steps(self) -> None:
        """Test that all LL steps are included."""
        ll_steps = ['LL', 'OLL', 'PLL', 'ZBLL', 'COLL', 'OLLCP']
        for step in ll_steps:
            self.assertIn(step, SUPPORTED_STEPS)

    def test_has_f2l_steps(self) -> None:
        """Test that F2L variants are included."""
        f2l_steps = ['F2L', 'ZZF2L', 'ZZRB', 'PetrusF2L']
        for step in f2l_steps:
            self.assertIn(step, SUPPORTED_STEPS)

    def test_has_last_slot_steps(self) -> None:
        """Test that last slot variants are included."""
        ls_steps = ['LS', 'ELS', 'ZZLS', 'CLS', 'WV', 'SV', 'VLS']
        for step in ls_steps:
            self.assertIn(step, SUPPORTED_STEPS)

    def test_has_roux_steps(self) -> None:
        """Test that Roux method steps are included."""
        roux_steps = ['CMLL', 'CMLLEO', 'SB']
        for step in roux_steps:
            self.assertIn(step, SUPPORTED_STEPS)

    def test_has_petrus_steps(self) -> None:
        """Test that Petrus method steps are included."""
        petrus_steps = ['Petrus2x2x3', 'PetrusEO']
        for step in petrus_steps:
            self.assertIn(step, SUPPORTED_STEPS)

    def test_total_count(self) -> None:
        """Test that we have 30+ steps as promised."""
        self.assertGreaterEqual(len(SUPPORTED_STEPS), 30)


class TestScrambleEasyCross(unittest.TestCase):
    """Tests for easy cross scramble generation."""

    def test_scramble_easy_cross(self) -> None:
        """Test scramble easy cross."""
        moves = scramble_easy_cross()

        self.assertEqual(
            len(moves), 10,
        )
        self.assertTrue(
            'U' not in moves,
        )
        self.assertTrue(
            'D' not in moves,
        )


class TestScrambleWithPieceConstraints(unittest.TestCase):
    """Tests for scramble_with_piece_constraints function."""

    def test_default_rng_when_none(self) -> None:
        """Test that default RNG is used when None is passed."""
        scramble = scramble_with_piece_constraints(rng=None)

        # Should return valid Algorithm
        self.assertIsInstance(scramble, Algorithm)

    def test_solve_corners_only(self) -> None:
        """Test solving only corners."""
        scramble = scramble_with_piece_constraints(
            solve_corners='U',
            rng=Random(42),
        )

        # Should return Algorithm
        self.assertIsInstance(scramble, Algorithm)

        # Apply and verify U corners are solved
        cube = VCube()
        cube.rotate(str(scramble))
        cp, _co, _ep, _eo, _ = cube.to_cubies

        # U corner indices: URF=0, UFL=1, ULB=2, UBR=3
        u_corners = [0, 1, 2, 3]
        for idx in u_corners:
            self.assertEqual(cp[idx], idx)

    def test_solve_edges_only(self) -> None:
        """Test solving only edges."""
        scramble = scramble_with_piece_constraints(
            solve_edges='U',
            rng=Random(42),
        )

        # Should return Algorithm
        self.assertIsInstance(scramble, Algorithm)

        # Apply and verify U edges are solved
        cube = VCube()
        cube.rotate(str(scramble))
        _cp, _co, ep, _eo, _ = cube.to_cubies

        # U edge indices: UR=0, UF=1, UL=2, UB=3
        u_edges = [0, 1, 2, 3]
        for idx in u_edges:
            self.assertEqual(ep[idx], idx)

    def test_orient_corners_all(self) -> None:
        """Test orienting all corners."""
        scramble = scramble_with_piece_constraints(
            orient_corners_spec='all',
            rng=Random(42),
        )

        # Apply and verify all corners are oriented
        cube = VCube()
        cube.rotate(str(scramble))
        _cp, co, _ep, _eo, _ = cube.to_cubies

        # All corners should have orientation 0
        self.assertEqual(co, SOLVED_CO)

    def test_orient_edges_all(self) -> None:
        """Test orienting all edges."""
        scramble = scramble_with_piece_constraints(
            orient_edges_spec='all',
            rng=Random(42),
        )

        # Apply and verify all edges are oriented
        cube = VCube()
        cube.rotate(str(scramble))
        _cp, _co, _ep, eo, _ = cube.to_cubies

        # All edges should have orientation 0
        self.assertEqual(eo, SOLVED_EO)

    def test_orient_specific_pieces(self) -> None:
        """Test orienting specific pieces."""
        scramble = scramble_with_piece_constraints(
            orient_corners_spec='U',
            orient_edges_spec='U',
            rng=Random(42),
        )

        # Apply and verify U layer is oriented
        cube = VCube()
        cube.rotate(str(scramble))
        _cp, co, _ep, eo, _ = cube.to_cubies

        # U corners should be oriented
        u_corners = [0, 1, 2, 3]
        for idx in u_corners:
            self.assertEqual(co[idx], 0)

        # U edges should be oriented
        u_edges = [0, 1, 2, 3]
        for idx in u_edges:
            self.assertEqual(eo[idx], 0)

    def test_derange_corners(self) -> None:
        """Test that derange ensures pieces are not in solved positions."""
        scramble = scramble_with_piece_constraints(
            derange_corners='U',
            rng=Random(42),
        )

        # Apply and verify U corners are not all solved
        cube = VCube()
        cube.rotate(str(scramble))
        cp, _co, _ep, _eo, _ = cube.to_cubies

        # At least one U corner should not be in solved position
        u_corners = [0, 1, 2, 3]
        unsolved_count = sum(1 for idx in u_corners if cp[idx] != idx)
        self.assertGreater(unsolved_count, 0)

    def test_derange_edges(self) -> None:
        """Test that derange ensures edges are not in solved positions."""
        scramble = scramble_with_piece_constraints(
            derange_edges='U',
            rng=Random(42),
        )

        # Apply and verify U edges are not all solved
        cube = VCube()
        cube.rotate(str(scramble))
        _cp, _co, ep, _eo, _ = cube.to_cubies

        # At least one U edge should not be in solved position
        u_edges = [0, 1, 2, 3]
        unsolved_count = sum(1 for idx in u_edges if ep[idx] != idx)
        self.assertGreater(unsolved_count, 0)

    def test_disorient_corners(self) -> None:
        """Test that disorient ensures corners are not correctly oriented."""
        scramble = scramble_with_piece_constraints(
            disorient_corners_spec='U',
            rng=Random(42),
        )

        # Apply and verify U corners are not all oriented
        cube = VCube()
        cube.rotate(str(scramble))
        _cp, co, _ep, _eo, _ = cube.to_cubies

        # At least one U corner should not be oriented
        u_corners = [0, 1, 2, 3]
        disoriented_count = sum(1 for idx in u_corners if co[idx] != 0)
        self.assertGreater(disoriented_count, 0)

    def test_disorient_edges(self) -> None:
        """Test that disorient ensures edges are not correctly oriented."""
        scramble = scramble_with_piece_constraints(
            disorient_edges_spec='U',
            rng=Random(42),
        )

        # Apply and verify U edges are not all oriented
        cube = VCube()
        cube.rotate(str(scramble))
        _cp, _co, _ep, eo, _ = cube.to_cubies

        # At least one U edge should not be oriented
        u_edges = [0, 1, 2, 3]
        disoriented_count = sum(1 for idx in u_edges if eo[idx] != 0)
        self.assertGreater(disoriented_count, 0)

    def test_combined_constraints(self) -> None:
        """Test multiple constraints together."""
        scramble = scramble_with_piece_constraints(
            solve_corners='D',
            solve_edges='D E',
            orient_corners_spec='all',
            orient_edges_spec='all',
            buffer_corners='U',
            buffer_edges='U',
            rng=Random(42),
        )

        # Should return valid Algorithm
        self.assertIsInstance(scramble, Algorithm)

        # Apply and verify
        cube = VCube()
        cube.rotate(str(scramble))
        cp, co, _ep, eo, _ = cube.to_cubies

        # D corners should be solved
        d_corners = [4, 5, 6, 7]
        for idx in d_corners:
            self.assertEqual(cp[idx], idx)

        # All corners should be oriented
        self.assertEqual(co, SOLVED_CO)

        # All edges should be oriented
        self.assertEqual(eo, SOLVED_EO)

    def test_custom_buffer_pieces(self) -> None:
        """Test using custom buffer pieces."""
        scramble = scramble_with_piece_constraints(
            orient_corners_spec='U',
            buffer_corners='D',
            buffer_edges='E',
            rng=Random(42),
        )

        # Should return valid Algorithm
        self.assertIsInstance(scramble, Algorithm)

    def test_empty_constraints(self) -> None:
        """Test with no constraints returns random scramble."""
        scramble = scramble_with_piece_constraints(rng=Random(42))

        # Should return valid Algorithm
        self.assertIsInstance(scramble, Algorithm)

    def test_all_parameters(self) -> None:
        """Test with all parameters specified."""
        scramble = scramble_with_piece_constraints(
            solve_corners='DFR',
            solve_edges='FR',
            orient_corners_spec='U',
            orient_edges_spec='U',
            derange_corners='',
            derange_edges='',
            disorient_corners_spec='',
            disorient_edges_spec='',
            buffer_corners='D',
            buffer_edges='E',
            rng=Random(42),
        )

        # Should return valid Algorithm
        self.assertIsInstance(scramble, Algorithm)


class TestRNGParameter(unittest.TestCase):
    """Tests for random number generator parameter functionality."""

    def test_scramble_easy_cross_deterministic_with_seed(self) -> None:
        """Test scramble_easy_cross produces identical results with seed."""
        rng1 = Random(42)
        rng2 = Random(42)

        result1 = scramble_easy_cross(rng1)
        result2 = scramble_easy_cross(rng2)

        self.assertEqual(
            str(result1),
            str(result2),
            'Same seed should produce identical easy cross scrambles',
        )
        self.assertEqual(
            len(result1),
            10,
            'Easy cross scramble should have 10 moves',
        )

    def test_scramble_easy_cross_different_seeds_produce_different_results(
            self) -> None:
        """Test scramble_easy_cross produces different results."""
        rng1 = Random(42)
        rng2 = Random(777)

        result1 = scramble_easy_cross(rng1)
        result2 = scramble_easy_cross(rng2)

        self.assertNotEqual(
            str(result1),
            str(result2),
            'Different seeds should produce different easy cross scrambles',
        )

    def test_scramble_easy_cross_uses_default_rng_when_none(self) -> None:
        """Test scramble_easy_cross works without explicit rng parameter."""
        result = scramble_easy_cross()

        self.assertEqual(
            len(result),
            10,
            'Should generate easy cross scramble with default RNG',
        )
        self.assertFalse(
            any(str(move).startswith(('U', 'D')) for move in result),
            'Easy cross should not contain U or D moves',
        )
