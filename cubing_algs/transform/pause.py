from cubing_algs.move import Move


def unpause_moves(old_moves: list[Move]) -> list[Move]:
    moves = []
    for move in old_moves:
        if not move.is_pause:
            moves.append(move)

    return moves


def pause_moves(old_moves: list[Move]) -> list[Move]:
    moves = []
    speed = 200  # Milliseconds
    threshold = speed * 2

    for m in old_moves:
        if not m.is_timed:
            return old_moves

    previous_time = old_moves[0].timed
    for move in old_moves:
        time = move.timed

        if time - previous_time > threshold:
            moves.extend(
                [
                    Move(f'.@{ time - speed }'),
                    move,
                ],
            )
        else:
            moves.append(move)
        previous_time = time

    return moves
