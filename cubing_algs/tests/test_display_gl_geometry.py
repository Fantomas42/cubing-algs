"""Tests for the geometry of the GPU rendering backend."""
import math
import struct
import unittest
from collections import Counter

from cubing_algs.constants import FACE_INDEXES
from cubing_algs.constants import FACE_NUMBER
from cubing_algs.display.gl.constants import AXES_COLORS
from cubing_algs.display.gl.constants import CUBIE_BEVEL
from cubing_algs.display.gl.constants import CUBIE_GAP
from cubing_algs.display.gl.constants import STICKER_LIFT
from cubing_algs.display.gl.constants import STICKER_MARGIN
from cubing_algs.display.gl.geometry import AXES_VERTEX_PACKING
from cubing_algs.display.gl.geometry import AXIS_NUMBER
from cubing_algs.display.gl.geometry import BODY_FACE
from cubing_algs.display.gl.geometry import CORE_VERTEX_PACKING
from cubing_algs.display.gl.geometry import CUBE_EXTENT
from cubing_algs.display.gl.geometry import FACE_BASES
from cubing_algs.display.gl.geometry import CubeGeometry
from cubing_algs.display.gl.geometry import Mesh
from cubing_algs.display.gl.geometry import Polygon
from cubing_algs.display.gl.geometry import Vertex
from cubing_algs.display.gl.geometry import body_polygons
from cubing_algs.display.gl.geometry import build_core_mesh
from cubing_algs.display.gl.geometry import build_cube_geometry
from cubing_algs.display.gl.geometry import build_cubie_mesh
from cubing_algs.display.gl.geometry import build_cubies
from cubing_algs.display.gl.geometry import build_mesh
from cubing_algs.display.gl.geometry import build_point
from cubing_algs.display.gl.geometry import core_radius
from cubing_algs.display.gl.geometry import corner_triangle
from cubing_algs.display.gl.geometry import cubie_center
from cubing_algs.display.gl.geometry import cubie_half
from cubing_algs.display.gl.geometry import edge_quad
from cubing_algs.display.gl.geometry import face_square
from cubing_algs.display.gl.geometry import is_surface
from cubing_algs.display.gl.geometry import oriented
from cubing_algs.display.gl.geometry import other_axes
from cubing_algs.display.gl.geometry import pack_axes
from cubing_algs.display.gl.geometry import pack_core
from cubing_algs.display.gl.geometry import sticker_polygons
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.display.image import FACE_DEFS
from cubing_algs.exceptions import InvalidCubeSizeError

PLACES = 9

# What is left of a coordinate once it has been through a buffer, where
# it travels as a single precision float.
SINGLE_PLACES = 6

# What a beveled cubie is made of: six faces, twelve edges, eight
# corners for the plastic, plus one sticker per face.
BODY_POLYGON_COUNT = 26

VERTEX_COUNT = 120
TRIANGLE_COUNT = 56

VERTEX_SIZE = 28
INDEX_SIZE = 4

# What the axes are made of: one segment per axis, two vertices each,
# and six floats per vertex.
AXES_VERTEX_COUNT = 6
AXES_VERTEX_SIZE = 24

# How finely the ball core is cut in the tests: coarse enough to read a
# failure, fine enough to have poles, a seam and plain cells.
CORE_TEST_RINGS = 4
CORE_TEST_SEGMENTS = 6

# Six floats per vertex of the core: its position and its normal.
CORE_VERTEX_SIZE = 24

SIZES = (1, 2, 3, 4, 5, 6, 7)


def axes_vertices(length: float) -> list[tuple[float, ...]]:
    """
    Read the vertices of the axes back from their buffer.

    Args:
        length: How far a segment reaches from the center.

    Returns:
        The position and the color of each vertex, in order.

    """
    packed = pack_axes(length)

    return [
        struct.unpack_from(AXES_VERTEX_PACKING, packed, offset)
        for offset in range(0, len(packed), AXES_VERTEX_SIZE)
    ]


def triangles(mesh: Mesh) -> list[tuple[Vertex, Vertex, Vertex]]:
    """
    Read the triangles of a mesh as triplets of vertices.

    Returns:
        The vertices of each triangle, in the order they are wound.

    """
    return [
        (
            mesh.vertices[mesh.indices[start]],
            mesh.vertices[mesh.indices[start + 1]],
            mesh.vertices[mesh.indices[start + 2]],
        )
        for start in range(0, len(mesh.indices), 3)
    ]


class TestBuildPoint(unittest.TestCase):
    """Tests for the build_point function."""

    def test_assigns_by_axis(self) -> None:
        """Test that each coordinate lands on the axis it is given for."""
        self.assertEqual(
            build_point(((0, 1.0), (1, 2.0), (2, 3.0))),
            Vec3(1.0, 2.0, 3.0),
        )

    def test_defaults_to_zero(self) -> None:
        """Test that an axis left out stays at the origin."""
        self.assertEqual(build_point(((1, 5.0),)), Vec3(0.0, 5.0, 0.0))

    def test_accepts_nothing(self) -> None:
        """Test that no assignment at all builds the origin."""
        self.assertEqual(build_point(()), Vec3(0.0, 0.0, 0.0))


class TestOtherAxes(unittest.TestCase):
    """Tests for the other_axes function."""

    def test_excludes_the_axis(self) -> None:
        """Test that the two remaining axes are named, in order."""
        for axis, expected in enumerate(((1, 2), (0, 2), (0, 1))):
            with self.subTest(axis=axis):
                self.assertEqual(other_axes(axis), expected)


class TestOriented(unittest.TestCase):
    """Tests for the oriented function."""

    def test_keeps_an_outward_winding(self) -> None:
        """Test that a polygon already facing outward is left alone."""
        points = (
            Vec3(1.0, -1.0, -1.0),
            Vec3(1.0, 1.0, -1.0),
            Vec3(1.0, 1.0, 1.0),
        )

        polygon = oriented(points, BODY_FACE)

        self.assertEqual(polygon.points, points)
        self.assertEqual(polygon.normal, Vec3(1.0, 0.0, 0.0))

    def test_reverses_an_inward_winding(self) -> None:
        """Test that a polygon facing the origin is turned around."""
        points = (
            Vec3(1.0, 1.0, 1.0),
            Vec3(1.0, 1.0, -1.0),
            Vec3(1.0, -1.0, -1.0),
        )

        polygon = oriented(points, BODY_FACE)

        self.assertEqual(polygon.points, tuple(reversed(points)))
        self.assertEqual(polygon.normal, Vec3(1.0, 0.0, 0.0))

    def test_keeps_the_face(self) -> None:
        """Test that the face of the polygon is carried over."""
        polygon = oriented(
            (
                Vec3(0.0, 1.0, 0.0),
                Vec3(1.0, 1.0, 0.0),
                Vec3(1.0, 1.0, 1.0),
            ),
            2,
        )

        self.assertEqual(polygon.face, 2)


class TestFaceBases(unittest.TestCase):
    """Tests for the face bases of a cubie."""

    def test_covers_every_face(self) -> None:
        """Test that there is one basis per face of the cube."""
        self.assertEqual(len(FACE_BASES), FACE_NUMBER)

    def test_is_right_handed(self) -> None:
        """Test that right crossed with up gives the normal."""
        for face, basis in enumerate(FACE_BASES):
            with self.subTest(face=face):
                self.assertEqual(
                    basis.right.cross(basis.up),
                    basis.normal,
                )

    def test_matches_the_svg_normals(self) -> None:
        """
        Test that the faces point where the SVG backend puts them.

        The order is the one of ``FACE_ORDER``, so that a sticker can be
        colored by indexing the state of the cube with its face.
        """
        for name, normal, _indices, _state in FACE_DEFS:
            with self.subTest(face=name):
                self.assertEqual(
                    FACE_BASES[FACE_INDEXES[name]].normal,
                    Vec3(*normal),
                )


class TestPolygons(unittest.TestCase):
    """Tests for the polygons of a cubie."""

    def test_face_square_lies_on_its_plane(self) -> None:
        """Test that a face square is flat, at the extent of the cubie."""
        polygon = face_square(1, 1.0, 1.0, 0.8)

        self.assertEqual([point.y for point in polygon.points], [1.0] * 4)
        self.assertEqual(polygon.normal, Vec3(0.0, 1.0, 0.0))
        self.assertEqual(polygon.face, BODY_FACE)

    def test_face_square_is_shrunk_by_the_bevel(self) -> None:
        """Test that a face square stops where the chamfer starts."""
        polygon = face_square(1, 1.0, 1.0, 0.8)

        self.assertEqual(
            {(point.x, point.z) for point in polygon.points},
            {(-0.8, -0.8), (0.8, -0.8), (0.8, 0.8), (-0.8, 0.8)},
        )

    def test_edge_quad_is_a_chamfer(self) -> None:
        """Test that an edge quad cuts at 45 degrees between two faces."""
        polygon = edge_quad((0, 1), (1.0, 1.0), 1.0, 0.8)

        self.assertEqual(len(polygon.points), 4)
        self.assertAlmostEqual(polygon.normal.x, polygon.normal.y, PLACES)
        self.assertAlmostEqual(polygon.normal.z, 0.0, PLACES)
        self.assertGreater(polygon.normal.x, 0.0)

    def test_corner_triangle_is_a_chamfer(self) -> None:
        """Test that a corner triangle cuts equally on the three axes."""
        polygon = corner_triangle((1.0, 1.0, -1.0), 1.0, 0.8)

        self.assertEqual(len(polygon.points), AXIS_NUMBER)
        self.assertAlmostEqual(polygon.normal.x, polygon.normal.y, PLACES)
        self.assertAlmostEqual(polygon.normal.x, -polygon.normal.z, PLACES)

    def test_body_is_a_chamfered_cube(self) -> None:
        """Test that the plastic has faces, edges and corners."""
        polygons = body_polygons(1.0, 0.2)

        self.assertEqual(len(polygons), BODY_POLYGON_COUNT)
        self.assertEqual(
            Counter(len(polygon.points) for polygon in polygons),
            Counter({4: 18, 3: 8}),
        )
        self.assertEqual(
            {polygon.face for polygon in polygons},
            {BODY_FACE},
        )

    def test_body_uses_the_same_corners(self) -> None:
        """Test that the chamfers share the corners of the faces."""
        polygons = body_polygons(1.0, 0.2)

        positions = {
            tuple(point)
            for polygon in polygons
            for point in polygon.points
        }

        self.assertEqual(len(positions), 24)

    def test_stickers_face_outward(self) -> None:
        """Test that each sticker sits on its own face of the cubie."""
        polygons = sticker_polygons(1.0, 0.2, 0.1, 0.01)

        self.assertEqual(len(polygons), FACE_NUMBER)

        for face, polygon in enumerate(polygons):
            with self.subTest(face=face):
                self.assertEqual(polygon.face, face)
                self.assertEqual(polygon.normal, FACE_BASES[face].normal)

    def test_stickers_float_above_the_plastic(self) -> None:
        """Test that a sticker stands just outside the face it covers."""
        polygon = sticker_polygons(1.0, 0.2, 0.1, 0.01)[0]

        self.assertEqual([point.y for point in polygon.points], [1.01] * 4)

    def test_stickers_stay_inside_the_face(self) -> None:
        """Test that a sticker never overflows the square it sits on."""
        polygon = sticker_polygons(1.0, 0.2, 0.1, 0.01)[0]

        for point in polygon.points:
            with self.subTest(point=point):
                self.assertAlmostEqual(abs(point.x), 0.72, PLACES)
                self.assertAlmostEqual(abs(point.z), 0.72, PLACES)


class TestBuildMesh(unittest.TestCase):
    """Tests for the build_mesh function."""

    def test_triangulates_a_fan(self) -> None:
        """Test that a polygon of n corners gives n - 2 triangles."""
        polygon = Polygon(
            (
                Vec3(0.0, 0.0, 0.0),
                Vec3(1.0, 0.0, 0.0),
                Vec3(1.0, 1.0, 0.0),
                Vec3(0.0, 1.0, 0.0),
            ),
            Vec3(0.0, 0.0, 1.0),
            0,
        )

        mesh = build_mesh([polygon])

        self.assertEqual(mesh.triangle_count, 2)
        self.assertEqual(mesh.indices, (0, 1, 2, 0, 2, 3))

    def test_never_shares_a_vertex(self) -> None:
        """Test that each polygon brings its own vertices, and normal."""
        first = Polygon(
            (Vec3(0.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0), Vec3(1.0, 1.0, 0.0)),
            Vec3(0.0, 0.0, 1.0),
            0,
        )
        second = Polygon(first.points, Vec3(0.0, 1.0, 0.0), 1)

        mesh = build_mesh([first, second])

        self.assertEqual(len(mesh.vertices), 6)
        self.assertEqual(mesh.indices, (0, 1, 2, 3, 4, 5))
        self.assertEqual(mesh.vertices[0].face, 0)
        self.assertEqual(mesh.vertices[3].face, 1)

    def test_builds_nothing_from_nothing(self) -> None:
        """Test that an empty mesh is a valid answer."""
        mesh = build_mesh([])

        self.assertEqual(mesh.vertices, ())
        self.assertEqual(mesh.triangle_count, 0)


class TestCubieMesh(unittest.TestCase):
    """Tests for the mesh of a single cubie."""

    def setUp(self) -> None:
        """Build the mesh of a cubie of half extent one."""
        self.mesh = build_cubie_mesh()

    def test_size(self) -> None:
        """Test the vertex and triangle counts of a cubie."""
        self.assertEqual(len(self.mesh.vertices), VERTEX_COUNT)
        self.assertEqual(self.mesh.triangle_count, TRIANGLE_COUNT)

    def test_faces_outward(self) -> None:
        """
        Test that every triangle is wound counter clockwise outside.

        This is what lets the renderer cull back faces: a triangle whose
        winding disagreed with its normal would vanish, or show through.
        """
        for index, (first, second, third) in enumerate(triangles(self.mesh)):
            with self.subTest(triangle=index):
                winding = (second.position - first.position).cross(
                    third.position - first.position,
                ).normalized()

                self.assertAlmostEqual(
                    winding.dot(first.normal), 1.0, PLACES,
                )

    def test_normals_are_unit(self) -> None:
        """Test that no normal needs to be normalized by a shader."""
        for index, vertex in enumerate(self.mesh.vertices):
            with self.subTest(vertex=index):
                self.assertAlmostEqual(vertex.normal.length(), 1.0, PLACES)

    def test_body_is_watertight(self) -> None:
        """
        Test that the plastic has no hole: every edge is shared twice.

        A chamfered cube is a closed solid, and stays one whatever the
        bevel: a missing polygon would show as an edge used only once.
        """
        edges: Counter[frozenset[tuple[float, ...]]] = Counter()

        for first, second, third in triangles(self.mesh):
            if first.face != BODY_FACE:
                continue

            corners = [tuple(vertex.position) for vertex in (
                first, second, third,
            )]

            for index, corner in enumerate(corners):
                edges[frozenset((corner, corners[(index + 1) % 3]))] += 1

        self.assertEqual(set(edges.values()), {2})

    def test_one_sticker_per_face(self) -> None:
        """Test that each face carries exactly one sticker quad."""
        faces = Counter(
            vertex.face for vertex in self.mesh.vertices
            if vertex.face != BODY_FACE
        )

        self.assertEqual(
            faces,
            Counter(dict.fromkeys(range(FACE_NUMBER), 4)),
        )

    def test_stays_within_its_extent(self) -> None:
        """Test that nothing but the sticker lift leaves the cubie."""
        reach = 1.0 + STICKER_LIFT

        for index, vertex in enumerate(self.mesh.vertices):
            with self.subTest(vertex=index):
                self.assertLessEqual(
                    max(abs(coordinate) for coordinate in vertex.position),
                    reach,
                )

    def test_scales_with_its_half_extent(self) -> None:
        """Test that a smaller cubie is the same shape, scaled down."""
        small = build_cubie_mesh(0.25)

        for index, vertex in enumerate(small.vertices):
            with self.subTest(vertex=index):
                self.assertEqual(
                    vertex.position,
                    self.mesh.vertices[index].position.scaled(0.25),
                )
                self.assertEqual(
                    vertex.normal,
                    self.mesh.vertices[index].normal,
                )

    def test_bevel_can_be_tuned(self) -> None:
        """Test that a wider bevel eats into the face squares."""
        beveled = build_cubie_mesh(bevel=CUBIE_BEVEL * 2)

        self.assertLess(
            max(abs(vertex.position.x) for vertex in beveled.vertices
                if vertex.face == FACE_INDEXES['U']),
            max(abs(vertex.position.x) for vertex in self.mesh.vertices
                if vertex.face == FACE_INDEXES['U']),
        )

    def test_margin_can_be_tuned(self) -> None:
        """Test that a wider margin shrinks the stickers."""
        inset = build_cubie_mesh(margin=STICKER_MARGIN * 2)

        self.assertLess(
            max(abs(vertex.position.x) for vertex in inset.vertices
                if vertex.face == FACE_INDEXES['U']),
            max(abs(vertex.position.x) for vertex in self.mesh.vertices
                if vertex.face == FACE_INDEXES['U']),
        )

    def test_lift_can_be_tuned(self) -> None:
        """Test that a higher lift raises the stickers."""
        raised = build_cubie_mesh(lift=STICKER_LIFT * 2)

        self.assertAlmostEqual(
            max(vertex.position.y for vertex in raised.vertices),
            1.0 + STICKER_LIFT * 2,
            PLACES,
        )


class TestMeshPacking(unittest.TestCase):
    """Tests for the serialization of a mesh."""

    def setUp(self) -> None:
        """Build the mesh of a cubie of half extent one."""
        self.mesh = build_cubie_mesh()

    def test_vertex_buffer_size(self) -> None:
        """Test that a vertex takes a position, a normal and an index."""
        self.assertEqual(
            len(self.mesh.pack_vertices()),
            VERTEX_COUNT * VERTEX_SIZE,
        )

    def test_index_buffer_size(self) -> None:
        """Test that an index takes four bytes."""
        self.assertEqual(
            len(self.mesh.pack_indices()),
            TRIANGLE_COUNT * 3 * INDEX_SIZE,
        )

    def test_vertex_buffer_content(self) -> None:
        """Test that a vertex is packed as the shader expects it."""
        vertex = self.mesh.vertices[0]

        self.assertEqual(
            self.mesh.pack_vertices()[:VERTEX_SIZE],
            struct.pack(
                '<6fi',
                *vertex.position,
                *vertex.normal,
                vertex.face,
            ),
        )

    def test_index_buffer_content(self) -> None:
        """Test that the indices are packed as unsigned integers."""
        self.assertEqual(
            struct.unpack('<3I', self.mesh.pack_indices()[:12]),
            self.mesh.indices[:3],
        )


class TestCubieGrid(unittest.TestCase):
    """Tests for the placement of the cubies of a cube."""

    def test_half_leaves_a_gap(self) -> None:
        """Test that a cubie is slightly smaller than its slot."""
        for size in SIZES:
            with self.subTest(size=size):
                self.assertLess(cubie_half(size), CUBE_EXTENT / size)
                self.assertAlmostEqual(
                    cubie_half(size),
                    CUBE_EXTENT * (1 - CUBIE_GAP) / size,
                    PLACES,
                )

    def test_centers_span_the_cube(self) -> None:
        """Test that the outer cubies reach the extent of the cube."""
        for size in SIZES:
            with self.subTest(size=size):
                first = cubie_center(0, 0, 0, size)
                last = cubie_center(size - 1, size - 1, size - 1, size)

                self.assertAlmostEqual(
                    first.x, -CUBE_EXTENT + CUBE_EXTENT / size, PLACES,
                )
                self.assertAlmostEqual(
                    last.x, CUBE_EXTENT - CUBE_EXTENT / size, PLACES,
                )

    def test_centers_are_evenly_spread(self) -> None:
        """Test that two neighbours are exactly one slot apart."""
        size = 5
        slot = 2 * CUBE_EXTENT / size

        for index in range(size - 1):
            with self.subTest(index=index):
                self.assertAlmostEqual(
                    cubie_center(index + 1, 0, 0, size).x
                    - cubie_center(index, 0, 0, size).x,
                    slot,
                    PLACES,
                )

    def test_center_of_an_odd_cube(self) -> None:
        """Test that the middle cubie of an odd cube sits at the origin."""
        self.assertEqual(cubie_center(1, 1, 1, 3), Vec3(0.0, 0.0, 0.0))

    def test_surface(self) -> None:
        """Test which cubies of a 3x3x3 can be seen."""
        self.assertTrue(is_surface(0, 1, 1, 3))
        self.assertTrue(is_surface(2, 2, 2, 3))
        self.assertFalse(is_surface(1, 1, 1, 3))

    def test_everything_is_surface_on_a_small_cube(self) -> None:
        """Test that a 2x2x2 has nothing to hide."""
        for x in range(2):
            for y in range(2):
                for z in range(2):
                    with self.subTest(cubie=(x, y, z)):
                        self.assertTrue(is_surface(x, y, z, 2))


class TestBuildCubies(unittest.TestCase):
    """Tests for the instances of a cube of a given size."""

    def test_count(self) -> None:
        """Test that a cube of size N keeps N³ - (N - 2)³ cubies."""
        for size in SIZES:
            with self.subTest(size=size):
                self.assertEqual(
                    len(build_cubies(size)),
                    size ** 3 - max(size - 2, 0) ** 3,
                )

    def test_known_counts(self) -> None:
        """Test the counts the plan is written against."""
        self.assertEqual(len(build_cubies(2)), 8)
        self.assertEqual(len(build_cubies(3)), 26)
        self.assertEqual(len(build_cubies(7)), 218)

    def test_drops_the_inner_cubies(self) -> None:
        """Test that no cubie buried inside the cube is generated."""
        size = 5

        for cubie in build_cubies(size):
            with self.subTest(cubie=cubie):
                self.assertTrue(is_surface(cubie.x, cubie.y, cubie.z, size))

    def test_has_no_duplicate(self) -> None:
        """Test that a slot of the grid is filled at most once."""
        cubies = build_cubies(4)

        self.assertEqual(
            len({(cubie.x, cubie.y, cubie.z) for cubie in cubies}),
            len(cubies),
        )

    def test_carries_its_center(self) -> None:
        """Test that a cubie knows where it stands."""
        for cubie in build_cubies(3):
            with self.subTest(cubie=cubie):
                self.assertEqual(
                    cubie.center,
                    cubie_center(cubie.x, cubie.y, cubie.z, 3),
                )

    def test_stays_within_the_cube(self) -> None:
        """Test that no cubie sticks out of the bounding cube."""
        for size in SIZES:
            half = cubie_half(size)

            for cubie in build_cubies(size):
                with self.subTest(size=size, cubie=cubie):
                    self.assertLessEqual(
                        max(abs(c) for c in cubie.center) + half,
                        CUBE_EXTENT,
                    )


class TestCubeGeometry(unittest.TestCase):
    """Tests for the geometry of a whole cube."""

    def test_gathers_the_mesh_and_the_instances(self) -> None:
        """Test that everything the renderer needs comes out at once."""
        geometry = build_cube_geometry(3)

        self.assertEqual(geometry.size, 3)
        self.assertEqual(geometry.half, cubie_half(3))
        self.assertEqual(geometry.cubies, build_cubies(3))
        self.assertEqual(geometry.mesh, build_cubie_mesh(cubie_half(3)))

    def test_shares_one_mesh_whatever_the_size(self) -> None:
        """Test that a bigger cube stays a single draw call."""
        for size in SIZES:
            with self.subTest(size=size):
                geometry = build_cube_geometry(size)

                self.assertEqual(
                    len(geometry.mesh.vertices),
                    VERTEX_COUNT,
                )


class TestCubeGeometryRadius(unittest.TestCase):
    """Tests for the sphere a whole cube fits in."""

    @staticmethod
    def farthest(geometry: CubeGeometry) -> float:
        """
        Measure the exact radius, by walking every vertex of every cubie.

        Returns:
            The distance of the farthest point of the cube to the origin.

        """
        return max(
            (cubie.center + vertex.position).length()
            for cubie in geometry.cubies
            for vertex in geometry.mesh.vertices
        )

    def test_holds_the_whole_cube(self) -> None:
        """Test that no point of the cube lies outside the sphere."""
        for size in SIZES:
            with self.subTest(size=size):
                geometry = build_cube_geometry(size)

                self.assertGreaterEqual(
                    geometry.radius,
                    self.farthest(geometry),
                )

    def test_holds_it_tightly(self) -> None:
        """Test that the bound stays within a tenth of a percent."""
        for size in SIZES:
            with self.subTest(size=size):
                geometry = build_cube_geometry(size)

                self.assertLess(
                    geometry.radius / self.farthest(geometry),
                    1.001,
                )

    def test_stays_inside_the_bounding_box(self) -> None:
        """Test that a cube never reaches the corners of its box."""
        for size in SIZES:
            with self.subTest(size=size):
                self.assertLess(
                    build_cube_geometry(size).radius,
                    math.sqrt(3) * CUBE_EXTENT,
                )

    def test_grows_with_the_size(self) -> None:
        """
        Test that a bigger cube fills its box better.

        The gap and the chamfer both shrink with the cubie they are a
        fraction of, so the corners of a 7x7x7 reach much closer to the
        corners of the box than those of a 2x2x2. This is exactly what
        the framing has to make up for.
        """
        radii = [build_cube_geometry(size).radius for size in SIZES]

        self.assertEqual(radii, sorted(radii))


class TestCoreRadius(unittest.TestCase):
    """Tests for the size of the ball core."""

    def test_reaches_past_the_cavity(self) -> None:
        """
        Test that the core comes out of the hollow of the cube.

        The cavity left by the outer layer is what a hole dug by the mask
        opens onto: a core flush with it would sit at the very bottom of
        that shaft, where its own wall hides it.
        """
        for size in SIZES:
            with self.subTest(size=size):
                cavity = CUBE_EXTENT - CUBE_EXTENT / size - cubie_half(size)

                self.assertGreater(core_radius(size), cavity)

    def test_stays_under_the_surface(self) -> None:
        """
        Test that the core never comes out of the cube.

        It sinks into the pieces, and must stop inside their plastic: a
        core reaching the skin would draw on the silhouette.
        """
        for size in SIZES:
            with self.subTest(size=size):
                surface = CUBE_EXTENT - CUBE_EXTENT / size + cubie_half(size)

                self.assertLess(core_radius(size), surface)

    def test_sinks_the_same_share_of_every_layer(self) -> None:
        """
        Test that the core keeps its proportions whatever the size.

        The bulge is a fraction of the half extent of a cubie, so the
        core buries itself in the same share of the outer layer from a
        2x2x2 to a 7x7x7.
        """
        shares = {
            round(
                (core_radius(size) - (
                    CUBE_EXTENT - CUBE_EXTENT / size - cubie_half(size)
                )) / (2 * cubie_half(size)),
                PLACES,
            )
            for size in SIZES
        }

        self.assertEqual(len(shares), 1)

    def test_grows_with_the_size(self) -> None:
        """Test that a bigger cube leaves room for a bigger core."""
        radii = [core_radius(size) for size in SIZES]

        self.assertEqual(radii, sorted(radii))

    def test_rejects_a_null_or_negative_size(self) -> None:
        """Test that a core needs a cube to sit in."""
        for size in (0, -1):
            with (
                    self.subTest(size=size),
                    self.assertRaises(InvalidCubeSizeError),
            ):
                core_radius(size)


class TestCoreMesh(unittest.TestCase):
    """Tests for the sphere of the ball core."""

    def setUp(self) -> None:
        """Build the mesh every test of the class reads."""
        self.radius = 0.75
        self.mesh = build_core_mesh(
            self.radius,
            rings=CORE_TEST_RINGS,
            segments=CORE_TEST_SEGMENTS,
        )

    def test_counts_its_triangles(self) -> None:
        """
        Test that the grid is cut as a sphere is.

        Two triangles per cell, but a single one against each pole, where
        two corners of the cell are the same point.
        """
        self.assertEqual(
            self.mesh.triangle_count,
            CORE_TEST_SEGMENTS * (2 * CORE_TEST_RINGS - 2),
        )

    def test_every_vertex_sits_on_the_sphere(self) -> None:
        """Test that the mesh is a sphere of the radius it was given."""
        for index, vertex in enumerate(self.mesh.vertices):
            with self.subTest(vertex=index):
                self.assertAlmostEqual(
                    vertex.position.length(), self.radius, PLACES,
                )

    def test_normals_are_the_directions_of_their_vertices(self) -> None:
        """
        Test that the core is shaded as a smooth sphere.

        The one mesh of the backend whose normals are not those of its
        polygons: on a sphere centered on the origin, the smooth normal
        of a vertex is the direction of the vertex itself.
        """
        for index, vertex in enumerate(self.mesh.vertices):
            with self.subTest(vertex=index):
                self.assertAlmostEqual(vertex.normal.length(), 1.0, PLACES)
                self.assertAlmostEqual(
                    vertex.normal.dot(vertex.position), self.radius, PLACES,
                )

    def test_belongs_to_no_face(self) -> None:
        """Test that the core takes no sticker color."""
        self.assertEqual(
            {vertex.face for vertex in self.mesh.vertices},
            {BODY_FACE},
        )

    def test_faces_outward(self) -> None:
        """Test that no triangle of the core is culled from outside."""
        for index, (first, second, third) in enumerate(triangles(self.mesh)):
            with self.subTest(triangle=index):
                winding = (second.position - first.position).cross(
                    third.position - first.position,
                )

                centroid = first.position + second.position + third.position

                self.assertGreater(winding.dot(centroid), 0.0)

    def test_is_watertight(self) -> None:
        """
        Test that the sphere has no hole: every edge is shared twice.

        The poles and the seam where the meridians wrap around are where
        this breaks: the sine of pi is not zero in floating point, so a
        pole computed rather than placed lands a hair away from the axis,
        differently for every cell around it.
        """
        edges: Counter[frozenset[tuple[float, ...]]] = Counter()

        for first, second, third in triangles(self.mesh):
            corners = [tuple(vertex.position) for vertex in (
                first, second, third,
            )]

            for index, corner in enumerate(corners):
                edges[frozenset((corner, corners[(index + 1) % 3]))] += 1

        self.assertEqual(set(edges.values()), {2})

    def test_scales_with_its_radius(self) -> None:
        """Test that a smaller core is the same sphere, scaled down."""
        small = build_core_mesh(
            self.radius / 3,
            rings=CORE_TEST_RINGS,
            segments=CORE_TEST_SEGMENTS,
        )

        self.assertEqual(small.indices, self.mesh.indices)

        for index, (tight, wide) in enumerate(
                zip(small.vertices, self.mesh.vertices, strict=True),
        ):
            with self.subTest(vertex=index):
                self.assertAlmostEqual(
                    (tight.position.scaled(3) - wide.position).length(),
                    0.0,
                    PLACES,
                )


class TestPackCore(unittest.TestCase):
    """Tests for the vertex buffer of the ball core."""

    def test_holds_every_vertex(self) -> None:
        """Test that the buffer covers the whole mesh."""
        mesh = build_core_mesh(1.0, rings=CORE_TEST_RINGS, segments=3)

        self.assertEqual(
            len(pack_core(mesh)),
            len(mesh.vertices) * CORE_VERTEX_SIZE,
        )

    def test_carries_position_and_normal(self) -> None:
        """Test that a vertex travels without its face index."""
        mesh = build_core_mesh(1.0, rings=CORE_TEST_RINGS, segments=3)
        packed = pack_core(mesh)

        for index, vertex in enumerate(mesh.vertices):
            read = struct.unpack_from(
                CORE_VERTEX_PACKING, packed, index * CORE_VERTEX_SIZE,
            )

            for channel, value in enumerate((*vertex.position, *vertex.normal)):
                with self.subTest(vertex=index, channel=channel):
                    self.assertAlmostEqual(read[channel], value, SINGLE_PLACES)


class TestPackAxes(unittest.TestCase):
    """Tests for the line buffer of the three axes."""

    def test_one_segment_per_axis(self) -> None:
        """Test that the buffer holds two vertices per axis."""
        self.assertEqual(len(axes_vertices(1.0)), AXES_VERTEX_COUNT)

    def test_every_segment_starts_at_the_center(self) -> None:
        """Test that an axis is drawn from the center of the cube."""
        for index, vertex in enumerate(axes_vertices(2.0)[::2]):
            with self.subTest(axis=index):
                self.assertEqual(vertex[:3], (0.0, 0.0, 0.0))

    def test_every_segment_reaches_the_length(self) -> None:
        """Test that an axis reaches as far as it is asked to."""
        self.assertEqual(
            [vertex[:3] for vertex in axes_vertices(2.0)[1::2]],
            [(2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0)],
        )

    def test_colors_name_the_axes(self) -> None:
        """Test that both ends of an axis carry the color naming it."""
        self.assertEqual(
            [vertex[3:] for vertex in axes_vertices(1.0)],
            [color for color in AXES_COLORS for _ in range(2)],
        )


class TestInvalidSize(unittest.TestCase):
    """Tests for the sizes no geometry can be built for."""

    def test_rejects_a_null_or_negative_size(self) -> None:
        """Test that a cube needs at least one cubie per axis."""
        for size in (0, -1):
            for build in (cubie_half, build_cubies, build_cube_geometry):
                with (
                        self.subTest(size=size, build=build.__name__),
                        self.assertRaises(InvalidCubeSizeError),
                ):
                    build(size)
