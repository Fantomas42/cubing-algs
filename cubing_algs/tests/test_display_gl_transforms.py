"""Tests for the linear algebra of the GPU rendering backend."""
import math
import struct
import unittest

from cubing_algs.display.gl.transforms import AXIS_X
from cubing_algs.display.gl.transforms import AXIS_Y
from cubing_algs.display.gl.transforms import AXIS_Z
from cubing_algs.display.gl.transforms import IDENTITY
from cubing_algs.display.gl.transforms import ORIGIN
from cubing_algs.display.gl.transforms import Euler
from cubing_algs.display.gl.transforms import Mat4
from cubing_algs.display.gl.transforms import OrientationTracker
from cubing_algs.display.gl.transforms import Quat
from cubing_algs.display.gl.transforms import Vec3

PLACES = 9


class VectorTestCase(unittest.TestCase):
    """Assertions on vectors and matrices."""

    def assert_vec3(
            self,
            actual: Vec3,
            expected: tuple[float, float, float],
    ) -> None:
        """Assert that a vector matches an expected triplet."""
        for index, (got, want) in enumerate(zip(actual, expected, strict=True)):
            with self.subTest(component='xyz'[index]):
                self.assertAlmostEqual(got, want, places=PLACES)

    def assert_quat(self, actual: Quat, expected: Quat) -> None:
        """Assert that two quaternions describe the same rotation."""
        # A quaternion and its opposite are the same rotation.
        if actual.w * expected.w < 0:
            actual = Quat(*(-value for value in actual))

        for index, (got, want) in enumerate(zip(actual, expected, strict=True)):
            with self.subTest(component='wxyz'[index]):
                self.assertAlmostEqual(got, want, places=PLACES)

    def assert_mat4(self, actual: Mat4, expected: Mat4) -> None:
        """Assert that two matrices are equal, coefficient by coefficient."""
        for index, (got, want) in enumerate(
                zip(actual.values, expected.values, strict=True),
        ):
            with self.subTest(coefficient=index):
                self.assertAlmostEqual(got, want, places=PLACES)


class TestVec3(VectorTestCase):
    """Tests for the Vec3 class."""

    def test_add(self) -> None:
        """Test that vectors add component wise."""
        self.assert_vec3(
            Vec3(1.0, 2.0, 3.0) + Vec3(0.5, -1.0, 2.0),
            (1.5, 1.0, 5.0),
        )

    def test_sub(self) -> None:
        """Test that vectors subtract component wise."""
        self.assert_vec3(
            Vec3(1.0, 2.0, 3.0) - Vec3(0.5, -1.0, 2.0),
            (0.5, 3.0, 1.0),
        )

    def test_neg(self) -> None:
        """Test that a negated vector points the other way."""
        self.assert_vec3(-Vec3(1.0, -2.0, 3.0), (-1.0, 2.0, -3.0))

    def test_scaled(self) -> None:
        """Test that scaling multiplies every component."""
        self.assert_vec3(Vec3(1.0, -2.0, 3.0).scaled(2.0), (2.0, -4.0, 6.0))

    def test_dot(self) -> None:
        """Test the dot product of two vectors."""
        self.assertAlmostEqual(
            Vec3(1.0, 2.0, 3.0).dot(Vec3(4.0, -5.0, 6.0)),
            12.0,
            places=PLACES,
        )

    def test_dot_orthogonal(self) -> None:
        """Test that orthogonal vectors have a null dot product."""
        self.assertAlmostEqual(AXIS_X.dot(AXIS_Y), 0.0, places=PLACES)

    def test_cross_follows_right_hand_rule(self) -> None:
        """Test that the cross product follows the right hand rule."""
        self.assert_vec3(AXIS_X.cross(AXIS_Y), AXIS_Z)
        self.assert_vec3(AXIS_Y.cross(AXIS_Z), AXIS_X)
        self.assert_vec3(AXIS_Z.cross(AXIS_X), AXIS_Y)

    def test_cross_anticommutative(self) -> None:
        """Test that swapping the operands reverses the cross product."""
        self.assert_vec3(AXIS_Y.cross(AXIS_X), -AXIS_Z)

    def test_length(self) -> None:
        """Test the euclidean length of a vector."""
        self.assertAlmostEqual(
            Vec3(3.0, 4.0, 0.0).length(),
            5.0,
            places=PLACES,
        )

    def test_normalized(self) -> None:
        """Test that a normalized vector keeps its direction."""
        normalized = Vec3(0.0, 0.0, -4.0).normalized()

        self.assert_vec3(normalized, (0.0, 0.0, -1.0))
        self.assertAlmostEqual(normalized.length(), 1.0, places=PLACES)

    def test_normalized_null_vector(self) -> None:
        """Test that a null vector normalizes to itself."""
        self.assert_vec3(ORIGIN.normalized(), ORIGIN)


class TestQuat(VectorTestCase):
    """Tests for the Quat class."""

    def test_identity(self) -> None:
        """Test that the identity quaternion rotates nothing."""
        self.assert_vec3(Quat.identity().rotate(Vec3(1.0, 2.0, 3.0)),
                         (1.0, 2.0, 3.0))

    def test_from_axis_angle(self) -> None:
        """Test a quarter turn built from an axis and an angle."""
        self.assert_quat(
            Quat.from_axis_angle(AXIS_Y, math.pi / 2),
            Quat(math.sqrt(2) / 2, 0.0, math.sqrt(2) / 2, 0.0),
        )

    def test_from_axis_angle_normalizes_axis(self) -> None:
        """Test that the axis does not need to be a unit vector."""
        self.assert_quat(
            Quat.from_axis_angle(Vec3(0.0, 5.0, 0.0), math.pi / 2),
            Quat.from_axis_angle(AXIS_Y, math.pi / 2),
        )

    def test_from_axis_angle_null_axis(self) -> None:
        """Test that a null axis gives the identity."""
        self.assert_quat(
            Quat.from_axis_angle(ORIGIN, math.pi / 3),
            Quat.identity(),
        )

    def test_rotate_around_y(self) -> None:
        """Test that a quarter turn around Y sends Z onto X."""
        quat = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        self.assert_vec3(quat.rotate(AXIS_Z), AXIS_X)

    def test_rotate_around_x(self) -> None:
        """Test that a quarter turn around X sends Y onto Z."""
        quat = Quat.from_axis_angle(AXIS_X, math.pi / 2)

        self.assert_vec3(quat.rotate(AXIS_Y), AXIS_Z)

    def test_multiply_applies_right_operand_first(self) -> None:
        """Test that the right operand of a product rotates first."""
        around_x = Quat.from_axis_angle(AXIS_X, math.pi / 2)
        around_y = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        combined = around_y * around_x

        self.assert_vec3(
            combined.rotate(AXIS_Y),
            around_y.rotate(around_x.rotate(AXIS_Y)),
        )

    def test_multiply_is_not_commutative(self) -> None:
        """Test that the order of two rotations matters."""
        around_x = Quat.from_axis_angle(AXIS_X, math.pi / 2)
        around_y = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        self.assertNotAlmostEqual(
            (around_y * around_x).rotate(AXIS_Z).x,
            (around_x * around_y).rotate(AXIS_Z).x,
            places=PLACES,
        )

    def test_conjugate_undoes_the_rotation(self) -> None:
        """Test that a quaternion composed with its conjugate is neutral."""
        quat = Quat.from_axis_angle(Vec3(1.0, 2.0, 3.0), 1.2)

        self.assert_quat(quat * quat.conjugate(), Quat.identity())

    def test_norm(self) -> None:
        """Test that a built quaternion is already a unit one."""
        quat = Quat.from_axis_angle(Vec3(1.0, 2.0, 3.0), 1.2)

        self.assertAlmostEqual(quat.norm(), 1.0, places=PLACES)

    def test_normalized(self) -> None:
        """Test that normalizing scales the quaternion to a unit norm."""
        normalized = Quat(2.0, 0.0, 0.0, 0.0).normalized()

        self.assert_quat(normalized, Quat.identity())

    def test_normalized_null_quaternion(self) -> None:
        """Test that a null quaternion normalizes to the identity."""
        self.assert_quat(Quat(0.0, 0.0, 0.0, 0.0).normalized(),
                         Quat.identity())

    def test_to_matrix(self) -> None:
        """Test that the matrix of a quaternion rotates the same way."""
        quat = Quat.from_axis_angle(Vec3(1.0, -2.0, 0.5), 0.7)
        matrix = quat.to_matrix()

        for vector in (AXIS_X, AXIS_Y, AXIS_Z, Vec3(1.0, 2.0, 3.0)):
            with self.subTest(vector=vector):
                self.assert_vec3(
                    matrix.transform_point(vector),
                    quat.rotate(vector),
                )

    def test_to_matrix_matches_rotation_y(self) -> None:
        """Test that a quaternion matrix matches the built in one."""
        self.assert_mat4(
            Quat.from_axis_angle(AXIS_Y, 0.4).to_matrix(),
            Mat4.rotation_y(0.4),
        )


class TestQuatSlerp(VectorTestCase):
    """Tests for Quat.dot and Quat.slerp."""

    def test_dot_of_identical_rotations(self) -> None:
        """Test that a quaternion dotted with itself gives one."""
        quat = Quat.from_axis_angle(Vec3(1.0, 2.0, 3.0), 1.2)

        self.assertAlmostEqual(quat.dot(quat), 1.0, places=PLACES)

    def test_dot_of_opposite_rotations(self) -> None:
        """Test that the two writings of a rotation dot to minus one."""
        quat = Quat.from_axis_angle(Vec3(1.0, 2.0, 3.0), 1.2)
        opposite = Quat(*(-value for value in quat))

        self.assertAlmostEqual(quat.dot(opposite), -1.0, places=PLACES)

    def test_slerp_at_zero_is_the_start(self) -> None:
        """Test that a slerp at t = 0 changes nothing."""
        start = Quat.from_axis_angle(AXIS_Y, 0.3)
        end = Quat.from_axis_angle(AXIS_Y, 1.5)

        self.assert_quat(start.slerp(end, 0.0), start)

    def test_slerp_at_one_is_the_end(self) -> None:
        """Test that a slerp at t = 1 lands exactly on the target."""
        start = Quat.from_axis_angle(AXIS_Y, 0.3)
        end = Quat.from_axis_angle(AXIS_Y, 1.5)

        self.assert_quat(start.slerp(end, 1.0), end)

    def test_slerp_at_the_midpoint(self) -> None:
        """Test that halfway between two turns around Y is their average."""
        start = Quat.from_axis_angle(AXIS_Y, 0.3)
        end = Quat.from_axis_angle(AXIS_Y, 1.5)

        self.assert_quat(
            start.slerp(end, 0.5),
            Quat.from_axis_angle(AXIS_Y, 0.9),
        )

    def test_slerp_stays_a_unit_quaternion(self) -> None:
        """Test that an interpolated rotation is never left unnormalized."""
        start = Quat.from_axis_angle(Vec3(1.0, 0.0, 0.0), 0.1)
        end = Quat.from_axis_angle(Vec3(0.0, 1.0, 1.0), 2.0)

        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            with self.subTest(t=t):
                self.assertAlmostEqual(
                    start.slerp(end, t).norm(), 1.0, places=PLACES,
                )

    def test_slerp_takes_the_shorter_arc(self) -> None:
        """Test that a slerp never crosses the sphere the long way round."""
        start = Quat.from_axis_angle(AXIS_Y, 0.1)
        end = Quat(*(-value for value in Quat.from_axis_angle(AXIS_Y, 0.2)))

        self.assert_quat(
            start.slerp(end, 0.5),
            Quat.from_axis_angle(AXIS_Y, 0.15),
        )

    def test_slerp_of_nearly_identical_rotations(self) -> None:
        """Test the linear fallback used when the arc is almost null."""
        start = Quat.from_axis_angle(AXIS_Y, 0.4)
        end = Quat.from_axis_angle(AXIS_Y, 0.4 + 1e-9)

        midpoint = start.slerp(end, 0.5)

        self.assertAlmostEqual(midpoint.norm(), 1.0, places=PLACES)
        self.assertLess(1.0 - abs(midpoint.dot(start)), 1e-8)


class TestEuler(VectorTestCase):
    """Tests for the Euler class and its extraction."""

    def test_from_degrees(self) -> None:
        """Test that degrees are converted to radians."""
        euler = Euler.from_degrees(90.0, -45.0, 180.0)

        self.assertAlmostEqual(euler.yaw, math.pi / 2, places=PLACES)
        self.assertAlmostEqual(euler.pitch, -math.pi / 4, places=PLACES)
        self.assertAlmostEqual(euler.roll, math.pi, places=PLACES)

    def test_degrees(self) -> None:
        """Test that angles are converted back to degrees."""
        yaw, pitch, roll = Euler.from_degrees(90.0, -45.0, 180.0).degrees()

        self.assertAlmostEqual(yaw, 90.0, places=PLACES)
        self.assertAlmostEqual(pitch, -45.0, places=PLACES)
        self.assertAlmostEqual(roll, 180.0, places=PLACES)

    def test_from_euler_composition_order(self) -> None:
        """Test that the angles compose as yaw, then pitch, then roll."""
        euler = Euler(0.3, -0.7, 1.1)

        self.assert_quat(
            Quat.from_euler(euler),
            Quat.from_axis_angle(AXIS_Y, euler.yaw)
            * Quat.from_axis_angle(AXIS_X, euler.pitch)
            * Quat.from_axis_angle(AXIS_Z, euler.roll),
        )

    def test_round_trip(self) -> None:
        """Test that extracting the angles of a rotation rebuilds it."""
        for euler in (
                Euler(0.0, 0.0, 0.0),
                Euler(0.3, -0.7, 1.1),
                Euler(-2.5, 0.2, -0.4),
                Euler(math.pi / 4, -math.pi / 3, math.pi / 6),
        ):
            with self.subTest(euler=euler):
                extracted = Quat.from_euler(euler).to_euler()

                self.assert_quat(
                    Quat.from_euler(extracted),
                    Quat.from_euler(euler),
                )

    def test_round_trip_keeps_the_angles(self) -> None:
        """Test that the extracted angles are the ones asked for."""
        euler = Euler(0.3, -0.7, 1.1)
        extracted = Quat.from_euler(euler).to_euler()

        self.assertAlmostEqual(extracted.yaw, euler.yaw, places=PLACES)
        self.assertAlmostEqual(extracted.pitch, euler.pitch, places=PLACES)
        self.assertAlmostEqual(extracted.roll, euler.roll, places=PLACES)

    def test_gimbal_lock_up(self) -> None:
        """Test that looking straight up reports no roll."""
        extracted = Quat.from_axis_angle(AXIS_X, math.pi / 2).to_euler()

        self.assertAlmostEqual(extracted.pitch, math.pi / 2, places=PLACES)
        self.assertEqual(extracted.roll, 0.0)

    def test_gimbal_lock_down(self) -> None:
        """Test that looking straight down reports no roll."""
        extracted = Quat.from_axis_angle(AXIS_X, -math.pi / 2).to_euler()

        self.assertAlmostEqual(extracted.pitch, -math.pi / 2, places=PLACES)
        self.assertEqual(extracted.roll, 0.0)

    def test_gimbal_lock_merges_yaw_and_roll(self) -> None:
        """Test that a locked rotation is still rebuilt exactly."""
        euler = Euler(0.4, math.pi / 2, 0.9)
        extracted = Quat.from_euler(euler).to_euler()

        self.assertEqual(extracted.roll, 0.0)
        self.assert_quat(Quat.from_euler(extracted), Quat.from_euler(euler))


class TestMat4(VectorTestCase):
    """Tests for the Mat4 class."""

    def test_rejects_a_wrong_size(self) -> None:
        """Test that a matrix must hold sixteen coefficients."""
        with self.assertRaises(ValueError):
            Mat4((1.0, 0.0, 0.0))

    def test_stored_column_major(self) -> None:
        """Test that the coefficients are stored column after column."""
        matrix = Mat4.translation(Vec3(1.0, 2.0, 3.0))

        self.assertEqual(matrix.values[12:], (1.0, 2.0, 3.0, 1.0))

    def test_from_rows_and_rows(self) -> None:
        """Test that the rows survive a round trip."""
        rows = (
            (1.0, 2.0, 3.0, 4.0),
            (5.0, 6.0, 7.0, 8.0),
            (9.0, 10.0, 11.0, 12.0),
            (13.0, 14.0, 15.0, 16.0),
        )

        self.assertEqual(Mat4.from_rows(rows).rows(), rows)

    def test_identity(self) -> None:
        """Test that the identity leaves a point alone."""
        self.assert_vec3(
            Mat4.identity().transform_point(Vec3(1.0, 2.0, 3.0)),
            (1.0, 2.0, 3.0),
        )

    def test_translation(self) -> None:
        """Test that a translation moves a point."""
        matrix = Mat4.translation(Vec3(1.0, -2.0, 3.0))

        self.assert_vec3(
            matrix.transform_point(Vec3(1.0, 1.0, 1.0)),
            (2.0, -1.0, 4.0),
        )

    def test_translation_leaves_directions_alone(self) -> None:
        """Test that a direction is not moved by a translation."""
        matrix = Mat4.translation(Vec3(1.0, -2.0, 3.0))

        self.assert_vec3(matrix.transform_direction(AXIS_X), AXIS_X)

    def test_rotation_x(self) -> None:
        """Test that a quarter turn around X sends Y onto Z."""
        self.assert_vec3(
            Mat4.rotation_x(math.pi / 2).transform_point(AXIS_Y),
            AXIS_Z,
        )

    def test_rotation_y(self) -> None:
        """Test that a quarter turn around Y sends Z onto X."""
        self.assert_vec3(
            Mat4.rotation_y(math.pi / 2).transform_point(AXIS_Z),
            AXIS_X,
        )

    def test_rotation_z(self) -> None:
        """Test that a quarter turn around Z sends X onto Y."""
        self.assert_vec3(
            Mat4.rotation_z(math.pi / 2).transform_point(AXIS_X),
            AXIS_Y,
        )

    def test_matmul_applies_right_operand_first(self) -> None:
        """Test that the right operand of a product applies first."""
        rotation = Mat4.rotation_z(math.pi / 2)
        translation = Mat4.translation(Vec3(1.0, 0.0, 0.0))

        # Translate, then rotate: the offset is rotated too.
        self.assert_vec3(
            (rotation @ translation).transform_point(ORIGIN),
            (0.0, 1.0, 0.0),
        )
        # Rotate, then translate: the offset stays on X.
        self.assert_vec3(
            (translation @ rotation).transform_point(ORIGIN),
            (1.0, 0.0, 0.0),
        )

    def test_matmul_with_identity(self) -> None:
        """Test that multiplying by the identity changes nothing."""
        matrix = Mat4.rotation_y(0.6) @ Mat4.translation(Vec3(1.0, 2.0, 3.0))

        self.assert_mat4(matrix @ Mat4.identity(), matrix)
        self.assert_mat4(Mat4.identity() @ matrix, matrix)

    def test_transposed(self) -> None:
        """Test that transposing swaps rows and columns."""
        matrix = Mat4.translation(Vec3(1.0, 2.0, 3.0))

        self.assertEqual(
            matrix.transposed().rows()[3],
            (1.0, 2.0, 3.0, 1.0),
        )

    def test_transposed_twice(self) -> None:
        """Test that transposing twice gives the matrix back."""
        matrix = Mat4.rotation_x(0.3) @ Mat4.translation(Vec3(1.0, 2.0, 3.0))

        self.assert_mat4(matrix.transposed().transposed(), matrix)

    def test_transposed_rotation_is_its_inverse(self) -> None:
        """Test that a rotation matrix is orthogonal."""
        rotation = Mat4.rotation_y(0.7) @ Mat4.rotation_x(-0.2)

        self.assert_mat4(rotation @ rotation.transposed(), Mat4.identity())


class TestMat4Camera(VectorTestCase):
    """Tests for the view and projection matrices."""

    def test_look_at_puts_the_target_ahead(self) -> None:
        """Test that the target lands on the line of sight."""
        view = Mat4.look_at(Vec3(4.0, 0.0, 0.0), ORIGIN, AXIS_Y)

        # The camera looks down its own -Z, at its own distance.
        self.assert_vec3(view.transform_point(ORIGIN), (0.0, 0.0, -4.0))

    def test_look_at_puts_the_eye_at_the_origin(self) -> None:
        """Test that the camera stands at the origin of its own space."""
        eye = Vec3(4.0, 3.0, -2.0)
        view = Mat4.look_at(eye, ORIGIN, AXIS_Y)

        self.assert_vec3(view.transform_point(eye), ORIGIN)

    def test_look_at_keeps_up_upward(self) -> None:
        """Test that the up direction points up in camera space."""
        view = Mat4.look_at(Vec3(4.0, 2.0, 1.0), ORIGIN, AXIS_Y)
        transformed = view.transform_direction(AXIS_Y)

        self.assertGreater(transformed.y, 0.0)
        self.assertAlmostEqual(transformed.x, 0.0, places=PLACES)

    def test_perspective_keeps_the_center(self) -> None:
        """Test that a point on the line of sight projects to the center."""
        matrix = Mat4.perspective(math.radians(60), 1.0, 0.1, 100.0)
        projected = matrix.transform_point(Vec3(0.0, 0.0, -5.0))

        self.assertAlmostEqual(projected.x, 0.0, places=PLACES)
        self.assertAlmostEqual(projected.y, 0.0, places=PLACES)

    def test_perspective_maps_the_clipping_planes(self) -> None:
        """Test that the near and far planes land on the clip space bounds."""
        matrix = Mat4.perspective(math.radians(60), 1.0, 0.1, 100.0)

        self.assertAlmostEqual(
            matrix.transform_point(Vec3(0.0, 0.0, -0.1)).z,
            -1.0,
            places=PLACES,
        )
        self.assertAlmostEqual(
            matrix.transform_point(Vec3(0.0, 0.0, -100.0)).z,
            1.0,
            places=PLACES,
        )

    def test_perspective_field_of_view(self) -> None:
        """Test that the top of the frustum lands on the top of the screen."""
        fov = math.radians(60)
        matrix = Mat4.perspective(fov, 1.0, 0.1, 100.0)
        height = 5.0 * math.tan(fov / 2)

        self.assertAlmostEqual(
            matrix.transform_point(Vec3(0.0, height, -5.0)).y,
            1.0,
            places=PLACES,
        )

    def test_perspective_aspect_ratio(self) -> None:
        """Test that a wide viewport spreads the frustum horizontally."""
        fov = math.radians(60)
        matrix = Mat4.perspective(fov, 2.0, 0.1, 100.0)
        width = 2.0 * 5.0 * math.tan(fov / 2)

        self.assertAlmostEqual(
            matrix.transform_point(Vec3(width, 0.0, -5.0)).x,
            1.0,
            places=PLACES,
        )

    def test_perspective_shrinks_with_distance(self) -> None:
        """Test that a farther point projects closer to the center."""
        matrix = Mat4.perspective(math.radians(60), 1.0, 0.1, 100.0)

        near = matrix.transform_point(Vec3(1.0, 0.0, -5.0))
        far = matrix.transform_point(Vec3(1.0, 0.0, -50.0))

        self.assertGreater(abs(near.x), abs(far.x))

    def test_transform_point_at_the_eye(self) -> None:
        """Test that a point with no depth is not divided by zero."""
        matrix = Mat4.perspective(math.radians(60), 1.0, 0.1, 100.0)
        projected = matrix.transform_point(ORIGIN)

        self.assertAlmostEqual(projected.x, 0.0, places=PLACES)
        self.assertAlmostEqual(projected.y, 0.0, places=PLACES)

    def test_pack(self) -> None:
        """Test that packing gives the column major floats of the matrix."""
        matrix = Mat4.translation(Vec3(1.0, 2.0, 3.0))
        packed = matrix.pack()

        self.assertEqual(len(packed), 64)
        self.assertEqual(struct.unpack('<16f', packed), matrix.values)


class TestOrientationTracker(VectorTestCase):
    """Tests for the OrientationTracker class."""

    def test_starts_at_the_identity(self) -> None:
        """Test that a fresh tracker holds no orientation."""
        tracker = OrientationTracker()

        self.assertIsNone(tracker.reference)
        self.assert_quat(tracker.orientation, Quat.identity())

    def test_first_quaternion_is_the_reference(self) -> None:
        """Test that the first quaternion received does not move the cube."""
        tracker = OrientationTracker()
        raw = Quat.from_axis_angle(AXIS_Y, 1.2)

        orientation = tracker.update(*raw)

        self.assert_quat(tracker.reference or Quat.identity(), raw)
        self.assert_quat(orientation, Quat.identity())

    def test_relative_to_the_reference(self) -> None:
        """Test that later quaternions are expressed relatively."""
        tracker = OrientationTracker()
        reference = Quat.from_axis_angle(AXIS_Y, 1.2)
        quarter = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        tracker.update(*reference)
        orientation = tracker.update(*(reference * quarter))

        self.assert_quat(orientation, quarter)

    def test_normalizes_the_raw_quaternion(self) -> None:
        """Test that a sensor quaternion does not need to be a unit one."""
        tracker = OrientationTracker()

        tracker.update(2.0, 0.0, 0.0, 0.0)
        orientation = tracker.update(0.0, 0.0, 4.0, 0.0)

        self.assertAlmostEqual(orientation.norm(), 1.0, places=PLACES)
        self.assert_quat(orientation, Quat(0.0, 0.0, 1.0, 0.0))

    def test_basis_swaps_the_sensor_axes(self) -> None:
        """
        Test the axis convention of the current term-timer module.

        Its sensors report a frame where Y and Z are swapped, which it
        fixes by rewriting the components as ``(w, x, z, -y)``. The same
        fix is here a basis, a quarter turn around X.
        """
        basis = Quat.from_axis_angle(AXIS_X, -math.pi / 2)
        tracker = OrientationTracker(basis=basis)
        raw = Quat.from_axis_angle(Vec3(1.0, 2.0, 3.0), 0.8)

        tracker.update(*Quat.identity())
        orientation = tracker.update(*raw)

        self.assert_quat(orientation, Quat(raw.w, raw.x, raw.z, -raw.y))

    def test_basis_holds_a_whole_feed(self) -> None:
        """
        Test a basis on a feed, not on a single quaternion.

        A basis conjugating the wrong way, or by the wrong angle, still
        looks right on some quaternions: the swap has to hold for every
        one of them, and around every axis.
        """
        basis = Quat.from_axis_angle(AXIS_X, -math.pi / 2)
        tracker = OrientationTracker(basis=basis)
        tracker.update(*Quat.identity())

        for axis in (AXIS_X, AXIS_Y, AXIS_Z, Vec3(1.0, -2.0, 0.5)):
            for angle in (0.3, math.pi / 2, 2.4, -1.1):
                with self.subTest(axis=axis, angle=angle):
                    raw = Quat.from_axis_angle(axis, angle)

                    self.assert_quat(
                        tracker.update(*raw),
                        Quat(raw.w, raw.x, raw.z, -raw.y),
                    )

    def test_update_alone_does_not_move_the_orientation(self) -> None:
        """Test that a raw quaternion only moves the target, not the display."""
        tracker = OrientationTracker()
        tracker.update(*Quat.identity())

        tracker.update(*Quat.from_axis_angle(AXIS_Y, math.pi / 2))

        self.assert_quat(tracker.orientation, Quat.identity())

    def test_advance_moves_the_orientation_towards_the_target(self) -> None:
        """Test that advancing slides the display a little closer."""
        tracker = OrientationTracker()
        tracker.update(*Quat.identity())
        tracker.update(*Quat.from_axis_angle(AXIS_Y, math.pi / 2))

        tracker.advance(0.01)

        self.assertNotEqual(tracker.orientation, Quat.identity())
        self.assertNotAlmostEqual(
            tracker.orientation.dot(tracker.target), 1.0, places=PLACES,
        )

    def test_advance_settles_on_the_target(self) -> None:
        """Test that enough elapsed time lands exactly on the target."""
        tracker = OrientationTracker()
        tracker.update(*Quat.identity())
        target = Quat.from_axis_angle(AXIS_Y, math.pi / 2)
        tracker.update(*target)

        tracker.advance(1.0)

        self.assert_quat(tracker.orientation, target)

    def test_advance_with_no_target_change_holds_still(self) -> None:
        """Test that a settled tracker does not drift on its own."""
        tracker = OrientationTracker()
        tracker.update(*Quat.identity())
        tracker.update(*Quat.from_axis_angle(AXIS_Y, math.pi / 2))
        tracker.advance(1.0)

        settled = tracker.orientation
        tracker.advance(0.5)

        self.assert_quat(tracker.orientation, settled)


class TestIdentity(VectorTestCase):
    """Tests for the shipped identity rotation."""

    def test_identity_is_the_null_rotation(self) -> None:
        """Test that the constant is the quaternion doing nothing."""
        self.assert_quat(IDENTITY, Quat.identity())
        self.assert_mat4(IDENTITY.to_matrix(), Mat4.identity())

    def test_basis_defaults_to_the_identity(self) -> None:
        """Test that a tracker without a basis passes the sensor through."""
        tracker = OrientationTracker()
        raw = Quat.from_axis_angle(Vec3(1.0, 2.0, 3.0), 0.8)

        tracker.update(*Quat.identity())

        self.assert_quat(tracker.update(*raw), raw)

    def test_reset(self) -> None:
        """Test that a reset makes the next quaternion the new reference."""
        tracker = OrientationTracker()
        tracker.update(*Quat.from_axis_angle(AXIS_Y, 1.2))
        tracker.update(*Quat.from_axis_angle(AXIS_Y, 2.0))

        tracker.reset()

        self.assertIsNone(tracker.reference)
        self.assert_quat(tracker.orientation, Quat.identity())
        self.assert_quat(tracker.target, Quat.identity())

        orientation = tracker.update(*Quat.from_axis_angle(AXIS_Y, 2.0))

        self.assert_quat(orientation, Quat.identity())
