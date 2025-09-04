class InvalidFaceError(Exception):
    """
    Exception raised when an invalid face is encountered.
    """


class InvalidCubeStateError(Exception):
    """
    Exception raised when an invalid cube is encountered.
    """


class InvalidMoveError(Exception):
    """
    Exception raised when an invalid move notation is encountered.

    This can occur when parsing algorithms with incorrect or unsupported
    move notations.
    """


class InvalidBracketError(InvalidMoveError):
    """
    Exception raised when an invalid bracket formation is encountered.
    """


class InvalidOperatorError(InvalidMoveError):
    """
    Exception raised when an invalid bracket formation is encountered.
    """
