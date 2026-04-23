"""Tests for trigger patterns and their variations."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.impacts import CycleAnalysis
from cubing_algs.impacts import compute_impacts
from cubing_algs.triggers import TRIGGER_PATTERNS
from cubing_algs.triggers import TriggerMatch
from cubing_algs.triggers import TriggerPattern


class TestTriggerPattern(unittest.TestCase):
    """Test the TriggerPattern NamedTuple."""

    def test_creation(self) -> None:
        """Test basic creation."""
        pattern = TriggerPattern(
            name='Test',
            moves='R U R',
            category='basic',
            ergonomic_bonus=0.1,
            speed_multiplier=1.2,
            variations=["L U L'"],
        )
        self.assertEqual(pattern.name, 'Test')
        self.assertEqual(pattern.moves, 'R U R')
        self.assertEqual(pattern.category, 'basic')

    def test_trigger_patterns_count(self) -> None:
        """Test that all 15 trigger patterns are defined."""
        self.assertEqual(len(TRIGGER_PATTERNS), 15)

    def test_primary_moves_are_unique(self) -> None:
        """Test that each pattern has unique primary moves."""
        seen: dict[str, str] = {}
        for pattern in TRIGGER_PATTERNS:
            if pattern.moves in seen:
                self.fail(
                    f"Pattern '{pattern.name}' has the same moves as "
                    f"'{seen[pattern.moves]}': '{pattern.moves}'"
                )
            seen[pattern.moves] = pattern.name

    def test_no_primary_moves_in_other_variations(self) -> None:
        """
        Test that no pattern's primary moves appear
        as another pattern's variation.
        """
        primary_moves = {p.moves: p.name for p in TRIGGER_PATTERNS}
        for pattern in TRIGGER_PATTERNS:
            for variation in pattern.variations:
                if (
                        variation in primary_moves
                        and primary_moves[variation] != pattern.name
                ):
                    self.fail(
                        f"Variation '{variation} "
                        f"of '{pattern.name}' duplicates "
                        f"primary moves of '{primary_moves[variation]}'",
                    )


class TestTriggerMatch(unittest.TestCase):
    """Test the TriggerMatch NamedTuple."""

    def test_creation(self) -> None:
        """Test basic creation."""
        pattern = TRIGGER_PATTERNS[0]
        match = TriggerMatch(
            pattern=pattern,
            start_index=0,
            end_index=3,
            matched_moves="R U R' U'",
        )
        self.assertEqual(match.start_index, 0)
        self.assertEqual(match.end_index, 3)
        self.assertEqual(match.matched_moves, "R U R' U'")


class TestTriggerVariationsConsistency(unittest.TestCase):
    """Verify that each trigger's variations have identical cubie impacts."""

    @staticmethod
    def impacts_for(moves: str) -> tuple[
        int | None, int | None, int | None, int | None,
        CycleAnalysis | None, CycleAnalysis | None,
        int | None, int | None,
    ]:
        """
        Compute the cubie-level impact summary for a move sequence.

        Returns a tuple of the metrics that must match across all variations
        of a trigger: corners_moved, corners_twisted, edges_moved,
        edges_flipped, corner_cycle_analysis, edge_cycle_analysis,
        corner_parity, edge_parity.

        Returns:
            Cubies informations.

        """
        impact = compute_impacts(Algorithm.parse_moves(moves))
        return (
            impact.cubies_corners_moved,
            impact.cubies_corners_twisted,
            impact.cubies_edges_moved,
            impact.cubies_edges_flipped,
            impact.cubies_corner_cycle_analysis,
            impact.cubies_edge_cycle_analysis,
            impact.cubies_corner_parity,
            impact.cubies_edge_parity,
        )

    def test_variations_match_main(self) -> None:
        """
        Each variation of a trigger must have
        the same cubie impact as the main.
        """
        for trigger in TRIGGER_PATTERNS:
            if not trigger.variations:
                continue
            main_impact = self.impacts_for(trigger.moves)
            for variation in trigger.variations:
                with self.subTest(trigger=trigger.name, variation=variation):
                    var_impact = self.impacts_for(variation)
                    self.assertEqual(
                        main_impact,
                        var_impact,
                        msg=(
                            f"Trigger '{trigger.name}': variation "
                            f"'{variation}' has different cubie impacts "
                            f"than main '{trigger.moves}'.\n"
                            f"  main:      {main_impact}\n"
                            f"  variation: {var_impact}"
                        ),
                    )
