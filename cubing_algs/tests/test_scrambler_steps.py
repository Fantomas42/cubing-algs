# ruff: noqa: S311
"""Tests for step-based scramble generation."""
import unittest
from random import Random

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.exceptions import InvalidStepError
from cubing_algs.scrambler.pieces import _calculate_parity
from cubing_algs.scrambler.steps import SUPPORTED_STEPS
from cubing_algs.scrambler.steps import _generate_step_state
from cubing_algs.scrambler.steps import scramble_ocll_case
from cubing_algs.scrambler.steps import scramble_step
from cubing_algs.vcube import VCube


class TestGenerateStepState(unittest.TestCase):
    """Tests for _generate_step_state function."""

    def test_all_supported_steps_generate(self) -> None:
        """Test that all supported steps generate valid states."""
        rng = Random(42)
        for step in SUPPORTED_STEPS:
            cp, co, ep, eo = _generate_step_state(step, rng)

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
                _calculate_parity(cp),
                _calculate_parity(ep),
                f'Step {step}: parity mismatch',
            )

    def test_invalid_step_raises(self) -> None:
        """Test that invalid step name raises error."""
        with self.assertRaises(InvalidStepError):
            _generate_step_state('INVALID_STEP', Random(42))

    def test_pll_only_permutation(self) -> None:
        """Test that PLL only permutes U layer."""
        _cp, co, _ep, eo = _generate_step_state('PLL', Random(42))

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
            _cp, co, _ep, eo = _generate_step_state('OLL', rng)

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
        cp, _co, _ep, _eo = _generate_step_state('F2L', Random(42))

        # All corners should potentially be permuted
        # Just check valid permutation
        self.assertEqual(set(cp), set(SOLVED_CP))

    def test_deterministic_with_seed(self) -> None:
        """Test that same seed produces same result."""
        cp1, co1, ep1, eo1 = _generate_step_state('PLL', Random(42))
        cp2, co2, ep2, eo2 = _generate_step_state('PLL', Random(42))

        self.assertEqual(cp1, cp2)
        self.assertEqual(co1, co2)
        self.assertEqual(ep1, ep2)
        self.assertEqual(eo1, eo2)


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
