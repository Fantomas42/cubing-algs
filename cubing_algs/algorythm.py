from cubing_algs.move import Move


class Algorythm:
    def __init__(self, moves: list[Move]):
        self.moves = moves

    def __len__(self) -> int:
        return len(self.moves)
