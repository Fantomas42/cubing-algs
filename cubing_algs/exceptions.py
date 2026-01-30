"""Custom exception classes for cube algorithm parsing and manipulation."""


class InvalidFaceError(Exception):
    """Exception raised when an invalid face is encountered."""


class InvalidCubeStateError(Exception):
    """Exception raised when an invalid cube is encountered."""


class InvalidMoveError(Exception):
    """
    Exception raised when an invalid move notation is encountered.

    This can occur when parsing algorithms with incorrect or unsupported
    move notations.
    """


class InvalidBracketError(InvalidMoveError):
    """Exception raised when an invalid bracket formation is encountered."""


class InvalidOperatorError(InvalidMoveError):
    """Exception raised when an invalid operator is encountered."""


class InvalidCaseNameError(ValueError):
    """Exception raised when requesting a case with an invalid name."""


class InvalidCollectionNameError(ValueError):
    """Exception raised when requesting a collection with an invalid name."""


class InvalidStepError(ValueError):
    """Exception raised when step name is not recognized."""


class InvalidPieceSpecError(ValueError):
    """Exception raise when piece specification cannot be parsed."""


class InvalidOrientationError(ValueError):
    """Exception raised when requesting an orientation with an invalid value."""


class InvalidFaceIndexError(ValueError):
    """Exception raised when requesting an unexisting face index by center."""


class InvalidFaceletsSolveError(ValueError):
    """Exception raised when the solver encounter invalid facelet format."""
