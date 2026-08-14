"""
Image encoding for the GPU rendering backend.

PNG is encoded in pure Python, so that the offscreen mode carries no
dependency beyond moderngl itself.
"""
import struct
import zlib
from pathlib import Path

# PNG color types indexed by the number of channels per pixel.
PNG_COLOR_TYPES = {
    1: 0,  # greyscale
    3: 2,  # truecolor
    4: 6,  # truecolor with alpha
}

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'

PNG_BIT_DEPTH = 8


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


def encode_png(
        pixels: bytes,
        size: tuple[int, int],
        *,
        channels: int = 4,
        flip: bool = True,
) -> bytes:
    """
    Encode raw pixels into a PNG image.

    Args:
        pixels: Rows of pixels, of ``channels`` bytes each.
        size: Width and height of the image, in pixels.
        channels: Number of bytes per pixel, one of PNG_COLOR_TYPES.
        flip: Reverse the row order, which is what a read of an OpenGL
            framebuffer needs, its origin being the bottom left corner.

    Returns:
        The bytes of the PNG file.

    Raises:
        ValueError: If the channel count is unsupported, or if the pixel
            buffer does not match the announced size.

    """
    if channels not in PNG_COLOR_TYPES:
        msg = f'Unsupported channel count: { channels }'
        raise ValueError(msg)

    width, height = size
    stride = width * channels
    expected = stride * height

    if len(pixels) != expected:
        msg = (
            f'Expected { expected } bytes of pixels for '
            f'{ width }x{ height }x{ channels }, got { len(pixels) }'
        )
        raise ValueError(msg)

    rows = range(height - 1, -1, -1) if flip else range(height)

    # Every scanline is prefixed by its filter type, 0 meaning none.
    raw = b''.join(
        b'\x00' + pixels[row * stride:(row + 1) * stride]
        for row in rows
    )

    header = struct.pack(
        '>IIBBBBB',
        width, height,
        PNG_BIT_DEPTH, PNG_COLOR_TYPES[channels],
        0, 0, 0,
    )

    return (
        PNG_SIGNATURE
        + png_chunk(b'IHDR', header)
        + png_chunk(b'IDAT', zlib.compress(raw, 9))
        + png_chunk(b'IEND', b'')
    )


def write_png(
        path: str | Path,
        pixels: bytes,
        size: tuple[int, int],
        *,
        channels: int = 4,
        flip: bool = True,
) -> Path:
    """
    Encode raw pixels and write them to a PNG file.

    Args:
        path: Destination of the file.
        pixels: Rows of pixels, of ``channels`` bytes each.
        size: Width and height of the image, in pixels.
        channels: Number of bytes per pixel, one of PNG_COLOR_TYPES.
        flip: Reverse the row order.

    Returns:
        The path the image was written to.

    """
    destination = Path(path)
    destination.write_bytes(
        encode_png(pixels, size, channels=channels, flip=flip),
    )

    return destination
