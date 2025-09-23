import unittest

from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OFFSET_ORIENTATION_MAP
from cubing_algs.exceptions import InvalidFaceError
from cubing_algs.vcube import VCube


class TestVCubeComputeOrientationMoves(unittest.TestCase):
    """
    Comprehensive tests for VCube.compute_orientation_moves method.

    Tests the orientation computation functionality through various scenarios:
    - Apply moves, rotate, check orientation computation
    - Move, rotate, check again
    - Verify correct orientation moves are computed
    """

    def setUp(self):
        """Set up test fixtures for each test method."""
        self.cube = VCube()

    def test_compute_orientation_moves_solved_cube_all_faces(self) -> None:
        """Test orientation computation on solved cube for all single faces."""
        expected_orientations = {
            'U': '',
            'R': "z'",
            'F': 'x',
            'D': 'z2',
            'L': 'z',
            'B': "x'",
        }

        for face, expected_moves in expected_orientations.items():
            with self.subTest(face=face):
                result = self.cube.compute_orientation_moves(face)
                self.assertEqual(result, expected_moves)

    def test_compute_orientation_moves_solved_cube_face_combinations(
        self,
    ) -> None:
        """Test orientation computation on solved cube for face combinations."""
        test_cases = [
            ('UF', ''),
            ('UR', 'y'),
            ('UL', "y'"),
            ('UB', 'y2'),
            ('DF', 'z2'),
            ('DR', 'y z2'),
            ('DL', "y' z2"),
            ('DB', 'x2'),
            ('FU', "x' z2"),
            ('FD', 'x'),
            ('FR', 'x y'),
            ('FL', "x y'"),
            ('BU', "x'"),
            ('BD', "x' y2"),
            ('BR', "x' y"),
            ('BL', "x' y'"),
            ('RU', "x' z'"),
            ('RD', "z' y"),
            ('RF', "z'"),
            ('RB', "z' y2"),
            ('LU', 'z y'),
            ('LD', "z y'"),
            ('LF', 'z'),
            ('LB', 'z y2'),
        ]

        for faces, expected_moves in test_cases:
            with self.subTest(faces=faces):
                result = self.cube.compute_orientation_moves(faces)
                self.assertEqual(result, expected_moves)

    def test_compute_orientation_moves_after_basic_moves(self) -> None:
        """Test orientation computation after applying basic moves."""
        # Test case: Apply R move, then compute orientations
        self.cube.rotate('R')

        # After R move, the cube is rotated but centers are in same position
        self.assertEqual(self.cube.compute_orientation_moves('U'), '')
        self.assertEqual(self.cube.compute_orientation_moves('F'), 'x')
        self.assertEqual(self.cube.compute_orientation_moves('R'), "z'")

        # Test with face combinations
        self.assertEqual(self.cube.compute_orientation_moves('UF'), '')
        self.assertEqual(self.cube.compute_orientation_moves('RF'), "z'")

    def test_compute_orientation_moves_after_rotation_sequence(self) -> None:
        """Test orientation computation after cube rotations."""
        # Apply x rotation (cube rotated around x-axis)
        self.cube.rotate('x')

        # After x rotation: U->F, F->D, D->B, B->U
        # Check that orientation moves correctly account
        # for new center positions
        self.assertEqual(self.cube.compute_orientation_moves('U'), "x'")
        self.assertEqual(self.cube.compute_orientation_moves('F'), '')
        self.assertEqual(self.cube.compute_orientation_moves('D'), 'x')
        self.assertEqual(self.cube.compute_orientation_moves('B'), 'z2')

    def test_compute_orientation_moves_complex_rotation_sequence(self) -> None:
        """Test orientation computation after complex rotation sequence."""
        # Apply y x z sequence
        self.cube.rotate('y x z')

        # Verify orientation computation works correctly
        result_u = self.cube.compute_orientation_moves('U')
        result_f = self.cube.compute_orientation_moves('F')

        # Results should be valid orientation strings from the map
        self.assertEqual(result_u, "x'")
        self.assertEqual(result_f, '')

    def test_compute_orientation_moves_after_moves_and_rotation(self) -> None:
        """Test pattern: apply moves, rotate, check, move, rotate, check."""
        # Step 1: Apply some moves
        self.cube.rotate("R U R'")

        # Compute initial orientation
        initial_orientation_u = self.cube.compute_orientation_moves('U')
        initial_orientation_f = self.cube.compute_orientation_moves('F')

        # Step 2: Apply rotation
        self.cube.rotate('y')

        # Step 3: Check orientation computation after rotation
        rotated_orientation_u = self.cube.compute_orientation_moves('U')
        rotated_orientation_f = self.cube.compute_orientation_moves('F')

        # Orientations should be different after rotation
        # (unless the rotation doesn't affect the specific face centers)

        # Step 4: Apply more moves
        self.cube.rotate("F D F'")

        # Step 5: Apply another rotation
        self.cube.rotate('z')

        # Step 6: Final check - should still compute valid orientations
        final_orientation_u = self.cube.compute_orientation_moves('U')
        final_orientation_f = self.cube.compute_orientation_moves('F')

        # All computed orientations should be valid
        self.assertEqual(initial_orientation_u, '')
        self.assertEqual(initial_orientation_f, 'x')
        self.assertEqual(rotated_orientation_u, '')
        self.assertEqual(rotated_orientation_f, 'z')
        self.assertEqual(final_orientation_u, "z'")
        self.assertEqual(final_orientation_f, '')

    def test_compute_orientation_moves_scrambled_cube(self) -> None:
        """Test orientation computation on a well-scrambled cube."""
        scramble = "R U2 R' D' R U' R' D R' U R U' R' U R U2 R' U' R U' R'"
        self.cube.rotate(scramble)

        # Test all single face orientations
        for face in FACE_ORDER:
            with self.subTest(face=face):
                result = self.cube.compute_orientation_moves(face)
                self.assertIn(result, OFFSET_ORIENTATION_MAP.values())

        # Test some face combinations
        face_combinations = ['UF', 'DR', 'LB', 'RF', 'DL', 'BU']
        for faces in face_combinations:
            with self.subTest(faces=faces):
                result = self.cube.compute_orientation_moves(faces)
                self.assertIn(result, OFFSET_ORIENTATION_MAP.values())

    def test_compute_orientation_moves_verification_with_oriented_copy(
        self,
    ) -> None:
        """
        Verify that compute_orientation_moves works correctly
        with oriented_copy.
        """
        # Apply some moves to scramble the cube
        self.cube.rotate("R U R' U' R' F R2 U' R' U' R U R' F'")

        test_orientations = ['UF', 'DR', 'LB', 'RF']

        for orientation in test_orientations:
            with self.subTest(orientation=orientation):
                # Get the computed orientation moves
                self.cube.compute_orientation_moves(orientation)

                # Create an oriented copy using these moves
                oriented_cube = self.cube.oriented_copy(orientation)

                # The oriented cube should have the specified faces
                # in correct positions
                if len(orientation) == 2:
                    # Check top face (first character)
                    self.assertEqual(oriented_cube.state[4], orientation[0])
                    # Check front face (second character)
                    self.assertEqual(oriented_cube.state[22], orientation[1])
                else:
                    # Single face orientation
                    self.assertEqual(oriented_cube.state[4], orientation[0])

    def test_compute_orientation_moves_consistency_after_operations(
        self,
    ) -> None:
        """
        Test that orientation computation remains consistent
        after multiple operations.
        """
        # Perform a sequence of moves and rotations
        operations = [
            "R U R'",
            'y',
            "F D F'",
            'x',
            "L U' L'",
            "z'",
            "R F R' F'",
        ]

        orientations_history = []

        for operation in operations:
            self.cube.rotate(operation)
            # Record orientation for 'UF' after each operation
            orientation = self.cube.compute_orientation_moves('UF')
            orientations_history.append(orientation)

            # Verify it's a valid orientation
            self.assertIn(orientation, OFFSET_ORIENTATION_MAP.values())

        # All recorded orientations should be valid
        self.assertEqual(len(orientations_history), len(operations))
        for orientation in orientations_history:
            self.assertIn(orientation, OFFSET_ORIENTATION_MAP.values())

    def test_compute_orientation_moves_all_offset_map_values(self) -> None:
        """Test that all values in OFFSET_ORIENTATION_MAP can be produced."""
        # This test verifies completeness of the orientation system
        found_orientations = set()

        # Test with solved cube in various orientations
        test_rotations = [
            '',  # identity
            'x', 'x2', "x'",
            'y', 'y2', "y'",
            'z', 'z2', "z'",
            'x y', 'x z', 'y z',
            "x' y", "x' z", "y' z",
            'x y z', "x' y' z'",
            'x2 y', 'x y2', 'y z2',
        ]

        for rotation in test_rotations:
            cube = VCube()
            if rotation:
                cube.rotate(rotation)

            for face in FACE_ORDER:
                orientation = cube.compute_orientation_moves(face)
                found_orientations.add(orientation)

            # Test some two-face combinations
            for face1 in ['U', 'D', 'F', 'B']:
                for face2 in ['F', 'R', 'L', 'B']:
                    if face1 != face2 and face1 + face2 not in {
                            'FB', 'BF', 'UD', 'DU',
                    }:
                        orientation = cube.compute_orientation_moves(
                            face1 + face2,
                        )
                        found_orientations.add(orientation)

        # We should have found a good portion of the possible orientations
        expected_orientations = set(OFFSET_ORIENTATION_MAP.values())
        coverage = len(found_orientations.intersection(expected_orientations))

        # We should find at least 80% of the possible orientations
        self.assertGreater(coverage / len(expected_orientations), 0.8)

    def test_compute_orientation_moves_edge_cases(self) -> None:
        """Test edge cases for compute_orientation_moves."""
        # Test empty string (should raise InvalidFaceError)
        with self.assertRaises(InvalidFaceError):
            self.cube.compute_orientation_moves('')

        # Test too many faces (should raise InvalidFaceError)
        with self.assertRaises(InvalidFaceError):
            self.cube.compute_orientation_moves('URF')

        # Test invalid face character (should raise InvalidFaceError)
        with self.assertRaises(InvalidFaceError):
            self.cube.compute_orientation_moves('UT')

        # Test opposite faces (should raise InvalidFaceError)
        with self.assertRaises(InvalidFaceError):
            self.cube.compute_orientation_moves('UD')

        with self.assertRaises(InvalidFaceError):
            self.cube.compute_orientation_moves('DU')

        with self.assertRaises(InvalidFaceError):
            self.cube.compute_orientation_moves('FB')

        with self.assertRaises(InvalidFaceError):
            self.cube.compute_orientation_moves('LR')

    def test_compute_orientation_moves_state_preservation(self) -> None:
        """Test that compute_orientation_moves doesn't modify cube state."""
        # Apply some moves to create a non-trivial state
        initial_moves = "R U2 R' D' R U' R' D"
        self.cube.rotate(initial_moves)
        initial_state = self.cube.state
        initial_history_length = len(self.cube.history)

        # Compute orientations for various faces
        test_faces = ['U', 'F', 'R', 'UF', 'DR', 'LB']

        for faces in test_faces:
            with self.subTest(faces=faces):
                # Compute orientation
                orientation_moves = self.cube.compute_orientation_moves(faces)

                # Verify state is unchanged
                self.assertEqual(self.cube.state, initial_state)
                self.assertEqual(len(self.cube.history), initial_history_length)

                # Verify result is valid
                self.assertIn(
                    orientation_moves,
                    OFFSET_ORIENTATION_MAP.values(),
                )

    def test_compute_orientation_moves_with_slice_moves(self) -> None:
        """Test orientation computation after slice moves."""
        # Apply slice moves
        self.cube.rotate('M E S')
        orientation_after_slice = self.cube.compute_orientation_moves('UF')
        self.assertEqual(orientation_after_slice, "y' z2")

        # Apply combination of slice and regular moves
        self.cube.rotate("M U2 S E'")
        final_orientation = self.cube.compute_orientation_moves('DR')
        self.assertEqual(final_orientation, 'z')

        # Test with more complex slice move sequences
        self.cube = VCube()  # Reset cube
        self.cube.rotate("M' S2 E M")
        slice_orientation = self.cube.compute_orientation_moves('UB')
        self.assertEqual(slice_orientation, 'z')

    def test_compute_orientation_moves_complex_algorithm_sequence(self) -> None:
        """Test orientation computation through a complex algorithm sequence."""
        # Simulate PLL algorithm (T-perm)
        t_perm = "R U R' F' R U R' U' R' F R2 U' R'"

        # Apply T-perm multiple times and check orientations
        for i in range(1, 4):  # Apply 1, 2, 3 times
            cube = VCube()
            for _ in range(i):
                cube.rotate(t_perm)

            with self.subTest(iterations=i):
                # Test multiple orientations
                for faces in ['U', 'UF', 'UR', 'DR']:
                    orientation = cube.compute_orientation_moves(faces)
                    self.assertIn(orientation, OFFSET_ORIENTATION_MAP.values())

        # Apply T-perm 3 times should return to solved (with AUF)
        cube = VCube()
        for _ in range(3):
            cube.rotate(t_perm)

        # Should still compute valid orientations
        orientation_u = cube.compute_orientation_moves('U')
        orientation_uf = cube.compute_orientation_moves('UF')

        self.assertEqual(orientation_u, '')
        self.assertEqual(orientation_uf, '')


class TestVCubeComputeOrientationMovesIntegration(unittest.TestCase):
    """Integration tests focusing on interaction with other VCube methods."""

    def setUp(self):
        """Set up test fixtures for each test method."""
        self.cube = VCube()

    def test_integration_with_get_face_center_indexes(self) -> None:
        """
        Test that compute_orientation_moves
        correctly uses face center information.
        """
        # Apply rotations that change center positions
        self.cube.rotate('x y z')

        # Get current center positions
        centers = self.cube.get_face_center_indexes()

        # Compute orientations - should be consistent
        # with actual center positions
        for i, center_color in enumerate(centers):
            if i == 0:  # U face position
                orientation = self.cube.compute_orientation_moves(center_color)
                # If this center color is at U position,
                # orienting to it should be empty or simple
                self.assertIn(orientation, OFFSET_ORIENTATION_MAP.values())

    def test_integration_with_get_face_index(self) -> None:
        """Test integration with get_face_index method."""
        # Apply some rotations
        self.cube.rotate('y2 x')

        # For each face color, verify orientation computation
        for face_color in FACE_ORDER:
            self.cube.get_face_index(face_color)

            # The face index should be consistent with orientation computation
            orientation = self.cube.compute_orientation_moves(face_color)
            self.assertIn(orientation, OFFSET_ORIENTATION_MAP.values())

            # Verify that the orientation moves would correctly position
            # this face
            test_cube = self.cube.copy()
            if orientation:
                test_cube.rotate(orientation)

            # After applying orientation moves,
            # the face should be at U position (index 0)
            new_face_index = test_cube.get_face_index(face_color)
            self.assertEqual(new_face_index, 0)

    def test_integration_with_oriented_copy_consistency(self) -> None:
        """
        Test consistency between compute_orientation_moves and oriented_copy.
        """
        scramble = "F R U' R' U' R U R' F' R U R' U' R' F R F'"
        self.cube.rotate(scramble)

        orientations_to_test = ['U', 'D', 'F', 'B', 'UF', 'DR', 'BL']

        for orientation in orientations_to_test:
            with self.subTest(orientation=orientation):
                # Get computed orientation moves
                computed_moves = self.cube.compute_orientation_moves(
                    orientation,
                )

                # Create oriented copy
                oriented_cube = self.cube.oriented_copy(orientation)

                # Apply the computed moves manually to a copy
                manual_cube = self.cube.copy()
                if computed_moves:
                    manual_cube.rotate(computed_moves)

                # Both should result in the same state
                self.assertEqual(oriented_cube.state, manual_cube.state)

    def test_integration_preserve_cube_validity(self) -> None:
        """Test that orientation computation preserves cube validity."""
        # Start with a valid but scrambled cube
        scramble = "R U R' U' R' F R2 U' R' U' R U R' F'"
        self.cube.rotate(scramble)

        # Verify initial validity
        self.assertTrue(self.cube.check_integrity())

        # Compute orientations (shouldn't modify cube)
        orientations = ['U', 'F', 'R', 'UF', 'UR', 'FR']

        for orientation in orientations:
            with self.subTest(orientation=orientation):
                self.cube.compute_orientation_moves(orientation)

                # Cube should still be valid
                self.assertTrue(self.cube.check_integrity())

                # Create oriented copy and verify it's also valid
                oriented_cube = self.cube.oriented_copy(orientation)
                self.assertTrue(oriented_cube.check_integrity())
