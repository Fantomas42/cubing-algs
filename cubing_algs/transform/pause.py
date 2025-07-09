from cubing_algs.constants import PAUSE_CHAR
from cubing_algs.move import Move


def unpause_moves(old_moves: list[Move]) -> list[Move]:
    moves = []
    for move in old_moves:
        if not move.is_pause:
            moves.append(move)

    return moves


def pause_moves(speed: int = 200, factor: int = 2,
                *, multiple: bool = False):
    """
    Create a configurable pause_moves function.

    Args:
        speed: Base speed in milliseconds (default: 200)
        factor: Multiplier for threshold calculation (default: 2)

    Returns:
        A function that can be used with transform() or called directly.
    """
    def _pause_moves(old_moves: list[Move]) -> list[Move]:
        if not old_moves:
            return old_moves

        moves = []
        threshold = speed * factor

        for m in old_moves:
            if not m.is_timed:
                return old_moves

        previous_time = old_moves[0].timed
        for move in old_moves:
            time = move.timed

            if time - previous_time > threshold:
                if multiple:
                    delta = time - previous_time
                    occurences = int(delta / threshold)
                    for i in range(occurences):
                        new_time = previous_time + ((i + 1) * threshold)
                        moves.append(
                            Move(
                                f'{ PAUSE_CHAR }@{ new_time }',
                            ),
                        )
                    moves.append(move)
                else:
                    moves.extend(
                        [
                            Move(f'{ PAUSE_CHAR }@{ time - speed }'),
                            move,
                        ],
                    )
            else:
                moves.append(move)
            previous_time = time

        return moves

    return _pause_moves
