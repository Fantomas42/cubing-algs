"""
Image encoding for the GPU rendering backend.

PNG is encoded in pure Python, so that the offscreen mode carries no
dependency beyond moderngl itself.

GIF is another matter: it takes a color quantization and an LZW coder,
neither of which is worth writing again. Pillow does it, and is asked
for only when an animation is being written, never at import time. An
animation with no Pillow around comes out as a series of PNG frames.
"""
import io
import struct
import zlib
from collections.abc import Sequence
from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING

from cubing_algs.display.gl.constants import COLOR_CHANNELS
from cubing_algs.display.gl.constants import MILLISECONDS
from cubing_algs.display.gl.constants import PILLOW_MISSING
from cubing_algs.display.gl.presentation import DEFAULT_PLAYBACK
from cubing_algs.display.gl.presentation import Playback

if TYPE_CHECKING:  # pragma: no cover
    from PIL import Image

# PNG color type of a truecolor image carrying an alpha channel, which
# is the only kind this backend writes: a render keeps its background
# transparent, and there is no second sort of picture to encode.
PNG_COLOR_TYPE = 6

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'

PNG_BIT_DEPTH = 8

# A GIF holds 256 colors at most: the last index is kept for the
# transparent one, the quantization gets the other 255.
GIF_TRANSPARENT_INDEX = 255
GIF_PALETTE_COLORS = 255

# Side a frame is sampled down to when the palette shared by the whole
# animation is picked: small enough for the sampling to cost nothing,
# large enough for every color of a frame to survive it.
GIF_SAMPLE_SIZE = 64

# Alpha below which a pixel is called transparent. A GIF knows no
# half transparency, so the antialiased fringe of the cube has to fall
# on one side or the other, and the middle is where it hurts least.
GIF_ALPHA_THRESHOLD = 127

# Disposal method 2, restore to background: without it every frame is
# painted over the last one and the cube leaves a trail behind it.
GIF_DISPOSAL_BACKGROUND = 2


def png_chunk(kind: bytes, data: bytes) -> bytes:
    """
    Build a PNG chunk: length, type, payload and CRC.

    Args:
        kind: Four letters chunk type, such as ``b'IHDR'``.
        data: Payload of the chunk, possibly empty.

    Returns:
        The bytes of the complete chunk.

    """
    return (
        struct.pack('>I', len(data))
        + kind
        + data
        + struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def encode_png(pixels: bytes, size: tuple[int, int]) -> bytes:
    """
    Encode raw pixels into a PNG image.

    The rows are reversed on the way: what is encoded comes from an
    OpenGL framebuffer, whose origin is the bottom left corner, and a
    file is read from the top down.

    Args:
        pixels: Rows of RGBA pixels.
        size: Width and height of the image, in pixels.

    Returns:
        The bytes of the PNG file.

    Raises:
        ValueError: If the pixel buffer does not match the announced
            size.

    """
    width, height = size
    stride = width * COLOR_CHANNELS
    expected = stride * height

    if len(pixels) != expected:
        msg = (
            f'Expected { expected } bytes of pixels for '
            f'{ width }x{ height }x{ COLOR_CHANNELS }, got { len(pixels) }'
        )
        raise ValueError(msg)

    # Every scanline is prefixed by its filter type, 0 meaning none.
    raw = b''.join(
        b'\x00' + pixels[row * stride:(row + 1) * stride]
        for row in range(height - 1, -1, -1)
    )

    header = struct.pack(
        '>IIBBBBB',
        width, height,
        PNG_BIT_DEPTH, PNG_COLOR_TYPE,
        0, 0, 0,
    )

    return (
        PNG_SIGNATURE
        + png_chunk(b'IHDR', header)
        + png_chunk(b'IDAT', zlib.compress(raw, 9))
        + png_chunk(b'IEND', b'')
    )


def write_png(path: str | Path, pixels: bytes, size: tuple[int, int]) -> Path:
    """
    Encode raw pixels and write them to a PNG file.

    Args:
        path: Destination of the file.
        pixels: Rows of RGBA pixels.
        size: Width and height of the image, in pixels.

    Returns:
        The path the image was written to.

    """
    destination = Path(path)
    destination.write_bytes(encode_png(pixels, size))

    return destination


def has_pillow() -> bool:
    """
    Tell whether Pillow is importable.

    Returns:
        True when an animation can be written as a GIF.

    """
    return find_spec('PIL') is not None


def gif_image(pixels: bytes, size: tuple[int, int]) -> 'Image.Image':
    """
    Read raw pixels into an image Pillow can work on.

    The rows are reversed on the way, as they are for a PNG: a read of
    an OpenGL framebuffer starts at the bottom left corner.

    Args:
        pixels: Rows of RGBA pixels.
        size: Width and height of the image, in pixels.

    Returns:
        The frame, still with its alpha channel.

    """
    from PIL import Image

    return Image.frombytes('RGBA', size, pixels).transpose(
        Image.Transpose.FLIP_TOP_BOTTOM,
    )


def gif_palette(images: Sequence['Image.Image']) -> 'Image.Image':
    """
    Pick the one palette the whole animation is drawn with.

    Quantizing each frame on its own gives every one of them its own
    color table, and colors that drift from frame to frame: the file
    then weighs about twice what it needs to. The palette is read from
    every frame, not from the first one alone, since a rotation brings
    faces into view that were nowhere to be seen at the start.

    The frames are sampled down first, to the nearest neighbour so that
    no color is invented by the resizing: what a palette needs is the
    colors of an image, not its shape.

    Args:
        images: The frames of the animation.

    Returns:
        A paletted image, to be handed to ``quantize()`` as a reference.

    """
    from PIL import Image

    sample = (GIF_SAMPLE_SIZE, GIF_SAMPLE_SIZE)
    mosaic = Image.new('RGB', (GIF_SAMPLE_SIZE, GIF_SAMPLE_SIZE * len(images)))

    for index, image in enumerate(images):
        mosaic.paste(
            image.convert('RGB').resize(sample, Image.Resampling.NEAREST),
            (0, index * GIF_SAMPLE_SIZE),
        )

    return mosaic.quantize(colors=GIF_PALETTE_COLORS)


def gif_frame(
        image: 'Image.Image',
        palette: 'Image.Image',
) -> 'Image.Image':
    """
    Turn one frame into the paletted image a GIF holds.

    The last index of the palette is kept for the transparent color: a
    GIF has no alpha channel, only a color it does not paint, so the
    antialiased fringe of the cube has to fall on one side or the other.

    Args:
        image: The frame, with its alpha channel.
        palette: The palette the whole animation is drawn with.

    Returns:
        The frame, as a paletted Pillow image.

    """
    from PIL import Image

    frame = image.convert('RGB').quantize(
        palette=palette,
        dither=Image.Dither.NONE,
    )

    frame.paste(
        GIF_TRANSPARENT_INDEX,
        None,
        image.getchannel('A').point(
            lambda alpha: 255 * (alpha <= GIF_ALPHA_THRESHOLD),
        ),
    )

    return frame


def encode_gif(
        frames: Sequence[bytes],
        size: tuple[int, int],
        *,
        playback: Playback = DEFAULT_PLAYBACK,
) -> bytes:
    """
    Encode a series of raw frames into an animated GIF.

    A GIF holds a duration per image, so holding the state the animation
    starts from and the one it ends on costs no frame at all: the two of
    them are simply shown longer than the rest.

    Args:
        frames: The frames, each one rows of RGBA pixels.
        size: Width and height of the images, in pixels.
        playback: How the animation runs: frame rate, how long the first
            and the last frame are held, and how many times it plays.

    Returns:
        The bytes of the GIF file.

    Raises:
        ImportError: When Pillow is not installed.
        ValueError: When there is no frame to encode.

    """
    if not has_pillow():
        raise ImportError(PILLOW_MISSING)

    if not frames:
        msg = 'An animation needs at least one frame'
        raise ValueError(msg)

    read = [gif_image(frame, size) for frame in frames]
    palette = gif_palette(read)
    images = [gif_frame(image, palette) for image in read]

    buffer = io.BytesIO()

    images[0].save(
        buffer,
        format='GIF',
        save_all=True,
        append_images=images[1:],
        duration=[
            round(seconds * MILLISECONDS)
            for seconds in playback.durations(len(images))
        ],
        loop=playback.loop,
        disposal=GIF_DISPOSAL_BACKGROUND,
        transparency=GIF_TRANSPARENT_INDEX,
    )

    return buffer.getvalue()


def write_gif(
        path: str | Path,
        frames: Sequence[bytes],
        size: tuple[int, int],
        *,
        playback: Playback = DEFAULT_PLAYBACK,
) -> Path:
    """
    Encode a series of raw frames and write them as an animated GIF.

    The frames come from a framebuffer, so their rows are reversed on
    the way: a file writer has no reason to want them upside down.

    Args:
        path: Destination of the file.
        frames: The frames, each one rows of RGBA pixels.
        size: Width and height of the images, in pixels.
        playback: How the animation runs: frame rate, how long the first
            and the last frame are held, and how many times it plays.

    Returns:
        The path the animation was written to.

    """
    destination = Path(path)
    destination.write_bytes(
        encode_gif(frames, size, playback=playback),
    )

    return destination


def write_frames(
        path: str | Path,
        frames: Sequence[bytes],
        size: tuple[int, int],
) -> list[Path]:
    """
    Write every frame of an animation as its own PNG file.

    What an animation falls back to when Pillow is missing: the frames
    are numbered next to the file the GIF would have been, and whatever
    encoder the caller has at hand can assemble them.

    Args:
        path: Destination the GIF would have been written to. Its stem
            names the frames and its folder holds them.
        frames: The frames, each one rows of RGBA pixels.
        size: Width and height of the images, in pixels.

    Returns:
        The paths the frames were written to, in order.

    """
    destination = Path(path)

    return [
        write_png(
            destination.with_name(f'{ destination.stem }_{index:04d}.png'),
            pixels,
            size,
        )
        for index, pixels in enumerate(frames)
    ]
