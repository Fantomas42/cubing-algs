"""Tests for mirror layout rendering."""
import unittest

from cubing_algs.display.constants import DISTANCE
from cubing_algs.display.image import ImageDisplay
from cubing_algs.vcube import VCube


class ComputeMirrorFacesTestCase(unittest.TestCase):
    """Tests for compute_mirror_faces."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.display = ImageDisplay(VCube())
        self.rotations = ImageDisplay.parse_rotation('y45x-34')

    def test_returns_three_hidden_faces(self) -> None:
        """At default rotation, exactly 3 faces are hidden."""
        faces = self.display.compute_mirror_faces(self.rotations, DISTANCE)
        self.assertEqual(len(faces), 3)

    def test_hidden_face_names_at_default_rotation(self) -> None:
        """At y45x-34, the hidden faces are D, L, B."""
        faces = self.display.compute_mirror_faces(self.rotations, DISTANCE)
        names = {f[0] for f in faces}
        self.assertEqual(names, {'D', 'L', 'B'})

    def test_face_data_structure(self) -> None:
        """Each item is (name, 4 corners, state_index)."""
        faces = self.display.compute_mirror_faces(self.rotations, DISTANCE)
        for face_name, corners_2d, face_index in faces:
            self.assertIsInstance(face_name, str)
            self.assertEqual(len(corners_2d), 4)
            self.assertIsInstance(face_index, int)

    def test_no_overlap_with_visible_faces(self) -> None:
        """Mirror faces and visible faces are disjoint and cover all 6 faces."""
        r = self.rotations
        mirror = self.display.compute_mirror_faces(r, DISTANCE)
        visible = self.display.compute_visible_faces(r, DISTANCE)
        mirror_names = {f[0] for f in mirror}
        visible_names = {f[0] for f in visible}
        self.assertEqual(mirror_names & visible_names, set())
        self.assertEqual(
            mirror_names | visible_names,
            {'U', 'R', 'F', 'D', 'L', 'B'},
        )


class RenderMirrorTestCase(unittest.TestCase):
    """Tests for render_mirror output."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()
        self.display = ImageDisplay(self.cube)

    def test_returns_valid_svg(self) -> None:
        """render_mirror produces a valid SVG document."""
        svg = self.display.render_mirror(
            200, self.cube.state, '1' * 54,
        )
        self.assertTrue(svg.startswith('<svg'))
        self.assertTrue(svg.endswith('</svg>'))
        self.assertIn('xmlns="http://www.w3.org/2000/svg"', svg)

    def test_six_face_groups(self) -> None:
        """render_mirror produces 6 face groups (3 hidden + 3 visible)."""
        svg = self.display.render_mirror(
            200, self.cube.state, '1' * 54,
        )
        self.assertEqual(svg.count('<g class="face-'), 6)

    def test_hidden_faces_have_opacity(self) -> None:
        """Hidden face groups carry opacity attribute."""
        svg = self.display.render_mirror(
            200, self.cube.state, '1' * 54, rotation='y45x-34',
        )
        for face in ('D', 'L', 'B'):
            self.assertIn(f'<g class="face-{face}" opacity="0.5">', svg)

    def test_visible_faces_no_opacity(self) -> None:
        """Visible face groups do not have an opacity attribute."""
        svg = self.display.render_mirror(
            200, self.cube.state, '1' * 54, rotation='y45x-34',
        )
        for face in ('U', 'F', 'R'):
            self.assertIn(f'<g class="face-{face}">', svg)
            self.assertNotIn(f'<g class="face-{face}" opacity=', svg)

    def test_mask_respected_on_hidden_faces(self) -> None:
        """Mask '2' (oriented) applied to all facelets produces valid SVG."""
        svg = self.display.render_mirror(
            200, self.cube.state, '2' * 54,
        )
        self.assertTrue(svg.startswith('<svg'))
        self.assertEqual(svg.count('<g class="face-'), 6)

    def test_arrows_on_visible_face_rendered(self) -> None:
        """Arrow on a visible face (U at y45x-34) appears in the output."""
        svg = self.display.render_mirror(
            200, self.cube.state, '1' * 54,
            rotation='y45x-34',
            arrows=[('U', 0, 'U', 8, '')],
        )
        self.assertIn('class="arrows"', svg)

    def test_arrows_on_hidden_face_skipped(self) -> None:
        """Arrow on a hidden face (D at y45x-34) is silently skipped."""
        svg = self.display.render_mirror(
            200, self.cube.state, '1' * 54,
            rotation='y45x-34',
            arrows=[('D', 0, 'D', 8, '')],
        )
        self.assertNotIn('class="arrows"', svg)


class RenderMirrorRoutingTestCase(unittest.TestCase):
    """Tests for layout='mirror' routing through render()."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.display = ImageDisplay(VCube())

    def test_render_mirror_layout_gives_six_groups(self) -> None:
        """render(layout='mirror') produces 6 face groups."""
        svg = self.display.render(layout='mirror')
        self.assertEqual(svg.count('<g class="face-'), 6)

    def test_render_default_gives_three_groups(self) -> None:
        """render() without layout still produces 3 face groups."""
        svg = self.display.render()
        self.assertEqual(svg.count('<g class="face-'), 3)

    def test_render_top_unaffected(self) -> None:
        """render(layout='top') still produces the top-view layout."""
        svg = self.display.render(layout='top')
        self.assertIn('class="face-U"', svg)
        self.assertEqual(svg.count('<g class="face-'), 5)

    def test_render_mirror_with_rotation(self) -> None:
        """render(layout='mirror', rotation=...) passes rotation through."""
        svg = self.display.render(layout='mirror', rotation='y45x-34')
        self.assertEqual(svg.count('<g class="face-'), 6)
        for face in ('D', 'L', 'B'):
            self.assertIn(f'<g class="face-{face}" opacity="0.5">', svg)
