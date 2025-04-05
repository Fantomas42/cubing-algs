from cubing_algs.move import Move


class Algorythm:
    def __init__(self, moves: list[Move]):
        self.moves = moves

    def __len__(self) -> int:
        return len(self.moves)

    def __str__(self):
        return ' '.join([str(m) for m in self.moves])

    def __repr__(self):
        return f'Algorythm("{ "".join([str(m) for m in self.moves]) }")'
