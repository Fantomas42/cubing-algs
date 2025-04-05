from cubing_algs.constants import JAPANESE_CHAR
from cubing_algs.constants import ROTATIONS


def is_japanese_move(move: str) -> bool:
    return JAPANESE_CHAR in move.lower()


def is_japanesable_move(move: str) -> bool:
    return (
        move[0].islower()
        and move[0] not in ROTATIONS
        and not is_japanese_move(move)
    )


def has_japanese_move(moves: list[str]) -> bool:
    return JAPANESE_CHAR in ''.join(moves).lower()


def has_japanesable_move(moves: list[str]) -> bool:
    return any(is_japanesable_move(move) for move in moves)


def japanese_move(move: str) -> str:
    return '%s%s%s' % (move[0].upper(), JAPANESE_CHAR, move[1:])


def unjapanese_move(move: str) -> str:
    return '%s%s' % (move[0].lower(), move[2:])


def japanese_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for _move in old_moves:
        move = str(_move)
        if is_japanesable_move(move):
            move = japanese_move(move)
        moves.append(move)

    return moves


def unjapanese_moves(old_moves: list[str]) -> list[str]:
    if not has_japanese_move(old_moves):
        return old_moves

    moves = []
    for _move in old_moves:
        move = str(_move)
        if is_japanese_move(move):
            move = unjapanese_move(move)
        moves.append(move)

    return moves
