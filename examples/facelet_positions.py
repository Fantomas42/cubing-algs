"""Display facelets by their position (0-53)."""
import sys

from cubing_algs.vcube import VCube


def show_facelets(pos: list[str]) -> None:
    """
    Prepare mask for displaying facelets.

    Args:
        pos: List of facelets

    """
    cube = VCube()
    mask = ['1'] * 54

    for p in pos:
        mask[int(p)] = '0'

    cube.show(mask=''.join(mask))


show_facelets(sys.argv[1:])
