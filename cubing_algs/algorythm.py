from collections.abc import Callable

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

    def __eq__(self, other):
        return self.moves == other.moves

    def transform(
            self,
            *processes: Callable[[list[Move]], list[Move]],
    ) -> 'Algorythm':

        new_moves = list(self.moves)
        for process in processes:
            new_moves = process(new_moves)

        if new_moves == self.moves:
            return self

        return Algorythm(new_moves)
