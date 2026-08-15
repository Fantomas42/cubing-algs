"""
Geometry of the GPU rendering backend.

Builds the mesh of one beveled cubie, and the instances placing it for a
cube of any size. Every piece of the cube shares that single mesh: it is
uploaded once and drawn in a single instanced call, whatever the size.

Pure Python, no GPU here. The cube spans ``[-1, 1]`` on each axis
whatever its size, exactly as ``display/image.py`` does, so both
backends frame the same scene.

A cubie is a chamfered cube: six square faces, twelve quads cutting its
edges, eight triangles cutting its corners, plus six sticker quads
floating just above the faces. The stickers carry the index of their
face in ``FACE_ORDER``; the plastic carries ``BODY_FACE``.

The ball core lives here too: a sphere filling the middle of the cube,
which the outer pieces hide until a hole is dug in them or a groove is
looked straight down.
"""
import math
import struct
from collections.abc import Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from typing import NamedTuple

from cubing_algs.display.gl.constants import AXES_COLORS
from cubing_algs.display.gl.constants import CORE_BULGE
from cubing_algs.display.gl.constants import CORE_RINGS
from cubing_algs.display.gl.constants import CORE_SEGMENTS
from cubing_algs.display.gl.constants import CUBIE_BEVEL
from cubing_algs.display.gl.constants import CUBIE_GAP
from cubing_algs.display.gl.constants import STICKER_LIFT
from cubing_algs.display.gl.constants import STICKER_MARGIN
from cubing_algs.display.gl.transforms import AXIS_X
from cubing_algs.display.gl.transforms import AXIS_Y
from cubing_algs.display.gl.transforms import AXIS_Z
from cubing_algs.display.gl.transforms import ORIGIN
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.exceptions import InvalidCubeSizeError

# Half extent of the whole cube on each axis, as in display/image.py.
CUBE_EXTENT = 1.0

# Number of axes of the space, and the two directions of each of them.
AXIS_NUMBER = 3
SIGNS = (-1.0, 1.0)

# The three axes of the grid, in the order their colors are given in.
AXES = (AXIS_X, AXIS_Y, AXIS_Z)

# Corners of a quad, in the tangent frame of its plane, wound counter
# clockwise when seen from outside.
QUAD_CORNERS = ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0))

# Face index of the plastic, which belongs to no face and takes no
# sticker color.
BODY_FACE = -1

# Layout of a vertex in the buffer, as moderngl reads it: position,
# normal, face index.
VERTEX_FORMAT = '3f 3f 1i'
VERTEX_ATTRIBUTES = ('in_position', 'in_normal', 'in_face')
VERTEX_PACKING = '<6fi'

# Layout of a vertex of the axes, as moderngl reads it: position, color.
AXES_VERTEX_FORMAT = '3f 3f'
AXES_VERTEX_ATTRIBUTES = ('in_position', 'in_color')
AXES_VERTEX_PACKING = '<6f'

# Layout of a vertex of the ball core: position, normal. It belongs to no
# face and takes no sticker color, so the face index of a cubie vertex
# would travel for nothing.
CORE_VERTEX_FORMAT = '3f 3f'
CORE_VERTEX_ATTRIBUTES = ('in_position', 'in_normal')
CORE_VERTEX_PACKING = '<6f'


class FaceBasis(NamedTuple):
    """
    Orientation of one face of a cubie.

    The three vectors form a right handed frame, ``right`` crossed with
    ``up`` giving ``normal``, so that a quad wound along ``QUAD_CORNERS``
    faces outward.
    """

    normal: Vec3
    right: Vec3
    up: Vec3


# The six faces, in the order of FACE_ORDER: U, R, F, D, L, B.
FACE_BASES: tuple[FaceBasis, ...] = (
    FaceBasis(AXIS_Y, AXIS_X, -AXIS_Z),
    FaceBasis(AXIS_X, -AXIS_Z, AXIS_Y),
    FaceBasis(AXIS_Z, AXIS_X, AXIS_Y),
    FaceBasis(-AXIS_Y, AXIS_X, AXIS_Z),
    FaceBasis(-AXIS_X, AXIS_Z, AXIS_Y),
    FaceBasis(-AXIS_Z, -AXIS_X, AXIS_Y),
)


class Vertex(NamedTuple):
    """One vertex of a mesh, with the face its sticker belongs to."""

    position: Vec3
    normal: Vec3
    face: int


class Polygon(NamedTuple):
    """A flat convex polygon, wound counter clockwise seen from outside."""

    points: tuple[Vec3, ...]
    normal: Vec3
    face: int


class Mesh(NamedTuple):
    """
    An indexed triangle mesh, ready to be uploaded to the GPU.

    Vertices are never shared between two polygons: each one carries the
    normal of its own face, which is what gives the cubie its flat,
    faceted look.
    """

    vertices: tuple[Vertex, ...]
    indices: tuple[int, ...]

    @property
    def triangle_count(self) -> int:
        """
        Count the triangles of the mesh.

        Returns:
            The number of triangles.

        """
        return len(self.indices) // 3

    def pack_vertices(self) -> bytes:
        """
        Serialize the vertices for a vertex buffer.

        Returns:
            The vertices, laid out as ``VERTEX_FORMAT`` describes them.

        """
        return b''.join(
            struct.pack(
                VERTEX_PACKING,
                *vertex.position,
                *vertex.normal,
                vertex.face,
            )
            for vertex in self.vertices
        )

    def pack_indices(self) -> bytes:
        """
        Serialize the triangles for an index buffer.

        Returns:
            The indices, as unsigned 32 bit integers.

        """
        return struct.pack(f'<{ len(self.indices) }I', *self.indices)


class Cubie(NamedTuple):
    """
    One piece of the cube, placed on its grid.

    The three indices run from ``0`` to ``size - 1``, from L to R, from
    D to U and from B to F, which is the order the facelets of a face
    are read in.
    """

    x: int
    y: int
    z: int
    center: Vec3


@dataclass(frozen=True, slots=True)
class CubeGeometry:
    """The mesh of a cubie and the instances drawing a whole cube with it."""

    size: int
    half: float
    mesh: Mesh
    cubies: tuple[Cubie, ...]

    @property
    def radius(self) -> float:
        """
        Measure the sphere the whole cube fits in.

        The cube never quite fills the ``[-1, 1]`` box it is laid out in:
        the gap eats ``CUBIE_GAP / size`` of it and the chamfer cuts the
        corners it would have reached, both by an amount that depends on
        the size. A camera framing the box would therefore draw a 2x2x2
        smaller than a 7x7x7; one framing this radius draws them alike.

        Bounded rather than walked: the farthest point of the cube can
        never lie beyond the farthest cubie plus the farthest vertex of
        the mesh, and that bound stays within a twentieth of a percent of
        the exact radius at every size, for a hundredth of the cost.

        Returns:
            The radius of the bounding sphere of the cube, in world
            units.

        """
        return (
            max(cubie.center.length() for cubie in self.cubies)
            + max(vertex.position.length() for vertex in self.mesh.vertices)
        )


def build_point(assignments: Iterable[tuple[int, float]]) -> Vec3:
    """
    Build a point from its coordinates, given by axis index.

    Args:
        assignments: The (axis, value) pairs, any missing axis staying
            at zero.

    Returns:
        The point.

    """
    values = [0.0, 0.0, 0.0]

    for axis, value in assignments:
        values[axis] = value

    return Vec3(*values)


def other_axes(axis: int) -> tuple[int, int]:
    """
    Name the two axes orthogonal to one axis.

    Args:
        axis: The axis to exclude.

    Returns:
        The two remaining axis indices, in increasing order.

    """
    first, second = (other for other in range(AXIS_NUMBER) if other != axis)

    return (first, second)


def oriented(points: tuple[Vec3, ...], face: int) -> Polygon:
    """
    Wind a polygon of a cubie counter clockwise, seen from outside.

    A cubie is convex and centered on the origin, so a polygon faces
    outward exactly when its normal points away from the origin: no
    winding table is needed, the geometry says it.

    Args:
        points: The corners of the polygon, in either winding.
        face: Index of the face the polygon belongs to, or ``BODY_FACE``.

    Returns:
        The polygon, wound outward, with its normal.

    """
    normal = (points[1] - points[0]).cross(
        points[2] - points[0],
    ).normalized()

    centroid = ORIGIN
    for point in points:
        centroid += point

    if normal.dot(centroid) < 0:
        return Polygon(tuple(reversed(points)), -normal, face)

    return Polygon(points, normal, face)


def face_square(axis: int, sign: float, half: float, inner: float) -> Polygon:
    """
    Build the flat square left on one side of a cubie by the bevel.

    Args:
        axis: The axis the face is orthogonal to.
        sign: Which side of that axis the face sits on.
        half: Half extent of the cubie.
        inner: Half extent of the square, the bevel removed.

    Returns:
        The polygon of the face, in plastic.

    """
    first, second = other_axes(axis)

    return oriented(
        tuple(
            build_point((
                (axis, sign * half),
                (first, right * inner),
                (second, up * inner),
            ))
            for right, up in QUAD_CORNERS
        ),
        BODY_FACE,
    )


def edge_quad(
        axes: tuple[int, int],
        signs: tuple[float, float],
        half: float,
        inner: float,
) -> Polygon:
    """
    Build the chamfer cutting the edge shared by two faces.

    Args:
        axes: Axes of the two faces meeting along the edge.
        signs: Which side of each of those axes they sit on.
        half: Half extent of the cubie.
        inner: Half extent of a face square, the bevel removed.

    Returns:
        The polygon of the chamfer, in plastic.

    """
    first, second = axes
    first_sign, second_sign = signs

    third, = (
        axis for axis in range(AXIS_NUMBER)
        if axis not in {first, second}
    )

    return oriented(
        tuple(
            build_point((
                (first, first_sign * (half if on_first else inner)),
                (second, second_sign * (inner if on_first else half)),
                (third, depth * inner),
            ))
            for on_first, depth in (
                (True, -1.0), (True, 1.0), (False, 1.0), (False, -1.0),
            )
        ),
        BODY_FACE,
    )


def corner_triangle(
        signs: tuple[float, float, float],
        half: float,
        inner: float,
) -> Polygon:
    """
    Build the chamfer cutting one corner of a cubie.

    Args:
        signs: Which side of each axis the corner sits on.
        half: Half extent of the cubie.
        inner: Half extent of a face square, the bevel removed.

    Returns:
        The triangle of the chamfer, in plastic.

    """
    return oriented(
        tuple(
            build_point(
                (
                    (axis, signs[axis] * (half if axis == extremal else inner))
                    for axis in range(AXIS_NUMBER)
                ),
            )
            for extremal in range(AXIS_NUMBER)
        ),
        BODY_FACE,
    )


def body_polygons(half: float, bevel: float) -> list[Polygon]:
    """
    Build the plastic of a cubie, faces and chamfers.

    Args:
        half: Half extent of the cubie.
        bevel: Width of the chamfer cutting its edges and corners.

    Returns:
        The polygons of the body: six squares, twelve edge quads and
        eight corner triangles.

    """
    inner = half - bevel

    faces = [
        face_square(axis, sign, half, inner)
        for axis in range(AXIS_NUMBER)
        for sign in SIGNS
    ]

    edges = [
        edge_quad((first, second), (first_sign, second_sign), half, inner)
        for first in range(AXIS_NUMBER)
        for second in range(first + 1, AXIS_NUMBER)
        for first_sign in SIGNS
        for second_sign in SIGNS
    ]

    corners = [
        corner_triangle((x_sign, y_sign, z_sign), half, inner)
        for x_sign in SIGNS
        for y_sign in SIGNS
        for z_sign in SIGNS
    ]

    return faces + edges + corners


def sticker_polygons(
        half: float,
        bevel: float,
        margin: float,
        lift: float,
) -> list[Polygon]:
    """
    Build the six stickers of a cubie, one per face.

    A sticker is always built, even for an inner side of the cubie that
    no one will ever see: which ones are actually colored is the job of
    the scene, and drawing them all keeps a single shared mesh.

    Args:
        half: Half extent of the cubie.
        bevel: Width of the chamfer cutting its edges and corners.
        margin: Inset of the sticker from the border of its face square.
        lift: How far the sticker floats above the plastic.

    Returns:
        The polygons of the stickers, in the order of ``FACE_ORDER``.

    """
    extent = (half - bevel) * (1 - margin)
    height = half + lift

    return [
        Polygon(
            tuple(
                basis.normal.scaled(height)
                + basis.right.scaled(right * extent)
                + basis.up.scaled(up * extent)
                for right, up in QUAD_CORNERS
            ),
            basis.normal,
            face,
        )
        for face, basis in enumerate(FACE_BASES)
    ]


def build_mesh(polygons: Sequence[Polygon]) -> Mesh:
    """
    Triangulate polygons into an indexed mesh.

    Each polygon is convex, so a fan around its first corner covers it
    without any further work.

    Args:
        polygons: The polygons to triangulate.

    Returns:
        The mesh of the polygons.

    """
    vertices: list[Vertex] = []
    indices: list[int] = []

    for polygon in polygons:
        base = len(vertices)

        vertices.extend(
            Vertex(point, polygon.normal, polygon.face)
            for point in polygon.points
        )

        for step in range(1, len(polygon.points) - 1):
            indices.extend((base, base + step, base + step + 1))

    return Mesh(tuple(vertices), tuple(indices))


def build_cubie_mesh(
        half: float = 1.0,
        *,
        bevel: float = CUBIE_BEVEL,
        margin: float = STICKER_MARGIN,
        lift: float = STICKER_LIFT,
) -> Mesh:
    """
    Build the mesh of a single beveled cubie, centered on the origin.

    Args:
        half: Half extent of the cubie.
        bevel: Width of the chamfer, as a fraction of ``half``.
        margin: Inset of a sticker from the border of its face square,
            as a fraction of that square.
        lift: How far a sticker floats above the plastic, as a fraction
            of ``half``.

    Returns:
        The mesh of the cubie: plastic first, then the six stickers.

    """
    return build_mesh(
        body_polygons(half, half * bevel)
        + sticker_polygons(half, half * bevel, margin, half * lift),
    )


def check_size(size: int) -> None:
    """
    Reject a cube size no geometry can be built for.

    Args:
        size: Size of the cube.

    Raises:
        InvalidCubeSizeError: When the size is not strictly positive.

    """
    if size <= 0:
        msg = f'Cube size must be positive, got { size }'
        raise InvalidCubeSizeError(msg)


def cubie_half(size: int) -> float:
    """
    Compute the half extent of a cubie of a cube of a given size.

    The gap between neighbours is taken here, which is what draws the
    grooves of the cube: the slots themselves stay perfectly adjacent.

    Args:
        size: Size of the cube.

    Returns:
        The half extent of a cubie, in world units.

    """
    check_size(size)

    return CUBE_EXTENT * (1 - CUBIE_GAP) / size


def cubie_center(x: int, y: int, z: int, size: int) -> Vec3:
    """
    Locate the center of a cubie of the grid.

    Args:
        x: Index of the cubie along the X axis, from L to R.
        y: Index of the cubie along the Y axis, from D to U.
        z: Index of the cubie along the Z axis, from B to F.
        size: Size of the cube.

    Returns:
        The center of the cubie, in world coordinates.

    """
    slot = 2 * CUBE_EXTENT / size

    return Vec3(*(
        (index + 0.5) * slot - CUBE_EXTENT
        for index in (x, y, z)
    ))


def is_surface(x: int, y: int, z: int, size: int) -> bool:
    """
    Tell whether a cubie of the grid can be seen.

    Args:
        x: Index of the cubie along the X axis.
        y: Index of the cubie along the Y axis.
        z: Index of the cubie along the Z axis.
        size: Size of the cube.

    Returns:
        ``True`` when at least one side of the cubie lies on the surface
        of the cube.

    """
    return any(
        index in {0, size - 1}
        for index in (x, y, z)
    )


def build_cubies(size: int) -> tuple[Cubie, ...]:
    """
    Place the visible cubies of a cube of a given size.

    The pieces buried inside the cube are left out: a cube of size ``N``
    keeps ``N³ - (N - 2)³`` of them, 26 for a 3x3x3 and 218 for a 7x7x7.

    Args:
        size: Size of the cube.

    Returns:
        The visible cubies, X varying fastest and Z slowest.

    """
    check_size(size)

    return tuple(
        Cubie(x, y, z, cubie_center(x, y, z, size))
        for z in range(size)
        for y in range(size)
        for x in range(size)
        if is_surface(x, y, z, size)
    )


def build_cube_geometry(size: int) -> CubeGeometry:
    """
    Build everything needed to draw a cube of a given size.

    Args:
        size: Size of the cube.

    Returns:
        The shared mesh of a cubie and the instances placing it.

    """
    half = cubie_half(size)

    return CubeGeometry(
        size=size,
        half=half,
        mesh=build_cubie_mesh(half),
        cubies=build_cubies(size),
    )


def core_radius(size: int) -> float:
    """
    Size the ball core of a cube of a given size.

    The outer layer leaves a cavity around the center of the cube, and
    the core fills it, swollen by ``CORE_BULGE`` so that it sinks into
    the pieces themselves: flush with the cavity it would sit at the very
    bottom of any hole dug by the mask, where the wall of the hole hides
    it. The bulge being a fraction of the half extent of a cubie, the
    core sinks into the same share of the outer layer whatever the size
    of the cube.

    A 1x1x1 gets one too, buried inside its single piece, where nothing
    can ever see it.

    Args:
        size: Size of the cube.

    Returns:
        The radius of the core, in world units, always strictly positive
        and always short of the surface of the cube.

    """
    half = cubie_half(size)
    cavity = CUBE_EXTENT - CUBE_EXTENT / size - half

    return cavity + CORE_BULGE * half


def core_point(
        radius: float,
        ring: int,
        segment: int,
        rings: int,
        segments: int,
) -> Vec3:
    """
    Place one vertex of the ball core on its sphere.

    Both poles are placed by hand rather than by the formula: the sine of
    pi is not zero in floating point, so the bottom one would land a
    fraction away from the axis, differently for every meridian, and stop
    being a single point. The meridians wrap around for the same reason,
    the last one having to be the first one and not a hair away from it.

    Args:
        radius: Radius of the sphere.
        ring: Index of the parallel, from the top pole to the bottom one.
        segment: Index of the meridian, around the Y axis.
        rings: How many parallels the sphere is cut in.
        segments: How many meridians the sphere is cut in.

    Returns:
        The point of the sphere, in world coordinates.

    """
    if ring == 0:
        return Vec3(0.0, radius, 0.0)

    if ring == rings:
        return Vec3(0.0, -radius, 0.0)

    polar = math.pi * ring / rings
    azimuth = 2 * math.pi * (segment % segments) / segments
    around = radius * math.sin(polar)

    return Vec3(
        around * math.cos(azimuth),
        radius * math.cos(polar),
        around * math.sin(azimuth),
    )


def core_polygons(radius: float, rings: int, segments: int) -> list[Polygon]:
    """
    Cut the sphere of the ball core into polygons.

    One quad per cell of the parallel and meridian grid, but a triangle
    against each pole, where the two corners sitting on it are the same
    point.

    Args:
        radius: Radius of the sphere, which ``core_radius`` keeps
            strictly positive: a sphere of no radius has no polygon, and
            no winding either.
        rings: How many parallels the sphere is cut in.
        segments: How many meridians the sphere is cut in.

    Returns:
        The polygons of the sphere, wound outward.

    """
    polygons: list[Polygon] = []

    for ring in range(rings):
        for segment in range(segments):
            corners = tuple(
                core_point(radius, *cell, rings, segments)
                for cell in (
                    (ring, segment),
                    (ring, segment + 1),
                    (ring + 1, segment + 1),
                    (ring + 1, segment),
                )
            )

            polygons.append(
                oriented(
                    tuple(
                        point for index, point in enumerate(corners)
                        if point != corners[index - 1]
                    ),
                    BODY_FACE,
                ),
            )

    return polygons


def build_core_mesh(
        radius: float,
        *,
        rings: int = CORE_RINGS,
        segments: int = CORE_SEGMENTS,
) -> Mesh:
    """
    Build the mesh of the ball core, centered on the origin.

    The one mesh of the backend whose normals are not those of its
    polygons: a sphere is meant to look round, and a faceted one seen
    from a hole reads as a defect rather than as a parti pris. On a
    sphere centered on the origin the smooth normal is the direction of
    the vertex itself.

    Args:
        radius: Radius of the sphere.
        rings: How many parallels the sphere is cut in.
        segments: How many meridians the sphere is cut in.

    Returns:
        The mesh of the ball core.

    """
    mesh = build_mesh(core_polygons(radius, rings, segments))

    return Mesh(
        tuple(
            Vertex(vertex.position, vertex.position.normalized(), vertex.face)
            for vertex in mesh.vertices
        ),
        mesh.indices,
    )


def pack_core(mesh: Mesh) -> bytes:
    """
    Serialize the ball core for a vertex buffer.

    Args:
        mesh: The mesh of the core.

    Returns:
        The vertices, laid out as ``CORE_VERTEX_FORMAT`` describes them.

    """
    return b''.join(
        struct.pack(CORE_VERTEX_PACKING, *vertex.position, *vertex.normal)
        for vertex in mesh.vertices
    )


def pack_axes(length: float) -> bytes:
    """
    Serialize the three axes of the grid, as segments of a line buffer.

    One segment per axis, from the center of the cube outwards, each
    carrying the color naming it: X red from L to R, Y green from D to U,
    Z blue from B to F, which is the frame the moves are turned in.

    Args:
        length: How far a segment reaches from the center, in world
            units.

    Returns:
        The six vertices, laid out as ``AXES_VERTEX_FORMAT`` describes
        them.

    """
    return b''.join(
        struct.pack(AXES_VERTEX_PACKING, *point, *color)
        for axis, color in zip(AXES, AXES_COLORS, strict=True)
        for point in (ORIGIN, axis.scaled(length))
    )
