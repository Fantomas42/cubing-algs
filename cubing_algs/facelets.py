from cubing_algs.constants import CORNER_FACELET_MAP
from cubing_algs.constants import EDGE_FACELET_MAP
from cubing_algs.constants import FACE_ORDER

FACES = ''.join(FACE_ORDER)


def cubies_to_facelets(cp, co, ep, eo):
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
