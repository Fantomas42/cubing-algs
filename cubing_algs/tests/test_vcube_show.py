"""Tests for VCube.show() output compatibility."""
import re
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from cubing_algs.annotations import Mask
from cubing_algs.masks import CENTERS_MASK
from cubing_algs.vcube import VCube


class VCubeShowMixin:
    """Testing tools for VCube.show() output verification."""

    ANSI_RE = re.compile(r'\x1b\[[^m]*m')
    # Default palette masked background: '#444444' → rgb(68,68,68)
    MASKED_BG = '\x1b[48;2;68;68;68m'

    @staticmethod
    def show_output(cube: VCube,
                    mode: str = '',
                    orientation: str = '',
                    mask: Mask = '',
                    layout: str = '') -> str:
        """
        Run cube.show() and capture stdout.

        Returns:
            Raw stdout output including ANSI escape codes.

        """
        buf = StringIO()
        with (
            patch('cubing_algs.display.vcube.USE_COLORS', new=True),
            redirect_stdout(buf),
        ):
            cube.show(
                mode=mode,
                orientation=orientation,
                mask=mask,
                layout=layout,
            )
        return buf.getvalue()

    def show_stripped(self, cube: VCube,
                      mode: str = '',
                      orientation: str = '',
                      mask: Mask = '',
                      layout: str = '') -> str:
        """
        Run cube.show() and return output with ANSI codes stripped.

        Returns:
            Plain text output with face letters and spacing.

        """
        return self.ANSI_RE.sub(
            '',
            self.show_output(
                cube,
                mode=mode,
                orientation=orientation,
                mask=mask,
                layout=layout,
            ),
        )

    def show_grid(self, cube: VCube,
                  mode: str = '',
                  orientation: str = '',
                  mask: Mask = '',
                  layout: str = '') -> str:
        """
        Run cube.show() and return a readable grid.

        Same layout as stripped output, but with case encoding:
        Uppercase = bright (visible), lowercase = dimmed (masked).

        Returns:
            Grid string with case-encoded mask information.

        """
        raw = self.show_output(
            cube,
            mode=mode,
            orientation=orientation,
            mask=mask,
            layout=layout,
        )

        i = 0
        result: list[str] = []
        is_masked = False

        while i < len(raw):
            if raw[i] == '\x1b':
                end = raw.index('m', i) + 1
                seq = raw[i:end]
                if seq.startswith('\x1b[48;2;'):
                    is_masked = seq == self.MASKED_BG
                i = end
            elif raw[i].isalpha():
                result.append(raw[i].lower() if is_masked else raw[i].upper())
                i += 1
            else:
                result.append(raw[i])
                i += 1
        return ''.join(result).rstrip('\n')


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowPLLTestCase(VCubeShowMixin, unittest.TestCase):
    """Test PLL mode output for T Perm case."""

    def setUp(self) -> None:
        """Set up T Perm cube state."""
        self.cube = VCube()
        self.cube.rotate("z2 L2 U' L2 D F2 R2 U R2 D' F2")

    def test_pll_mode_grid(self) -> None:
        """Test PLL mode mask dims D-face and highlights edges."""
        grid = self.show_grid(self.cube, mode='pll')

        expected = (
            '          L  R  L \n'
            '       B  d  d  d  F \n'
            '       B  d  d  d  F \n'
            '       R  d  d  d  R \n'
            '          F  L  B '
        )
        self.assertEqual(grid, expected)

    def test_pll_linear_layout(self) -> None:
        """Test PLL mode with linear layout."""
        grid = self.show_grid(self.cube, mode='pll', layout='linear')

        expected = (
            ' d  d  d   R  F  F   F  L  B   u  u  u   B  B  R   L  R  L \n'
            ' d  d  d   l  l  l   f  f  f   u  u  u   r  r  r   b  b  b \n'
            ' d  d  d   l  l  l   f  f  f   u  u  u   r  r  r   b  b  b '
        )
        self.assertEqual(grid, expected)

    def test_pll_extended_layout(self) -> None:
        """Test PLL mode with extended net layout."""
        grid = self.show_grid(self.cube, mode='pll', layout='extended')

        expected = (
            '                L  R  L \n'
            '             B  d  d  d  F \n'
            '             B  d  d  d  F \n'
            '             R  d  d  d  R \n'
            '    D  D  D                 D  D  D  D  D  D \n'
            ' L  B  B  R     F  L  B     R  F  F  L  R  L  B \n'
            ' B  r  r  r     f  f  f     l  l  l  b  b  b  R \n'
            ' B  r  r  r     f  f  f     l  l  l  b  b  b  R \n'
            '    U  U  U                 U  U  U  U  U  U \n'
            '             R  u  u  u  L \n'
            '             R  u  u  u  L \n'
            '             R  u  u  u  L \n'
            '                B  B  B '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowOLLTestCase(VCubeShowMixin, unittest.TestCase):
    """Test OLL mode output for case 14 Anti-Gun."""

    def setUp(self) -> None:
        """Set up OLL case 14 Anti-Gun cube state."""
        self.cube = VCube()
        self.cube.rotate("z2 F U F' R' F R U' R' F' R")

    def test_oll_mode_grid(self) -> None:
        """Test OLL mode mask highlights U-face colors and dims D-face."""
        grid = self.show_grid(self.cube, mode='oll')

        expected = (
            '          b  D  D \n'
            '       D  l  f  r  f \n'
            '       r  D  D  D  b \n'
            '       r  b  l  D  l \n'
            '          D  D  f '
        )
        self.assertEqual(grid, expected)

    def test_oll_linear_layout(self) -> None:
        """Test OLL mode with linear layout."""
        grid = self.show_grid(self.cube, mode='oll', layout='linear')

        expected = (
            ' l  f  r   l  b  f   D  D  f   u  u  u   D  r  r   D  D  b \n'
            ' D  D  D   l  l  l   f  f  f   u  u  u   r  r  r   b  b  b \n'
            ' b  l  D   l  l  l   f  f  f   u  u  u   r  r  r   b  b  b '
        )
        self.assertEqual(grid, expected)

    def test_oll_extended_layout(self) -> None:
        """Test OLL mode with extended net layout."""
        grid = self.show_grid(self.cube, mode='oll', layout='extended')

        expected = (
            '                B  D  D \n'
            '             D  l  f  r  F \n'
            '             R  D  D  D  B \n'
            '             R  b  l  D  L \n'
            '    L  D  B                 D  D  R  R  F  L \n'
            ' B  D  r  r     D  D  f     l  b  f  D  D  b  D \n'
            ' B  r  r  r     f  f  f     l  l  l  b  b  b  R \n'
            ' B  r  r  r     f  f  f     l  l  l  b  b  b  R \n'
            '    U  U  U                 U  U  U  U  U  U \n'
            '             R  u  u  u  L \n'
            '             R  u  u  u  L \n'
            '             R  u  u  u  L \n'
            '                B  B  B '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowPLLExampleTestCase(VCubeShowMixin, unittest.TestCase):
    """Test PLL mode matching examples/pll.py for T Perm with y x' prefix."""

    def setUp(self) -> None:
        """Set up T Perm cube state with y x' prefix."""
        self.cube = VCube()
        self.cube.rotate("y x' L2 U' L2 D F2 R2 U R2 D' F2")

    def test_no_mode(self) -> None:
        """Test plain show() without mode."""
        grid = self.show_grid(self.cube)

        expected = (
            '          L  L  L \n'
            '          L  L  L \n'
            '          L  L  L \n'
            ' D  D  F  U  B  D  F  U  U  B  F  B \n'
            ' F  F  F  U  U  U  B  B  B  D  D  D \n'
            ' F  F  F  U  U  U  B  B  B  D  D  D \n'
            '          R  R  R \n'
            '          R  R  R \n'
            '          R  R  R '
        )
        self.assertEqual(grid, expected)

    def test_pll_mode(self) -> None:
        """Test PLL mode dims D-face and highlights edges."""
        grid = self.show_grid(self.cube, mode='pll')

        expected = (
            '          B  F  B \n'
            '       D  l  l  l  U \n'
            '       D  l  l  l  U \n'
            '       F  l  l  l  F \n'
            '          U  B  D '
        )
        self.assertEqual(grid, expected)

    def test_pll_orientation_ld(self) -> None:
        """Test PLL mode with LD orientation."""
        grid = self.show_grid(self.cube, mode='pll', orientation='LD')

        expected = (
            '          D  B  U \n'
            '       F  l  l  l  F \n'
            '       U  l  l  l  D \n'
            '       U  l  l  l  D \n'
            '          B  F  B '
        )
        self.assertEqual(grid, expected)

    def test_pll_orientation_dl(self) -> None:
        """Test PLL mode with DL orientation."""
        grid = self.show_grid(self.cube, mode='pll', orientation='DL')

        expected = (
            '          r  r  r \n'
            '       f  d  d  d  b \n'
            '       f  d  d  d  b \n'
            '       D  B  F  B  U \n'
            '          l  l  l '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowOLLExampleTestCase(VCubeShowMixin, unittest.TestCase):
    """Test OLL mode matching for case 14 Anti-Gun in different orientations."""

    def setUp(self) -> None:
        """Set up OLL case 14 Anti-Gun cube state with y x prefix."""
        self.cube = VCube()
        self.cube.rotate("y x F U F' R' F R U' R' F' R")

    def test_no_mode(self) -> None:
        """Test plain show() without mode."""
        grid = self.show_grid(self.cube)

        expected = (
            '          B  D  F \n'
            '          R  R  R \n'
            '          U  B  R \n'
            ' R  F  F  R  R  D  B  U  D  R  R  U \n'
            ' F  F  F  D  D  D  B  B  B  U  U  U \n'
            ' F  F  F  D  D  D  B  B  B  U  U  U \n'
            '          L  L  L \n'
            '          L  L  L \n'
            '          L  L  L '
        )
        self.assertEqual(grid, expected)

    def test_oll_mode(self) -> None:
        """Test OLL mode highlights U-face colors and dims others."""
        grid = self.show_grid(self.cube, mode='oll')

        expected = (
            '          u  R  R \n'
            '       R  b  d  f  d \n'
            '       f  R  R  R  u \n'
            '       f  u  b  R  b \n'
            '          R  R  d '
        )
        self.assertEqual(grid, expected)

    def test_oll_orientation_ru(self) -> None:
        """Test OLL mode with RU orientation."""
        grid = self.show_grid(self.cube, mode='oll', orientation='RU')

        expected = (
            '          d  R  R \n'
            '       b  R  b  u  f \n'
            '       u  R  R  R  f \n'
            '       d  f  d  b  R \n'
            '          R  R  u '
        )
        self.assertEqual(grid, expected)

    def test_oll_orientation_ur(self) -> None:
        """Test OLL mode with UR orientation."""
        grid = self.show_grid(self.cube, mode='oll', orientation='UR')

        expected = (
            '          l  l  l \n'
            '       f  u  u  u  b \n'
            '       f  u  u  u  b \n'
            '       R  u  R  R  d \n'
            '          b  d  f '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowOrientedTestCase(VCubeShowMixin, unittest.TestCase):
    """Test orientation + CENTERS_MASK after R U R' U'."""

    def setUp(self) -> None:
        """Set up cube with R U R' U' applied."""
        self.cube = VCube()
        self.cube.rotate("R U R' U'")

    def test_orientation_uf(self) -> None:
        """Test default UF orientation with centers mask."""
        grid = self.show_grid(
            self.cube, orientation='UF', mask=CENTERS_MASK,
        )

        expected = (
            '          u  u  l \n'
            '          u  U  f \n'
            '          u  u  f \n'
            ' b  l  l  f  f  d  r  r  u  b  r  r \n'
            ' l  L  l  f  F  u  b  R  r  b  B  b \n'
            ' l  l  l  f  f  f  u  r  r  b  b  b \n'
            '          d  d  r \n'
            '          d  D  d \n'
            '          d  d  d '
        )
        self.assertEqual(grid, expected)

    def test_orientation_df(self) -> None:
        """Test DF orientation with centers mask."""
        grid = self.show_grid(
            self.cube, orientation='DF', mask=CENTERS_MASK,
        )

        expected = (
            '          d  d  d \n'
            '          d  D  d \n'
            '          r  d  d \n'
            ' r  r  u  f  f  f  l  l  l  b  b  b \n'
            ' r  R  b  u  F  f  l  L  l  b  B  b \n'
            ' u  r  r  d  f  f  l  l  b  r  r  b \n'
            '          f  u  u \n'
            '          f  U  u \n'
            '          l  u  u '
        )
        self.assertEqual(grid, expected)

    def test_orientation_fr(self) -> None:
        """Test FR orientation with centers mask."""
        grid = self.show_grid(
            self.cube, orientation='FR', mask=CENTERS_MASK,
        )

        expected = (
            '          f  f  f \n'
            '          f  F  f \n'
            '          f  u  d \n'
            ' d  d  r  u  b  r  f  u  u  l  l  l \n'
            ' d  D  d  r  R  r  f  U  u  l  L  l \n'
            ' d  d  d  r  r  u  l  u  u  b  l  l \n'
            '          b  b  b \n'
            '          b  B  r \n'
            '          b  b  r '
        )
        self.assertEqual(grid, expected)

    def test_orientation_bl(self) -> None:
        """Test BL orientation with centers mask."""
        grid = self.show_grid(
            self.cube, orientation='BL', mask=CENTERS_MASK,
        )

        expected = (
            '          b  b  b \n'
            '          b  B  r \n'
            '          b  b  r \n'
            ' d  d  d  l  l  b  u  u  l  u  r  r \n'
            ' d  D  d  l  L  l  u  U  f  r  R  r \n'
            ' r  d  d  l  l  l  u  u  f  r  b  u \n'
            '          f  f  f \n'
            '          f  F  f \n'
            '          f  u  d '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowCrossTestCase(VCubeShowMixin, unittest.TestCase):
    """Test cross mode output after scramble."""

    def setUp(self) -> None:
        """Set up scrambled cube for cross visualization."""
        self.cube = VCube()
        self.cube.rotate('B L F L F R F L B R')

    def test_cross_mode_grid(self) -> None:
        """Test cross mode mask highlights cross-relevant facelets."""
        grid = self.show_grid(self.cube, mode='cross')

        expected = (
            '          b  d  r \n'
            '          b  F  d \n'
            '          u  f  d \n'
            ' l  d  r  b  r  f  l  l  u  f  r  d \n'
            ' l  R  U  B  U  f  l  L  U  F  d  b \n'
            ' b  L  f  l  R  l  b  r  r  d  d  r \n'
            '          u  U  u \n'
            '          U  B  b \n'
            '          d  f  f '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowF2LTestCase(VCubeShowMixin, unittest.TestCase):
    """Test F2L mode output for various cases."""

    def test_f2l_mode_grid(self) -> None:
        """Test F2L mode after y' z2 R U R' U' z2 y2."""
        cube = VCube()
        cube.rotate("y' z2 R U R' U' z2 y2")
        grid = self.show_grid(cube, mode='f2l')

        expected = (
            '          d  d  f \n'
            '          d  d  L \n'
            '          d  d  L \n'
            ' r  f  f  l  l  U  B  B  d  r  b  b \n'
            ' F  F  F  L  L  d  r  B  B  R  R  R \n'
            ' F  F  F  L  L  l  d  B  B  R  R  R \n'
            '          U  U  b \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_f2l_special_case_1(self) -> None:
        """Test F2L mode after z2 F' L F L' z2."""
        cube = VCube()
        cube.rotate("z2 F' L F L' z2")
        grid = self.show_grid(cube, mode='f2l')

        expected = (
            '          d  d  r \n'
            '          d  d  r \n'
            '          l  F  F \n'
            ' b  b  d  f  R  R  U  d  d  b  l  l \n'
            ' B  B  B  R  R  d  f  F  F  L  L  L \n'
            ' B  B  B  R  R  d  f  F  F  L  L  L \n'
            '          U  U  r \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_f2l_special_case_2(self) -> None:
        """Test F2L mode after z2 L U' L' U' L U L' U' L U2 L' z2."""
        cube = VCube()
        cube.rotate("z2 L U' L' U' L U L' U' L U2 L' z2")
        grid = self.show_grid(cube, mode='f2l')

        expected = (
            '          f  d  f \n'
            '          d  d  d \n'
            '          l  d  d \n'
            ' d  r  b  d  l  b  r  b  d  r  f  l \n'
            ' L  L  L  B  B  B  R  R  R  F  F  F \n'
            ' L  L  L  B  B  R  U  R  R  F  F  F \n'
            '          U  U  B \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_f2l_special_case_3(self) -> None:
        """Test F2L mode after z2 R' D' R U R' D R U' z2."""
        cube = VCube()
        cube.rotate("z2 R' D' R U R' D R U' z2")
        grid = self.show_grid(cube, mode='f2l')

        expected = (
            '          d  d  d \n'
            '          d  d  d \n'
            '          d  d  L \n'
            ' r  r  r  f  f  F  U  l  f  l  b  b \n'
            ' R  R  R  F  F  F  L  L  L  B  B  B \n'
            ' R  R  R  F  F  l  d  L  L  B  B  B \n'
            '          U  U  b \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_f2l_special_case_4(self) -> None:
        """Test F2L mode after z2 R U' R' U R U' R' U R U' R' z2."""
        cube = VCube()
        cube.rotate("z2 R U' R' U R U' R' U R U' R' z2")
        grid = self.show_grid(cube, mode='f2l')

        expected = (
            '          l  d  l \n'
            '          d  d  d \n'
            '          d  d  U \n'
            ' f  b  b  r  r  L  F  f  b  d  l  d \n'
            ' R  R  R  F  F  F  L  L  L  B  B  B \n'
            ' R  R  R  F  F  f  r  L  L  B  B  B \n'
            '          U  U  d \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowAF2LTestCase(VCubeShowMixin, unittest.TestCase):
    """Test AF2L mode output for various cases."""

    def test_af2l_mode_grid(self) -> None:
        """Test AF2L mode after z2 B' U' B F U F' U2."""
        cube = VCube()
        cube.rotate("z2 B' U' B F U F' U2")
        grid = self.show_grid(cube, mode='af2l')

        expected = (
            '          R  R  f \n'
            '          R  d  d \n'
            '          b  d  d \n'
            ' F  F  d  l  r  r  f  b  l  d  B  U \n'
            ' L  L  L  B  B  l  d  R  d  f  F  F \n'
            ' L  L  L  B  B  d  r  R  B  R  F  F \n'
            '          U  U  b \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_af2l_special_case_1(self) -> None:
        """Test AF2L mode after z2 L2 B L B' L B U B' z2."""
        cube = VCube()
        cube.rotate("z2 L2 B L B' L B U B' z2")
        grid = self.show_grid(cube, mode='af2l')

        expected = (
            '          d  d  f \n'
            '          d  d  r \n'
            '          L  L  r \n'
            ' l  l  U  B  B  d  b  d  d  r  f  f \n'
            ' b  F  F  L  L  F  R  B  B  R  R  d \n'
            ' b  F  F  L  L  F  U  B  B  R  R  d \n'
            '          U  U  R \n'
            '          U  U  U \n'
            '          l  U  U '
        )
        self.assertEqual(grid, expected)

    def test_af2l_special_case_2(self) -> None:
        """Test AF2L mode after z2 R' U2 R U' R' F R F' z2."""
        cube = VCube()
        cube.rotate("z2 R' U2 R U' R' F R F' z2")
        grid = self.show_grid(cube, mode='af2l')

        expected = (
            '          l  d  b \n'
            '          L  d  d \n'
            '          L  L  l \n'
            ' f  F  F  U  B  b  d  l  r  d  f  d \n'
            ' F  F  d  b  L  r  d  B  B  R  R  R \n'
            ' F  F  B  U  L  r  d  B  B  R  R  R \n'
            '          L  U  f \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowF2LOrientedTestCase(VCubeShowMixin, unittest.TestCase):
    """Test F2L mode with different y-rotation orientations."""

    def test_f2l_no_orientation(self) -> None:
        """Test F2L mode without y-rotation prefix."""
        cube = VCube()
        cube.rotate("z2 R U' R' U R' F R F' U")
        grid = self.show_grid(cube, mode='f2l')

        expected = (
            '          d  d  d \n'
            '          f  d  d \n'
            '          f  l  U \n'
            ' l  d  d  r  d  L  F  b  b  r  r  f \n'
            ' R  R  R  F  F  F  L  L  L  B  B  B \n'
            ' R  R  R  F  F  d  b  L  L  B  B  B \n'
            '          U  U  l \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_f2l_y_rotation(self) -> None:
        """Test F2L mode with y rotation prefix."""
        cube = VCube()
        cube.rotate("y z2 R U' R' U R' F R F' U")
        grid = self.show_grid(cube, mode='f2l')

        expected = (
            '          d  d  d \n'
            '          r  d  d \n'
            '          r  f  U \n'
            ' f  d  d  b  d  F  R  l  l  b  b  r \n'
            ' B  B  B  R  R  R  F  F  F  L  L  L \n'
            ' B  B  B  R  R  d  l  F  F  L  L  L \n'
            '          U  U  f \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_f2l_y2_rotation(self) -> None:
        """Test F2L mode with y2 rotation prefix."""
        cube = VCube()
        cube.rotate("y2 z2 R U' R' U R' F R F' U")
        grid = self.show_grid(cube, mode='f2l')

        expected = (
            '          d  d  d \n'
            '          b  d  d \n'
            '          b  r  U \n'
            ' r  d  d  l  d  R  B  f  f  l  l  b \n'
            ' L  L  L  B  B  B  R  R  R  F  F  F \n'
            ' L  L  L  B  B  d  f  R  R  F  F  F \n'
            '          U  U  r \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_f2l_y_prime_rotation(self) -> None:
        """Test F2L mode with y' rotation prefix."""
        cube = VCube()
        cube.rotate("y' z2 R U' R' U R' F R F' U")
        grid = self.show_grid(cube, mode='f2l')

        expected = (
            '          d  d  d \n'
            '          l  d  d \n'
            '          l  b  U \n'
            ' b  d  d  f  d  B  L  r  r  f  f  l \n'
            ' F  F  F  L  L  L  B  B  B  R  R  R \n'
            ' F  F  F  L  L  d  r  B  B  R  R  R \n'
            '          U  U  b \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class VCubeShowNon3x3ModeTestCase(VCubeShowMixin, unittest.TestCase):
    """Test that show() with mode args does not raise for non-3x3x3 cubes."""

    def setUp(self) -> None:
        """Set up a 4x4x4 cube."""
        self.cube = VCube(size=4)

    def test_oll_mode_no_error(self) -> None:
        """Test OLL mode on a 4x4x4 cube does not raise."""
        output = self.show_stripped(self.cube, mode='oll')
        self.assertIsInstance(output, str)

    def test_pll_mode_no_error(self) -> None:
        """Test PLL mode on a 4x4x4 cube does not raise."""
        output = self.show_stripped(self.cube, mode='pll')
        self.assertIsInstance(output, str)

    def test_ll_mode_no_error(self) -> None:
        """Test LL mode on a 4x4x4 cube does not raise."""
        output = self.show_stripped(self.cube, mode='ll')
        self.assertIsInstance(output, str)

    def test_cross_mode_no_error(self) -> None:
        """Test cross mode on a 4x4x4 cube does not raise."""
        output = self.show_stripped(self.cube, mode='cross')
        self.assertIsInstance(output, str)

    def test_mode_changes_layout_without_masking(self) -> None:
        """
        Test that mode sets the layout but applies no masking on a 4x4x4.

        OLL mode implies layout='top'. The output must match an explicit
        layout='top' call (same layout, no mask difference).
        """
        output_mode = self.show_stripped(self.cube, mode='oll')
        output_top = self.show_stripped(self.cube, layout='top')
        self.assertEqual(output_mode, output_top)
