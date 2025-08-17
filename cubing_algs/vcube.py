# ruff: noqa: TRY003
from importlib.util import find_spec

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_ORDER
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies
from cubing_algs.move import InvalidMoveError
from cubing_algs.vcube_print import VCubePrinter

FAST_ROTATE_AVAILABLE = False
if find_spec('cubing_algs.vcube_rotate') is not None:  # pragma: no cover
    from cubing_algs import vcube_rotate  # type: ignore[attr-defined]
    FAST_ROTATE_AVAILABLE = True

INITIAL = ''
for face in FACE_ORDER:
    INITIAL += face * 9


class InvalidCubeStateError(Exception):
    ...


class VCube:
    """
    Virtual 3x3 cube for tracking moves on facelets
    """
    size = 3

    def __init__(self, initial: str | None = None):
        if initial:
            self._state = initial
            self.check_state()
        else:
            self._state = INITIAL

        self.history: list[str] = []

    @property
    def state(self) -> str:
        return self._state

    @staticmethod
    def from_cubies(cp: list[int], co: list[int],
                    ep: list[int], eo: list[int]) -> 'VCube':
        return VCube(cubies_to_facelets(cp, co, ep, eo))

    @property
    def to_cubies(self) -> tuple[list[int], list[int], list[int], list[int]]:
        return facelets_to_cubies(self._state)

    @property
    def is_solved(self) -> bool:
        return self.state == INITIAL

    def check_state(self) -> bool:
        # TODO(me): Check corners, edges stickers # noqa: FIX002

        if len(self._state) != 54:
            msg = 'State string must be 54 characters long'
            raise InvalidCubeStateError(msg)

        color_counts: dict[str, int] = {}
        for i in self._state:
            color_counts.setdefault(i, 0)
            color_counts[i] += 1

        if set(color_counts.keys()) - set(FACE_ORDER):
            msg = (
                'State string can only '
                f'contains { " ".join(FACE_ORDER) } characters'
            )
            raise InvalidCubeStateError(msg)

        if not all(count == 9 for count in color_counts.values()):
            msg = 'State string must have nine of each color'
            raise InvalidCubeStateError(msg)

        return True

    def rotate(self, moves: str | Algorithm, allow_fast: bool = True) -> str:  # noqa: FBT001, FBT002
        if isinstance(moves, Algorithm):
            for m in moves:
                self.rotate_move(str(m), allow_fast=allow_fast)
        else:
            for m in moves.split(' '):
                self.rotate_move(m, allow_fast=allow_fast)
        return self._state

    def rotate_move(self, move: str, *, allow_fast: bool = True) -> str:
        if allow_fast and FAST_ROTATE_AVAILABLE:
            try:
                self._state = vcube_rotate.rotate_move(self._state, move)
            except ValueError as e:
                raise InvalidMoveError(str(e)) from e
            else:
                self.history.append(move)
                return self._state

        return self._rotate_move_python(move)

    def _rotate_move_python(self, move: str) -> str:  # noqa: PLR0912, PLR0914, PLR0915
        # Parse the move
        face = move[0]
        direction = 1  # Default: clockwise

        if len(move) > 1:
            if move[1] == "'":
                # Counterclockwise (equivalent to 3 clockwise rotations)
                direction = 3
            elif move[1] == '2':
                # 180 degrees (equivalent to 2 clockwise rotations)
                direction = 2
            else:
                msg = 'Invalid move modifier'
                raise InvalidMoveError(msg)

        for _ in range(direction):
            if face == 'U':
                # U rotation: The top rows of the four sides rotate
                # Front top row → Left top row → Back top row
                # → Right top row → Front top row

                # Extract the top rows of F, R, B, L faces
                f_top = self._state[18:21]
                r_top = self._state[9:12]
                b_top = self._state[45:48]
                l_top = self._state[36:39]

                # Extract and rotate the U face itself
                u_face = self._state[0:9]
                rotated_u = (
                    u_face[6] + u_face[3] + u_face[0] +
                    u_face[7] + u_face[4] + u_face[1] +
                    u_face[8] + u_face[5] + u_face[2]
                )

                # Update state with the rotated face U and shifted top rows
                self._state = (
                    rotated_u +                  # U face rotated
                    b_top + self._state[12:18] +  # R face with B's top row
                    r_top + self._state[21:27] +  # F face with R's top row
                    self._state[27:36] +          # D face unchanged
                    f_top + self._state[39:45] +  # L face with F's top row
                    l_top + self._state[48:54]    # B face with L's top row
                )

            elif face == 'R':
                # R rotation affects U, F, D, B faces
                # Keep R face intact but rotate it clockwise
                r_face = [
                    self._state[9:12],
                    self._state[12:15],
                    self._state[15:18],
                ]
                rotated_r = (
                    r_face[2][0] + r_face[1][0] + r_face[0][0] +
                    r_face[2][1] + r_face[1][1] + r_face[0][1] +
                    r_face[2][2] + r_face[1][2] + r_face[0][2]
                )

                # Extract columns from U, F, D, B that will be affected
                u_right_col = [
                    self._state[2],
                    self._state[5],
                    self._state[8],
                ]
                f_right_col = [
                    self._state[20],
                    self._state[23],
                    self._state[26],
                ]
                d_right_col = [
                    self._state[29],
                    self._state[32],
                    self._state[35],
                ]
                # Note: B's left column as seen from B's perspective
                b_left_col = [self._state[45], self._state[48], self._state[51]]

                # Rotate
                new_u_right = f_right_col
                new_f_right = d_right_col
                # Reversed due to B's orientation
                new_d_right = [b_left_col[2], b_left_col[1], b_left_col[0]]
                # Reversed due to B's orientation
                new_b_left = [u_right_col[2], u_right_col[1], u_right_col[0]]

                # Update state
                self._state = (
                    self._state[0:2] + new_u_right[0] +
                    self._state[3:5] + new_u_right[1] +
                    self._state[6:8] + new_u_right[2] +    # U face
                    rotated_r +                           # R face
                    self._state[18:20] + new_f_right[0] +
                    self._state[21:23] + new_f_right[1] +
                    self._state[24:26] + new_f_right[2] +  # F face
                    self._state[27:29] + new_d_right[0] +
                    self._state[30:32] + new_d_right[1] +
                    self._state[33:35] + new_d_right[2] +  # D face
                    self._state[36:45] +                   # L face
                    new_b_left[0] + self._state[46:48] +
                    new_b_left[1] + self._state[49:51] +
                    new_b_left[2] + self._state[52:54]     # B face
                )

            elif face == 'F':
                # F rotation affects U, R, D, L faces
                # Keep F face intact but rotate it clockwise
                f_face = [
                    self._state[18:21],
                    self._state[21:24],
                    self._state[24:27],
                ]
                rotated_f = (
                    f_face[2][0] + f_face[1][0] + f_face[0][0] +
                    f_face[2][1] + f_face[1][1] + f_face[0][1] +
                    f_face[2][2] + f_face[1][2] + f_face[0][2]
                )

                # Extract affected parts
                u_bottom_row = self._state[6:9]
                r_left_col = [self._state[9], self._state[12], self._state[15]]
                d_top_row = self._state[27:30]
                l_right_col = [
                    self._state[38],
                    self._state[41],
                    self._state[44],
                ]

                # Rotate
                new_u_bottom = [l_right_col[2], l_right_col[1], l_right_col[0]]
                new_r_left = u_bottom_row
                new_d_top = [r_left_col[2], r_left_col[1], r_left_col[0]]
                new_l_right = d_top_row

                # Update state
                self._state = (
                    self._state[0:6] + new_u_bottom[0] +
                    new_u_bottom[1] + new_u_bottom[2] +   # U face
                    new_r_left[0] + self._state[10:12] +
                    new_r_left[1] + self._state[13:15] +
                    new_r_left[2] + self._state[16:18] +   # R face
                    rotated_f +                           # F face
                    new_d_top[0] + new_d_top[1] +
                    new_d_top[2] + self._state[30:36] +    # D face
                    self._state[36:38] + new_l_right[0] +
                    self._state[39:41] + new_l_right[1] +
                    self._state[42:44] + new_l_right[2] +  # L face
                    self._state[45:54]                     # B face
                )

            elif face == 'D':
                # D rotation affects F, R, B, L (bottom rows)
                # Keep D face intact but rotate it clockwise
                d_face = [
                    self._state[27:30],
                    self._state[30:33],
                    self._state[33:36],
                ]
                rotated_d = (
                    d_face[2][0] + d_face[1][0] + d_face[0][0] +
                    d_face[2][1] + d_face[1][1] + d_face[0][1] +
                    d_face[2][2] + d_face[1][2] + d_face[0][2]
                )

                # Extract bottom rows
                f_bottom = self._state[24:27]
                r_bottom = self._state[15:18]
                b_bottom = self._state[51:54]
                l_bottom = self._state[42:45]

                # Rotate
                new_f_bottom = l_bottom
                new_r_bottom = f_bottom
                new_b_bottom = r_bottom
                new_l_bottom = b_bottom

                # Update state
                self._state = (
                    self._state[0:9] +                   # U face
                    self._state[9:15] + new_r_bottom +   # R face
                    self._state[18:24] + new_f_bottom +  # F face
                    rotated_d +                         # D face
                    self._state[36:42] + new_l_bottom +  # L face
                    self._state[45:51] + new_b_bottom    # B face
                )

            elif face == 'L':
                # L rotation affects U, F, D, B faces
                # Keep L face intact but rotate it clockwise
                l_face = [
                    self._state[36:39],
                    self._state[39:42],
                    self._state[42:45],
                ]
                rotated_l = (
                    l_face[2][0] + l_face[1][0] + l_face[0][0] +
                    l_face[2][1] + l_face[1][1] + l_face[0][1] +
                    l_face[2][2] + l_face[1][2] + l_face[0][2]
                )

                # Extract columns
                u_left_col = [
                    self._state[0],
                    self._state[3],
                    self._state[6],
                ]
                f_left_col = [
                    self._state[18],
                    self._state[21],
                    self._state[24],
                ]
                d_left_col = [
                    self._state[27],
                    self._state[30],
                    self._state[33],
                ]
                b_right_col = [
                    self._state[47],
                    self._state[50],
                    self._state[53],
                ]

                # Rotate
                new_u_left = [b_right_col[2], b_right_col[1], b_right_col[0]]
                new_f_left = u_left_col
                new_d_left = f_left_col
                new_b_right = [d_left_col[2], d_left_col[1], d_left_col[0]]

                # Update state
                self._state = (
                    new_u_left[0] + self._state[1:3] +
                    new_u_left[1] + self._state[4:6] +
                    new_u_left[2] + self._state[7:9] +    # U face
                    self._state[9:18] +                   # R face
                    new_f_left[0] + self._state[19:21] +
                    new_f_left[1] + self._state[22:24] +
                    new_f_left[2] + self._state[25:27] +  # F face
                    new_d_left[0] + self._state[28:30] +
                    new_d_left[1] + self._state[31:33] +
                    new_d_left[2] + self._state[34:36] +  # D face
                    rotated_l +                          # L face
                    self._state[45:47] + new_b_right[0] +
                    self._state[48:50] + new_b_right[1] +
                    self._state[51:53] + new_b_right[2]   # B face
                )

            elif face == 'B':
                # B rotation affects U, L, D, R faces
                # Keep B face intact but rotate it clockwise
                b_face = [
                    self._state[45:48],
                    self._state[48:51],
                    self._state[51:54],
                ]
                rotated_b = (
                    b_face[2][0] + b_face[1][0] + b_face[0][0] +
                    b_face[2][1] + b_face[1][1] + b_face[0][1] +
                    b_face[2][2] + b_face[1][2] + b_face[0][2]
                )

                # Extract affected parts
                u_top_row = self._state[0:3]
                r_right_col = [
                    self._state[11],
                    self._state[14],
                    self._state[17],
                ]
                d_bottom_row = self._state[33:36]
                l_left_col = [
                    self._state[36],
                    self._state[39],
                    self._state[42],
                ]

                # Rotate
                new_u_top = r_right_col
                new_r_right = [
                    d_bottom_row[2],
                    d_bottom_row[1],
                    d_bottom_row[0],
                ]
                new_d_bottom = l_left_col
                new_l_left = [u_top_row[2], u_top_row[1], u_top_row[0]]

                # Update state
                self._state = (
                    new_u_top[0] + new_u_top[1] +
                    new_u_top[2] + self._state[3:9] +       # U face
                    self._state[9:11] + new_r_right[0] +
                    self._state[12:14] + new_r_right[1] +
                    self._state[15:17] + new_r_right[2] +   # R face
                    self._state[18:27] +                    # F face
                    self._state[27:33] + new_d_bottom[0]
                    + new_d_bottom[1] + new_d_bottom[2] +  # D face
                    new_l_left[0] + self._state[37:39] +
                    new_l_left[1] + self._state[40:42] +
                    new_l_left[2] + self._state[43:45] +    # L face
                    rotated_b                              # B face
                )

            elif face == 'M':
                # M is the middle slice between L and R (same direction as L)
                # Extract columns
                u_middle_col = [
                    self._state[1],
                    self._state[4],
                    self._state[7],
                ]
                f_middle_col = [
                    self._state[19],
                    self._state[22],
                    self._state[25],
                ]
                d_middle_col = [
                    self._state[28],
                    self._state[31],
                    self._state[34],
                ]
                b_middle_col = [
                    self._state[46],
                    self._state[49],
                    self._state[52],
                ]

                # Rotate (like L)
                new_u_middle = [
                    b_middle_col[2],
                    b_middle_col[1],
                    b_middle_col[0],
                ]
                new_f_middle = u_middle_col
                new_d_middle = f_middle_col
                new_b_middle = [
                    d_middle_col[2],
                    d_middle_col[1],
                    d_middle_col[0],
                ]

                # Update state
                self._state = (
                    self._state[0] + new_u_middle[0] +
                    self._state[2:4] + new_u_middle[1] +
                    self._state[5:7] + new_u_middle[2] +
                    self._state[8:9] +    # U face
                    self._state[9:18] +   # R face
                    self._state[18] + new_f_middle[0] +
                    self._state[20:22] + new_f_middle[1] +
                    self._state[23:25] + new_f_middle[2] +
                    self._state[26:27] +  # F face
                    self._state[27] + new_d_middle[0] +
                    self._state[29:31] + new_d_middle[1] +
                    self._state[32:34] + new_d_middle[2] +
                    self._state[35:36] +  # D face
                    self._state[36:45] +  # L face
                    self._state[45:46] + new_b_middle[0] +
                    self._state[47:49] + new_b_middle[1] +
                    self._state[50:52] + new_b_middle[2] +
                    self._state[53:54]    # B face
                )

            elif face == 'S':
                # S is the middle slice between F and B (same direction as F)
                # Extract affected parts
                u_middle_row = self._state[3:6]
                r_middle_col = [
                    self._state[10],
                    self._state[13],
                    self._state[16],
                ]
                d_middle_row = self._state[30:33]
                l_middle_col = [
                    self._state[37],
                    self._state[40],
                    self._state[43],
                ]

                # Rotate (like F)
                new_u_middle = [
                    l_middle_col[2],
                    l_middle_col[1],
                    l_middle_col[0],
                ]
                new_r_middle = u_middle_row
                new_d_middle = [
                    r_middle_col[2],
                    r_middle_col[1],
                    r_middle_col[0],
                ]
                new_l_middle = d_middle_row

                # Update state
                self._state = (
                    self._state[0:3] + new_u_middle[0] +
                    new_u_middle[1] + new_u_middle[2] +
                    self._state[6:9] +    # U face
                    self._state[9:10] + new_r_middle[0] +
                    self._state[11:13] + new_r_middle[1] +
                    self._state[14:16] + new_r_middle[2] +
                    self._state[17:18] +  # R face
                    self._state[18:27] +  # F face
                    self._state[27:30] + new_d_middle[0] +
                    new_d_middle[1] + new_d_middle[2] +
                    self._state[33:36] +  # D face
                    self._state[36:37] + new_l_middle[0] +
                    self._state[38:40] + new_l_middle[1] +
                    self._state[41:43] + new_l_middle[2] +
                    self._state[44:45] +  # L face
                    self._state[45:54]    # B face
                )

            elif face == 'E':
                # E is the middle slice between U and D (same direction as D)
                # Extract middle rows
                f_middle = self._state[21:24]
                r_middle = self._state[12:15]
                b_middle = self._state[48:51]
                l_middle = self._state[39:42]

                # Rotate (like D)
                new_f_middle = l_middle
                new_r_middle = f_middle
                new_b_middle = r_middle
                new_l_middle = b_middle

                # Update state
                self._state = (
                    self._state[0:9] +    # U face
                    self._state[9:12] +
                    new_r_middle +
                    self._state[15:18] +  # R face
                    self._state[18:21] +
                    new_f_middle +
                    self._state[24:27] +  # F face
                    self._state[27:36] +  # D face
                    self._state[36:39] +
                    new_l_middle +
                    self._state[42:45] +  # L face
                    self._state[45:48] +
                    new_b_middle +
                    self._state[51:54]    # B face
                )

            elif face == 'x':
                # x is the rotation of the entire cube around the x axis
                # (same as R, with M' and L' together)

                # Extract all faces
                u_face = self._state[0:9]
                r_face = self._state[9:18]
                f_face = self._state[18:27]
                d_face = self._state[27:36]
                l_face = self._state[36:45]
                b_face = self._state[45:54]

                # Rotate R face
                r_rotated = (
                    r_face[6] + r_face[3] + r_face[0] +
                    r_face[7] + r_face[4] + r_face[1] +
                    r_face[8] + r_face[5] + r_face[2]
                )

                # Rotate L face (counterclockwise)
                l_rotated = (
                    l_face[2] + l_face[5] + l_face[8] +
                    l_face[1] + l_face[4] + l_face[7] +
                    l_face[0] + l_face[3] + l_face[6]
                )

                # Update state - this is a full cube rotation,
                # so faces move to new positions
                self._state = (
                    f_face +        # U becomes F
                    r_rotated +     # R stays R but rotates
                    d_face +        # F becomes D
                    b_face[::-1] +  # D becomes inverted B
                    l_rotated +     # L stays L but rotates
                    u_face[::-1]    # B becomes inverted U
                )

            elif face == 'y':
                # y is the rotation of the entire cube around the y axis
                # (same as U, with E' and D' together)

                # Extract all faces
                u_face = self._state[0:9]
                r_face = self._state[9:18]
                f_face = self._state[18:27]
                d_face = self._state[27:36]
                l_face = self._state[36:45]
                b_face = self._state[45:54]

                # Rotate U face
                u_rotated = (
                    u_face[6] + u_face[3] + u_face[0] +
                    u_face[7] + u_face[4] + u_face[1] +
                    u_face[8] + u_face[5] + u_face[2]
                )

                # Rotate D face (counterclockwise)
                d_rotated = (
                    d_face[2] + d_face[5] + d_face[8] +
                    d_face[1] + d_face[4] + d_face[7] +
                    d_face[0] + d_face[3] + d_face[6]
                )

                # Update state
                self._state = (
                    u_rotated +  # U stays U but rotates
                    b_face +     # R becomes B
                    r_face +     # F becomes R
                    d_rotated +  # D stays D but rotates
                    f_face +     # L becomes F
                    l_face       # B becomes L
                )

            elif face == 'z':
                # z is the rotation of the entire cube around the z axis
                # (same as F, with S and B' together)

                # Extract all faces
                u_face = self._state[0:9]
                r_face = self._state[9:18]
                f_face = self._state[18:27]
                d_face = self._state[27:36]
                l_face = self._state[36:45]
                b_face = self._state[45:54]

                # Rotate F face
                f_rotated = (
                    f_face[6] + f_face[3] + f_face[0] +
                    f_face[7] + f_face[4] + f_face[1] +
                    f_face[8] + f_face[5] + f_face[2]
                )

                # Rotate B face (counterclockwise)
                b_rotated = (
                    b_face[2] + b_face[5] + b_face[8] +
                    b_face[1] + b_face[4] + b_face[7] +
                    b_face[0] + b_face[3] + b_face[6]
                )

                # The other faces need to be rotated
                # as they move to new positions
                # For example, when U becomes L,
                # it also needs to be rotated 90° clockwise
                u_transformed = (
                    u_face[6] + u_face[3] + u_face[0] +
                    u_face[7] + u_face[4] + u_face[1] +
                    u_face[8] + u_face[5] + u_face[2]
                )
                r_transformed = (
                    r_face[6] + r_face[3] + r_face[0] +
                    r_face[7] + r_face[4] + r_face[1] +
                    r_face[8] + r_face[5] + r_face[2]
                )
                d_transformed = (
                    d_face[6] + d_face[3] + d_face[0] +
                    d_face[7] + d_face[4] + d_face[1] +
                    d_face[8] + d_face[5] + d_face[2]
                )
                l_transformed = (
                    l_face[6] + l_face[3] + l_face[0] +
                    l_face[7] + l_face[4] + l_face[1] +
                    l_face[8] + l_face[5] + l_face[2]
                )

                # Update state
                self._state = (
                    l_transformed +  # U becomes L
                    u_transformed +  # R becomes U
                    f_rotated +      # F stays F but rotates
                    r_transformed +  # D becomes R
                    d_transformed +  # L becomes D
                    b_rotated        # B stays B but rotates counterclockwise
                )
            else:
                msg = 'Invalid move face'
                raise InvalidMoveError(msg)

        self.history.append(move)

        return self._state

    def display(self, orientation: str = '',
                colors: list[str] | None = None) -> str:
        display = VCubePrinter(self, orientation, colors).print_cube()

        print(display, end='')

        return display

    def __str__(self) -> str:
        """
        Return the facelets of the cube
        """
        faces = []
        for i, face in enumerate(FACE_ORDER):
            faces.append(f'{ face }: { self._state[i * 9: (i + 1) * 9]}')

        return '\n'.join(faces)

    def __repr__(self) -> str:
        """
        Return a string representation that can be used
        to recreate the VCube.
        """
        return f"VCube('{ self._state }')"
