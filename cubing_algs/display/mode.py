"""Mode handling for visual display."""
from typing import TYPE_CHECKING

from cubing_algs.annotations import CubeDisplayMask
from cubing_algs.annotations import CubeOrientation
from cubing_algs.annotations import POVDisplayMask
from cubing_algs.constants import ADJACENT_FACES
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.display.masks import AF2L_MASK
from cubing_algs.display.masks import CLL_MASK
from cubing_algs.display.masks import CLS_MASK
from cubing_algs.display.masks import CMLL_MASK
from cubing_algs.display.masks import COLL_MASK
from cubing_algs.display.masks import CPLL_MASK
from cubing_algs.display.masks import CROSS_BOTTOM_MASK
from cubing_algs.display.masks import CROSS_TOP_MASK
from cubing_algs.display.masks import DIMMED_MASK
from cubing_algs.display.masks import ELL_MASK
from cubing_algs.display.masks import ELS_MASK
from cubing_algs.display.masks import EO_CROSS_MASK
from cubing_algs.display.masks import EO_EDGE_MASK
from cubing_algs.display.masks import EO_LINE_MASK
from cubing_algs.display.masks import EO_MASK
from cubing_algs.display.masks import EO_SLICE_MASK
from cubing_algs.display.masks import EOLL_MASK
from cubing_algs.display.masks import EPLL_MASK
from cubing_algs.display.masks import F2L_BL_MASK
from cubing_algs.display.masks import F2L_BR_MASK
from cubing_algs.display.masks import F2L_FL_MASK
from cubing_algs.display.masks import F2L_FR_MASK
from cubing_algs.display.masks import F2L_MASK
from cubing_algs.display.masks import HIDDEN_MASK
from cubing_algs.display.masks import L6EO_MASK
from cubing_algs.display.masks import L10P_MASK
from cubing_algs.display.masks import LL_MASK
from cubing_algs.display.masks import LS_MASK
from cubing_algs.display.masks import LS_OCLL_MASK
from cubing_algs.display.masks import LS_OLL_MASK
from cubing_algs.display.masks import LSE_MASK
from cubing_algs.display.masks import MASKED_MASK
from cubing_algs.display.masks import NO_CENTER_MASK
from cubing_algs.display.masks import NO_CORNER_MASK
from cubing_algs.display.masks import NO_EDGE_MASK
from cubing_algs.display.masks import OCLL_MASK
from cubing_algs.display.masks import OLL_MASK
from cubing_algs.display.masks import ORIENTED_MASK
from cubing_algs.display.masks import PLL_MASK
from cubing_algs.display.masks import VISIBLE_MASK
from cubing_algs.display.masks import ZBLL_MASK
from cubing_algs.display.masks import ZBLS_MASK

if TYPE_CHECKING:
    from cubing_algs.vcube import VCube

MODE_CONFIGS: dict[str, tuple[POVDisplayMask, str, str]] = {
    'll':           (LL_MASK,           'top', ''),                          # noqa: E241
    'oll':          (OLL_MASK,          'top', ''),                          # noqa: E241
    'ocll':         (OCLL_MASK,         'top', ''),                          # noqa: E241
    'pll':          (PLL_MASK,          'top', ''),                          # noqa: E241
    'cpll':         (CPLL_MASK,         'top', ''),                          # noqa: E241
    'epll':         (EPLL_MASK,         'top', ''),                          # noqa: E241
    'zbll':         (ZBLL_MASK,         'top', ''),                          # noqa: E241
    'cll':          (CLL_MASK,          'top', ''),                          # noqa: E241
    'coll':         (COLL_MASK,         'top', ''),                          # noqa: E241
    'ell':          (ELL_MASK,          'top', ''),                          # noqa: E241
    'eoll':         (EOLL_MASK,         'top', ''),                          # noqa: E241
    'ls':           (LS_MASK,           '',    ''),                          # noqa: E241
    'ls-oll':       (LS_OLL_MASK,       '',    ''),                          # noqa: E241
    'ls-ocll':      (LS_OCLL_MASK,      '',    ''),                          # noqa: E241
    'els':          (ELS_MASK,          '',    ''),                          # noqa: E241
    'zbls':         (ZBLS_MASK,         '',    ''),                          # noqa: E241
    # vls / wvls show the same pieces as ls-oll / ls-ocll, so share the mask
    'vls':          (LS_OLL_MASK,       '',    ''),                          # noqa: E241
    'wvls':         (LS_OCLL_MASK,      '',    ''),                          # noqa: E241
    'cls':          (CLS_MASK,          '',    ''),                          # noqa: E241
    'cross-top':    (CROSS_TOP_MASK,    '',    'cross_top_orientation'),     # noqa: E241
    'cross-bottom': (CROSS_BOTTOM_MASK, '',    'cross_bottom_orientation'),  # noqa: E241
    'cross':        (CROSS_BOTTOM_MASK, '',    'cross_bottom_orientation'),  # noqa: E241
    'f2l':          (F2L_MASK,          '',    'f2l_orientation'),           # noqa: E241
    'af2l':         (AF2L_MASK,         '',    'f2l_orientation'),           # noqa: E241
    'f2l-fr':       (F2L_FR_MASK,       '',    ''),                          # noqa: E241
    'f2l-fl':       (F2L_FL_MASK,       '',    ''),                          # noqa: E241
    'f2l-br':       (F2L_BR_MASK,       '',    ''),                          # noqa: E241
    'f2l-bl':       (F2L_BL_MASK,       '',    ''),                          # noqa: E241
    'cmll':         (CMLL_MASK,         '',    ''),                          # noqa: E241
    'lse':          (LSE_MASK,          '',    ''),                          # noqa: E241
    'l6eo':         (L6EO_MASK,         '',    ''),                          # noqa: E241
    'l10p':         (L10P_MASK,         '',    ''),                          # noqa: E241
    'eo':           (EO_MASK,           '',    ''),                          # noqa: E241
    'eo-cross':     (EO_CROSS_MASK,     '',    ''),                          # noqa: E241
    'eo-line':      (EO_LINE_MASK,      '',    ''),                          # noqa: E241
    'eo-slice':     (EO_SLICE_MASK,     '',    ''),                          # noqa: E241
    'eo-edge':      (EO_EDGE_MASK,      '',    ''),                          # noqa: E241
    'visible':      (VISIBLE_MASK,      '',    ''),                          # noqa: E241
    'dimmed':       (DIMMED_MASK,       '',    ''),                          # noqa: E241
    'masked':       (MASKED_MASK,       '',    ''),                          # noqa: E241
    'oriented':     (ORIENTED_MASK,     '',    ''),                          # noqa: E241
    'hidden':       (HIDDEN_MASK,       '',    ''),                          # noqa: E241
    'no-center':    (NO_CENTER_MASK,    '',    ''),                          # noqa: E241
    'no-corner':    (NO_CORNER_MASK,    '',    ''),                          # noqa: E241
    'no-edge':      (NO_EDGE_MASK,      '',    ''),                          # noqa: E241
}


class ModeDisplay:
    """Mixin handling mode computing tools."""

    cube: 'VCube'
    face_size: int
    cube_size: int

    def compute_best_front_face(self, color: str, front: str) -> str:
        """
        Determine the best front face with most matching color facelets.

        Gives priority to the default front face on ties.

        Returns:
            The character representing the face.

        """
        face = ''
        max_score = -1

        faces = list(ADJACENT_FACES[color])
        faces.remove(front)
        faces.insert(0, front)

        for f in faces:
            facelets = self.cube.get_face_by_center(f)
            count_facelets = facelets.count(color)

            if count_facelets > max_score:
                face = f
                max_score = count_facelets

        return face

    def cross_top_orientation(self) -> CubeOrientation:
        """
        Determine the front face with the most cross top color facelets.

        Returns:
            Characters representing the new face orientation.

        """
        top = self.cube.orientation[0]
        front = self.cube.orientation[1]

        new_front = self.compute_best_front_face(
            top, front,
        )

        if front == new_front:
            return ''

        return f'{ top }{ new_front }'

    def cross_bottom_orientation(self) -> CubeOrientation:
        """
        Determine the front face with the most cross bottom color facelets.

        Returns:
            Characters representing the new face orientation.

        """
        top = self.cube.orientation[0]
        bottom = OPPOSITE_FACES[top]
        front = self.cube.orientation[1]

        new_front = self.compute_best_front_face(
            bottom, front,
        )

        if front == new_front:
            return ''

        return f'{ top }{ new_front }'

    def f2l_orientation(self) -> CubeOrientation:
        """
        Determine the optimal front face orientation for F2L display mode
        keeping the initial top face orientation.

        Align F2L into FR slot for consistent results,
        select face with the most broken F2L.

        Returns:
            Characters representing the new face orientation.

        """
        top = self.cube.orientation[0]
        front = self.cube.orientation[1]
        adjacent_faces = ADJACENT_FACES[top]
        face_number = len(adjacent_faces)

        index = adjacent_faces.index(front)
        faces = adjacent_faces[index:] + adjacent_faces[:index]

        rows = [
            self.cube.get_face_by_center(face)[self.cube_size:self.face_size]
            for face in faces
        ]
        start_diff = [
            rows[i][0] != faces[i] or rows[i][-self.cube_size] != faces[i]
            for i in range(face_number)
        ]
        end_diff = [
            rows[i][self.cube_size - 1] != faces[i] or rows[i][-1] != faces[i]
            for i in range(face_number)
        ]

        fr_slots = [
            end_diff[i] or start_diff[(i + 1) % face_number]
            for i in range(face_number)
        ]
        fl_slots = [
            start_diff[i] or end_diff[(i - 1) % face_number]
            for i in range(face_number)
        ]

        check_order = [0, 1, 3, 2]
        selected_face = front

        for i in check_order:
            if fr_slots[i] and fl_slots[i]:
                selected_face = faces[i]
                break
        else:
            for i in check_order:
                if fr_slots[i]:
                    selected_face = faces[i]
                    break

        if selected_face == front:
            return ''

        return f'{ top }{ selected_face }'

    @staticmethod
    def scale_mask(
            mask: POVDisplayMask,
            target_size: int,
    ) -> POVDisplayMask:
        """
        Scale a 3x3 mask to a different cube size.

        Each of the 9 positions per 3x3 face acts as a template for
        a region in the target NxN face:

        - 4 corners map 1:1 to the 4 target corners
        - 4 edges expand to all border non-corner facelets on that side
        - 1 center expands to all interior facelets

        Args:
            mask: A 54-character binary mask for a 3x3 cube.
            target_size: The target cube size (e.g. 2, 4, 5).

        Returns:
            A display mask string of length ``6 * target_size ** 2``.

        """
        n = target_size
        result: list[str] = []

        for face in range(6):
            template = mask[face * 9:(face + 1) * 9]

            for row in range(n):
                for col in range(n):
                    if row == 0:
                        r = 0
                    elif row == n - 1:
                        r = 2
                    else:
                        r = 1

                    if col == 0:
                        c = 0
                    elif col == n - 1:
                        c = 2
                    else:
                        c = 1

                    result.append(template[r * 3 + c])

        return ''.join(result)

    def realign_mask(self, mask: POVDisplayMask) -> CubeDisplayMask:
        """
        Convert a mask from user-POV coordinates to cube-internal coordinates.

        Masks are authored from the user's point of view (e.g. '1' at U
        positions means "the top face as I see it"). But internally the
        cube may be oriented differently — if the user holds D on top
        (a z2 from solved), the physical top is the D face, not U.

        This method applies the inverse of the cube's orientation to the
        mask so that its '1' bits land on the correct internal face
        positions. The realigned mask can then be replayed through the
        algorithm's move history by ``map_mask``.

        Args:
            mask: The mask to realign, in user-POV coordinates.

        Returns:
            The mask expressed in cube-internal coordinates.

        """
        from cubing_algs.vcube import VCube  # noqa: PLC0415

        cube = VCube(
            mask,
            size=self.cube_size,
            check=False,
        )

        # Detect if internal orientation is broken
        if len(set(self.cube.face_center_colors)) == self.cube.face_number:
            moves = self.cube.compute_orientation_moves('UF')
        else:
            moves = ' '.join(self.cube.history)

        cube.rotate(moves)

        return cube.state

    def map_mask(
            self,
            cube: 'VCube',
            mask: CubeDisplayMask,
    ) -> CubeDisplayMask:
        """
        Map raw display mask to facelets position for display filtering.

        Args:
            cube: The virtual cube instance to process.
            mask: Mask string in cubies format or empty string.

        Returns:
            Mask string mapped to final facelets positions.

        """
        if not mask:
            return '1' * len(cube.state)

        from cubing_algs.vcube import VCube  # noqa: PLC0415

        cube_mask = VCube(
            initial=mask,
            size=self.cube_size,
            check=False,
        )
        cube_mask.rotate(' '.join(cube.history))

        return cube_mask.state

    def resolve_mode(self, mode: str) -> tuple[CubeDisplayMask, str, str]:
        """
        Resolve display mode into mask, layout, and orientation settings.

        Args:
            mode: Solving-stage preset name (e.g. ``'oll'``, ``'f2l'``).

        Returns:
            Tuple of (mask, layout, orientation) for the given mode,
            or a tuple of empty strings if the mode is unknown.

        """
        if mode not in MODE_CONFIGS:
            return '', '', ''

        mask, layout, orientation_cb = MODE_CONFIGS[mode]

        orientation = ''
        if orientation_cb:
            orientation = getattr(self, orientation_cb)()

        if self.cube_size != 3:
            mask = self.scale_mask(mask, self.cube_size)

        mask = self.realign_mask(mask)

        return mask, layout, orientation
