from cubing_algs.algorithm import Algorithm
from cubing_algs.exceptions import InvalidBracketError
from cubing_algs.exceptions import InvalidOperatorError
from cubing_algs.transform.mirror import mirror_moves


def find_innermost_brackets(text: str) -> tuple[int, int] | None:
    """
    Find the position of the innermost (deepest nested) brackets.
    """
    max_depth = 0
    current_depth = 0
    innermost_start = -1
    innermost_end = -1

    i = 0
    while i < len(text):
        if text[i] == '[':
            current_depth += 1
            if current_depth > max_depth:  # pragma: no branch
                max_depth = current_depth
                innermost_start = i
        elif text[i] == ']':
            if current_depth == max_depth and innermost_start != -1:
                innermost_end = i
                return (innermost_start, innermost_end)
            current_depth -= 1
        i += 1

    return None


def split_on_separator(text: str, separator: str) -> tuple[str, str] | None:
    """
    Split text on separator, but only if the separator is at the top level
    (not inside nested brackets).
    """
    bracket_depth = 0

    for i, char in enumerate(text):
        if char == '[':
            bracket_depth += 1
        elif char == ']':
            bracket_depth -= 1
        elif char == separator and bracket_depth == 0:
            return (text[:i], text[i + 1:])

    return None


def invert_moves(old_moves: str) -> str:
    """
    Invert an algorithm string (reverse order and invert each move).
    """
    algo = Algorithm() + old_moves

    return str(algo.transform(mirror_moves))


def expand_commutators_and_conjugates(moves: str) -> str:
    """
    Expand commutators [A, B] and conjugates [A: B] in a move string.

    Commutator [A, B] = A B A' B'
    Conjugate [A: B] = A B A'
    """
    result = moves

    while '[' in result:
        bracket_pos = find_innermost_brackets(result)
        if bracket_pos is None:
            msg = f'Malformed bracket in { result }'
            raise InvalidBracketError(msg)

        start, end = bracket_pos

        bracket_content = result[start + 1:end]

        colon_split = split_on_separator(bracket_content, ':')
        comma_split = split_on_separator(bracket_content, ',')

        if colon_split is not None:
            a_part, b_part = colon_split

            a_expanded = expand_commutators_and_conjugates(a_part)
            b_expanded = expand_commutators_and_conjugates(b_part)

            a_inverted = invert_moves(a_expanded)
            expanded = f'{a_expanded} {b_expanded} {a_inverted}'

        elif comma_split is not None:
            a_part, b_part = comma_split

            a_expanded = expand_commutators_and_conjugates(a_part)
            b_expanded = expand_commutators_and_conjugates(b_part)

            a_inverted = invert_moves(a_expanded)
            b_inverted = invert_moves(b_expanded)
            expanded = f'{a_expanded} {b_expanded} {a_inverted} {b_inverted}'

        else:
            msg = f'Invalid operator in { bracket_content }'
            raise InvalidOperatorError(msg)

        result = result[:start] + ' ' + expanded + ' ' + result[end + 1:]

    return result.strip()
