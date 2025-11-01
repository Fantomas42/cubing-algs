"""
Compression round-trip integrity tests.

These tests ensure that compressed algorithms can be parsed back
to produce the same result as the original algorithm.
"""

import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.structure import compress


class CompressionRoundTripTestCase(unittest.TestCase):  # noqa: PLR0904
    """Test that compressed algorithms round-trip correctly."""

    def test_simple_commutator_roundtrip(self) -> None:
        """Test round-trip for simple commutator."""
        original = Algorithm.parse_moves("R U R' U'")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_simple_conjugate_roundtrip(self) -> None:
        """Test round-trip for simple conjugate."""
        original = Algorithm.parse_moves("R U R'")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_sexy_move_roundtrip(self) -> None:
        """Test round-trip for sexy move (F R U R' U' F')."""
        original = Algorithm.parse_moves("F R U R' U' F'")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_sledgehammer_roundtrip(self) -> None:
        """Test round-trip for sledgehammer (R' F R F')."""
        original = Algorithm.parse_moves("R' F R F'")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_sune_roundtrip(self) -> None:
        """Test round-trip for Sune."""
        original = Algorithm.parse_moves("R U R' U R U2 R'")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_t_perm_roundtrip_default(self) -> None:
        """Test round-trip for T-Perm with default score."""
        original = Algorithm.parse_moves(
            "R U R' F' R U R' U' R' F R2 U' R'",
        )
        compressed = compress(original)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_t_perm_roundtrip_min_score_0(self) -> None:
        """Test round-trip for T-Perm with min_score=0."""
        original = Algorithm.parse_moves(
            "R U R' F' R U R' U' R' F R2 U' R'",
        )
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_t_perm_roundtrip_min_score_3(self) -> None:
        """Test round-trip for T-Perm with min_score=3.0."""
        original = Algorithm.parse_moves(
            "R U R' F' R U R' U' R' F R2 U' R'",
        )
        compressed = compress(original, min_score=3.0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_jb_perm_roundtrip(self) -> None:
        """Test round-trip for Jb-Perm."""
        original = Algorithm.parse_moves(
            "R U R' U' R' F R2 U' R' U' R U R' F'",
        )
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_y_perm_roundtrip(self) -> None:
        """Test round-trip for Y-Perm."""
        original = Algorithm.parse_moves(
            "F R U' R' U' R U R' F' R U R' U' R' F R F'",
        )
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_niklas_roundtrip(self) -> None:
        """Test round-trip for Niklas commutator."""
        original = Algorithm.parse_moves("R U' L' U R' U' L U")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_double_commutator_roundtrip(self) -> None:
        """Test round-trip for two consecutive commutators."""
        original = Algorithm.parse_moves("R U R' U' F D F' D'")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_edge_flip_roundtrip(self) -> None:
        """Test round-trip for edge flip (M U M' U')."""
        original = Algorithm.parse_moves("M U M' U'")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_corner_twist_roundtrip(self) -> None:
        """Test round-trip for corner twist."""
        original = Algorithm.parse_moves("R' D' R D R' D' R D")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_no_structure_roundtrip(self) -> None:
        """Test round-trip when no structures are detected."""
        original = Algorithm.parse_moves('R U F D L B')
        compressed = compress(original, min_score=50)

        # Should just return the original moves
        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_single_move_roundtrip(self) -> None:
        """Test round-trip for single move."""
        original = Algorithm.parse_moves('R')
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_double_move_roundtrip(self) -> None:
        """Test round-trip for algorithms with double moves."""
        original = Algorithm.parse_moves('R2 U2 R2 U2')
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_wide_moves_roundtrip(self) -> None:
        """Test round-trip for algorithms with wide moves."""
        original = Algorithm.parse_moves("Rw U Rw' U'")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_complex_nested_roundtrip(self) -> None:
        """Test round-trip for complex nested structure."""
        original = Algorithm.parse_moves("R U F D L B U' F' D' L' B' R'")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_partial_structure_roundtrip(self) -> None:
        """Test round-trip with partial structure coverage."""
        original = Algorithm.parse_moves("R U R' U' F D")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))

    def test_multiple_conjugates_roundtrip(self) -> None:
        """Test round-trip with multiple conjugates."""
        original = Algorithm.parse_moves("R U R' F D F' L B L' U D")
        compressed = compress(original, min_score=0)

        parsed = Algorithm.parse_moves(compressed)
        self.assertEqual(str(parsed), str(original))
