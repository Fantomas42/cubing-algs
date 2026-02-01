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

        self.assertEqual(
            str(scramble),
            "U' F B' R2 F B' L2 U' F2 U B2 U' R2 B2 D' B2",
        )

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

        self.assertIsInstance(scramble_with, Algorithm)
        self.assertIsInstance(scramble_without, Algorithm)
        self.assertEqual(
            str(scramble_with),
            "U' F B' R2 F B' L2 U' F2 U B2 U' R2 B2 D' B2",
        )
        self.assertEqual(
            str(scramble_without),
            "U' F B' R2 F B' L2 U' F2 U B2 U' R2 B2 D' B2",
        )

    def test_deterministic_with_seed(self) -> None:
        """Test that same seed produces same scramble."""
        scramble1 = scramble_step('PLL', Random(42), include_auf=False)
        scramble2 = scramble_step('PLL', Random(42), include_auf=False)

        self.assertEqual(str(scramble1), str(scramble2))
        self.assertEqual(
            str(scramble1),
            "U' F B' R2 F B' L2 U' F2 U B2 U' R2 B2 D' B2",
        )

    def test_default_rng_when_none(self) -> None:
        """Test that default RNG is used when None is passed."""
        scramble = scramble_step('PLL', None, include_auf=False)

        # Should return valid Algorithm
        self.assertIsInstance(scramble, Algorithm)


class TestScrambleOCLLCase(unittest.TestCase):
    """Tests for scramble_ocll_case function."""

    def test_all_ocll_cases(self) -> None:
        """Test all OCLL case types."""
        expected = {
            'T': "R U R D R' U' R B2 U' L2 U L2 D' B2 R2 U'",
            'U': "R F2 L' D2 L F2 R D' F2 U F2 U2 R2 D B2 U2",
            'L': "R' B L' F2 L B' R U' F2 L2 U2 F2 U' L2 F2 U L2",
            'H': "R' U' R2 U' R U2 R2 U' R' U B2 U B2 D' R2 D R2 U2",
            'Pi': "U2 F U2 F' U L2 B' U' B L2 B2 U F2 D' R2 B2 D F2 L2",
            'Sune': "L' U' L U' L' U2 L' U' F2 U F2 L2 D F2 D' F2 U2",
            'AntiSune': "F2 R U' R' U' R U2 R' D F2 D' F2 U' F2 L2 U L2 U2",
            'Solved': "U F2 R L B2 R L' D B2 R2 U' B2 U F2 U' B2 L2",
        }
        rng = Random(42)

        for case, expected_scramble in expected.items():
            scramble = scramble_ocll_case(case, rng)

            self.assertIsInstance(scramble, Algorithm)
            self.assertEqual(str(scramble), expected_scramble)

    def test_invalid_case_raises(self) -> None:
        """Test that invalid case raises error."""
        with self.assertRaises(InvalidStepError):
            scramble_ocll_case('INVALID', Random(42))

    def test_case_insensitive(self) -> None:
        """Test that case names are case-insensitive."""
        # These should all work
        t_upper = scramble_ocll_case('T', Random(42))
        t_lower = scramble_ocll_case('t', Random(42))
        sune_lower = scramble_ocll_case('sune', Random(42))
        sune_upper = scramble_ocll_case('SUNE', Random(42))

        self.assertEqual(t_upper, t_lower)
        self.assertEqual(sune_lower, sune_upper)
        self.assertEqual(
            str(t_upper),
            "R U R D R' U' R B2 U' L2 U L2 D' B2 R2 U'",
        )
        self.assertEqual(
            str(sune_lower),
            "B' U' B U' F' L2 F' D B2 L2 U B2 U' F2 U R2 U",
        )

    def test_solved_case(self) -> None:
        """Test that solved case returns valid scramble."""
        scramble = scramble_ocll_case('Solved', Random(42))

        self.assertEqual(
            str(scramble),
            "U' F B' R2 F B' L2 U' F2 U B2 U' R2 B2 D' B2",
        )

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
        self.assertEqual(
            str(scramble1),
            "R U R D R' U' R B2 U' L2 U L2 D' B2 R2 U'",
        )

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
            str(result1),
            'F R F L F R F R B R',
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
