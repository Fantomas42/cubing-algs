"""
Linear algebra of the GPU rendering backend.

Pure Python, no dependency: vectors, quaternions, Euler angles and 4x4
matrices. The renderer is not CPU bound, it only pushes a handful of
matrices per frame, so numpy would buy nothing here.

Conventions, chosen to match OpenGL so that no transposition ever
happens on the way to a shader:

- right handed coordinates, the camera looks down its own ``-Z``
- column vectors: ``matrix @ vector`` transforms ``vector``
- ``a @ b`` applies ``b`` first, then ``a``
- matrices are stored **column major**, as GLSL expects them
- every angle is in radians
"""
import math
import struct
from dataclasses import dataclass
from typing import NamedTuple
from typing import Self

# Below this length a vector is considered null and cannot be
# normalized, and a quaternion falls back to the identity.
EPSILON = 1e-10

# Where the pitch of an Euler extraction is considered locked: the yaw
# and the roll then act on the same axis and cannot be told apart.
GIMBAL_LOCK_THRESHOLD = 1.0 - 1e-9

MATRIX_LENGTH = 16


class Vec3(NamedTuple):
    """A vector, or a point, of the 3D space."""

    x: float
    y: float
    z: float

    def __add__(self, other: 'Vec3') -> 'Vec3':  # type: ignore[override]
        """
        Add two vectors component wise.

        Returns:
            The sum of the two vectors.

        """
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vec3') -> 'Vec3':
        """
        Subtract a vector component wise.

        Returns:
            The difference of the two vectors.

        """
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self) -> 'Vec3':
        """
        Reverse the direction of the vector.

        Returns:
            The opposite vector.

        """
        return Vec3(-self.x, -self.y, -self.z)

    def scaled(self, factor: float) -> 'Vec3':
        """
        Multiply the vector by a scalar.

        Args:
            factor: The scalar to multiply by.

        Returns:
            The scaled vector.

        """
        return Vec3(self.x * factor, self.y * factor, self.z * factor)

    def dot(self, other: 'Vec3') -> float:
        """
        Compute the dot product with another vector.

        Args:
            other: The other vector.

        Returns:
            The dot product of the two vectors.

        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Vec3') -> 'Vec3':
        """
        Compute the cross product with another vector.

        Args:
            other: The other vector.

        Returns:
            A vector orthogonal to both, following the right hand rule.

        """
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self) -> float:
        """
        Compute the euclidean length of the vector.

        Returns:
            The length of the vector.

        """
        return math.sqrt(self.dot(self))

    def normalized(self) -> 'Vec3':
        """
        Scale the vector to a unit length.

        Returns:
            The unit vector of the same direction, or the null vector
            when the vector is too short to have a direction.

        """
        length = self.length()
        if length < EPSILON:
            return Vec3(0.0, 0.0, 0.0)

        return self.scaled(1.0 / length)


ORIGIN = Vec3(0.0, 0.0, 0.0)
AXIS_X = Vec3(1.0, 0.0, 0.0)
AXIS_Y = Vec3(0.0, 1.0, 0.0)
AXIS_Z = Vec3(0.0, 0.0, 1.0)


class Euler(NamedTuple):
    """
    A rotation as three angles, in radians.

    The convention is intrinsic ``Y`` then ``X`` then ``Z``, that is
    ``rotation_y(yaw) @ rotation_x(pitch) @ rotation_z(roll)``. It is
    the natural one for a camera and for a cube seen by a user: the yaw
    turns the object around the vertical axis, the pitch tilts it toward
    the viewer, the roll spins it around the line of sight.
    """

    yaw: float
    pitch: float
    roll: float

    @classmethod
    def from_degrees(cls, yaw: float, pitch: float, roll: float) -> Self:
        """
        Build an Euler triplet from angles given in degrees.

        Args:
            yaw: Rotation around the Y axis, in degrees.
            pitch: Rotation around the X axis, in degrees.
            roll: Rotation around the Z axis, in degrees.

        Returns:
            The matching Euler angles, in radians.

        """
        return cls(
            math.radians(yaw),
            math.radians(pitch),
            math.radians(roll),
        )

    def degrees(self) -> tuple[float, float, float]:
        """
        Convert the three angles to degrees.

        Returns:
            The (yaw, pitch, roll) triplet, in degrees.

        """
        return (
            math.degrees(self.yaw),
            math.degrees(self.pitch),
            math.degrees(self.roll),
        )


class Quat(NamedTuple):
    """
    A unit quaternion, representing a rotation of the 3D space.

    Most operations assume a unit quaternion, which is what every
    constructor returns. Only ``__mul__`` on hand built values, or a
    sensor feed, can drift: call ``normalized()`` then.
    """

    w: float
    x: float
    y: float
    z: float

    @classmethod
    def identity(cls) -> Self:
        """
        Build the quaternion of the null rotation.

        Returns:
            The identity quaternion.

        """
        return cls(1.0, 0.0, 0.0, 0.0)

    @classmethod
    def from_axis_angle(cls, axis: Vec3, angle: float) -> Self:
        """
        Build the quaternion rotating around an axis.

        Args:
            axis: The axis of the rotation, of any length.
            angle: The angle of the rotation, in radians, counter
                clockwise when the axis points toward the viewer.

        Returns:
            The matching unit quaternion, or the identity when the axis
            is null.

        """
        unit = axis.normalized()
        if unit == ORIGIN:
            return cls.identity()

        half = angle / 2
        sin_half = math.sin(half)

        return cls(
            math.cos(half),
            unit.x * sin_half,
            unit.y * sin_half,
            unit.z * sin_half,
        )

    @classmethod
    def from_euler(cls, euler: Euler) -> 'Quat':
        """
        Build the quaternion of an Euler triplet.

        Args:
            euler: The angles to compose, see ``Euler`` for the order.

        Returns:
            The matching unit quaternion.

        """
        yaw = cls.from_axis_angle(AXIS_Y, euler.yaw)
        pitch = cls.from_axis_angle(AXIS_X, euler.pitch)
        roll = cls.from_axis_angle(AXIS_Z, euler.roll)

        return yaw * pitch * roll

    def __mul__(self, other: 'Quat') -> 'Quat':  # type: ignore[override]
        """
        Compose two rotations, the other one applying first.

        Args:
            other: The rotation applied before this one.

        Returns:
            The quaternion of the combined rotation.

        """
        return Quat(
            self.w * other.w
            - self.x * other.x - self.y * other.y - self.z * other.z,
            self.w * other.x + self.x * other.w
            + self.y * other.z - self.z * other.y,
            self.w * other.y - self.x * other.z
            + self.y * other.w + self.z * other.x,
            self.w * other.z + self.x * other.y
            - self.y * other.x + self.z * other.w,
        )

    def norm(self) -> float:
        """
        Compute the euclidean norm of the quaternion.

        Returns:
            The norm, 1.0 for a rotation.

        """
        return math.sqrt(
            self.w * self.w + self.x * self.x
            + self.y * self.y + self.z * self.z,
        )

    def normalized(self) -> 'Quat':
        """
        Scale the quaternion to a unit norm.

        Returns:
            The unit quaternion of the same rotation, or the identity
            when the norm is too small to mean anything.

        """
        norm = self.norm()
        if norm < EPSILON:
            return Quat.identity()

        return Quat(
            self.w / norm,
            self.x / norm,
            self.y / norm,
            self.z / norm,
        )

    def conjugate(self) -> 'Quat':
        """
        Negate the vector part of the quaternion.

        For a unit quaternion, the conjugate is the inverse rotation.

        Returns:
            The conjugate quaternion.

        """
        return Quat(self.w, -self.x, -self.y, -self.z)

    def rotate(self, vector: Vec3) -> Vec3:
        """
        Apply the rotation to a vector.

        Args:
            vector: The vector to rotate.

        Returns:
            The rotated vector.

        """
        axis = Vec3(self.x, self.y, self.z)
        cross = axis.cross(vector)

        return (
            vector
            + cross.scaled(2 * self.w)
            + axis.cross(cross).scaled(2)
        )

    def to_matrix(self) -> 'Mat4':
        """
        Convert the rotation to a matrix.

        Returns:
            The rotation matrix of the quaternion.

        """
        w, x, y, z = self

        xx, yy, zz = x * x, y * y, z * z
        xy, xz, yz = x * y, x * z, y * z
        wx, wy, wz = w * x, w * y, w * z

        return Mat4.from_rows((
            (1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy), 0.0),
            (2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx), 0.0),
            (2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy), 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ))

    def to_euler(self) -> Euler:
        """
        Extract the Euler angles of the rotation.

        At the gimbal lock, where the cube points straight up or down,
        the yaw and the roll act on the same axis: the whole rotation is
        then reported as yaw, with a null roll.

        Returns:
            The (yaw, pitch, roll) triplet, in radians, such that
            ``Quat.from_euler()`` rebuilds the same rotation.

        """
        w, x, y, z = self

        # Terms of the rotation matrix needed by the extraction.
        m12 = 2 * (y * z - w * x)
        sin_pitch = -m12

        if abs(sin_pitch) >= GIMBAL_LOCK_THRESHOLD:
            m00 = 1 - 2 * (y * y + z * z)
            m20 = 2 * (x * z - w * y)

            return Euler(
                math.atan2(-m20, m00),
                math.copysign(math.pi / 2, sin_pitch),
                0.0,
            )

        m02 = 2 * (x * z + w * y)
        m22 = 1 - 2 * (x * x + y * y)
        m10 = 2 * (x * y + w * z)
        m11 = 1 - 2 * (x * x + z * z)

        return Euler(
            math.atan2(m02, m22),
            math.asin(sin_pitch),
            math.atan2(m10, m11),
        )


@dataclass(frozen=True, slots=True)
class Mat4:
    """
    A 4x4 matrix, stored column major as OpenGL expects it.

    ``values`` holds the sixteen coefficients, column after column:
    ``values[column * 4 + row]``. Build one with ``from_rows()`` to keep
    the source readable, and read one back with ``rows()``.
    """

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        """
        Reject any tuple that is not a 4x4 matrix.

        Raises:
            ValueError: When the tuple does not hold sixteen values.

        """
        if len(self.values) != MATRIX_LENGTH:
            msg = (
                f'A Mat4 holds { MATRIX_LENGTH } coefficients, '
                f'got { len(self.values) }'
            )
            raise ValueError(msg)

    @classmethod
    def from_rows(
            cls,
            rows: tuple[
                tuple[float, float, float, float],
                tuple[float, float, float, float],
                tuple[float, float, float, float],
                tuple[float, float, float, float],
            ],
    ) -> Self:
        """
        Build a matrix from its four rows.

        Args:
            rows: The rows of the matrix, as written on paper.

        Returns:
            The matrix, stored column major.

        """
        return cls(tuple(
            rows[row][column]
            for column in range(4)
            for row in range(4)
        ))

    @classmethod
    def identity(cls) -> Self:
        """
        Build the identity matrix.

        Returns:
            The identity matrix.

        """
        return cls.from_rows((
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ))

    @classmethod
    def translation(cls, offset: Vec3) -> Self:
        """
        Build a translation matrix.

        Args:
            offset: The translation to apply.

        Returns:
            The translation matrix.

        """
        return cls.from_rows((
            (1.0, 0.0, 0.0, offset.x),
            (0.0, 1.0, 0.0, offset.y),
            (0.0, 0.0, 1.0, offset.z),
            (0.0, 0.0, 0.0, 1.0),
        ))

    @classmethod
    def rotation_x(cls, angle: float) -> Self:
        """
        Build a rotation matrix around the X axis.

        Args:
            angle: The angle of the rotation, in radians.

        Returns:
            The rotation matrix.

        """
        cos, sin = math.cos(angle), math.sin(angle)

        return cls.from_rows((
            (1.0, 0.0, 0.0, 0.0),
            (0.0, cos, -sin, 0.0),
            (0.0, sin, cos, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ))

    @classmethod
    def rotation_y(cls, angle: float) -> Self:
        """
        Build a rotation matrix around the Y axis.

        Args:
            angle: The angle of the rotation, in radians.

        Returns:
            The rotation matrix.

        """
        cos, sin = math.cos(angle), math.sin(angle)

        return cls.from_rows((
            (cos, 0.0, sin, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (-sin, 0.0, cos, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ))

    @classmethod
    def rotation_z(cls, angle: float) -> Self:
        """
        Build a rotation matrix around the Z axis.

        Args:
            angle: The angle of the rotation, in radians.

        Returns:
            The rotation matrix.

        """
        cos, sin = math.cos(angle), math.sin(angle)

        return cls.from_rows((
            (cos, -sin, 0.0, 0.0),
            (sin, cos, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ))

    @classmethod
    def look_at(cls, eye: Vec3, target: Vec3, up: Vec3) -> Self:
        """
        Build the view matrix of a camera looking at a point.

        Args:
            eye: Where the camera stands.
            target: What the camera looks at.
            up: Which way is up, only its component orthogonal to the
                line of sight matters.

        Returns:
            The matrix taking world coordinates to camera coordinates,
            where the camera sits at the origin and looks down ``-Z``.

        """
        forward = (target - eye).normalized()
        right = forward.cross(up).normalized()
        upward = right.cross(forward)

        return cls.from_rows((
            (right.x, right.y, right.z, -right.dot(eye)),
            (upward.x, upward.y, upward.z, -upward.dot(eye)),
            (-forward.x, -forward.y, -forward.z, forward.dot(eye)),
            (0.0, 0.0, 0.0, 1.0),
        ))

    @classmethod
    def perspective(
            cls,
            fov: float,
            aspect: float,
            near: float,
            far: float,
    ) -> Self:
        """
        Build a perspective projection matrix.

        Args:
            fov: The vertical field of view, in radians.
            aspect: The width over height ratio of the viewport.
            near: Distance to the near clipping plane, strictly positive.
            far: Distance to the far clipping plane.

        Returns:
            The projection matrix, mapping the frustum to the OpenGL
            clip space where depth runs from -1 to 1.

        """
        focal = 1.0 / math.tan(fov / 2)
        depth = near - far

        return cls.from_rows((
            (focal / aspect, 0.0, 0.0, 0.0),
            (0.0, focal, 0.0, 0.0),
            (0.0, 0.0, (far + near) / depth, 2 * far * near / depth),
            (0.0, 0.0, -1.0, 0.0),
        ))

    def rows(self) -> tuple[tuple[float, ...], ...]:
        """
        Read the matrix back as four rows.

        Returns:
            The rows of the matrix, as written on paper.

        """
        return tuple(
            tuple(self.values[column * 4 + row] for column in range(4))
            for row in range(4)
        )

    def __matmul__(self, other: 'Mat4') -> 'Mat4':
        """
        Multiply two matrices, the other one applying first.

        Args:
            other: The transformation applied before this one.

        Returns:
            The matrix of the combined transformation.

        """
        left, right = self.values, other.values

        return Mat4(tuple(
            sum(
                left[step * 4 + index % 4] * right[index // 4 * 4 + step]
                for step in range(4)
            )
            for index in range(MATRIX_LENGTH)
        ))

    def transposed(self) -> 'Mat4':
        """
        Swap the rows and the columns of the matrix.

        Returns:
            The transposed matrix.

        """
        return Mat4(tuple(
            self.values[index % 4 * 4 + index // 4]
            for index in range(MATRIX_LENGTH)
        ))

    def transform_direction(self, direction: Vec3) -> Vec3:
        """
        Apply the matrix to a direction, ignoring its translation.

        Args:
            direction: The direction to transform.

        Returns:
            The transformed direction.

        """
        values = self.values

        return Vec3(
            values[0] * direction.x
            + values[4] * direction.y + values[8] * direction.z,
            values[1] * direction.x
            + values[5] * direction.y + values[9] * direction.z,
            values[2] * direction.x
            + values[6] * direction.y + values[10] * direction.z,
        )

    def transform_point(self, point: Vec3) -> Vec3:
        """
        Apply the matrix to a point, dividing by the homogeneous weight.

        The division is what turns a projection matrix into an actual
        perspective: with an affine matrix the weight stays 1 and
        nothing happens.

        Args:
            point: The point to transform.

        Returns:
            The transformed point.

        """
        values = self.values
        transformed = self.transform_direction(point) + Vec3(
            values[12], values[13], values[14],
        )

        weight = (
            values[3] * point.x + values[7] * point.y
            + values[11] * point.z + values[15]
        )

        if abs(weight) < EPSILON:
            return transformed

        return transformed.scaled(1.0 / weight)

    def pack(self) -> bytes:
        """
        Serialize the matrix for an OpenGL uniform.

        Returns:
            The sixteen coefficients as column major floats, ready to be
            written to a buffer or a uniform.

        """
        return struct.pack('<16f', *self.values)


class OrientationTracker:
    """
    Turn the raw quaternions of a sensor into a display rotation.

    A bluetooth cube reports its absolute orientation in its own frame,
    with an arbitrary zero: the first quaternion received is therefore
    kept as the reference, and every later one is expressed relatively
    to it. The ``basis`` then absorbs the axis convention of the sensor,
    which rarely matches the one of the renderer.

    Nothing here is specific to a brand of cube: a tracker is just the
    reference quaternion, the basis, and the current orientation.
    """

    def __init__(self, basis: Quat | None = None) -> None:
        """
        Initialize the tracker, waiting for its first quaternion.

        Args:
            basis: Rotation from the sensor frame to the display frame.
                Defaults to the identity, for a sensor already aligned
                with the renderer axes.

        """
        self.basis = basis or Quat.identity()
        self.reference: Quat | None = None
        self.orientation = Quat.identity()

    def update(self, w: float, x: float, y: float, z: float) -> Quat:
        """
        Feed a raw quaternion from the sensor.

        The first call only records the reference orientation and leaves
        the cube where it is.

        Args:
            w: Scalar component of the raw quaternion.
            x: X component of the raw quaternion.
            y: Y component of the raw quaternion.
            z: Z component of the raw quaternion.

        Returns:
            The orientation to display, in the renderer frame.

        """
        raw = Quat(w, x, y, z).normalized()

        if self.reference is None:
            self.reference = raw
            return self.orientation

        relative = (self.reference.conjugate() * raw).normalized()

        self.orientation = (
            self.basis * relative * self.basis.conjugate()
        ).normalized()

        return self.orientation

    def reset(self) -> None:
        """
        Forget the reference orientation and the current one.

        The next quaternion received becomes the new reference, which is
        how a user re-centers a cube that has drifted.
        """
        self.reference = None
        self.orientation = Quat.identity()
