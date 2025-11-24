"""Cubing cases module for managing algorithm cases and collections."""
from cubing_algs.cases.case import Case
from cubing_algs.cases.collection import COLLECTIONS
from cubing_algs.cases.collection import CaseCollection
from cubing_algs.exceptions import InvalidCaseNameError
from cubing_algs.exceptions import InvalidCollectionNameError


def list_collections() -> list[str]:
    """
    List all available case collections.

    Returns:
        Sorted list of collection names (e.g., ['F2L', 'OLL', 'PLL'])

    Example:
        >>> list_collections()
        ['CFOP/AF2L', 'CFOP/F2L', 'CFOP/OLL', 'CFOP/PLL']

    """
    return sorted(COLLECTIONS.keys())


def get_collection(name: str) -> CaseCollection:
    """
    Get a case collection by name.

    Supports both prefixed and unprefixed formats:
    - Full format: 'CFOP/OLL', 'CFOP/PLL'
    - Short format: 'OLL', 'PLL' (method prefix optional)

    Args:
        name: Collection name (e.g., 'OLL', 'CFOP/OLL', 'PLL')

    Returns:
        The CaseCollection object

    Raises:
        InvalidCollectionNameError: If collection doesn't exist

    Example:
        >>> oll = get_collection('OLL')
        >>> oll = get_collection('CFOP/OLL')  # Also works
        >>> oll.size
        57

    """
    # Try exact match
    if name in COLLECTIONS:
        return COLLECTIONS[name]

    # Try case-insensitive match on full name
    name_lower = name.lower()
    for collection_name, collection in COLLECTIONS.items():
        if collection_name.lower() == name_lower:
            return collection

    # Try matching without prefix (e.g., 'OLL' matches 'CFOP/OLL')
    for collection_name, collection in COLLECTIONS.items():
        _, short_name = collection_name.split('/', 1)
        if short_name == name:
            return collection
        if short_name.lower() == name_lower:
            return collection

    available = ', '.join(sorted(COLLECTIONS.keys()))
    msg = f"'{name}' is not a valid collection. Available: {available}"
    raise InvalidCollectionNameError(msg)


def _match_exact(cases: dict[str, Case], name: str) -> Case | None:
    """
    Try exact case name match.

    Returns:
        Matching Case or None if not found

    """
    return cases.get(name)


def _match_case_insensitive(
    cases: dict[str, Case],
    name_lower: str,
) -> Case | None:
    """
    Try case-insensitive match on case name.

    Returns:
        Matching Case or None if not found

    """
    for case_name, case in cases.items():
        if case_name.lower() == name_lower:
            return case
    return None


def _match_code(
    cases: dict[str, Case],
    name_lower: str,
) -> Case | None:
    """
    Try match on case code.

    Returns:
        Matching Case or None if not found

    """
    for case in cases.values():
        if case.code.lower() == name_lower:
            return case
    return None


def _match_alias(
    cases: dict[str, Case],
    name_lower: str,
) -> Case | None:
    """
    Try match on aliases (case-insensitive).

    Returns:
        Matching Case or None if not found

    """
    for case in cases.values():
        for alias in case.aliases:
            if alias.lower() == name_lower:
                return case
    return None


def get_case(collection: str, name: str) -> Case:
    """
    Get a case by collection and name with smart name resolution.

    Supports multiple lookup strategies:
    - Exact case name match (e.g., 'OLL 01')
    - Case-insensitive name match (e.g., 'oll 01')
    - Code match (e.g., '01' for OLL)
    - Alias match (e.g., 'Sune', 'X-PLL')

    Args:
        collection: Collection name with optional method prefix
            (e.g., 'OLL', 'CFOP/OLL', 'PLL', 'CFOP/PLL')
        name: Case name, alias, or code to search for

    Returns:
        The matching Case object

    Raises:
        InvalidCaseNameError: If no matching case is found

    Example:
        >>> case = get_case('OLL', 'OLL 01')
        >>> case = get_case('CFOP/OLL', 'OLL 01')  # With prefix
        >>> case = get_case('OLL', 'oll 01')  # Case-insensitive
        >>> case = get_case('OLL', '27')  # By code
        >>> case = get_case('OLL', 'Sune')  # By alias
        >>> case = get_case('PLL', 'X-PLL')  # By alias

    """
    coll = get_collection(collection)
    cases = coll.cases
    name_lower = name.lower()

    # Try matching strategies in order of specificity
    result = (
        _match_exact(cases, name)
        or _match_case_insensitive(cases, name_lower)
        or _match_code(cases, name_lower)
        or _match_alias(cases, name_lower)
    )

    if result is not None:
        return result

    # No match found - provide helpful error
    msg = f"No case found matching '{name}' in collection '{coll.name}'"
    raise InvalidCaseNameError(msg)


__all__ = [
    'COLLECTIONS',
    'Case',
    'CaseCollection',
    'get_case',
    'get_collection',
    'list_collections',
]
