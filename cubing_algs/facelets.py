from cubing_algs.constants import CORNER_FACELET_MAP
from cubing_algs.constants import EDGE_FACELET_MAP
from cubing_algs.constants import FACES


def cubies_to_facelets(cp: list[int], co: list[int],
                       ep: list[int], eo: list[int],
                       so: list[int]) -> str:
    """
    Convert Corner/Edge Permutation/Orientation cube state
    to the Kociemba facelets representation string.

    Example - solved state:
      cp = [0, 1, 2, 3, 4, 5, 6, 7]
      co = [0, 0, 0, 0, 0, 0, 0, 0]
      ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
      eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      so = [0, 1, 2, 3, 4, 5]
      facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

    Example - state after F R moves made:
      cp = [0, 5, 2, 1, 7, 4, 6, 3]
      co = [1, 2, 0, 2, 1, 1, 0, 2]
      ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
      eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
      so = [0, 1, 2, 3, 4, 5]
      facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

    Args:
        cp: Corner Permutation
        co: Corner Orientation
        ep: Edge Permutation
        eo: Edge Orientation
        so: Spatial Orientation

    Returns:
        Cube state in the Kociemba facelets representation string
    """
    facelets = [''] * 54

    for i in range(6):
        facelets[9 * i + 4] = FACES[so[i]]

    for i in range(8):
        for p in range(3):
            real_facelet_idx = CORNER_FACELET_MAP[i][(p + co[i]) % 3]
            color_face_idx = CORNER_FACELET_MAP[cp[i]][p] // 9
            facelets[real_facelet_idx] = FACES[so[color_face_idx]]

    for i in range(12):
        for p in range(2):
            real_facelet_idx = EDGE_FACELET_MAP[i][(p + eo[i]) % 2]
            color_face_idx = EDGE_FACELET_MAP[ep[i]][p] // 9
            facelets[real_facelet_idx] = FACES[so[color_face_idx]]

    return ''.join(facelets)


def facelets_to_cubies(facelets: str) -> tuple[
        list[int], list[int], list[int], list[int], list[int],
]:
    """
    Convert Kociemba facelets representation string to
    Corner/Edge Permutation/Orientation cube state.

    Args:
        facelets: 54-character string representing the cube state
                  in Kociemba facelets format (URFDLB)

    Returns:
        tuple: (cp, co, ep, eo, so) where:
            cp: Corner Permutation list of 8 integers
            co: Corner Orientation list of 8 integers
            ep: Edge Permutation list of 12 integers
            eo: Edge Orientation list of 12 integers
            so: Spatial Orientation list of 6 integers

    Example:
        facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
        returns: (
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5],
        )
    """
    # Get center colors to create color mapping
    so = [0] * 6
    for i in range(6):
        so[i] = FACES.find(facelets[9 * i + 4])

    # Invert the spatial orientation to create color mapping
    so_inv = [0] * 6
    for i in range(6):
        so_inv[so[i]] = i

    # Create color mapping array (convert facelet colors to face indices)
    f = [0] * 54
    for i in range(54):
        f[i] = so_inv[FACES.find(facelets[i])]

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
            if f[CORNER_FACELET_MAP[i][ori]] in {0, 3}:
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

    return cp, co, ep, eo, so
