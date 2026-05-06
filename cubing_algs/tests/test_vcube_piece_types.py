"""Tests for VCube facelet piece type classification."""
import unittest

from cubing_algs.vcube import VCube


class TestFaceletPieceTypesSmallCubes(unittest.TestCase):
    """Tests for piece type classification on 2x2, 3x3, and 4x4 cubes."""

    def test_3x3_total_keys(self) -> None:
        """Test that 3x3 produces 54 entries."""
        cube = VCube(size=3)
        self.assertEqual(len(cube.facelet_piece_types), 9)

    def test_3x3_corners(self) -> None:
        """Test corner detection on 3x3 for all faces."""
        cube = VCube(size=3)
        corner_positions = [0, 2, 6, 8]
        for face in range(6):
            for pos in corner_positions:
                index = face * 9 + pos
                with self.subTest(face=face, pos=pos):
                    self.assertEqual(
                        cube.get_facelet_piece_types(index),
                        ['corner'],
                    )

    def test_3x3_edges(self) -> None:
        """Test edge detection on 3x3 (all edges are midges)."""
        cube = VCube(size=3)
        edge_positions = [1, 3, 5, 7]
        for face in range(6):
            for pos in edge_positions:
                index = face * 9 + pos
                with self.subTest(face=face, pos=pos):
                    self.assertEqual(
                        cube.get_facelet_piece_types(index),
                        ['midge', 'edge'],
                    )

    def test_3x3_fixed_centers(self) -> None:
        """Test fixed center detection on 3x3 for all faces."""
        cube = VCube(size=3)
        for face in range(6):
            index = face * 9 + 4
            with self.subTest(face=face):
                self.assertEqual(
                    cube.get_facelet_piece_types(index),
                    ['fixed_center', 'center'],
                )

    def test_2x2_all_corners(self) -> None:
        """Test that all 2x2 facelets are corners."""
        cube = VCube(size=2)
        self.assertEqual(len(cube.facelet_piece_types), 4)
        for index in range(24):
            with self.subTest(index=index):
                self.assertEqual(
                    cube.get_facelet_piece_types(index),
                    ['corner'],
                )

    def test_4x4_x_centers(self) -> None:
        """Test that all 4x4 centers are x_centers (even cube)."""
        cube = VCube(size=4)
        center_positions = [5, 6, 9, 10]
        for pos in center_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['x_center', 'center'],
                )

    def test_cached_property_returns_same_object(self) -> None:
        """Test that facelet_piece_types is cached (same id on repeat)."""
        cube = VCube(size=3)
        first = cube.facelet_piece_types
        second = cube.facelet_piece_types
        self.assertIs(first, second)

    def test_get_facelet_piece_types_matches_dict(self) -> None:
        """Test that method returns the same as dict lookup."""
        cube = VCube(size=3)
        for index in range(54):
            with self.subTest(index=index):
                self.assertEqual(
                    cube.get_facelet_piece_types(index),
                    cube.facelet_piece_types[index % cube.face_size],
                )


class TestFaceletPieceTypesLargeCubes(unittest.TestCase):
    """Tests for piece type classification on 5x5, 6x6, and 7x7 cubes."""

    def test_5x5_total_keys(self) -> None:
        """Test that 5x5 produces 150 entries."""
        cube = VCube(size=5)
        self.assertEqual(len(cube.facelet_piece_types), 25)

    def test_5x5_corners(self) -> None:
        """Test corner detection on 5x5."""
        cube = VCube(size=5)
        corner_positions = [0, 4, 20, 24]
        for pos in corner_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['corner'],
                )

    def test_5x5_edges(self) -> None:
        """Test edge detection on 5x5."""
        cube = VCube(size=5)
        edge_positions = [
            1, 2, 3,
            5, 9,
            10, 14,
            15, 19,
            21, 22, 23,
        ]
        edge_pieces: list[list[str]] = [
            ['wing', 'edge'], ['midge', 'edge'], ['wing', 'edge'],
            ['wing', 'edge'], ['wing', 'edge'],
            ['midge', 'edge'], ['midge', 'edge'],
            ['wing', 'edge'], ['wing', 'edge'],
            ['wing', 'edge'], ['midge', 'edge'], ['wing', 'edge'],
        ]
        for pos, expected in zip(edge_positions, edge_pieces, strict=True):
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    expected,
                )

    def test_5x5_fixed_center(self) -> None:
        """Test fixed center detection on 5x5."""
        cube = VCube(size=5)
        self.assertEqual(
            cube.get_facelet_piece_types(12),
            ['fixed_center', 'center'],
        )

    def test_5x5_t_centers(self) -> None:
        """Test t_center detection on 5x5 (middle row/col, not fixed)."""
        cube = VCube(size=5)
        t_center_positions = [7, 11, 13, 17]
        for pos in t_center_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['t_center', 'center'],
                )

    def test_5x5_x_centers(self) -> None:
        """Test x_center detection on 5x5 (diagonal from fixed center)."""
        cube = VCube(size=5)
        x_center_positions = [6, 8, 16, 18]
        for pos in x_center_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['x_center', 'center'],
                )

    def test_6x6_corners(self) -> None:
        """Test corner detection on 6x6."""
        cube = VCube(size=6)
        corner_positions = [0, 5, 30, 35]
        for pos in corner_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['corner'],
                )

    def test_6x6_wings(self) -> None:
        """Test wing detection on 6x6 (border, not corner or midge)."""
        cube = VCube(size=6)
        wing_positions = [
            1, 2, 3, 4,
            6, 11,
            12, 17,
            18, 23,
            24, 29,
            31, 32, 33, 34,
        ]
        for pos in wing_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['wing', 'edge'],
                )

    def test_6x6_x_centers(self) -> None:
        """Test x_center detection on 6x6 (equal row/col offset)."""
        cube = VCube(size=6)
        x_center_positions = [
            7, 10,
            14, 15,
            20, 21,
            25, 28,
        ]
        for pos in x_center_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['x_center', 'center'],
                )

    def test_6x6_oblique_centers(self) -> None:
        """Test oblique_center detection on 6x6 (unequal row/col offset)."""
        cube = VCube(size=6)
        oblique_positions = [
            8, 9,
            13, 16,
            19, 22,
            26, 27,
        ]
        for pos in oblique_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['oblique_center', 'center'],
                )

    def test_7x7_oblique_centers(self) -> None:
        """Test oblique_center detection on 7x7."""
        cube = VCube(size=7)
        oblique_positions = [9, 11, 15, 33]
        for pos in oblique_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['oblique_center', 'center'],
                )

    def test_7x7_x_centers(self) -> None:
        """Test x_center detection on 7x7."""
        cube = VCube(size=7)
        x_center_positions = [8, 12, 16, 32, 36, 40]
        for pos in x_center_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['x_center', 'center'],
                )

    def test_7x7_t_centers(self) -> None:
        """Test t_center detection on 7x7."""
        cube = VCube(size=7)
        t_center_positions = [10, 17, 22, 26, 31, 38]
        for pos in t_center_positions:
            with self.subTest(pos=pos):
                self.assertEqual(
                    cube.get_facelet_piece_types(pos),
                    ['t_center', 'center'],
                )

    def test_7x7_fixed_center(self) -> None:
        """Test fixed center detection on 7x7."""
        cube = VCube(size=7)
        self.assertEqual(
            cube.get_facelet_piece_types(24),
            ['fixed_center', 'center'],
        )
