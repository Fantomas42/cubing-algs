"""Tests for the orbit camera of the GPU rendering backend."""
import math
import unittest

from cubing_algs.display.constants import DISTANCE
from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.camera import fit_fov
from cubing_algs.display.gl.camera import parse_rotation
from cubing_algs.display.gl.constants import BOUNDING_RADIUS
from cubing_algs.display.gl.constants import CAMERA_MAX_DISTANCE
from cubing_algs.display.gl.constants import CAMERA_MIN_DISTANCE
from cubing_algs.display.gl.constants import PITCH_LIMIT
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.display.image import CUBE_VERTICES
from cubing_algs.display.image import FACE_DEFS
from cubing_algs.display.image import ImageDisplay
from cubing_algs.vcube import VCube

PLACES = 9

IMAGE_SIZE = 512


class TestFitFov(unittest.TestCase):
    """Tests for the fit_fov function."""

    def test_tangent_to_the_sphere(self) -> None:
        """Test that the field of view touches the bounding sphere."""
        fov = fit_fov(1.0, 2.0)

        self.assertAlmostEqual(math.sin(fov / 2), 0.5, places=PLACES)

    def test_narrows_with_distance(self) -> None:
        """Test that a farther camera needs a narrower field of view."""
        self.assertLess(fit_fov(1.0, 10.0), fit_fov(1.0, 5.0))

    def test_widens_with_radius(self) -> None:
        """Test that a bigger scene needs a wider field of view."""
        self.assertGreater(fit_fov(2.0, 10.0), fit_fov(1.0, 10.0))

    def test_matches_the_svg_scale(self) -> None:
        """
        Test that the framing is the one of the SVG backend.

        ``image.py`` scales its drawing so that the widest projected
        point of the bounding sphere touches the border of the image,
        which is exactly what a tangent field of view does.
        """
        for distance in (2.0, 4.0, DISTANCE):
            with self.subTest(distance=distance):
                extent = math.sqrt(
                    3 * distance ** 2 / (distance ** 2 - 3),
                )

                self.assertAlmostEqual(
                    math.tan(fit_fov(BOUNDING_RADIUS, distance) / 2),
                    extent / distance,
                    places=PLACES,
                )

    def test_camera_inside_the_sphere(self) -> None:
        """Test that a camera inside the scene is refused."""
        with self.assertRaises(ValueError):
            fit_fov(2.0, 1.0)

    def test_camera_on_the_sphere(self) -> None:
        """Test that a camera on the surface of the scene is refused."""
        with self.assertRaises(ValueError):
            fit_fov(2.0, 2.0)


class TestParseRotation(unittest.TestCase):
    """Tests for the parse_rotation function."""

    def test_default_rotation(self) -> None:
        """Test that an empty string gives the default rotation."""
        yaw, pitch, roll = parse_rotation('')

        self.assertAlmostEqual(yaw, math.radians(45), places=PLACES)
        self.assertAlmostEqual(pitch, math.radians(34), places=PLACES)
        self.assertEqual(roll, 0.0)

    def test_invalid_rotation(self) -> None:
        """Test that an unreadable string falls back on the default."""
        self.assertEqual(parse_rotation('nonsense'), parse_rotation(''))

    def test_pitch_is_reversed(self) -> None:
        """Test that a negative x angle raises the camera."""
        _, pitch, _ = parse_rotation('x-30')

        self.assertAlmostEqual(pitch, math.radians(30), places=PLACES)

    def test_roll(self) -> None:
        """Test that a z angle spins the camera."""
        _, _, roll = parse_rotation('z20')

        self.assertAlmostEqual(roll, math.radians(20), places=PLACES)

    def test_repeated_axes_add_up(self) -> None:
        """Test that two angles on the same axis are summed."""
        yaw, _, _ = parse_rotation('y30y15')

        self.assertAlmostEqual(yaw, math.radians(45), places=PLACES)


class TestOrbitCamera(unittest.TestCase):
    """Tests for the OrbitCamera class."""

    def assert_vec3(
            self,
            actual: Vec3,
            expected: tuple[float, float, float],
    ) -> None:
        """Assert that a vector matches an expected triplet."""
        for index, (got, want) in enumerate(zip(actual, expected, strict=True)):
            with self.subTest(component='xyz'[index]):
                self.assertAlmostEqual(got, want, places=PLACES)

    def test_defaults(self) -> None:
        """Test that a camera is built framing the cube from its front."""
        camera = OrbitCamera()

        self.assertEqual(camera.distance, DISTANCE)
        self.assert_vec3(camera.position, (0.0, 0.0, DISTANCE))
        self.assertAlmostEqual(
            camera.fov,
            fit_fov(BOUNDING_RADIUS, DISTANCE),
            places=PLACES,
        )

    def test_from_rotation(self) -> None:
        """Test that a camera is built from a rotation string."""
        camera = OrbitCamera.from_rotation('y45x-34', 8.0)

        self.assertAlmostEqual(camera.yaw, math.radians(45), places=PLACES)
        self.assertAlmostEqual(camera.pitch, math.radians(34), places=PLACES)
        self.assertEqual(camera.distance, 8.0)
        self.assertAlmostEqual(
            camera.fov,
            fit_fov(BOUNDING_RADIUS, 8.0),
            places=PLACES,
        )

    def test_from_rotation_defaults(self) -> None:
        """Test that the library defaults are used when nothing is given."""
        camera = OrbitCamera.from_rotation()

        self.assertAlmostEqual(camera.yaw, math.radians(45), places=PLACES)
        self.assertAlmostEqual(camera.pitch, math.radians(34), places=PLACES)
        self.assertEqual(camera.distance, DISTANCE)

    def test_position_keeps_the_distance(self) -> None:
        """Test that the camera stands at its distance from the target."""
        camera = OrbitCamera.from_rotation('y120x-25', 7.0)

        self.assertAlmostEqual(
            (camera.position - camera.target).length(),
            7.0,
            places=PLACES,
        )

    def test_position_follows_the_target(self) -> None:
        """Test that the camera moves with its target."""
        camera = OrbitCamera(target=Vec3(1.0, 2.0, 3.0))

        self.assert_vec3(camera.position, (1.0, 2.0, 3.0 + DISTANCE))

    def test_position_above_the_cube(self) -> None:
        """Test that a quarter turn of pitch puts the camera on top."""
        camera = OrbitCamera(pitch=math.pi / 2, distance=4.0)

        self.assert_vec3(camera.position, (0.0, 4.0, 0.0))

    def test_up_is_orthogonal_to_the_line_of_sight(self) -> None:
        """Test that the up direction never leans on the line of sight."""
        for pitch in (0.0, 0.5, math.pi / 2, -math.pi / 2):
            with self.subTest(pitch=pitch):
                camera = OrbitCamera(yaw=0.7, pitch=pitch)
                sight = camera.target - camera.position

                self.assertAlmostEqual(
                    camera.up.dot(sight),
                    0.0,
                    places=PLACES,
                )

    def test_view_puts_the_target_ahead(self) -> None:
        """Test that the target lands on the line of sight of the camera."""
        camera = OrbitCamera.from_rotation('y45x-34', 8.0)
        transformed = camera.view().transform_point(camera.target)

        self.assert_vec3(transformed, (0.0, 0.0, -8.0))

    def test_view_at_the_pole(self) -> None:
        """Test that looking straight down still gives a usable view."""
        camera = OrbitCamera.from_rotation('x-90', 8.0)
        # The front face is below the center of the screen, as the cube
        # is seen from above.
        transformed = camera.view_projection().transform_point(
            Vec3(0.0, 0.0, 1.0),
        )

        self.assertAlmostEqual(transformed.x, 0.0, places=PLACES)
        self.assertLess(transformed.y, 0.0)

    def test_view_roll_spins_the_image(self) -> None:
        """Test that a roll turns the image around the line of sight."""
        camera = OrbitCamera.from_rotation('z90', 8.0)
        transformed = camera.view().transform_direction(Vec3(1.0, 0.0, 0.0))

        self.assert_vec3(transformed, (0.0, -1.0, 0.0))

    def test_projection_frames_the_cube(self) -> None:
        """Test that the bounding sphere touches the border of the screen."""
        camera = OrbitCamera.from_rotation('y45x-34')
        # The topmost point of the bounding sphere, as seen from the
        # camera: the tangent point sits slightly toward the viewer.
        offset = BOUNDING_RADIUS ** 2 / camera.distance
        radius = BOUNDING_RADIUS * math.sqrt(
            1 - BOUNDING_RADIUS ** 2 / camera.distance ** 2,
        )
        top = camera.position.normalized().scaled(offset) + camera.up.scaled(
            radius,
        )

        self.assertAlmostEqual(
            camera.view_projection().transform_point(top).y,
            1.0,
            places=PLACES,
        )

    def test_orbit(self) -> None:
        """Test that orbiting adds to the angles of the camera."""
        camera = OrbitCamera(yaw=0.2, pitch=0.1)

        camera.orbit(0.3, -0.05)

        self.assertAlmostEqual(camera.yaw, 0.5, places=PLACES)
        self.assertAlmostEqual(camera.pitch, 0.05, places=PLACES)

    def test_orbit_clamps_the_pitch(self) -> None:
        """Test that orbiting cannot take the camera over the pole."""
        camera = OrbitCamera()

        camera.orbit(0.0, 10.0)
        self.assertAlmostEqual(camera.pitch, PITCH_LIMIT, places=PLACES)

        camera.orbit(0.0, -20.0)
        self.assertAlmostEqual(camera.pitch, -PITCH_LIMIT, places=PLACES)

    def test_zoom(self) -> None:
        """Test that zooming scales the distance to the target."""
        camera = OrbitCamera(distance=10.0)

        camera.zoom(0.5)

        self.assertAlmostEqual(camera.distance, 5.0, places=PLACES)

    def test_zoom_is_clamped(self) -> None:
        """Test that zooming keeps the camera outside and in sight."""
        camera = OrbitCamera(distance=10.0)

        camera.zoom(0.001)
        self.assertEqual(camera.distance, CAMERA_MIN_DISTANCE)

        camera.zoom(1000.0)
        self.assertEqual(camera.distance, CAMERA_MAX_DISTANCE)


class TestSvgAgreement(unittest.TestCase):
    """
    Tests that the camera frames exactly like the SVG backend.

    This is the acceptance criterion of the whole camera: the wireframe
    of the bounding cube, projected by the camera, must land on the
    drawing of ``image.py`` pixel for pixel.
    """

    def setUp(self) -> None:
        """Build the SVG display used as the reference."""
        self.display = ImageDisplay(VCube())

    def svg_corners(
            self,
            rotation: str,
            distance: float,
    ) -> list[tuple[float, float]]:
        """
        Project the corners of the cube the way image.py does.

        Returns:
            The eight corners, in pixels of the SVG image.

        """
        rotations = self.display.parse_rotation(rotation)
        extent = math.sqrt(3 * distance ** 2 / (distance ** 2 - 3))
        scale = IMAGE_SIZE / (2 * extent)
        center = IMAGE_SIZE / 2

        return [
            self.display.point_to_svg_coords(
                self.display.project(
                    self.display.rotate_point(vertex, rotations),
                    distance,
                ),
                center, center, scale,
            )
            for vertex in CUBE_VERTICES
        ]

    @staticmethod
    def camera_corners(
            rotation: str,
            distance: float,
    ) -> list[tuple[float, float]]:
        """
        Project the corners of the cube with the orbit camera.

        Returns:
            The eight corners, in pixels of a viewport of the same size.

        """
        matrix = OrbitCamera.from_rotation(rotation, distance).view_projection()
        half = IMAGE_SIZE / 2

        projected = [
            matrix.transform_point(Vec3(*vertex))
            for vertex in CUBE_VERTICES
        ]

        return [
            (half + point.x * half, half - point.y * half)
            for point in projected
        ]

    def test_agrees_with_the_svg_projection(self) -> None:
        """Test that both backends project the cube on the same pixels."""
        for rotation in ('y45x-34', 'y45x-34z20', 'y120x-90', 'x-90', 'z45'):
            for distance in (4.0, DISTANCE):
                with self.subTest(rotation=rotation, distance=distance):
                    for svg, camera in zip(
                            self.svg_corners(rotation, distance),
                            self.camera_corners(rotation, distance),
                            strict=True,
                    ):
                        self.assertAlmostEqual(svg[0], camera[0], places=6)
                        self.assertAlmostEqual(svg[1], camera[1], places=6)

    def test_agrees_on_the_visible_faces(self) -> None:
        """Test that both backends agree on which faces can be seen."""
        camera = OrbitCamera.from_rotation('y45x-34')
        position = camera.position - camera.target

        visible = {
            face
            for face, _, _ in self.display.compute_visible_faces(
                self.display.parse_rotation('y45x-34'),
                DISTANCE,
            )
        }

        for face, normal, _, _ in FACE_DEFS:
            with self.subTest(face=face):
                self.assertEqual(
                    Vec3(*normal).dot(position) > 0,
                    face in visible,
                )
