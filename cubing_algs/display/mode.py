"""Mode handling for visual display."""
from cubing_algs.annotations import Mask
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.masks import CROSS_BOTTOM_MASK
from cubing_algs.masks import CROSS_TOP_MASK
from cubing_algs.masks import F2L_CLL_MASK
from cubing_algs.masks import F2L_ELL_MASK
from cubing_algs.masks import F2L_LL_MASK
from cubing_algs.masks import F2L_MASK
from cubing_algs.masks import L3_MASK
from cubing_algs.masks import OLL_MASK
from cubing_algs.masks import PLL_MASK

F2L_FACE_ORIENTATIONS = {
    'FL': 'F',
    'FR': 'R',
    'BL': 'L',
    'BR': 'B',
}

F2L_ADJACENT_FACES = {
    'R': ('B', 'F'),
    'L': ('F', 'B'),
    'B': ('L', 'R'),
    'F': ('R', 'L'),
}

MODE_CONFIGS: dict[str, tuple[Mask, str, str]] = {
    'oll':          (OLL_MASK,          'top', ''),                          # noqa: E241
    'pll':          (PLL_MASK,          'top', ''),                          # noqa: E241
    'll':           (L3_MASK,           'top', ''),                          # noqa: E241
    'cross-top':    (CROSS_TOP_MASK,    '',    'cross_top_orientation'),     # noqa: E241
    'cross-bottom': (CROSS_BOTTOM_MASK, '',    'cross_bottom_orientation'),  # noqa: E241
    'cross':        (CROSS_BOTTOM_MASK, '',    'cross_bottom_orientation'),  # noqa: E241
    'f2l':          (F2L_MASK,          '',    'f2l_orientation'),           # noqa: E241
    'af2l':         (F2L_MASK,          '',    'f2l_orientation'),           # noqa: E241
    'f2l+ll':       (F2L_LL_MASK,       '',    'f2l_orientation'),           # noqa: E241
    'f2l+cll':      (F2L_CLL_MASK,      '',    'f2l_orientation'),           # noqa: E241
    'f2l+ell':      (F2L_ELL_MASK,      '',    'f2l_orientation'),           # noqa: E241
}


class ModeDisplay:
    """Mixin handling mode computing tools."""

    def cross_top_orientation(self) -> str:
        """
        Determine the face orientation of the cube
        to the the cross facing by doing a x' rotation.

        Returns:
            Two characters representing the face orientation.

        """
        cube_orientation = self.cube.orientation

        return (
            f'{ OPPOSITE_FACES[cube_orientation[1]] }'
            f'{ cube_orientation[0] }'
        )

    def cross_bottom_orientation(self) -> str:
        """
        Determine the face orientation of the cube
        to the the cross facing by doing a x rotation.

        Returns:
            Two characters representing the face orientation.

        """
        cube_orientation = self.cube.orientation

        return (
            f'{ cube_orientation[1] }'
            f'{ OPPOSITE_FACES[cube_orientation[0]] }'
        )

    def f2l_orientation(self) -> str:
        """
        Determine the optimal front face orientation for F2L display mode
        keeping the initial top face orientation.

        Align F2L into FR slot for consistant results.

        Returns:
            Two haracters representing the face orientation.

        """
        impacted_faces = ''
        saved_facelets = ''

        top = self.cube.orientation[0]

        for face in set(FACE_ORDER) - {top, OPPOSITE_FACES[top]}:
            exclusion_pattern = face * (self.face_size - self.cube_size)
            facelets = self.cube.get_face_by_center(face)[
                self.cube_size:self.face_size
            ]

            if exclusion_pattern != facelets:
                impacted_faces += face
                saved_facelets = facelets

        if impacted_faces and len(impacted_faces) != 2:
            last_face = impacted_faces[-1]
            index = (
                0
                if saved_facelets[0] != last_face
                or saved_facelets[3] != last_face
                else 1
            )
            impacted_faces = (
                last_face
                # Will not work with U and D
                + F2L_ADJACENT_FACES[last_face][index]
            )

        new_front = F2L_FACE_ORIENTATIONS.get(
            ''.join(sorted(impacted_faces)),
            '',
        )

        return f'{ top }{ new_front }'

    def compensate_mask(self, mask: Mask) -> Mask:
        """
        Compensate the mask to preserve user orientation.

        Returns:
            The mask rotated.

        """
        from cubing_algs.vcube import VCube  # noqa: PLC0415

        cube = VCube(
            mask,
            size=self.cube_size,
            check=False,
        )
        cube.rotate(
            self.cube.compute_orientation_moves('UF'),
        )

        return cube.state

    def resolve_mode(self, mode: str) -> tuple[Mask, str, str]:
        """
        Resolve display mode into mask, layout, and orientation settings.

        Args:
            mode: Solving-stage preset name (e.g. ``'oll'``, ``'f2l'``).

        Returns:
            Tuple of (mask, layout, orientation) for the given mode.

        """
        if mode not in MODE_CONFIGS:
            return '', '', ''

        mask, layout, orientation_cb = MODE_CONFIGS[mode]

        orientation = ''
        if orientation_cb:
            orientation = getattr(self, orientation_cb)()

        mask = self.compensate_mask(mask) if self.cube_size == 3 else ''

        return mask, layout, orientation
