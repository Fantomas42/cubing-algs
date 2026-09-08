"""
Scene of the GPU rendering backend.

Turns a ``VCube`` into what a renderer needs to draw it: one instance per
visible cubie, each carrying its model matrix and the six colors of its
sides. Pure Python, and backend agnostic: nothing here knows about
OpenGL, the very same scene could be rasterized in SVG.

No permutation table lives here. The colors are read straight from the
facelet string of the cube, through the ``(face, row, column)`` mapping
that ``display/image.py`` already uses, and the palette is the one of the
SVG backend, so that both renderings show the same colors.

The masks and the modes follow the same road: ``ModeDisplay`` resolves
them once, for both backends. Only the hidden code parts ways, a cubie
nobody may see being dropped from the scene rather than painted over.
"""
import struct
from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from functools import lru_cache
from typing import TYPE_CHECKING
from typing import NamedTuple

from cubing_algs.annotations import CubeDisplayMask
from cubing_algs.annotations import CubeFacelets
from cubing_algs.display.gl.geometry import FACE_BASES
from cubing_algs.display.gl.geometry import CubeGeometry
from cubing_algs.display.gl.geometry import Cubie
from cubing_algs.display.gl.geometry import FaceBasis
from cubing_algs.display.gl.geometry import build_cube_geometry
from cubing_algs.display.gl.transforms import Mat4
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.display.image import ImageDisplay
from cubing_algs.display.palettes import hex_to_rgba

if TYPE_CHECKING:  # pragma: no cover
    from cubing_algs.vcube import VCube

# A color of the scene, as three channels running from 0 to 1.
type Color = tuple[float, float, float]

# Number of sides of a cubie, one color each.
SIDE_NUMBER = len(FACE_BASES)

# Key of the color of the plastic in the palette of the SVG backend.
# The one entry this module reads by name: the colors a mask asks for
# are resolved by ``get_sticker_fill()``, which knows the keys of the
# codes it answers.
PLASTIC_KEY = 'cube_color'

# The one code of a display mask this backend reads for itself, as
# ``display/masks.py`` writes it: a piece hidden on every side is
# dropped rather than painted, which is where the two backends part
# ways. The other four say a color, and only the SVG backend resolves
# them.
MASK_HIDDEN = '3'

# Layout of an instance in the buffer, as moderngl reads it: model
# matrix, then the six colors as two mat3, three colors per matrix.
# GLSL 3.30 forbids an array of vertex inputs; a matrix is the portable
# way to hand several vectors over in one attribute.
INSTANCE_FORMAT = '16f 9f 9f/i'
INSTANCE_ATTRIBUTES = ('in_model', 'in_colors_low', 'in_colors_high')
INSTANCE_PACKING = f'<{ SIDE_NUMBER * 3 }f'

# Size of one instance in the buffer: a model matrix and the colors.
INSTANCE_SIZE = struct.calcsize('<16f') + struct.calcsize(INSTANCE_PACKING)

CHANNEL_MAXIMUM = 255.0

# How many color combinations keep their packed bytes. A cube of any
# size holds a couple of dozen of them, and a session changing palette,
# mask or mode brings a couple of dozen more: this is a memo of what a
# frame is packing right now, not a store of everything ever drawn.
COLOR_PACKING_CACHE = 512


class FaceLayout(NamedTuple):
    """
    Where the facelets of one face sit on the grid of cubies.

    A face is read row after row, from its top left corner as seen from
    outside. ``axis`` is the axis the face is orthogonal to and ``sign``
    which end of it the face sits on; the other four fields tell which
    grid axis a row and a column run along, and in which direction.
    """

    axis: int
    sign: int
    row_axis: int
    row_sign: int
    col_axis: int
    col_sign: int


def axis_direction(vector: Vec3) -> tuple[int, int]:
    """
    Name the axis a vector runs along, and the way it points.

    Args:
        vector: A vector parallel to one of the three axes.

    Returns:
        The index of the axis, and 1 or -1 for its direction.

    Raises:
        ValueError: When the vector is parallel to no axis.

    """
    for axis, value in enumerate(vector):
        if value:
            return axis, 1 if value > 0 else -1

    msg = f'Vector { vector } runs along no axis'
    raise ValueError(msg)


def build_face_layout(basis: FaceBasis) -> FaceLayout:
    """
    Read the layout of a face out of the frame of its stickers.

    The frame already says everything: its normal names the side of the
    cube the face lies on, its ``right`` the way a column runs, and the
    opposite of its ``up`` the way a row runs, rows being counted from
    the top of the face down.

    Args:
        basis: Orientation of the face, as the geometry defines it.

    Returns:
        The layout of the face on the grid of cubies.

    """
    axis, sign = axis_direction(basis.normal)
    row_axis, row_sign = axis_direction(-basis.up)
    col_axis, col_sign = axis_direction(basis.right)

    return FaceLayout(axis, sign, row_axis, row_sign, col_axis, col_sign)


# The six faces, in the order of FACE_ORDER: U, R, F, D, L, B.
FACE_LAYOUTS: tuple[FaceLayout, ...] = tuple(
    build_face_layout(basis)
    for basis in FACE_BASES
)


def grid_position(index: int, sign: int, size: int) -> int:
    """
    Read a grid index along an axis running one way or the other.

    Args:
        index: Index of the cubie on the grid axis.
        sign: Direction the row or the column runs along that axis.
        size: Size of the cube.

    Returns:
        The row or column number of the facelet.

    """
    if sign > 0:
        return index

    return size - 1 - index


def facelet_index(face: int, cubie: Cubie, size: int) -> int | None:
    """
    Locate the facelet shown by one side of a cubie.

    Args:
        face: Index of the side, in the order of ``FACE_ORDER``.
        cubie: The cubie the side belongs to.
        size: Size of the cube.

    Returns:
        The position of the facelet in the state string, or None when
        that side of the cubie is buried inside the cube.

    """
    layout = FACE_LAYOUTS[face]
    grid = (cubie.x, cubie.y, cubie.z)

    if grid[layout.axis] != (size - 1 if layout.sign > 0 else 0):
        return None

    row = grid_position(grid[layout.row_axis], layout.row_sign, size)
    col = grid_position(grid[layout.col_axis], layout.col_sign, size)

    return face * size * size + row * size + col


def scale_channels(channels: tuple[int, int, int]) -> Color:
    """
    Turn three channels running from 0 to 255 into a color of the scene.

    Args:
        channels: The red, green and blue channels, as bytes.

    Returns:
        The three channels of the color, from 0 to 1.

    """
    red, green, blue = channels

    return (
        red / CHANNEL_MAXIMUM,
        green / CHANNEL_MAXIMUM,
        blue / CHANNEL_MAXIMUM,
    )


def build_color(hex_color: str) -> Color:
    """
    Convert a color of a palette into a color of the scene.

    Args:
        hex_color: The color, as ``#rrggbb`` or ``#rrggbbaa``. The alpha
            channel is dropped: the cube is opaque.

    Returns:
        The three channels of the color, from 0 to 1.

    """
    return scale_channels(hex_to_rgba(hex_color)[:3])


def plastic_color(display: ImageDisplay) -> Color:
    """
    Give the color of the plastic, which is the cube itself.

    The one color of a scene no mask ever asks for: it paints the body
    of a piece and the sides of it buried inside the cube, where there
    is no facelet to read a code of.

    Args:
        display: The SVG backend resolving the palette.

    Returns:
        The color of the plastic.

    """
    return build_color(display.palette[PLASTIC_KEY])


def build_colors(
        display: ImageDisplay,
        state: CubeFacelets,
        mask: CubeDisplayMask,
) -> dict[tuple[str, str], Color]:
    """
    Resolve the color of every facelet the cube shows, once each.

    Read through ``ImageDisplay.get_sticker_fill()``, which is the very
    function the SVG backend paints with: the five codes of
    ``display/masks.py`` are therefore read in one place for both
    backends, the dimming included, and a code can no longer come to
    mean one thing here and another thing there. It answers in
    hexadecimal for every code, so nothing is left to convert but the
    color itself.

    Only the pairs the cube truly holds are resolved - at most six face
    letters by five codes, whatever the size of the cube - so a 7x7
    resolves a couple of dozen colors instead of the fifteen hundred
    facelets it draws.

    Args:
        display: The SVG backend resolving the palette and the codes.
        state: Facelet string of the cube.
        mask: Display mask of the cube, one code per facelet.

    Returns:
        The color of each (face letter, mask code) pair the cube shows.

    """
    return {
        pair: build_color(display.get_sticker_fill(*pair))
        for pair in set(zip(state, mask, strict=True))
    }


def cubie_facelets(cubie: Cubie, size: int) -> tuple[int | None, ...]:
    """
    Locate the six facelets a cubie shows, one per side.

    Read once and handed to whoever asks: which sides are buried
    decides both whether the piece is drawn at all and what colors it
    takes, and locating them twice is half the cost of building a
    scene on a big cube.

    Args:
        cubie: The cubie to look at.
        size: Size of the cube.

    Returns:
        The position of each side in the state string, in the order of
        ``FACE_ORDER``, None for a side buried inside the cube.

    """
    return tuple(
        facelet_index(face, cubie, size)
        for face in range(SIDE_NUMBER)
    )


def cubie_hidden(
        facelets: tuple[int | None, ...],
        mask: CubeDisplayMask,
) -> bool:
    """
    Tell whether a cubie is to be left out of the scene altogether.

    A piece is dropped when every facelet it shows is hidden, which digs
    a real hole in the cube, something the SVG backend cannot do and the
    only place where the two renderings part ways. A piece hidden on one
    side only keeps its place, that side taking the plastic color.

    Args:
        facelets: The six facelets of the cubie, as
            ``cubie_facelets()`` locates them.
        mask: Display mask of the cube, one code per facelet.

    Returns:
        True when the cubie must not be drawn.

    """
    codes = [
        mask[index]
        for index in facelets
        if index is not None
    ]

    return bool(codes) and all(code == MASK_HIDDEN for code in codes)


def cubie_colors(
        facelets: tuple[int | None, ...],
        state: CubeFacelets,
        mask: CubeDisplayMask,
        colors: Mapping[tuple[str, str], Color],
        plastic: Color,
) -> tuple[Color, ...]:
    """
    Pick the colors of the six sides of a cubie.

    A side buried inside the cube takes the color of the plastic: the
    mesh carries its six stickers whatever happens, and this is what
    makes the ones nobody can see disappear.

    Args:
        facelets: The six facelets of the cubie, as
            ``cubie_facelets()`` locates them.
        state: Facelet string of the cube.
        mask: Display mask of the cube, one code per facelet.
        colors: The color of each (face letter, mask code) pair, as
            ``build_colors()`` resolves them.
        plastic: The color of the cube itself.

    Returns:
        The six colors, in the order of ``FACE_ORDER``.

    """
    return tuple(
        plastic
        if index is None
        else colors[state[index], mask[index]]
        for index in facelets
    )


@lru_cache(maxsize=COLOR_PACKING_CACHE)
def pack_colors(colors: tuple[Color, ...]) -> bytes:
    """
    Serialize the six colors of a cubie, once per combination.

    A turning layer hands over a new instance on every frame, of the
    same piece, hence of the same colors: what moves is the model
    matrix, and packing eighteen floats behind it again was half of
    what an animated frame spent on the processor. Keyed by the colors
    themselves rather than by the instance carrying them, so nothing
    can go stale - two instances of the same colors are one entry, and
    a cube holds a couple of dozen of them whatever its size.

    Args:
        colors: The six colors of a cubie, in the order of
            ``FACE_ORDER``.

    Returns:
        The colors, laid out as ``INSTANCE_PACKING`` describes them.

    """
    return struct.pack(
        INSTANCE_PACKING,
        *(channel for color in colors for channel in color),
    )


@dataclass(frozen=True, slots=True)
class CubieInstance:
    """One cubie of the scene: where it stands, and how it is colored."""

    cubie: Cubie
    model: Mat4
    colors: tuple[Color, ...]

    def pack(self) -> bytes:
        """
        Serialize the instance for an instance buffer.

        Returns:
            The instance, laid out as ``INSTANCE_FORMAT`` describes it.

        """
        return self.model.pack() + pack_colors(self.colors)


@dataclass(frozen=True, slots=True)
class Scene:
    """
    A cube ready to be drawn: a shared mesh, and the cubies placing it.

    Everything a backend needs is here, and nothing else: the geometry
    holds the mesh uploaded once, the instances hold what changes from
    one cubie, one state or one mask to the next.
    """

    geometry: CubeGeometry
    instances: tuple[CubieInstance, ...]
    plastic: Color

    # The very same cube with no piece in it, built once and handed
    # back as itself afterwards. A renderer skips the upload of a scene
    # it recognizes **by identity**, so anything a caller draws frame
    # after frame has to be the same object every time: a cube nobody
    # is connected to is exactly that, and this is the one place able
    # to promise it.
    #
    # Held in a list rather than in the field itself: a frozen dataclass
    # refuses the write, and what a mutable field contains is the one
    # place it does not reach. Kept out of the comparison, a memo saying
    # nothing about what the scene is.
    memo: list['Scene'] = field(
        init=False, repr=False, compare=False, default_factory=list,
    )

    @property
    def size(self) -> int:
        """
        Tell the size of the cube of the scene.

        Returns:
            The size of the cube.

        """
        return self.geometry.size

    def mapped(
            self,
            place: 'Callable[[CubieInstance], CubieInstance]',
    ) -> 'Scene':
        """
        Build the scene one function moving every piece leads to.

        The shape every effect on a cube is written in - a turn, an
        opening, a blast - and it is here so that the identity a
        renderer caches on is decided once: a function handing every
        piece back untouched hands the very same scene back, and costs
        no upload at all.

        Args:
            place: What each piece is passed through, giving back where
                it now stands.

        Returns:
            The cube, its pieces moved, or itself when none of them
            were.

        """
        placed = tuple(place(instance) for instance in self.instances)

        if all(
                moved is instance
                for moved, instance in zip(placed, self.instances, strict=True)
        ):
            return self

        return replace(self, instances=placed)

    def emptied(self) -> 'Scene':
        """
        Hand the very same cube over with no piece at all in it.

        Nothing is drawn away from the window and hoped to be out of
        it: the pieces are simply not handed to the renderer, and what
        is drawn before them and on its own - the ball core - is left
        alone in the picture.

        The same object every time, which is what makes it free: a
        window showing no cube draws this scene at every frame, and a
        renderer uploads it once.

        Returns:
            The cube of the same geometry, holding no instance.

        """
        if not self.memo:
            self.memo.append(replace(self, instances=()))

        return self.memo[0]

    def exploded(self, spread: float) -> 'Scene':
        """
        Push every cubie away from the center of the cube.

        The offset is taken along the resting center of a piece, and
        composed **into** the model matrix rather than on top of it, so
        that whatever turn the matrix already holds carries it along.
        Translations commute, so a piece standing still simply stands
        further out; a turning layer orbits on the open lattice and
        lands exactly where the scene rebuilt on the cube it turned
        draws it. Applied on top instead, a piece flies along the place
        it left and jumps onto the place it reached the frame the move
        lands - measured, more than a unit for a corner of an open 3x3,
        against 0.18 for the fastest frame of the turn itself.

        A null spread hands the very same scene back, so a cube that is
        not open costs nothing and keeps the identity the instance
        buffer is cached on.

        Args:
            spread: How far a cubie flies, as a share of the distance
                from its center to the one of the cube.

        Returns:
            The very same cube, its pieces pushed apart.

        """
        if not spread:
            return self

        return self.mapped(
            lambda instance: replace(
                instance,
                model=instance.model @ Mat4.translation(
                    instance.cubie.center.scaled(spread),
                ),
            ),
        )

    def pack_instances(self) -> bytes:
        """
        Serialize every instance for an instance buffer.

        Returns:
            The instances, one after the other.

        """
        return b''.join(instance.pack() for instance in self.instances)


def resolve_display(
        cube: 'VCube',
        palette_name: str = '',
        *,
        mode: str = '',
        mask: CubeDisplayMask = '',
) -> tuple['VCube', CubeDisplayMask]:
    """
    Settle what a display mode asks for, before anything is drawn.

    A mode may reorient the cube, as it does in SVG. The layout it
    carries is dropped: ``top`` is a flat view of the up face, which has
    no meaning for a backend drawing a solid.

    Split out of ``build_scene()`` because an animation resolves it once
    and redraws many times: the orientation of a mode is computed from
    the state of the cube, and would jump around were it read again at
    every move.

    Args:
        cube: The cube to draw.
        palette_name: Name of the color palette. Empty for the default
            one.
        mode: Display preset presetting the mask and the orientation,
            such as ``oll`` or ``f2l``.
        mask: Display mask, one code per facelet. Overrides the mask the
            mode would have set.

    Returns:
        The cube as the mode wants it shown, and the mask to draw it
        through, still to be replayed by ``map_mask()``.

    """
    mode_mask, _, orientation = ImageDisplay(
        cube, palette_name,
    ).resolve_mode(mode.lower())

    if orientation:
        cube = cube.oriented_copy(orientation, full=True)

    return cube, mask or mode_mask


def build_scene(
        cube: 'VCube',
        palette_name: str = '',
        geometry: CubeGeometry | None = None,
        *,
        mode: str = '',
        mask: CubeDisplayMask = '',
) -> Scene:
    """
    Build the scene drawing a cube.

    The palette, the mode and the mask are all resolved by the SVG
    backend rather than read again here: both renderings must show the
    same cube, and the surest way of getting there is to have a single
    place resolving them.

    Args:
        cube: The cube to draw.
        palette_name: Name of the color palette. Empty for the default
            one.
        geometry: Geometry to place the cubies with, built from the size
            of the cube when left out.
        mode: Display preset presetting the mask and the orientation,
            such as ``oll`` or ``f2l``.
        mask: Display mask, one code per facelet. Overrides the mask the
            mode would have set.

    Returns:
        The scene of the cube.

    """
    cube, resolved = resolve_display(
        cube, palette_name, mode=mode, mask=mask,
    )

    display = ImageDisplay(cube, palette_name)
    codes = display.map_mask(cube, resolved)

    built = geometry or build_cube_geometry(cube.size)
    state = cube.state
    colors = build_colors(display, state, codes)
    plastic = plastic_color(display)

    placed = (
        (cubie, cubie_facelets(cubie, built.size))
        for cubie in built.cubies
    )

    return Scene(
        geometry=built,
        instances=tuple(
            CubieInstance(
                cubie=cubie,
                model=Mat4.translation(cubie.center),
                colors=cubie_colors(facelets, state, codes, colors, plastic),
            )
            for cubie, facelets in placed
            if not cubie_hidden(facelets, codes)
        ),
        plastic=plastic,
    )
