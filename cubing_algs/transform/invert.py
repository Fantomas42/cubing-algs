def invert(move: str) -> str:
    if move.endswith("'"):
        return move[:1]
    return "%s'" % move
