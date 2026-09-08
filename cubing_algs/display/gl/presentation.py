"""
What a picture of a cube is made of, gathered in one object.

Framing, palette, mode, mask, image size, lighting and the way the cube
is held all describe the same thing: the picture to make. They used to
travel as seven arguments in a row, which is how the way a bluetooth
sensor holds a cube could reach ``Renderer.draw()`` and go no further.

The object is threaded whole through the pipeline, each layer reading
the fields that concern it: the pure layer takes the palette, the mode
and the mask, the camera takes the rotation and the distance, the GPU
layer takes the size, the look and the orientation. One vocabulary from
the CLI down to the draw call, and no function re-deriving what another
has already settled.

``Playback`` is the other half, and deliberately not the same object: it
says how an animation runs, not what a frame of it looks like.

Pure Python, no external dependency.
"""
from dataclasses import dataclass

from cubing_algs.annotations import CubeDisplayMask
from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.constants import ANIMATION_LOOP
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import FRAME_RATE
from cubing_algs.display.gl.constants import HOLD_END
from cubing_algs.display.gl.constants import HOLD_START
from cubing_algs.display.gl.constants import MOVE_DURATION
from cubing_algs.display.gl.constants import RENDER_SIZE
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.transforms import IDENTITY
from cubing_algs.display.gl.transforms import Quat


@dataclass(frozen=True, slots=True)
class Presentation:
    """
    How a cube is turned into a picture.

    Every field has the default the library renders with, so that
    ``Presentation()`` is the plain picture and a variant is one
    ``dataclasses.replace()`` away.
    """

    palette: str = ''
    mode: str = ''
    mask: CubeDisplayMask = ''
    rotation: str = ''
    distance: float = 0.0
    image_size: int = RENDER_SIZE
    look: Look = DEFAULT_LOOK
    orientation: Quat = IDENTITY

    @property
    def size(self) -> tuple[int, int]:
        """
        Give the size of the image, the way moderngl asks for it.

        Returns:
            Width and height, in pixels.

        """
        return (self.image_size, self.image_size)

    def camera(self, radius: float) -> OrbitCamera:
        """
        Build the camera framing a cube of a given size.

        The radius is the one of the geometry actually built, not the
        one of the box it is laid out in: the gap and the chamfer make a
        cube smaller than its box, by a share depending on its size.

        A picture is square, so nothing is said of the aspect here: a
        window is not a picture, and the viewer fits its own through
        ``OrbitCamera.from_rotation()``.

        Args:
            radius: Radius of the bounding sphere of the scene.

        Returns:
            A camera looking at the origin, framing the sphere exactly.

        """
        return OrbitCamera.from_rotation(
            self.rotation, self.distance, radius,
        )


@dataclass(frozen=True, slots=True)
class Playback:
    """
    How an animation runs, once every frame of it is known.

    Kept apart from ``Presentation``: a frame rate and a loop count say
    nothing about what a frame looks like, and a still image has no use
    for either.

    The two holds are the pace of an animation as well: what a looping
    GIF gives the eye to read the state it starts from and the one it
    ends on. They reach the file it is written to, which knows a duration
    per image, and not the series of PNG frames an animation falls back
    to, which carries no timing at all.
    """

    frame_rate: float = FRAME_RATE
    duration: float = MOVE_DURATION
    loop: int = ANIMATION_LOOP
    hold_start: float = HOLD_START
    hold_end: float = HOLD_END

    def durations(self, frames: int) -> list[float]:
        """
        Tell how long every frame of an animation is shown.

        Every frame lasts what the frame rate says, save the first and
        the last one, which are held long enough to be read. A hold
        shorter than a frame falls back to the plain pace, so a null one
        simply plays the animation through.

        A single frame is both the first and the last, and takes
        ``hold_end``: an animation of no move at all is a state reached
        rather than a state departed from.

        Args:
            frames: How many frames the animation is made of.

        Returns:
            The time each frame is shown for, in seconds, in order.

        """
        step = 1.0 / self.frame_rate
        schedule = [step] * frames

        if not schedule:
            return schedule

        schedule[0] = max(step, self.hold_start)
        schedule[-1] = max(step, self.hold_end)

        return schedule


# The picture the library draws when it is asked for nothing in
# particular, and the pace it plays an animation at.
DEFAULT_PRESENTATION = Presentation()
DEFAULT_PLAYBACK = Playback()
