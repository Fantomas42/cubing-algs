from cubing_algs.move import Move
from cubing_algs.parsing import check_moves
from cubing_algs.parsing import split_moves


class Algorythm:
    def __init__(self, raw_moves: str | list[Move]):
        if isinstance(raw_moves, list):
            self.moves = raw_moves
            check_moves(self.moves)
        else:
            self.moves = split_moves(raw_moves)

        #self.execution_moves = remove_final_rotations(self.moves)
