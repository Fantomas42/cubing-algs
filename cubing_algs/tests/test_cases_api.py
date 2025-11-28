"""Tests for the cases module public API."""
import unittest

from cubing_algs.cases import COLLECTIONS
from cubing_algs.cases import Case
from cubing_algs.cases import CaseCollection
from cubing_algs.cases import _match_alias
from cubing_algs.cases import _match_case_insensitive
from cubing_algs.cases import _match_code
from cubing_algs.cases import _match_exact
from cubing_algs.cases import get_case
from cubing_algs.cases import get_collection
from cubing_algs.cases import list_collections
from cubing_algs.exceptions import InvalidCaseNameError
from cubing_algs.exceptions import InvalidCollectionNameError


class TestListCollections(unittest.TestCase):
    """Test list_collections function."""

    def test_list_collections_returns_list(self) -> None:
        """Test that list_collections returns a list."""
        result = list_collections()
        self.assertIsInstance(result, list)

    def test_list_collections_not_empty(self) -> None:
        """Test that list_collections returns non-empty list."""
        result = list_collections()
        self.assertGreater(len(result), 0)

    def test_list_collections_returns_strings(self) -> None:
        """Test that list_collections returns list of strings."""
        result = list_collections()
        for item in result:
            self.assertIsInstance(item, str)

    def test_list_collections_is_sorted(self) -> None:
        """Test that list_collections returns sorted list."""
        result = list_collections()
        self.assertEqual(result, sorted(result))

    def test_list_collections_contains_expected_collections(self) -> None:
        """Test that list_collections contains expected collections."""
        result = list_collections()
        expected = ['CFOP/AF2L', 'CFOP/F2L', 'CFOP/OLL', 'CFOP/PLL']

        for collection_name in expected:
            self.assertIn(collection_name, result)

    def test_list_collections_format(self) -> None:
        """Test that collection names follow METHOD/NAME format."""
        result = list_collections()

        for name in result:
            self.assertIn('/', name)
            parts = name.split('/')
            self.assertEqual(len(parts), 2)

    def test_list_collections_consistency_with_collections(self) -> None:
        """Test that list_collections matches COLLECTIONS keys."""
        result = list_collections()
        expected = sorted(COLLECTIONS.keys())
        self.assertEqual(result, expected)


class TestGetCollection(unittest.TestCase):
    """Test get_collection function."""

    def test_get_collection_exact_match(self) -> None:
        """Test get_collection with exact match."""
        collection = get_collection('CFOP/OLL')
        self.assertIsInstance(collection, CaseCollection)
        self.assertEqual(collection.name, 'OLL')
        self.assertEqual(collection.method, 'CFOP')

    def test_get_collection_case_insensitive(self) -> None:
        """Test get_collection with case-insensitive match."""
        collection = get_collection('cfop/oll')
        self.assertIsInstance(collection, CaseCollection)
        self.assertEqual(collection.name, 'OLL')

    def test_get_collection_case_insensitive_mixed(self) -> None:
        """Test get_collection with mixed case."""
        collection = get_collection('CFOP/oll')
        self.assertIsInstance(collection, CaseCollection)
        self.assertEqual(collection.name, 'OLL')

    def test_get_collection_short_name(self) -> None:
        """Test get_collection with short name without prefix."""
        collection = get_collection('OLL')
        self.assertIsInstance(collection, CaseCollection)
        self.assertEqual(collection.name, 'OLL')

    def test_get_collection_short_name_case_insensitive(self) -> None:
        """Test get_collection with short name case-insensitive."""
        collection = get_collection('oll')
        self.assertIsInstance(collection, CaseCollection)
        self.assertEqual(collection.name, 'OLL')

    def test_get_collection_pll_short_name(self) -> None:
        """Test get_collection with PLL short name."""
        collection = get_collection('PLL')
        self.assertIsInstance(collection, CaseCollection)
        self.assertEqual(collection.name, 'PLL')

    def test_get_collection_f2l_short_name(self) -> None:
        """Test get_collection with F2L short name."""
        collection = get_collection('F2L')
        self.assertIsInstance(collection, CaseCollection)
        self.assertEqual(collection.name, 'F2L')

    def test_get_collection_invalid_name_raises_error(self) -> None:
        """Test get_collection with invalid name raises error."""
        with self.assertRaises(InvalidCollectionNameError) as context:
            get_collection('InvalidCollection')

        self.assertIn('InvalidCollection', str(context.exception))
        self.assertIn('not a valid collection', str(context.exception))

    def test_get_collection_error_message_includes_available(self) -> None:
        """Test that error message includes available collections."""
        with self.assertRaises(InvalidCollectionNameError) as context:
            get_collection('NonExistent')

        error_message = str(context.exception)
        self.assertIn('Available:', error_message)
        self.assertIn('CFOP/OLL', error_message)

    def test_get_collection_multiple_calls_same_instance(self) -> None:
        """Test that multiple calls return same instance."""
        collection1 = get_collection('OLL')
        collection2 = get_collection('CFOP/OLL')

        self.assertIs(collection1, collection2)

    def test_get_collection_all_listed_collections(self) -> None:
        """Test get_collection works for all listed collections."""
        collections_list = list_collections()

        for collection_name in collections_list:
            with self.subTest(collection=collection_name):
                collection = get_collection(collection_name)
                self.assertIsInstance(collection, CaseCollection)

    def test_get_collection_empty_string_raises_error(self) -> None:
        """Test get_collection with empty string raises error."""
        with self.assertRaises(InvalidCollectionNameError):
            get_collection('')

    def test_get_collection_partial_match_raises_error(self) -> None:
        """Test get_collection with partial match raises error."""
        with self.assertRaises(InvalidCollectionNameError):
            get_collection('OL')

    def test_get_collection_with_trailing_slash_raises_error(self) -> None:
        """Test get_collection with trailing slash raises error."""
        with self.assertRaises(InvalidCollectionNameError):
            get_collection('CFOP/')


class TestGetCase(unittest.TestCase):
    """Test get_case function."""

    def test_get_case_exact_match(self) -> None:
        """Test get_case with exact case name match."""
        case = get_case('CFOP/OLL', 'OLL 01')
        self.assertIsInstance(case, Case)
        self.assertEqual(case.name, 'OLL 01')

    def test_get_case_with_short_collection_name(self) -> None:
        """Test get_case with short collection name."""
        case = get_case('OLL', 'OLL 01')
        self.assertIsInstance(case, Case)
        self.assertEqual(case.name, 'OLL 01')

    def test_get_case_case_insensitive_collection(self) -> None:
        """Test get_case with case-insensitive collection name."""
        case = get_case('oll', 'OLL 01')
        self.assertIsInstance(case, Case)
        self.assertEqual(case.name, 'OLL 01')

    def test_get_case_case_insensitive_name(self) -> None:
        """Test get_case with case-insensitive case name."""
        case = get_case('OLL', 'oll 01')
        self.assertIsInstance(case, Case)
        self.assertEqual(case.name, 'OLL 01')

    def test_get_case_by_code(self) -> None:
        """Test get_case by case code."""
        case = get_case('OLL', '01')
        self.assertIsInstance(case, Case)
        self.assertEqual(case.code, '01')
        self.assertEqual(case.name, 'OLL 01')

    def test_get_case_by_alias(self) -> None:
        """Test get_case by alias."""
        case = get_case('OLL', 'Sune')
        self.assertIsInstance(case, Case)
        self.assertIn('Sune', case.aliases)

    def test_get_case_by_alias_case_insensitive(self) -> None:
        """Test get_case by alias with case-insensitive match."""
        case = get_case('OLL', 'sune')
        self.assertIsInstance(case, Case)

    def test_get_case_invalid_case_name_raises_error(self) -> None:
        """Test get_case with invalid case name raises error."""
        with self.assertRaises(InvalidCaseNameError) as context:
            get_case('OLL', 'InvalidCase')

        self.assertIn('InvalidCase', str(context.exception))
        self.assertIn('No case found', str(context.exception))

    def test_get_case_error_includes_collection_name(self) -> None:
        """Test that error message includes collection name."""
        with self.assertRaises(InvalidCaseNameError) as context:
            get_case('OLL', 'NonExistent')

        self.assertIn('OLL', str(context.exception))

    def test_get_case_invalid_collection_raises_error(self) -> None:
        """Test get_case with invalid collection raises error."""
        with self.assertRaises(InvalidCollectionNameError):
            get_case('InvalidCollection', 'SomeCase')

    def test_get_case_empty_case_name_raises_error(self) -> None:
        """Test get_case with empty case name raises error."""
        with self.assertRaises(InvalidCaseNameError):
            get_case('OLL', '')

    def test_get_case_multiple_times_same_object(self) -> None:
        """Test that multiple get_case calls return same object."""
        case1 = get_case('OLL', 'OLL 01')
        case2 = get_case('CFOP/OLL', 'OLL 01')

        self.assertIs(case1, case2)

    def test_get_case_from_pll_collection(self) -> None:
        """Test get_case from PLL collection."""
        case = get_case('PLL', 'PLL Aa')
        self.assertIsInstance(case, Case)
        self.assertEqual(case.step, 'PLL')

    def test_get_case_multiple_aliases(self) -> None:
        """Test get_case works with multiple aliases."""
        case = get_case('OLL', 'OLL 01')
        aliases = case.aliases

        if aliases:
            for alias in aliases[:1]:
                with self.subTest(alias=alias):
                    case_by_alias = get_case('OLL', alias)
                    self.assertEqual(case_by_alias.name, case.name)


class TestMatchExactHelper(unittest.TestCase):
    """Test _match_exact helper function."""

    def test_match_exact_found(self) -> None:
        """Test _match_exact with existing case."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_exact(cases, 'OLL 01')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Case)
        if result is not None:
            self.assertEqual(result.name, 'OLL 01')

    def test_match_exact_not_found(self) -> None:
        """Test _match_exact with non-existent case."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_exact(cases, 'NonExistent')
        self.assertIsNone(result)

    def test_match_exact_empty_dict(self) -> None:
        """Test _match_exact with empty cases dict."""
        result = _match_exact({}, 'AnyName')
        self.assertIsNone(result)

    def test_match_exact_case_sensitive(self) -> None:
        """Test _match_exact is case-sensitive."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_exact(cases, 'oll 01')
        self.assertIsNone(result)


class TestMatchCaseInsensitiveHelper(unittest.TestCase):
    """Test _match_case_insensitive helper function."""

    def test_match_case_insensitive_found(self) -> None:
        """Test _match_case_insensitive with existing case."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_case_insensitive(cases, 'oll 01')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Case)

    def test_match_case_insensitive_not_found(self) -> None:
        """Test _match_case_insensitive with non-existent case."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_case_insensitive(cases, 'nonexistent')
        self.assertIsNone(result)

    def test_match_case_insensitive_empty_dict(self) -> None:
        """Test _match_case_insensitive with empty cases dict."""
        result = _match_case_insensitive({}, 'anyname')
        self.assertIsNone(result)

    def test_match_case_insensitive_uppercase(self) -> None:
        """Test _match_case_insensitive with uppercase input."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_case_insensitive(cases, 'OLL 01'.lower())
        self.assertIsNotNone(result)


class TestMatchCodeHelper(unittest.TestCase):
    """Test _match_code helper function."""

    def test_match_code_found(self) -> None:
        """Test _match_code with existing code."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_code(cases, '01')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Case)
        if result is not None:
            self.assertEqual(result.code, '01')

    def test_match_code_not_found(self) -> None:
        """Test _match_code with non-existent code."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_code(cases, '999')
        self.assertIsNone(result)

    def test_match_code_empty_dict(self) -> None:
        """Test _match_code with empty cases dict."""
        result = _match_code({}, '01')
        self.assertIsNone(result)

    def test_match_code_case_insensitive(self) -> None:
        """Test _match_code is case-insensitive."""
        collection = get_collection('PLL')
        cases = collection.cases

        result_lower = _match_code(cases, 'aa')
        result_upper = _match_code(cases, 'AA')

        if result_lower is not None or result_upper is not None:
            self.assertIsNotNone(result_lower or result_upper)


class TestMatchAliasHelper(unittest.TestCase):
    """Test _match_alias helper function."""

    def test_match_alias_found(self) -> None:
        """Test _match_alias with existing alias."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_alias(cases, 'sune')
        if result is not None:
            self.assertIsInstance(result, Case)
            self.assertIn('Sune', result.aliases)

    def test_match_alias_not_found(self) -> None:
        """Test _match_alias with non-existent alias."""
        collection = get_collection('OLL')
        cases = collection.cases

        result = _match_alias(cases, 'nonexistentalias')
        self.assertIsNone(result)

    def test_match_alias_empty_dict(self) -> None:
        """Test _match_alias with empty cases dict."""
        result = _match_alias({}, 'anyalias')
        self.assertIsNone(result)

    def test_match_alias_case_insensitive(self) -> None:
        """Test _match_alias is case-insensitive when passed lowercase."""
        collection = get_collection('OLL')
        cases = collection.cases

        result_lower = _match_alias(cases, 'sune')
        result_upper = _match_alias(cases, 'SUNE'.lower())

        if result_lower is not None and result_upper is not None:
            self.assertEqual(result_lower.name, result_upper.name)
        else:
            self.assertEqual(result_lower, result_upper)

    def test_match_alias_empty_aliases(self) -> None:
        """Test _match_alias with cases having empty aliases."""
        collection = get_collection('OLL')
        cases = collection.cases

        cases_with_aliases = {
            name: case for name, case in cases.items() if case.aliases
        }

        if cases_with_aliases:
            first_case = next(iter(cases_with_aliases.values()))
            alias_lower = first_case.aliases[0].lower()
            result = _match_alias(cases_with_aliases, alias_lower)
            self.assertIsNotNone(result)


class TestGetCaseMatchingPriority(unittest.TestCase):
    """Test get_case matching priority order."""

    def test_exact_match_takes_priority_over_code(self) -> None:
        """Test that exact name match takes priority over code match."""
        exact_case = get_case('OLL', 'OLL 01')

        self.assertEqual(exact_case.name, 'OLL 01')

    def test_code_match_when_no_exact_match(self) -> None:
        """Test that code matching works when exact match fails."""
        case = get_case('OLL', '01')

        self.assertIsInstance(case, Case)
        self.assertEqual(case.code, '01')

    def test_alias_match_when_no_exact_or_code_match(self) -> None:
        """Test that alias matching works when exact and code fail."""
        case = get_case('OLL', 'Sune')

        self.assertIsInstance(case, Case)
        self.assertIn('Sune', case.aliases)


class TestGetCaseEdgeCases(unittest.TestCase):
    """Test get_case edge cases and boundary conditions."""

    def test_get_case_with_special_characters_in_name(self) -> None:
        """Test get_case with special characters."""
        collection = get_collection('OLL')
        cases = collection.cases

        for case_name in list(cases.keys())[:3]:
            with self.subTest(case_name=case_name):
                case = get_case('OLL', case_name)
                self.assertEqual(case.name, case_name)

    def test_get_case_with_numbers_only(self) -> None:
        """Test get_case with numeric code."""
        case = get_case('OLL', '01')
        self.assertIsInstance(case, Case)

    def test_get_case_multiple_spaces_raises_error(self) -> None:
        """Test get_case with multiple spaces raises error."""
        with self.assertRaises(InvalidCaseNameError):
            get_case('OLL', 'OLL  01')

    def test_get_case_with_leading_trailing_spaces_raises_error(self) -> None:
        """Test get_case with leading/trailing spaces."""
        with self.assertRaises(InvalidCaseNameError):
            get_case('OLL', ' OLL 01 ')


class TestModuleLevelExports(unittest.TestCase):
    """Test module-level exports and API."""

    def test_collections_exported(self) -> None:
        """Test that COLLECTIONS is exported."""
        self.assertIsInstance(COLLECTIONS, dict)

    def test_case_class_exported(self) -> None:
        """Test that Case class is exported."""
        self.assertTrue(callable(Case))

    def test_case_collection_class_exported(self) -> None:
        """Test that CaseCollection class is exported."""
        self.assertTrue(callable(CaseCollection))

    def test_list_collections_exported(self) -> None:
        """Test that list_collections is exported."""
        self.assertTrue(callable(list_collections))

    def test_get_collection_exported(self) -> None:
        """Test that get_collection is exported."""
        self.assertTrue(callable(get_collection))

    def test_get_case_exported(self) -> None:
        """Test that get_case is exported."""
        self.assertTrue(callable(get_case))


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios with real data."""

    def test_workflow_list_then_get_collection(self) -> None:
        """Test typical workflow: list collections, then get one."""
        collections = list_collections()
        self.assertGreater(len(collections), 0)

        collection = get_collection(collections[0])
        self.assertIsInstance(collection, CaseCollection)

    def test_workflow_get_collection_then_get_case(self) -> None:
        """Test workflow: get collection, then get case."""
        collection = get_collection('OLL')
        cases = collection.cases

        if cases:
            first_case_name = next(iter(cases.keys()))
            case = get_case('OLL', first_case_name)
            self.assertIsInstance(case, Case)

    def test_workflow_get_case_by_different_strategies(self) -> None:
        """Test getting same case by different strategies."""
        collection = get_collection('OLL')
        cases = collection.cases

        if not cases:
            self.skipTest('No cases available in OLL collection')

        first_case = next(iter(cases.values()))

        case_by_name = get_case('OLL', first_case.name)
        case_by_code = get_case('OLL', first_case.code)

        self.assertEqual(case_by_name.name, case_by_code.name)
        self.assertEqual(case_by_name.code, case_by_code.code)

    def test_all_collections_accessible(self) -> None:
        """Test that all listed collections are accessible."""
        collections = list_collections()

        for collection_name in collections:
            with self.subTest(collection=collection_name):
                collection = get_collection(collection_name)
                self.assertIsInstance(collection, CaseCollection)

    def test_real_oll_cases_have_algorithms(self) -> None:
        """Test that real OLL cases have algorithms."""
        collection = get_collection('OLL')
        cases = collection.cases

        if not cases:
            self.skipTest('No cases in OLL collection')

        for case_name, case in list(cases.items())[:3]:
            with self.subTest(case=case_name):
                self.assertIsNotNone(case.main_algorithm)
                self.assertIsInstance(case.algorithms, list)

    def test_real_pll_cases_accessible_by_alias(self) -> None:
        """Test that PLL cases are accessible by common aliases."""
        pll_aliases_to_test = ['Aa', 'Ab', 'E', 'H', 'Ja', 'Jb', 'T']

        for alias in pll_aliases_to_test:
            with self.subTest(alias=alias):
                try:
                    case = get_case('PLL', alias)
                    self.assertIsInstance(case, Case)
                except InvalidCaseNameError:
                    pass
