"""Custom exception classes for cube algorithm parsing and manipulation."""


class CubingAlgsError(Exception):
    """Base exception for all cubing-algs library errors."""


class InvalidFaceError(CubingAlgsError):
    """Exception raised when an invalid face is encountered."""


class InvalidCubeStateError(CubingAlgsError):
    """
    Exception raised when an invalid cube state is encountered.

    This covers structural issues such as incorrect facelets string length,
    invalid characters, wrong color counts, non-unique centers, invalid
    corner/edge permutations or orientations, and parity mismatches.
    """


class InvalidMoveError(CubingAlgsError):
    """
    Exception raised when an invalid move notation is encountered.

    This can occur when parsing algorithms with incorrect or unsupported
    move notations.
    """


class InvalidBracketError(InvalidMoveError):
    """Exception raised when an invalid bracket formation is encountered."""


class InvalidOperatorError(InvalidMoveError):
    """Exception raised when an invalid operator is encountered."""


class InvalidPatternNameError(CubingAlgsError):
    """Exception raised when requesting a pattern with an invalid name."""


class InvalidCaseNameError(CubingAlgsError):
    """Exception raised when requesting a case with an invalid name."""


class InvalidCollectionNameError(CubingAlgsError):
    """Exception raised when requesting a collection with an invalid name."""


class InvalidStepError(CubingAlgsError):
    """Exception raised when step name is not recognized."""


class InvalidSlotSpecError(CubingAlgsError):
    """Exception raised when an invalid F2L slot is specified."""


class InvalidPieceSpecError(CubingAlgsError):
    """Exception raised when a piece specification cannot be parsed."""


class InvalidOrientationError(CubingAlgsError):
    """Exception raised when requesting an orientation with an invalid value."""


class InvalidFaceIndexError(CubingAlgsError):
    """Exception raised when requesting a non-existent face index by center."""


class InvalidFaceletsSolveError(CubingAlgsError):
    """
    Exception raised when the solver encounters invalid facelet format.

    This occurs when the facelets string cannot be solved, typically due to
    an impossible or malformed cube state passed to the solver.
    """


class PaletteAlreadyExistsError(CubingAlgsError):
    """Exception raised when registering a palette that already exists."""


class EffectAlreadyExistsError(CubingAlgsError):
    """Exception raised when registering an effect that already exists."""


class StyleAlreadyExistsError(CubingAlgsError):
    """Exception raised when registering a style that already exists."""
