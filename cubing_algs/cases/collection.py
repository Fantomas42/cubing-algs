"""Collection management for cubing cases."""
import json
from pathlib import Path
from typing import Final

from cubing_algs.cases.case import Case
from cubing_algs.exceptions import InvalidCaseNameError


class CaseCollection:
    """
    Manages a collection of cubing cases loaded from JSON files.

    Handles lazy loading of cases and provides lookup by case name.
    """

    def __init__(self, method: str, source: Path) -> None:
        """
        Initialize a CaseCollection from a JSON file.

        Args:
            method: The solving method (e.g., 'cfop')
            source: Path to the JSON file containing case data

        """
        self.method = method
        self.source = source
        self.name = source.stem

        self.loaded_cases = {}

    @property
    def cases(self) -> list:
        """
        Load and return all cases in the collection.

        Cases are loaded lazily on first access from the JSON file.

        Returns:
            Dictionary mapping case names to Case objects

        """
        if not self.loaded_cases:
            with self.source.open('r') as fd:
                cases = json.load(fd)
                for case_data in cases:
                    c = Case(self.method, self.name, case_data)
                    self.loaded_cases[c.name] = c

        return self.loaded_cases

    def get(self, name: str) -> Case:
        """
        Get a case by name.

        Args:
            name: The name of the case to retrieve

        Returns:
            The Case object with the given name

        Raises:
            InvalidCaseNameError: If no case exists with the given name

        """
        cases = self.cases

        if name in cases:
            return cases[name]

        msg = f'{ name } is not a valid case'
        raise InvalidCaseNameError(msg)

    @property
    def size(self) -> int:
        """
        Return the number of cases in the collection.

        Returns:
            Total number of cases

        """
        return len(self.cases)

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the collection.

        Returns:
            String representation with collection name and size

        """
        return f'Collection { self.name }: { self.size }'

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation.

        Returns:
            String representation with method and source path

        """
        return f"CaseCollection('{ self.method }', '{ self.source }')"


CASES_DIRECTORY: Final = Path(__file__).parent

METHODS = ['CFOP']

COLLECTIONS = {}


for method in METHODS:
    method_directory = CASES_DIRECTORY / method

    for cases_path in method_directory.glob('*.json'):
        cc = CaseCollection(method, cases_path)

        COLLECTIONS[cc.name] = cc
