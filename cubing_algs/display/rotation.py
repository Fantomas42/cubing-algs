"""
The rotation strings every backend frames a cube with.

``y45x-34`` is the one vocabulary the SVG, the terminal and the GPU
backends share to say where a cube is looked at from, and this module is
the whole of what it means: the grammar it is written in, how it is
read, and how one is written back out.

It lives beside the backends rather than inside one of them because all
three need it, and because reading a rotation used to mean reaching into
``ImageDisplay`` - a fourteen hundred line SVG class - for a static
method that touches nothing of an image.
"""
import re
from argparse import ArgumentTypeError

from cubing_algs.annotations import RegexPattern
from cubing_algs.display.constants import ROTATION

# The grammar of a framing: axis parts, each an axis letter and a signed
# angle in degrees, repeated and in any order. The pattern anchors the
# whole string, so nothing is ever read out of a partial match.
ROTATION_PATTERN: RegexPattern = re.compile(r'^([xyz]-?[0-9]+)+$')
ROTATION_PARTS: RegexPattern = re.compile(r'([xyz])(-?[0-9]+)')

# The axes a framing is written with, in the order a camera composes
# them: a yaw around the vertical, a pitch above the horizon, a roll
# around the line of sight.
AXES = ('y', 'x', 'z')

FULL_TURN = 360


def valid_rotation(rotation: str) -> bool:
    """
    Tell whether a string names a framing at all.

    ``parse_rotation()`` falls back on the library default for anything
    it cannot read, which is what a renderer wants and what a command
    line does not: a typo would then draw the very picture the option
    was meant to change, and say nothing about it. This is what a caller
    refusing one asks first.

    Args:
        rotation: The string to check.

    Returns:
        True when the string is made of axis and angle parts.

    """
    return bool(ROTATION_PATTERN.match(rotation))


def rotation_argument(rotation: str) -> str:
    """
    Read the framing a command line option names, or refuse it.

    The other half of ``valid_rotation()``, and the reason it exists:
    a renderer handed a typo falls back on the library framing and
    draws a cube, which is what it must do; a command line doing the
    same opens the very picture the option was meant to change, and
    says nothing at all about it. So an option is given this rather
    than the parser.

    An empty string is the framing of the library asked for by name,
    and it is let through: an option left out and an option left empty
    mean the same thing.

    Args:
        rotation: The argument, as it was typed.

    Returns:
        The rotation string, empty for the framing of the library.

    Raises:
        ArgumentTypeError: When the argument names no rotation.

    """
    if rotation and not valid_rotation(rotation):
        msg = (
            f'"{ rotation }" is not a rotation, '
            f'expected AXISDEGREES parts, e.g. { ROTATION }'
        )
        raise ArgumentTypeError(msg)

    return rotation


def parse_rotation(rotation: str) -> list[tuple[str, int]]:
    """
    Read a rotation string as the axis and angle parts it is made of.

    The parts are handed back in the order they were written, repeated
    axes included: what adds them up is the caller, and it is the one
    place the two backends disagree - ``image.py`` applies each part in
    written order where an orbit camera composes them yaw, pitch, roll.
    Both agree on any chain shaped ``y…x…z…``, which covers every
    rotation the library ships.

    A string that names no rotation is read as the library default
    rather than refused: a renderer handed a typo draws a cube.

    Args:
        rotation: Rotation string like ``y45x-34``.

    Returns:
        List of ``(axis, degrees)`` tuples.

    """
    if not valid_rotation(rotation):
        rotation = ROTATION

    return [
        (match.group(1), int(match.group(2)))
        for match in ROTATION_PARTS.finditer(rotation)
    ]


def fold_rotation(rotation: str) -> dict[str, int]:
    """
    Add the parts of a framing up, axis by axis.

    Args:
        rotation: Rotation string like ``y45x-34``, empty for the
            library default.

    Returns:
        The total turn of each of the three axes, in degrees.

    """
    parts = dict.fromkeys(AXES, 0)

    for axis, degrees in parse_rotation(rotation or ROTATION):
        parts[axis] += degrees

    return parts


def format_rotation(parts: dict[str, int]) -> str:
    """
    Write a framing back out as the string a backend reads.

    The yaw is written whatever it says, where the other two are written
    only when they turn something: a framing whose parts all came out at
    zero would be an empty string, and an empty rotation is the default
    of the library rather than a cube looked straight in the F face.

    Args:
        parts: The total turn of each axis, in degrees.

    Returns:
        The rotation string standing for those angles.

    """
    return ''.join(
        f'{ axis }{ parts[axis] }'
        for axis in AXES
        if parts[axis] or axis == 'y'
    )


def turned_rotation(
        rotation: str,
        yaw: int = 0,
        pitch: int = 0,
        roll: int = 0,
) -> str:
    """
    Turn a framing, and write out the angle it lands on.

    The turn is added to what the framing already carries and the string
    is written out again, rather than appended to it: the parts of a
    rotation do add up per axis, so appending would frame the very same
    thing, but what comes out is then a pile of the turns that were
    asked for - ``y45x-34y180`` - instead of the angle the camera ends
    up at.

    An axis nothing is added to is written back exactly as it was read:
    only a turned one is brought inside a single revolution, so passing
    behind a cube leaves the elevation it was seen at alone rather than
    rewriting ``x-34`` as ``x326``.

    Args:
        rotation: The framing to turn, empty for the library default.
        yaw: Degrees to add around the vertical.
        pitch: Degrees to add above the horizon.
        roll: Degrees to add around the line of sight.

    Returns:
        The framing standing where the turn leaves it.

    """
    parts = fold_rotation(rotation)

    for axis, degrees in zip(AXES, (yaw, pitch, roll), strict=True):
        if degrees:
            parts[axis] = (parts[axis] + degrees) % FULL_TURN

    return format_rotation(parts)
