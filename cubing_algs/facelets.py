from cubing_algs.constants import CORNER_FACELET_MAP
from cubing_algs.constants import EDGE_FACELET_MAP
from cubing_algs.constants import FACE_ORDER

FACES = ''.join(FACE_ORDER)


def cubies_to_facelets(cp: list[int], co: list[int],
                       ep: list[int], eo: list[int]) -> str:
    """
    Convert Corner/Edge Permutation/Orientation cube state
    to the Kociemba facelets representation string.

    Example - solved state:
      cp = [0, 1, 2, 3, 4, 5, 6, 7]
      co = [0, 0, 0, 0, 0, 0, 0, 0]
      ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
      eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

    Example - state after F R moves made:
      cp = [0, 5, 2, 1, 7, 4, 6, 3]
      co = [1, 2, 0, 2, 1, 1, 0, 2]
      ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
      eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
      facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

    Args:
        cp: Corner Permutation
        co: Corner Orientation
        ep: Edge Permutation
        eo: Edge Orientation

    Returns:
        Cube state in the Kociemba facelets representation string
    """
    facelets = []

    for i in range(54):
        facelets.append(FACES[i // 9])

    for i in range(8):
        for p in range(3):
            facelets[
                CORNER_FACELET_MAP[i][(p + co[i]) % 3]
            ] = FACES[
                CORNER_FACELET_MAP[cp[i]][p] // 9
            ]

    for i in range(12):
        for p in range(2):
            facelets[
                EDGE_FACELET_MAP[i][(p + eo[i]) % 2]
            ] = FACES[
                EDGE_FACELET_MAP[ep[i]][p] // 9
            ]

    return ''.join(facelets)


def facelets_to_cubies(facelets: str) -> tuple[
        list[int], list[int], list[int], list[int],
]:
    """
    Convert Kociemba facelets representation string to
    Corner/Edge Permutation/Orientation cube state.

    Args:
        facelets: 54-character string representing the cube state
                  in Kociemba facelets format (URFDLB)

    Returns:
        tuple: (cp, co, ep, eo) where:
            cp: Corner Permutation list of 8 integers
            co: Corner Orientation list of 8 integers
            ep: Edge Permutation list of 12 integers
            eo: Edge Orientation list of 12 integers

    Example:
        facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
        returns: (
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        )
    """
    # Get center colors to create color mapping
    centers = (
        facelets[4] + facelets[13] +
        facelets[22] + facelets[31] +
        facelets[40] + facelets[49]
    )

    # Create color mapping array (convert facelet colors to face indices)
    f = []
    for i in range(54):
        color_index = centers.find(facelets[i])
        f.append(color_index)

    # Initialize arrays
    cp = [0] * 8
    co = [0] * 8
    ep = [0] * 12
    eo = [0] * 12

    # Process corners
    for i in range(8):
        # Find orientation by looking for U or D face (0 or 3 in color mapping)
        ori = 0
        for ori in range(3):
            if (
                    f[CORNER_FACELET_MAP[i][ori]] == 0
                    or f[CORNER_FACELET_MAP[i][ori]] == 3
            ):
                break

        # Get the other two colors
        col1 = f[CORNER_FACELET_MAP[i][(ori + 1) % 3]]
        col2 = f[CORNER_FACELET_MAP[i][(ori + 2) % 3]]

        # Find matching corner piece
        for j in range(8):
            expected_col1 = CORNER_FACELET_MAP[j][1] // 9
            expected_col2 = CORNER_FACELET_MAP[j][2] // 9
            if col1 == expected_col1 and col2 == expected_col2:
                cp[i] = j
                co[i] = ori % 3
                break

    # Process edges
    for i in range(12):
        color1 = f[EDGE_FACELET_MAP[i][0]]
        color2 = f[EDGE_FACELET_MAP[i][1]]

        for j in range(12):
            expected_color1 = EDGE_FACELET_MAP[j][0] // 9
            expected_color2 = EDGE_FACELET_MAP[j][1] // 9

            if color1 == expected_color1 and color2 == expected_color2:
                ep[i] = j
                eo[i] = 0
                break
            if color1 == expected_color2 and color2 == expected_color1:
                ep[i] = j
                eo[i] = 1
                break

    return cp, co, ep, eo
