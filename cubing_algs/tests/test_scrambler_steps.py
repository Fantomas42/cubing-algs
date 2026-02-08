# ruff: noqa: S311
"""Tests for step-based scramble generation."""
import unittest
from random import Random

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.exceptions import InvalidSlotSpecError
from cubing_algs.exceptions import InvalidStepError
from cubing_algs.integrity import compute_parity
from cubing_algs.scrambler.steps import SUPPORTED_STEPS
from cubing_algs.scrambler.steps import generate_step_state
from cubing_algs.scrambler.steps import scramble_easy_cross
from cubing_algs.scrambler.steps import scramble_f2l
from cubing_algs.scrambler.steps import scramble_ocll_case
from cubing_algs.scrambler.steps import scramble_step
from cubing_algs.scrambler.steps import scramble_x_cross
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
        f2l_steps = ['F2L', 'ZZF2L', 'ZZRB', 'PETRUSF2L']
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
        petrus_steps = ['PETRUS2x2x3', 'PETRUSEO']
        for step in petrus_steps:
            self.assertIn(step, SUPPORTED_STEPS)

    def test_total_count(self) -> None:
        """Test that we have 30+ steps as promised."""
        self.assertGreaterEqual(len(SUPPORTED_STEPS), 30)


class TestScrambleEasyCross(unittest.TestCase):
    """Tests for easy cross scramble generation."""

    def test_scramble_easy_cross_easy(self) -> None:
        """Test scramble_easy_cross with easy difficulty."""
        _, solution = scramble_easy_cross('easy')

        self.assertEqual(
            len(solution),
            3,
        )

    def test_scramble_easy_cross_normal(self) -> None:
        """Test scramble_easy_cross with normal difficulty."""
        _, solution = scramble_easy_cross('normal')

        self.assertEqual(
            len(solution),
            5,
        )

    def test_scramble_easy_cross_hard(self) -> None:
        """Test scramble_easy_cross with hard difficulty."""
        _, solution = scramble_easy_cross('hard')

        self.assertEqual(
            len(solution),
            7,
        )

    def test_scramble_easy_cross_invalid_difficulty(self) -> None:
        """Test scramble_easy_cross with invalid difficulty."""
        _, solution = scramble_easy_cross('invalid')

        self.assertEqual(
            len(solution),
            5,
        )

    def test_scramble_easy_cross_deterministic_with_seed(self) -> None:
        """Test scramble_easy_cross produces identical results with seed."""
        rng1 = Random(42)
        rng2 = Random(42)

        scramble_1, solution_1 = scramble_easy_cross(rng=rng1)
        scramble_2, solution_2 = scramble_easy_cross(rng=rng2)

        self.assertEqual(
            str(scramble_1),
            str(scramble_2),
            'Same seed should produce identical easy cross scrambles',
        )

        self.assertEqual(
            str(solution_1),
            str(solution_2),
            'Same seed should produce identical easy cross solutions',
        )

        self.assertEqual(
            str(scramble_1),
            "U2 F2 B2 R2 F' U' D2 B D' F' B' R U R2 D' F2 B2 D2 R2 D F2 D",
        )

        self.assertEqual(
            str(solution_1),
            "U' F U2 L F2",
        )

    def test_scramble_easy_cross_different_seeds_produce_different_results(
            self) -> None:
        """Test scramble_easy_cross produces different results."""
        rng1 = Random(42)
        rng2 = Random(777)

        scramble_1, solution_1 = scramble_easy_cross(rng=rng1)
        scramble_2, solution_2 = scramble_easy_cross(rng=rng2)

        self.assertNotEqual(
            str(scramble_1),
            str(scramble_2),
            'Different seed should produce different easy cross scrambles',
        )

        self.assertNotEqual(
            str(solution_1),
            str(solution_2),
            'Different seed should produce different easy cross solutions',
        )


class TestScrambleXCross(unittest.TestCase):
    """Tests for x-cross scramble generation."""

    def test_scramble_x_cross_easy(self) -> None:
        """Test scramble_x_cross with easy difficulty."""
        _, solution = scramble_x_cross('easy')

        self.assertEqual(
            len(solution),
            5,
        )

    def test_scramble_x_cross_normal(self) -> None:
        """Test scramble_x_cross with normal difficulty."""
        _, solution = scramble_x_cross('normal')

        self.assertEqual(
            len(solution),
            7,
        )

    def test_scramble_x_cross_hard(self) -> None:
        """Test scramble_x_cross with hard difficulty."""
        _, solution = scramble_x_cross('hard')

        self.assertEqual(
            len(solution),
            9,
        )

    def test_scramble_x_cross_invalid_difficulty(self) -> None:
        """Test scramble_x_cross with invalid difficulty."""
        _, solution = scramble_x_cross('invalid')

        self.assertEqual(
            len(solution),
            7,
        )

    def test_scramble_x_cross_slot_fr(self) -> None:
        """Test scramble_x_cross targeting FR slot."""
        rng = Random(42)
        scramble, solution = scramble_x_cross(slots=['FR'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertIsInstance(solution, Algorithm)
        self.assertEqual(
            str(scramble),
            "U2 R2 F' R2 D B' R' L2 U F L' U D R2 D' R2 B2 U' L2 D2 R2",
        )
        self.assertEqual(
            str(solution),
            "L U' F U2 L F2 R'",
        )

    def test_scramble_x_cross_slot_fl(self) -> None:
        """Test scramble_x_cross targeting FL slot."""
        rng = Random(42)
        scramble, solution = scramble_x_cross(slots=['FL'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertIsInstance(solution, Algorithm)
        self.assertEqual(
            str(scramble),
            "U2 R2 B' U2 F D B U F' R' L U' L2 F2 D' R2 U B2 U2 L2 B2",
        )
        self.assertEqual(
            str(solution),
            "L U' F U2 L F2 R'",
        )

    def test_scramble_x_cross_slot_br(self) -> None:
        """Test scramble_x_cross targeting BR slot."""
        rng = Random(42)
        scramble, solution = scramble_x_cross(slots=['BR'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertIsInstance(solution, Algorithm)
        self.assertEqual(
            str(scramble),
            "F' L' D R' F B2 U B2 R' B' R U L2 D' F2 L2 U R2 F2 D'",
        )
        self.assertEqual(
            str(solution),
            "L U' F U2 L F2 R'",
        )

    def test_scramble_x_cross_slot_bl(self) -> None:
        """Test scramble_x_cross targeting BL slot."""
        rng = Random(42)
        scramble, solution = scramble_x_cross(slots=['BL'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertIsInstance(solution, Algorithm)
        self.assertEqual(
            str(scramble),
            "L2 B2 U F' B' L' F' D2 R' U R D F2 R2 U B2 U' R2 D' R2 D",
        )
        self.assertEqual(
            str(solution),
            "L U' F U2 L F2 R'",
        )

    def test_scramble_x_cross_deterministic_with_seed(self) -> None:
        """Test scramble_x_cross produces identical results with seed."""
        rng1 = Random(42)
        rng2 = Random(42)

        scramble_1, solution_1 = scramble_x_cross(rng=rng1)
        scramble_2, solution_2 = scramble_x_cross(rng=rng2)

        self.assertEqual(
            str(scramble_1),
            str(scramble_2),
            'Same seed should produce identical x-cross scrambles',
        )

        self.assertEqual(
            str(solution_1),
            str(solution_2),
            'Same seed should produce identical x-cross solutions',
        )

        self.assertEqual(
            str(scramble_1),
            "U2 R2 F' R2 D B' R' L2 U F L' U D R2 D' R2 B2 U' L2 D2 R2",
        )

        self.assertEqual(
            str(solution_1),
            "L U' F U2 L F2 R'",
        )

    def test_scramble_x_cross_different_seeds_produce_different_results(
            self) -> None:
        """Test scramble_x_cross produces different results."""
        rng1 = Random(42)
        rng2 = Random(777)

        scramble_1, solution_1 = scramble_x_cross(rng=rng1)
        scramble_2, solution_2 = scramble_x_cross(rng=rng2)

        self.assertNotEqual(
            str(scramble_1),
            str(scramble_2),
            'Different seed should produce different x-cross scrambles',
        )

        self.assertNotEqual(
            str(solution_1),
            str(solution_2),
            'Different seed should produce different x-cross solutions',
        )

    def test_scramble_x_cross_different_slots_produce_different_results(
            self) -> None:
        """Test scramble_x_cross produces different results for slots."""
        rng1 = Random(123)
        rng2 = Random(123)

        scramble_fr, _ = scramble_x_cross(slots=['FR'], rng=rng1)
        scramble_bl, _ = scramble_x_cross(slots=['BL'], rng=rng2)

        self.assertNotEqual(
            str(scramble_fr),
            str(scramble_bl),
            'Different slots should produce different x-cross scrambles',
        )

    def test_scramble_x_cross_returns_valid_algorithms(self) -> None:
        """Test scramble_x_cross returns valid Algorithm instances."""
        scramble, solution = scramble_x_cross('normal', ['FR'], Random(42))

        self.assertIsInstance(scramble, Algorithm)
        self.assertIsInstance(solution, Algorithm)

    def test_scramble_x_cross_default_parameters(self) -> None:
        """Test scramble_x_cross with all default parameters."""
        scramble, solution = scramble_x_cross()

        self.assertIsInstance(scramble, Algorithm)
        self.assertIsInstance(solution, Algorithm)
        self.assertGreater(len(scramble), 0)
        self.assertGreater(len(solution), 0)

    def test_scramble_x_cross_all_slots(self) -> None:
        """Test scramble_x_cross works with all valid slots."""
        valid_slots = ['FR', 'FL', 'BR', 'BL']
        rng = Random(42)

        for slot in valid_slots:
            scramble, solution = scramble_x_cross(slots=[slot], rng=rng)

            self.assertIsInstance(scramble, Algorithm)
            self.assertIsInstance(solution, Algorithm)
            self.assertGreater(len(scramble), 0)
            self.assertGreater(len(solution), 0)

    def test_scramble_x_cross_all_difficulties(self) -> None:
        """Test scramble_x_cross works with all valid difficulties."""
        valid_difficulties = ['easy', 'normal', 'hard']
        rng = Random(42)

        for difficulty in valid_difficulties:
            scramble, solution = scramble_x_cross(
                difficulty=difficulty, rng=rng,
            )

            self.assertIsInstance(scramble, Algorithm)
            self.assertIsInstance(solution, Algorithm)
            self.assertGreater(len(scramble), 0)
            self.assertGreater(len(solution), 0)

    def test_scramble_x_cross_invalid_slot(self) -> None:
        """Test scramble_x_cross raises error for invalid slot."""
        with self.assertRaises(InvalidSlotSpecError):
            scramble_x_cross(slots=['XX'])

    def test_scramble_x_cross_invalid_slot_in_list(self) -> None:
        """Test scramble_x_cross raises error for invalid slot in list."""
        with self.assertRaises(InvalidSlotSpecError):
            scramble_x_cross(slots=['FR', 'XX'])

    def test_scramble_x_cross_all_four_slots_raises(self) -> None:
        """Test scramble_x_cross raises error when all slots preserved."""
        with self.assertRaises(InvalidSlotSpecError):
            scramble_x_cross(slots=['FR', 'FL', 'BR', 'BL'])


class TestScrambleMultiSlotCross(unittest.TestCase):
    """Tests for xx-cross and xxx-cross scramble generation."""

    def test_scramble_xx_cross_easy(self) -> None:
        """Test xx-cross easy solution length (3 + 2*2 = 7)."""
        _, solution = scramble_x_cross('easy', ['FR', 'FL'])

        self.assertEqual(len(solution), 7)

    def test_scramble_xx_cross_normal(self) -> None:
        """Test xx-cross normal solution length (5 + 2*2 = 9)."""
        _, solution = scramble_x_cross('normal', ['FR', 'FL'])

        self.assertEqual(len(solution), 9)

    def test_scramble_xx_cross_hard(self) -> None:
        """Test xx-cross hard solution length (7 + 2*2 = 11)."""
        _, solution = scramble_x_cross('hard', ['FR', 'FL'])

        self.assertEqual(len(solution), 11)

    def test_scramble_xxx_cross_easy(self) -> None:
        """Test xxx-cross easy solution length (3 + 2*3 = 9)."""
        _, solution = scramble_x_cross('easy', ['FR', 'FL', 'BR'])

        self.assertEqual(len(solution), 9)

    def test_scramble_xxx_cross_normal(self) -> None:
        """Test xxx-cross normal solution length (5 + 2*3 = 11)."""
        _, solution = scramble_x_cross('normal', ['FR', 'FL', 'BR'])

        self.assertEqual(len(solution), 11)

    def test_scramble_xxx_cross_hard(self) -> None:
        """Test xxx-cross hard solution length (7 + 2*3 = 13)."""
        _, solution = scramble_x_cross('hard', ['FR', 'FL', 'BR'])

        self.assertEqual(len(solution), 13)


class TestScrambleF2L(unittest.TestCase):
    """Tests for F2L scramble generation."""

    def test_scramble_f2l_slot_fr(self) -> None:
        """Test scramble_f2l targeting FR slot."""
        rng = Random(42)
        scramble = scramble_f2l(slots=['FR'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertEqual(
            str(scramble),
            "R U' R U B U' B U' F2 L2 D L2 F2 U2 B2 U' R2",
        )

    def test_scramble_f2l_slot_fl(self) -> None:
        """Test scramble_f2l targeting FL slot."""
        rng = Random(42)
        scramble = scramble_f2l(slots=['FL'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertEqual(
            str(scramble),
            "U F U2 R U R2 F R' F2 U' R2 D R2 D' F2 U R2 F2",
        )

    def test_scramble_f2l_slot_br(self) -> None:
        """Test scramble_f2l targeting BR slot."""
        rng = Random(42)
        scramble = scramble_f2l(slots=['BR'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertEqual(
            str(scramble),
            "U' B' R B R F D' F' D2 L2 D' F2 R2 U B2 R2 F2 R2",
        )

    def test_scramble_f2l_slot_bl(self) -> None:
        """Test scramble_f2l targeting BL slot."""
        rng = Random(42)
        scramble = scramble_f2l(slots=['BL'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertEqual(
            str(scramble),
            "L2 U2 L B D L D2 B' D L2 B2 L2 U' L2 U B2 U2 L2",
        )

    def test_scramble_f2l_default_parameters(self) -> None:
        """Test scramble_f2l with all default parameters."""
        scramble = scramble_f2l()

        self.assertIsInstance(scramble, Algorithm)
        self.assertGreater(len(scramble), 0)

    def test_scramble_f2l_default_slot_is_fr(self) -> None:
        """Test scramble_f2l defaults to FR slot."""
        rng1 = Random(42)
        rng2 = Random(42)

        scramble_default = scramble_f2l(rng=rng1)
        scramble_fr = scramble_f2l(slots=['FR'], rng=rng2)

        self.assertEqual(str(scramble_default), str(scramble_fr))

    def test_scramble_f2l_deterministic_with_seed(self) -> None:
        """Test scramble_f2l produces identical results with same seed."""
        rng1 = Random(42)
        rng2 = Random(42)

        scramble_1 = scramble_f2l(rng=rng1)
        scramble_2 = scramble_f2l(rng=rng2)

        self.assertEqual(
            str(scramble_1),
            str(scramble_2),
            'Same seed should produce identical F2L scrambles',
        )
        self.assertEqual(
            str(scramble_1),
            "R U' R U B U' B U' F2 L2 D L2 F2 U2 B2 U' R2",
        )

    def test_scramble_f2l_different_seeds_produce_different_results(
            self) -> None:
        """Test scramble_f2l produces different results with different seeds."""
        rng1 = Random(42)
        rng2 = Random(777)

        scramble_1 = scramble_f2l(slots=['FR'], rng=rng1)
        scramble_2 = scramble_f2l(slots=['FR'], rng=rng2)

        self.assertNotEqual(
            str(scramble_1),
            str(scramble_2),
            'Different seeds should produce different F2L scrambles',
        )

    def test_scramble_f2l_different_slots_produce_different_results(
            self) -> None:
        """Test scramble_f2l produces different results for different slots."""
        rng1 = Random(123)
        rng2 = Random(123)

        scramble_fr = scramble_f2l(slots=['FR'], rng=rng1)
        scramble_bl = scramble_f2l(slots=['BL'], rng=rng2)

        self.assertNotEqual(
            str(scramble_fr),
            str(scramble_bl),
            'Different slots should produce different F2L scrambles',
        )

    def test_scramble_f2l_multiple_slots(self) -> None:
        """Test scramble_f2l works with multiple slots."""
        rng = Random(42)
        scramble = scramble_f2l(slots=['FR', 'FL'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertEqual(
            str(scramble),
            "U' L2 B2 D R D2 R' U F2 D F2 R2 B2 U2 L2 D F2",
        )

    def test_scramble_f2l_all_four_slots(self) -> None:
        """Test scramble_f2l works with all four slots."""
        rng = Random(42)
        scramble = scramble_f2l(slots=['FR', 'FL', 'BR', 'BL'], rng=rng)

        self.assertIsInstance(scramble, Algorithm)
        self.assertEqual(
            str(scramble),
            "U F U2 L2 D' B D2 R F2 R D B2 D2 F2 L2 U B2 L2 B2 L2",
        )

    def test_scramble_f2l_invalid_slot_raises(self) -> None:
        """Test scramble_f2l raises error for invalid slot."""
        with self.assertRaises(InvalidSlotSpecError):
            scramble_f2l(slots=['XX'])

    def test_scramble_f2l_invalid_slot_in_list_raises(self) -> None:
        """Test scramble_f2l raises error for invalid slot in list."""
        with self.assertRaises(InvalidSlotSpecError):
            scramble_f2l(slots=['FR', 'XX'])

    def test_scramble_f2l_returns_algorithm_instance(self) -> None:
        """Test scramble_f2l returns a valid Algorithm instance."""
        scramble = scramble_f2l(slots=['FR'], rng=Random(42))

        self.assertIsInstance(scramble, Algorithm)

    def test_scramble_f2l_all_slots_valid(self) -> None:
        """Test scramble_f2l works with each individual valid slot."""
        valid_slots = ['FR', 'FL', 'BR', 'BL']
        rng = Random(42)

        for slot in valid_slots:
            scramble = scramble_f2l(slots=[slot], rng=rng)

            self.assertIsInstance(scramble, Algorithm)
            self.assertGreater(len(scramble), 0)
