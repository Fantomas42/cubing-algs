"""Tests for the image encoding of the GPU rendering backend."""
import io
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from typing import TYPE_CHECKING
from typing import cast
from unittest import mock

from cubing_algs.display.gl.encode import GIF_TRANSPARENT_INDEX
from cubing_algs.display.gl.encode import PNG_SIGNATURE
from cubing_algs.display.gl.encode import encode_gif
from cubing_algs.display.gl.encode import encode_png
from cubing_algs.display.gl.encode import has_pillow
from cubing_algs.display.gl.encode import png_chunk
from cubing_algs.display.gl.encode import write_frames
from cubing_algs.display.gl.encode import write_gif
from cubing_algs.display.gl.encode import write_png

if TYPE_CHECKING:  # pragma: no cover
    from PIL import Image

GIF_SIGNATURE = b'GIF89a'

# Two tiny frames, a red square and a blue one, the last column of
# each left fully transparent.
FRAME_SIZE = (2, 2)
RED_FRAME = (b'\xff\x00\x00\xff' + b'\x00\x00\x00\x00') * 2
BLUE_FRAME = (b'\x00\x00\xff\xff' + b'\x00\x00\x00\x00') * 2

requires_pillow = unittest.skipUnless(
    has_pillow(),
    'Pillow is not installed',
)


def frames_of(data: bytes) -> list['Image.Image']:
    """
    Split an animated GIF into its frames.

    Returns:
        The frames of the animation, in order.

    """
    from PIL import Image
    from PIL import ImageSequence

    with Image.open(io.BytesIO(data)) as animation:
        return [
            frame.copy()
            for frame in ImageSequence.Iterator(animation)
        ]


def pixel_of(
        frame: 'Image.Image',
        mode: str,
        point: tuple[int, int],
) -> tuple[int, ...]:
    """
    Read one pixel of a frame, converted to a given mode.

    Returns:
        The channels of the pixel.

    """
    return cast('tuple[int, ...]', frame.convert(mode).getpixel(point))


def read_chunks(data: bytes) -> dict[bytes, bytes]:
    """
    Split a PNG file into its chunks.

    Returns:
        Mapping of chunk types to their payload.

    """
    chunks: dict[bytes, bytes] = {}
    offset = len(PNG_SIGNATURE)

    while offset < len(data):
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        chunks[kind] = data[offset + 8:offset + 8 + length]
        offset += 12 + length

    return chunks


def read_pixels(data: bytes, width: int, channels: int) -> bytes:
    """
    Decode a PNG into its raw pixels, dropping the filter bytes.

    Returns:
        The concatenated rows of pixels.

    """
    raw = zlib.decompress(read_chunks(data)[b'IDAT'])
    stride = width * channels + 1

    return b''.join(
        raw[row + 1:row + stride]
        for row in range(0, len(raw), stride)
    )


class TestPngChunk(unittest.TestCase):
    """Tests for png_chunk function."""

    def test_layout(self) -> None:
        """Test that a chunk carries length, type, payload and CRC."""
        chunk = png_chunk(b'IEND', b'')

        self.assertEqual(chunk[:4], struct.pack('>I', 0))
        self.assertEqual(chunk[4:8], b'IEND')
        self.assertEqual(len(chunk), 12)

    def test_crc(self) -> None:
        """Test that the CRC covers both type and payload."""
        chunk = png_chunk(b'IDAT', b'payload')
        expected = zlib.crc32(b'IDATpayload') & 0xFFFFFFFF

        self.assertEqual(struct.unpack('>I', chunk[-4:])[0], expected)


class TestEncodePng(unittest.TestCase):
    """Tests for encode_png function."""

    def test_signature(self) -> None:
        """Test that the file starts with the PNG signature."""
        data = encode_png(b'\x00' * 16, (2, 2))

        self.assertEqual(data[:8], PNG_SIGNATURE)

    def test_header(self) -> None:
        """Test that IHDR carries the dimensions and the color type."""
        data = encode_png(b'\x00' * 24, (3, 2))
        header = read_chunks(data)[b'IHDR']

        width, height, depth, color_type = struct.unpack('>IIBB', header[:10])

        self.assertEqual(width, 3)
        self.assertEqual(height, 2)
        self.assertEqual(depth, 8)
        self.assertEqual(color_type, 6)

    def test_ends_with_iend(self) -> None:
        """Test that the file is properly terminated."""
        data = encode_png(b'\x00' * 16, (2, 2))

        self.assertIn(b'IEND', read_chunks(data))

    def test_roundtrip_without_flip(self) -> None:
        """Test that pixels are preserved when rows are kept in order."""
        pixels = bytes(range(2 * 2 * 4))
        data = encode_png(pixels, (2, 2), flip=False)

        self.assertEqual(read_pixels(data, 2, 4), pixels)

    def test_roundtrip_with_flip(self) -> None:
        """Test that flipping reverses the row order."""
        top = b'\x01' * 8
        bottom = b'\x02' * 8
        data = encode_png(bottom + top, (2, 2), flip=True)

        self.assertEqual(read_pixels(data, 2, 4), top + bottom)

    def test_three_channels(self) -> None:
        """Test that RGB pixels use the truecolor type."""
        data = encode_png(b'\xff' * 12, (2, 2), channels=3)
        header = read_chunks(data)[b'IHDR']

        self.assertEqual(header[9], 2)

    def test_single_channel(self) -> None:
        """Test that greyscale pixels use the greyscale type."""
        data = encode_png(b'\x80' * 4, (2, 2), channels=1)
        header = read_chunks(data)[b'IHDR']

        self.assertEqual(header[9], 0)

    def test_unsupported_channels(self) -> None:
        """Test that an unknown channel count is rejected."""
        with self.assertRaises(ValueError) as context:
            encode_png(b'\x00' * 8, (2, 2), channels=2)

        self.assertIn('channel count', str(context.exception))

    def test_pixel_count_mismatch(self) -> None:
        """Test that a truncated pixel buffer is rejected."""
        with self.assertRaises(ValueError) as context:
            encode_png(b'\x00' * 8, (2, 2))

        self.assertIn('Expected 16 bytes', str(context.exception))


class TestWritePng(unittest.TestCase):
    """Tests for write_png function."""

    def test_writes_file(self) -> None:
        """Test that the encoded image lands on disk."""
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'out.png'
            written = write_png(destination, b'\x00' * 16, (2, 2))

            self.assertEqual(written, destination)
            self.assertEqual(destination.read_bytes()[:8], PNG_SIGNATURE)

    def test_accepts_string_path(self) -> None:
        """Test that a string destination is accepted."""
        with tempfile.TemporaryDirectory() as directory:
            destination = str(Path(directory) / 'out.png')
            written = write_png(destination, b'\x00' * 16, (2, 2))

            self.assertTrue(written.exists())


class TestWriteFrames(unittest.TestCase):
    """Tests for the fallback writing an animation as PNG frames."""

    def test_one_file_per_frame(self) -> None:
        """Test that every frame lands on disk under its own name."""
        with tempfile.TemporaryDirectory() as directory:
            written = write_frames(
                Path(directory) / 'anim.gif',
                [RED_FRAME, BLUE_FRAME],
                FRAME_SIZE,
            )

            self.assertEqual(
                [path.name for path in written],
                ['anim_0000.png', 'anim_0001.png'],
            )
            self.assertTrue(all(path.exists() for path in written))

    def test_the_frames_are_png(self) -> None:
        """Test that a frame is a plain PNG anybody can read."""
        with tempfile.TemporaryDirectory() as directory:
            written = write_frames(
                Path(directory) / 'anim.gif',
                [RED_FRAME],
                FRAME_SIZE,
            )

            self.assertEqual(
                written[0].read_bytes()[:8],
                PNG_SIGNATURE,
            )

    def test_no_frame_writes_nothing(self) -> None:
        """Test that an empty animation leaves the folder alone."""
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                write_frames(Path(directory) / 'anim.gif', [], FRAME_SIZE),
                [],
            )


@requires_pillow
class TestEncodeGif(unittest.TestCase):
    """Tests for the GIF encoding of an animation."""

    def test_signature(self) -> None:
        """Test that the file starts with the GIF signature."""
        data = encode_gif(
            [RED_FRAME, BLUE_FRAME], FRAME_SIZE, frame_rate=25.0,
        )

        self.assertEqual(data[:6], GIF_SIGNATURE)

    def test_holds_every_frame(self) -> None:
        """Test that the animation keeps all of its frames."""
        data = encode_gif(
            [RED_FRAME, BLUE_FRAME, RED_FRAME], FRAME_SIZE, frame_rate=25.0,
        )

        self.assertEqual(len(frames_of(data)), 3)

    def test_the_frame_rate_sets_the_delay(self) -> None:
        """Test that the duration of a frame follows the frame rate."""
        data = encode_gif([RED_FRAME], FRAME_SIZE, frame_rate=10.0)

        self.assertEqual(frames_of(data)[0].info['duration'], 100)

    def test_the_colors_of_the_frames_survive(self) -> None:
        """Test that a frame keeps the colors it was given."""
        first, second = frames_of(
            encode_gif([RED_FRAME, BLUE_FRAME], FRAME_SIZE, frame_rate=25.0),
        )

        self.assertEqual(pixel_of(first, 'RGB', (0, 0)), (255, 0, 0))
        self.assertEqual(pixel_of(second, 'RGB', (0, 0)), (0, 0, 255))

    def test_the_background_stays_transparent(self) -> None:
        """Test that an empty pixel is not painted at all."""
        frame = frames_of(
            encode_gif([RED_FRAME], FRAME_SIZE, frame_rate=25.0),
        )[0]

        # Pillow shrinks a palette that holds a handful of colors, and
        # moves the transparent index along with it.
        self.assertIn('transparency', frame.info)
        self.assertLessEqual(frame.info['transparency'], GIF_TRANSPARENT_INDEX)
        self.assertEqual(pixel_of(frame, 'RGBA', (1, 0))[3], 0)

    def test_rows_are_flipped_by_default(self) -> None:
        """Test that a framebuffer read comes out the right way up."""
        pixels = b'\x00\x00\xff\xff' * 2 + b'\xff\x00\x00\xff' * 2

        flipped = frames_of(
            encode_gif([pixels], FRAME_SIZE, frame_rate=25.0),
        )[0]
        kept = frames_of(
            encode_gif([pixels], FRAME_SIZE, frame_rate=25.0, flip=False),
        )[0]

        self.assertEqual(pixel_of(flipped, 'RGB', (0, 0)), (255, 0, 0))
        self.assertEqual(pixel_of(kept, 'RGB', (0, 0)), (0, 0, 255))

    def test_no_frame_is_rejected(self) -> None:
        """Test that an empty animation cannot be encoded."""
        with self.assertRaises(ValueError) as context:
            encode_gif([], FRAME_SIZE, frame_rate=25.0)

        self.assertIn('one frame', str(context.exception))


@requires_pillow
class TestWriteGif(unittest.TestCase):
    """Tests for write_gif function."""

    def test_writes_file(self) -> None:
        """Test that the encoded animation lands on disk."""
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'out.gif'
            written = write_gif(
                destination, [RED_FRAME, BLUE_FRAME], FRAME_SIZE,
                frame_rate=25.0,
            )

            self.assertEqual(written, destination)
            self.assertEqual(destination.read_bytes()[:6], GIF_SIGNATURE)


class TestPillowMissing(unittest.TestCase):
    """Tests for what happens when Pillow is nowhere to be found."""

    def test_encoding_a_gif_names_the_missing_dependency(self) -> None:
        """Test that the error tells what to install."""
        with (
                mock.patch(
                    'cubing_algs.display.gl.encode.has_pillow',
                    return_value=False,
                ),
                self.assertRaises(ImportError) as context,
        ):
            encode_gif([RED_FRAME], FRAME_SIZE, frame_rate=25.0)

        self.assertIn('Pillow', str(context.exception))
