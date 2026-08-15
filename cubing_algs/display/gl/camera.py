"""
Orbit camera of the GPU rendering backend.

The camera turns around a target at a fixed distance, which is the only
way one ever looks at a cube. It is deliberately built to frame exactly
like the SVG backend of ``display/image.py``, so that both renderings
can be compared side by side.
"""
import math
from dataclasses import dataclass
from dataclasses import field
from typing import Self

from cubing_algs.display.constants import DISTANCE
from cubing_algs.display.constants import ROTATION
from cubing_algs.display.gl.constants import BOUNDING_RADIUS
from cubing_algs.display.gl.constants import CAMERA_FAR
from cubing_algs.display.gl.constants import CAMERA_MAX_DISTANCE
from cubing_algs.display.gl.constants import CAMERA_MIN_DISTANCE
from cubing_algs.display.gl.constants import CAMERA_NEAR
from cubing_algs.display.gl.constants import PITCH_LIMIT
from cubing_algs.display.gl.transforms import ORIGIN
from cubing_algs.display.gl.transforms import Mat4
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.display.image import ImageDisplay


def fit_fov(radius: float, distance: float) -> float:
    """
    Compute the field of view framing a sphere seen from a distance.

    This is the angle of the cone tangent to the sphere, which is also
    what ``image.py`` computes the hard way when it scales its SVG to
    ``sqrt(3 * distance ** 2 / (distance ** 2 - 3))``: same framing,
    written as an angle instead of a scale factor.

    Args:
        radius: Radius of the bounding sphere of the scene.
        distance: Distance from the camera to the center of the sphere.

    Returns:
        The vertical field of view, in radians.

    Raises:
        ValueError: When the camera stands inside the sphere, where no
            field of view can contain it.

    """
    if distance <= radius:
        msg = (
            f'A camera at { distance } cannot frame a sphere '
            f'of radius { radius }: it stands inside it'
        )
        raise ValueError(msg)

    return 2 * math.asin(radius / distance)


def fit_aspect(fov: float, aspect: float) -> float:
    """
    Widen a field of view so that a narrow viewport still frames it all.

    A field of view is vertical, so a viewport taller than it is wide
    holds less of the scene sideways than upwards: the cube would then
    be cut on both sides. Widening the vertical angle by exactly what
    the width lacks puts it back inside, and leaves any viewport at
    least as wide as it is tall untouched.

    Args:
        fov: The vertical field of view framing the scene, in radians.
        aspect: Width over height ratio of the viewport.

    Returns:
        The vertical field of view to use, in radians.

    """
    if aspect >= 1.0:
        return fov

    return 2 * math.atan(math.tan(fov / 2) / aspect)


def parse_rotation(rotation: str) -> tuple[float, float, float]:
    """
    Read a rotation string as the angles of an orbit camera.

    The string is the one of the SVG backend, such as ``y45x-34``. Its
    ``y`` parts turn the camera around the cube, its ``x`` parts raise
    it, its ``z`` parts spin it around its line of sight. Repeated axes
    add up.

    Unlike ``image.py``, which applies each rotation in the order it is
    written, the angles are here composed in the fixed yaw, pitch, roll
    order of an orbit camera. Both agree on any string of the usual
    ``y…x…`` form, which covers every rotation the library ships.

    Args:
        rotation: The rotation string, empty for the default one.

    Returns:
        The (yaw, pitch, roll) angles, in radians.

    """
    angles = {'y': 0.0, 'x': 0.0, 'z': 0.0}

    for axis, degrees in ImageDisplay.parse_rotation(rotation or ROTATION):
        angles[axis] += degrees

    return (
        math.radians(angles['y']),
        math.radians(-angles['x']),
        math.radians(angles['z']),
    )


@dataclass(slots=True)
class OrbitCamera:
    """
    A camera orbiting around a target.

    The yaw turns the camera around the vertical axis of the target, the
    pitch raises it above the horizon, the roll spins the image around
    the line of sight. All three are in radians.
    """

    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0
    distance: float = DISTANCE
    target: Vec3 = ORIGIN
    fov: float = field(
        default_factory=lambda: fit_fov(BOUNDING_RADIUS, DISTANCE),
    )
    aspect: float = 1.0
    near: float = CAMERA_NEAR
    far: float = CAMERA_FAR

    @classmethod
    def from_rotation(
            cls,
            rotation: str = '',
            distance: float = 0.0,
            radius: float = BOUNDING_RADIUS,
            aspect: float = 1.0,
    ) -> Self:
        """
        Build the camera framing a scene, as the SVG backend does.

        Args:
            rotation: Rotation string of the SVG backend, such as
                ``y45x-34``. Empty for the library default.
            distance: Distance to the center of the scene. Zero for the
                library default.
            radius: Radius of the bounding sphere of the scene.
            aspect: Width over height ratio of the viewport.

        Returns:
            A camera looking at the origin, framing the sphere exactly.

        """
        yaw, pitch, roll = parse_rotation(rotation)
        distance = distance or DISTANCE

        return cls(
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            distance=distance,
            fov=fit_aspect(fit_fov(radius, distance), aspect),
            aspect=aspect,
        )

    @property
    def position(self) -> Vec3:
        """
        Tell where the camera stands.

        Returns:
            The position of the camera, in world coordinates.

        """
        cos_pitch = math.cos(self.pitch)

        return self.target + Vec3(
            cos_pitch * math.sin(self.yaw),
            math.sin(self.pitch),
            cos_pitch * math.cos(self.yaw),
        ).scaled(self.distance)

    @property
    def up(self) -> Vec3:
        """
        Tell which way is up for the camera.

        Computed from the pitch rather than left to the world vertical,
        so that the camera keeps working when it looks straight down at
        the cube, where the two would be parallel.

        Returns:
            The up direction of the camera, orthogonal to its line of
            sight, in world coordinates.

        """
        sin_pitch = math.sin(self.pitch)

        return Vec3(
            -math.sin(self.yaw) * sin_pitch,
            math.cos(self.pitch),
            -math.cos(self.yaw) * sin_pitch,
        )

    def view(self) -> Mat4:
        """
        Build the view matrix of the camera.

        Returns:
            The matrix taking world coordinates to camera coordinates.

        """
        look_at = Mat4.look_at(self.position, self.target, self.up)

        if not self.roll:
            return look_at

        return Mat4.rotation_z(-self.roll) @ look_at

    def projection(self) -> Mat4:
        """
        Build the projection matrix of the camera.

        Returns:
            The matrix taking camera coordinates to clip space.

        """
        return Mat4.perspective(
            self.fov,
            self.aspect,
            self.near,
            self.far,
        )

    def view_projection(self) -> Mat4:
        """
        Build the matrix projecting the world onto the screen.

        Returns:
            The product of the projection and the view matrices.

        """
        return self.projection() @ self.view()

    def orbit(self, delta_yaw: float, delta_pitch: float) -> None:
        """
        Turn the camera around its target.

        The pitch is clamped just short of the poles, where the up
        direction would become parallel to the line of sight and the
        view matrix would collapse.

        Args:
            delta_yaw: How much to turn around the target, in radians.
            delta_pitch: How much to raise the camera, in radians.

        """
        self.yaw += delta_yaw
        self.pitch = max(
            -PITCH_LIMIT,
            min(PITCH_LIMIT, self.pitch + delta_pitch),
        )

    def zoom(self, factor: float) -> None:
        """
        Move the camera closer to its target, or further away.

        Args:
            factor: Multiplier of the distance, below 1 to come closer.

        """
        self.distance = max(
            CAMERA_MIN_DISTANCE,
            min(CAMERA_MAX_DISTANCE, self.distance * factor),
        )
