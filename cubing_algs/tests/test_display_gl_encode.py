"""Tests for the image encoding of the GPU rendering backend."""
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from cubing_algs.display.gl.encode import PNG_SIGNATURE
from cubing_algs.display.gl.encode import encode_png
from cubing_algs.display.gl.encode import png_chunk
from cubing_algs.display.gl.encode import write_png


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
