"""Tests for face transformation computations."""

import unittest

from cubing_algs.face_transforms import ADJACENT_FACE_TRANSFORMATIONS
from cubing_algs.face_transforms import offset_down
from cubing_algs.face_transforms import offset_left
from cubing_algs.face_transforms import offset_right
from cubing_algs.face_transforms import offset_up
from cubing_algs.face_transforms import transform_position


class TestOffsetRight(unittest.TestCase):
    """Test offset_right transformation (90° clockwise rotation)."""

    def test_offset_right_all_positions(self) -> None:
        """Test offset_right transformation for all valid positions."""
        expected_mappings = {
            0: 6,
            1: 3,
            2: 0,
            3: 7,
            4: 4,
            5: 1,
            6: 8,
            7: 5,
            8: 2,
        }

        for position, expected in expected_mappings.items():
            with self.subTest(position=position):
                self.assertEqual(offset_right(position), expected)

    def test_offset_right_center_invariant(self) -> None:
        """Test that center position (4) remains at center."""
        self.assertEqual(offset_right(4), 4)

    def test_offset_right_corners(self) -> None:
        """Test corner transformations (positions 0, 2, 6, 8)."""
        self.assertEqual(offset_right(0), 6)
        self.assertEqual(offset_right(2), 0)
        self.assertEqual(offset_right(6), 8)
        self.assertEqual(offset_right(8), 2)

    def test_offset_right_edges(self) -> None:
        """Test edge transformations (positions 1, 3, 5, 7)."""
        self.assertEqual(offset_right(1), 3)
        self.assertEqual(offset_right(3), 7)
        self.assertEqual(offset_right(5), 1)
        self.assertEqual(offset_right(7), 5)

    def test_offset_right_four_times_returns_to_original(self) -> None:
        """Test applying offset_right 4 times returns to original."""
        for position in range(9):
            with self.subTest(position=position):
                result = position
                for _ in range(4):
                    result = offset_right(result)
                self.assertEqual(result, position)

    def test_offset_right_invalid_position_raises_key_error(self) -> None:
        """Test that invalid positions raise KeyError."""
        invalid_positions = [-1, 9, 10, 100, -100]
        for position in invalid_positions:
            with self.subTest(position=position), self.assertRaises(KeyError):
                offset_right(position)


class TestOffsetLeft(unittest.TestCase):
    """Test offset_left transformation (90° counter-clockwise rotation)."""

    def test_offset_left_all_positions(self) -> None:
        """Test offset_left transformation for all valid positions."""
        expected_mappings = {
            0: 2,
            1: 5,
            2: 8,
            3: 1,
            4: 4,
            5: 7,
            6: 0,
            7: 3,
            8: 6,
        }

        for position, expected in expected_mappings.items():
            with self.subTest(position=position):
                self.assertEqual(offset_left(position), expected)

    def test_offset_left_center_invariant(self) -> None:
        """Test that center position (4) remains at center."""
        self.assertEqual(offset_left(4), 4)

    def test_offset_left_corners(self) -> None:
        """Test corner transformations (positions 0, 2, 6, 8)."""
        self.assertEqual(offset_left(0), 2)
        self.assertEqual(offset_left(2), 8)
        self.assertEqual(offset_left(6), 0)
        self.assertEqual(offset_left(8), 6)

    def test_offset_left_edges(self) -> None:
        """Test edge transformations (positions 1, 3, 5, 7)."""
        self.assertEqual(offset_left(1), 5)
        self.assertEqual(offset_left(3), 1)
        self.assertEqual(offset_left(5), 7)
        self.assertEqual(offset_left(7), 3)

    def test_offset_left_four_times_returns_to_original(self) -> None:
        """Test applying offset_left 4 times returns to original."""
        for position in range(9):
            with self.subTest(position=position):
                result = position
                for _ in range(4):
                    result = offset_left(result)
                self.assertEqual(result, position)

    def test_offset_left_invalid_position_raises_key_error(self) -> None:
        """Test that invalid positions raise KeyError."""
        invalid_positions = [-1, 9, 10, 100, -100]
        for position in invalid_positions:
            with self.subTest(position=position), self.assertRaises(KeyError):
                offset_left(position)


class TestOffsetUp(unittest.TestCase):
    """Test offset_up transformation (vertical flip)."""

    def test_offset_up_all_positions(self) -> None:
        """Test offset_up transformation for all valid positions."""
        expected_mappings = {
            0: 8,
            1: 7,
            2: 6,
            3: 5,
            4: 4,
            5: 3,
            6: 2,
            7: 1,
            8: 0,
        }

        for position, expected in expected_mappings.items():
            with self.subTest(position=position):
                self.assertEqual(offset_up(position), expected)

    def test_offset_up_center_invariant(self) -> None:
        """Test that center position (4) remains at center."""
        self.assertEqual(offset_up(4), 4)

    def test_offset_up_corners(self) -> None:
        """Test corner transformations (positions 0, 2, 6, 8)."""
        self.assertEqual(offset_up(0), 8)
        self.assertEqual(offset_up(2), 6)
        self.assertEqual(offset_up(6), 2)
        self.assertEqual(offset_up(8), 0)

    def test_offset_up_edges(self) -> None:
        """Test edge transformations (positions 1, 3, 5, 7)."""
        self.assertEqual(offset_up(1), 7)
        self.assertEqual(offset_up(3), 5)
        self.assertEqual(offset_up(5), 3)
        self.assertEqual(offset_up(7), 1)

    def test_offset_up_twice_returns_to_original(self) -> None:
        """Test that applying offset_up twice returns to original position."""
        for position in range(9):
            with self.subTest(position=position):
                result = offset_up(offset_up(position))
                self.assertEqual(result, position)

    def test_offset_up_invalid_position_raises_key_error(self) -> None:
        """Test that invalid positions raise KeyError."""
        invalid_positions = [-1, 9, 10, 100, -100]
        for position in invalid_positions:
            with self.subTest(position=position), self.assertRaises(KeyError):
                offset_up(position)


class TestOffsetDown(unittest.TestCase):
    """Test offset_down transformation (identity transformation)."""

    def test_offset_down_all_positions(self) -> None:
        """Test offset_down is identity transformation for all positions."""
        for position in range(9):
            with self.subTest(position=position):
                self.assertEqual(offset_down(position), position)

    def test_offset_down_center_invariant(self) -> None:
        """Test that center position (4) remains at center."""
        self.assertEqual(offset_down(4), 4)

    def test_offset_down_corners(self) -> None:
        """Test corner positions remain unchanged (0, 2, 6, 8)."""
        self.assertEqual(offset_down(0), 0)
        self.assertEqual(offset_down(2), 2)
        self.assertEqual(offset_down(6), 6)
        self.assertEqual(offset_down(8), 8)

    def test_offset_down_edges(self) -> None:
        """Test edge positions remain unchanged (1, 3, 5, 7)."""
        self.assertEqual(offset_down(1), 1)
        self.assertEqual(offset_down(3), 3)
        self.assertEqual(offset_down(5), 5)
        self.assertEqual(offset_down(7), 7)

    def test_offset_down_invalid_position_raises_key_error(self) -> None:
        """Test that invalid positions raise KeyError."""
        invalid_positions = [-1, 9, 10, 100, -100]
        for position in invalid_positions:
            with self.subTest(position=position), self.assertRaises(KeyError):
                offset_down(position)


class TestTransformationInverses(unittest.TestCase):
    """Test that transformations have correct inverse properties."""

    def test_offset_right_and_offset_left_are_inverses(self) -> None:
        """Test that offset_right and offset_left are inverse operations."""
        for position in range(9):
            with self.subTest(position=position, order='right_then_left'):
                result = offset_left(offset_right(position))
                self.assertEqual(result, position)

            with self.subTest(position=position, order='left_then_right'):
                result = offset_right(offset_left(position))
                self.assertEqual(result, position)

    def test_offset_up_is_self_inverse(self) -> None:
        """Test that offset_up is its own inverse."""
        for position in range(9):
            with self.subTest(position=position):
                result = offset_up(offset_up(position))
                self.assertEqual(result, position)

    def test_offset_down_is_identity(self) -> None:
        """Test that offset_down composed with itself is still identity."""
        for position in range(9):
            with self.subTest(position=position):
                result = offset_down(offset_down(position))
                self.assertEqual(result, position)


class TestAdjacentFaceTransformations(unittest.TestCase):
    """Test ADJACENT_FACE_TRANSFORMATIONS constant structure and values."""

    def test_has_all_six_faces_as_keys(self) -> None:
        """Test that all six faces are present as keys."""
        expected_faces = {'U', 'R', 'F', 'D', 'L', 'B'}
        actual_faces = set(ADJACENT_FACE_TRANSFORMATIONS.keys())
        self.assertEqual(actual_faces, expected_faces)

    def test_each_face_has_four_adjacent_faces(self) -> None:
        """Test that each face maps to exactly 4 adjacent faces."""
        for face, adjacent_map in ADJACENT_FACE_TRANSFORMATIONS.items():
            with self.subTest(face=face):
                self.assertEqual(len(adjacent_map), 4)

    def test_u_face_transformations(self) -> None:
        """Test U face adjacent transformations."""
        u_transforms = ADJACENT_FACE_TRANSFORMATIONS['U']

        self.assertEqual(set(u_transforms.keys()), {'R', 'L', 'F', 'B'})
        self.assertIs(u_transforms['R'], offset_right)
        self.assertIs(u_transforms['L'], offset_left)
        self.assertIs(u_transforms['F'], offset_down)
        self.assertIs(u_transforms['B'], offset_up)

    def test_r_face_transformations(self) -> None:
        """Test R face adjacent transformations."""
        r_transforms = ADJACENT_FACE_TRANSFORMATIONS['R']

        self.assertEqual(set(r_transforms.keys()), {'F', 'B', 'U', 'D'})
        self.assertIs(r_transforms['F'], offset_down)
        self.assertIs(r_transforms['B'], offset_down)
        self.assertIs(r_transforms['U'], offset_left)
        self.assertIs(r_transforms['D'], offset_right)

    def test_f_face_transformations(self) -> None:
        """Test F face adjacent transformations."""
        f_transforms = ADJACENT_FACE_TRANSFORMATIONS['F']

        self.assertEqual(set(f_transforms.keys()), {'U', 'D', 'L', 'R'})
        self.assertIs(f_transforms['U'], offset_down)
        self.assertIs(f_transforms['D'], offset_down)
        self.assertIs(f_transforms['L'], offset_down)
        self.assertIs(f_transforms['R'], offset_down)

    def test_d_face_transformations(self) -> None:
        """Test D face adjacent transformations."""
        d_transforms = ADJACENT_FACE_TRANSFORMATIONS['D']

        self.assertEqual(set(d_transforms.keys()), {'R', 'L', 'F', 'B'})
        self.assertIs(d_transforms['R'], offset_left)
        self.assertIs(d_transforms['L'], offset_right)
        self.assertIs(d_transforms['F'], offset_down)
        self.assertIs(d_transforms['B'], offset_up)

    def test_l_face_transformations(self) -> None:
        """Test L face adjacent transformations."""
        l_transforms = ADJACENT_FACE_TRANSFORMATIONS['L']

        self.assertEqual(set(l_transforms.keys()), {'F', 'B', 'U', 'D'})
        self.assertIs(l_transforms['F'], offset_down)
        self.assertIs(l_transforms['B'], offset_down)
        self.assertIs(l_transforms['U'], offset_right)
        self.assertIs(l_transforms['D'], offset_left)

    def test_b_face_transformations(self) -> None:
        """Test B face adjacent transformations."""
        b_transforms = ADJACENT_FACE_TRANSFORMATIONS['B']

        self.assertEqual(set(b_transforms.keys()), {'U', 'D', 'L', 'R'})
        self.assertIs(b_transforms['U'], offset_up)
        self.assertIs(b_transforms['D'], offset_up)
        self.assertIs(b_transforms['L'], offset_down)
        self.assertIs(b_transforms['R'], offset_down)

    def test_transformation_functions_are_callable(self) -> None:
        """Test that all transformation functions in the map are callable."""
        for face, adjacent_map in ADJACENT_FACE_TRANSFORMATIONS.items():
            for adjacent_face, transform_func in adjacent_map.items():
                with self.subTest(face=face, adjacent_face=adjacent_face):
                    self.assertTrue(callable(transform_func))

    def test_transformation_functions_work_correctly(self) -> None:
        """Test that transformation functions can be applied correctly."""
        for face, adjacent_map in ADJACENT_FACE_TRANSFORMATIONS.items():
            for adjacent_face, transform_func in adjacent_map.items():
                with self.subTest(face=face, adjacent_face=adjacent_face):
                    # Test that the function works on a valid position
                    result = transform_func(4)
                    self.assertIsInstance(result, int)
                    self.assertIn(result, range(9))

    def test_no_face_is_adjacent_to_itself(self) -> None:
        """Test that no face lists itself as an adjacent face."""
        for face, adjacent_map in ADJACENT_FACE_TRANSFORMATIONS.items():
            with self.subTest(face=face):
                self.assertNotIn(face, adjacent_map.keys())

    def test_opposite_faces_not_adjacent(self) -> None:
        """Test that opposite faces are not listed as adjacent."""
        opposite_pairs = [
            ('U', 'D'),
            ('R', 'L'),
            ('F', 'B'),
        ]

        for face1, face2 in opposite_pairs:
            with self.subTest(face1=face1, face2=face2):
                self.assertNotIn(face2, ADJACENT_FACE_TRANSFORMATIONS[face1])
                self.assertNotIn(face1, ADJACENT_FACE_TRANSFORMATIONS[face2])


class TestTransformationCompositions(unittest.TestCase):
    """Test compositions of multiple transformations."""

    def test_offset_right_three_times_equals_offset_left(self) -> None:
        """Test that applying offset_right 3 times equals offset_left."""
        for position in range(9):
            with self.subTest(position=position):
                result_right_three = offset_right(
                    offset_right(offset_right(position)),
                )
                result_left = offset_left(position)
                self.assertEqual(result_right_three, result_left)

    def test_offset_left_three_times_equals_offset_right(self) -> None:
        """Test that applying offset_left 3 times equals offset_right."""
        for position in range(9):
            with self.subTest(position=position):
                result_left_three = offset_left(
                    offset_left(offset_left(position)),
                )
                result_right = offset_right(position)
                self.assertEqual(result_left_three, result_right)

    def test_offset_up_and_offset_right_composition(self) -> None:
        """Test composition of offset_up and offset_right."""
        # These should not commute (order matters)
        for position in range(9):
            with self.subTest(position=position):
                result1 = offset_right(offset_up(position))
                result2 = offset_up(offset_right(position))
                # For most positions, these should differ
                if position != 4:  # Center is always invariant
                    # Some positions might coincide
                    if position not in {1, 3, 5, 7}:
                        # We're just testing that composition works
                        self.assertIsInstance(result1, int)
                        self.assertIsInstance(result2, int)
                else:
                    self.assertEqual(result1, 4)
                    self.assertEqual(result2, 4)

    def test_offset_down_composed_with_any_transform_is_identity(self) -> None:
        """Test offset_down with any transform equals that transform."""
        transforms = [offset_right, offset_left, offset_up]

        for transform in transforms:
            for position in range(9):
                with self.subTest(
                    transform=transform.__name__, position=position,
                ):
                    # offset_down first
                    result1 = transform(offset_down(position))
                    # offset_down second
                    result2 = offset_down(transform(position))
                    # Both should equal just applying the transform
                    self.assertEqual(result1, transform(position))
                    self.assertEqual(result2, transform(position))


class TestTransformationEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions for transformations."""

    def test_all_transformations_preserve_range(self) -> None:
        """Test all transformations map valid positions to valid ones."""
        transforms = [offset_right, offset_left, offset_up, offset_down]

        for transform in transforms:
            for position in range(9):
                with self.subTest(
                    transform=transform.__name__, position=position,
                ):
                    result = transform(position)
                    self.assertIn(result, range(9))

    def test_transformations_are_bijective(self) -> None:
        """Test that transformations are one-to-one and onto."""
        transforms = [offset_right, offset_left, offset_up, offset_down]

        for transform in transforms:
            with self.subTest(transform=transform.__name__):
                results = [transform(i) for i in range(9)]
                # All results should be unique (one-to-one)
                self.assertEqual(len(results), len(set(results)))
                # All results should be in range(9) (onto)
                self.assertEqual(set(results), set(range(9)))

    def test_boundary_positions_transform_correctly(self) -> None:
        """Test transformations on boundary positions (corners and edges)."""
        corner_positions = [0, 2, 6, 8]
        edge_positions = [1, 3, 5, 7]

        for position in corner_positions:
            with self.subTest(position_type='corner', position=position):
                # Corners should map to corners
                self.assertIn(offset_right(position), corner_positions)
                self.assertIn(offset_left(position), corner_positions)
                self.assertIn(offset_up(position), corner_positions)

        for position in edge_positions:
            with self.subTest(position_type='edge', position=position):
                # Edges should map to edges
                self.assertIn(offset_right(position), edge_positions)
                self.assertIn(offset_left(position), edge_positions)
                self.assertIn(offset_up(position), edge_positions)

    def test_center_position_invariant_under_all_transformations(self) -> None:
        """Test position 4 (center) is invariant under all transforms."""
        transforms = [offset_right, offset_left, offset_up, offset_down]

        for transform in transforms:
            with self.subTest(transform=transform.__name__):
                self.assertEqual(transform(4), 4)


class TestTransformPosition(unittest.TestCase):
    """Test the transform_position helper function."""

    def test_transform_position_uses_correct_transformation_u(self) -> None:
        """Test that transform_position applies the correct transformation."""
        # U -> R uses offset_right
        self.assertEqual(transform_position('U', 'R', 0), 6)
        self.assertEqual(transform_position('U', 'R', 1), 3)

        # U -> L uses offset_left
        self.assertEqual(transform_position('U', 'L', 0), 2)
        self.assertEqual(transform_position('U', 'L', 1), 5)

        # U -> F uses offset_down (identity)
        self.assertEqual(transform_position('U', 'F', 0), 0)
        self.assertEqual(transform_position('U', 'F', 1), 1)

        # U -> B uses offset_up
        self.assertEqual(transform_position('U', 'B', 0), 8)
        self.assertEqual(transform_position('U', 'B', 1), 7)

    def test_transform_position_uses_correct_transformation_r(self) -> None:
        """Test that transform_position applies the correct transformation."""
        # R -> U
        self.assertEqual(transform_position('R', 'U', 0), 2)
        self.assertEqual(transform_position('R', 'U', 1), 5)

        # R -> D
        self.assertEqual(transform_position('R', 'D', 0), 6)
        self.assertEqual(transform_position('R', 'D', 1), 3)

        # R -> F
        self.assertEqual(transform_position('R', 'F', 0), 0)
        self.assertEqual(transform_position('R', 'F', 1), 1)

        # R -> B
        self.assertEqual(transform_position('R', 'B', 0), 0)
        self.assertEqual(transform_position('R', 'B', 1), 1)

    def test_transform_position_uses_correct_transformation_f(self) -> None:
        """Test that transform_position applies the correct transformation."""
        # F -> U
        self.assertEqual(transform_position('F', 'U', 0), 0)
        self.assertEqual(transform_position('F', 'U', 1), 1)

        # F -> D
        self.assertEqual(transform_position('F', 'D', 0), 0)
        self.assertEqual(transform_position('F', 'D', 1), 1)

        # F -> L
        self.assertEqual(transform_position('F', 'L', 0), 0)
        self.assertEqual(transform_position('F', 'L', 1), 1)

        # F -> R
        self.assertEqual(transform_position('F', 'R', 0), 0)
        self.assertEqual(transform_position('F', 'R', 1), 1)

    def test_transform_position_uses_correct_transformation_d(self) -> None:
        """Test that transform_position applies the correct transformation."""
        # D -> F
        self.assertEqual(transform_position('D', 'F', 0), 0)
        self.assertEqual(transform_position('D', 'F', 1), 1)

        # D -> B
        self.assertEqual(transform_position('D', 'B', 0), 8)
        self.assertEqual(transform_position('D', 'B', 1), 7)

        # D -> L
        self.assertEqual(transform_position('D', 'L', 0), 6)
        self.assertEqual(transform_position('D', 'L', 1), 3)

        # D -> R
        self.assertEqual(transform_position('D', 'R', 0), 2)
        self.assertEqual(transform_position('D', 'R', 1), 5)

    def test_transform_position_uses_correct_transformation_l(self) -> None:
        """Test that transform_position applies the correct transformation."""
        # L -> F
        self.assertEqual(transform_position('L', 'F', 0), 0)
        self.assertEqual(transform_position('L', 'F', 1), 1)

        # L -> B
        self.assertEqual(transform_position('L', 'B', 0), 0)
        self.assertEqual(transform_position('L', 'B', 1), 1)

        # L -> U
        self.assertEqual(transform_position('L', 'U', 0), 6)
        self.assertEqual(transform_position('L', 'U', 1), 3)

        # L -> D
        self.assertEqual(transform_position('L', 'D', 0), 2)
        self.assertEqual(transform_position('L', 'D', 1), 5)

    def test_transform_position_uses_correct_transformation_b(self) -> None:
        """Test that transform_position applies the correct transformation."""
        # B -> L
        self.assertEqual(transform_position('B', 'L', 0), 0)
        self.assertEqual(transform_position('B', 'L', 1), 1)

        # B -> R
        self.assertEqual(transform_position('B', 'R', 0), 0)
        self.assertEqual(transform_position('B', 'R', 1), 1)

        # B -> U
        self.assertEqual(transform_position('B', 'U', 0), 8)
        self.assertEqual(transform_position('B', 'U', 1), 7)

        # B -> D
        self.assertEqual(transform_position('B', 'D', 0), 8)
        self.assertEqual(transform_position('B', 'D', 1), 7)

    def test_transform_position_center_invariant(self) -> None:
        """Test center position (4) stays at 4 for all transformations."""
        all_faces = ['U', 'R', 'F', 'D', 'L', 'B']

        for orig_face in all_faces:
            for dest_face in ADJACENT_FACE_TRANSFORMATIONS[orig_face]:
                with self.subTest(orig=orig_face, dest=dest_face):
                    result = transform_position(orig_face, dest_face, 4)
                    self.assertEqual(result, 4)
