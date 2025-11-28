"""Tests for the CaseCollection class."""
import json
import unittest
from pathlib import Path
from unittest.mock import mock_open
from unittest.mock import patch

from cubing_algs.cases.case import Case
from cubing_algs.cases.collection import CASES_DIRECTORY
from cubing_algs.cases.collection import COLLECTIONS
from cubing_algs.cases.collection import METHODS
from cubing_algs.cases.collection import CaseCollection
from cubing_algs.exceptions import InvalidCaseNameError


class TestCaseCollectionInitialization(unittest.TestCase):
    """Test CaseCollection initialization."""

    def test_init_with_valid_parameters(self) -> None:
        """Test CaseCollection initialization with valid parameters."""
        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        self.assertEqual(collection.method, 'CFOP')
        self.assertEqual(collection.source, test_path)
        self.assertEqual(collection.name, 'OLL')
        self.assertEqual(collection.loaded_cases, {})

    def test_name_derived_from_source_stem(self) -> None:
        """Test that collection name is derived from source file stem."""
        test_path = Path('/path/to/PLL.json')
        collection = CaseCollection('CFOP', test_path)

        self.assertEqual(collection.name, 'PLL')

    def test_init_with_different_file_names(self) -> None:
        """Test initialization with different file names."""
        test_cases = [
            ('F2L.json', 'F2L'),
            ('OLL.json', 'OLL'),
            ('PLL.json', 'PLL'),
            ('AF2L.json', 'AF2L'),
        ]

        for filename, expected_name in test_cases:
            with self.subTest(filename=filename):
                test_path = Path(f'/path/{filename}')
                collection = CaseCollection('CFOP', test_path)
                self.assertEqual(collection.name, expected_name)

    def test_init_empty_loaded_cases(self) -> None:
        """Test that loaded_cases starts empty."""
        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        self.assertIsInstance(collection.loaded_cases, dict)
        self.assertEqual(len(collection.loaded_cases), 0)


class TestCaseCollectionCasesProperty(unittest.TestCase):
    """Test CaseCollection cases property with lazy loading."""

    def test_cases_property_lazy_loading(self) -> None:
        """Test that cases are loaded lazily from JSON file."""
        test_data = [
            {
                'name': 'OLL 01',
                'code': '01',
                'description': 'Test case 1',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': 'R U R',
                'algorithms': [],
            },
            {
                'name': 'OLL 02',
                'code': '02',
                'description': 'Test case 2',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': 'F U F',
                'algorithms': [],
            },
        ]

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            cases = collection.cases

        self.assertEqual(len(cases), 2)
        self.assertIn('OLL 01', cases)
        self.assertIn('OLL 02', cases)
        self.assertIsInstance(cases['OLL 01'], Case)
        self.assertIsInstance(cases['OLL 02'], Case)

    def test_cases_property_caching(self) -> None:
        """Test that cases are cached after first load."""
        test_data = [
            {
                'name': 'Test Case',
                'code': '01',
                'description': '',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': '',
                'algorithms': [],
            },
        ]

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            cases1 = collection.cases
            cases2 = collection.cases

        self.assertIs(cases1, cases2)
        m.assert_called_once()

    def test_cases_property_empty_file(self) -> None:
        """Test cases property with empty JSON array."""
        test_data: list[dict[str, object]] = []

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            cases = collection.cases

        self.assertEqual(len(cases), 0)
        self.assertIsInstance(cases, dict)

    def test_cases_property_creates_case_objects(self) -> None:
        """Test that cases property creates Case objects with correct data."""
        test_data = [
            {
                'name': 'PLL Aa',
                'code': 'Aa',
                'description': 'Adjacent corner swap',
                'aliases': ['A-Perm'],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': ['PLL'],
                'status': 'OK',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 9,
                'optimal_stm': 9,
                'probability': 0.05555,
                'probability_label': '1/18',
                'main': "x R' U R' D2 R U' R' D2 R2 x'",
                'algorithms': [],
            },
        ]

        test_path = Path('/fake/path/PLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            cases = collection.cases

        case = cases['PLL Aa']
        self.assertEqual(case.method, 'CFOP')
        self.assertEqual(case.step, 'PLL')
        self.assertEqual(case.name, 'PLL Aa')
        self.assertEqual(case.code, 'Aa')


class TestCaseCollectionGetMethod(unittest.TestCase):
    """Test CaseCollection get method."""

    def test_get_existing_case(self) -> None:
        """Test getting an existing case by name."""
        test_data = [
            {
                'name': 'OLL 27',
                'code': '27',
                'description': 'Sune',
                'aliases': ['Sune'],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': '',
                'algorithms': [],
            },
        ]

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            case = collection.get('OLL 27')

        self.assertIsInstance(case, Case)
        self.assertEqual(case.name, 'OLL 27')

    def test_get_nonexistent_case(self) -> None:
        """Test getting a nonexistent case raises InvalidCaseNameError."""
        test_data = [
            {
                'name': 'OLL 01',
                'code': '01',
                'description': '',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': '',
                'algorithms': [],
            },
        ]

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with (
            patch('pathlib.Path.open', m),
            self.assertRaises(InvalidCaseNameError) as context,
        ):
            collection.get('OLL 99')

        self.assertIn('OLL 99', str(context.exception))
        self.assertIn('not a valid case', str(context.exception))

    def test_get_from_empty_collection(self) -> None:
        """Test getting a case from empty collection raises error."""
        test_data: list[dict[str, object]] = []

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with (
            patch('pathlib.Path.open', m),
            self.assertRaises(InvalidCaseNameError),
        ):
            collection.get('Any Case')

    def test_get_multiple_cases(self) -> None:
        """Test getting multiple different cases."""
        test_data = [
            {
                'name': 'OLL 01',
                'code': '01',
                'description': '',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': '',
                'algorithms': [],
            },
            {
                'name': 'OLL 02',
                'code': '02',
                'description': '',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': '',
                'algorithms': [],
            },
        ]

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            case1 = collection.get('OLL 01')
            case2 = collection.get('OLL 02')

        self.assertEqual(case1.name, 'OLL 01')
        self.assertEqual(case2.name, 'OLL 02')
        self.assertIsNot(case1, case2)


class TestCaseCollectionSizeProperty(unittest.TestCase):
    """Test CaseCollection size property."""

    def test_size_property_with_cases(self) -> None:
        """Test size property returns correct count."""
        test_data = [
            {
                'name': f'Case {i}',
                'code': f'{i:02d}',
                'description': '',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': '',
                'algorithms': [],
            }
            for i in range(5)
        ]

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            size = collection.size

        self.assertEqual(size, 5)
        self.assertIsInstance(size, int)

    def test_size_property_empty_collection(self) -> None:
        """Test size property with empty collection."""
        test_data: list[dict[str, object]] = []

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            size = collection.size

        self.assertEqual(size, 0)

    def test_size_property_single_case(self) -> None:
        """Test size property with single case."""
        test_data = [
            {
                'name': 'Single Case',
                'code': '01',
                'description': '',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': '',
                'algorithms': [],
            },
        ]

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            size = collection.size

        self.assertEqual(size, 1)


class TestCaseCollectionStringMethods(unittest.TestCase):
    """Test CaseCollection string representation methods."""

    def test_str_method(self) -> None:
        """Test __str__ returns correct format."""
        test_data = [
            {
                'name': 'Case 1',
                'code': '01',
                'description': '',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': '',
                'algorithms': [],
            },
            {
                'name': 'Case 2',
                'code': '02',
                'description': '',
                'aliases': [],
                'arrows': '',
                'symmetry': '',
                'family': '',
                'groups': [],
                'status': '',
                'recognition': {'cases': [], 'moves': []},
                'optimal_cycles': 0,
                'optimal_htm': 0,
                'optimal_stm': 0,
                'probability': 0.0,
                'probability_label': '',
                'main': '',
                'algorithms': [],
            },
        ]

        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            result = str(collection)

        self.assertEqual(result, 'Collection OLL: 2')

    def test_str_method_empty_collection(self) -> None:
        """Test __str__ with empty collection."""
        test_data: list[dict[str, object]] = []

        test_path = Path('/fake/path/PLL.json')
        collection = CaseCollection('CFOP', test_path)

        json_content = json.dumps(test_data)
        m = mock_open(read_data=json_content)

        with patch('pathlib.Path.open', m):
            result = str(collection)

        self.assertEqual(result, 'Collection PLL: 0')

    def test_repr_method(self) -> None:
        """Test __repr__ returns correct format."""
        test_path = Path('/fake/path/OLL.json')
        collection = CaseCollection('CFOP', test_path)

        result = repr(collection)

        expected = "CaseCollection('CFOP', '/fake/path/OLL.json')"
        self.assertEqual(result, expected)

    def test_repr_with_different_paths(self) -> None:
        """Test __repr__ with different source paths."""
        test_cases = [
            ('CFOP', Path('/path/to/F2L.json')),
            ('Roux', Path('/another/path/CMLL.json')),
            ('ZZ', Path('/some/path/ZBLL.json')),
        ]

        for method, source_path in test_cases:
            with self.subTest(method=method, path=source_path):
                collection = CaseCollection(method, source_path)
                result = repr(collection)
                expected = f"CaseCollection('{method}', '{source_path}')"
                self.assertEqual(result, expected)


class TestModuleLevelConstants(unittest.TestCase):
    """Test module-level constants and initialization."""

    def test_cases_directory_exists(self) -> None:
        """Test that CASES_DIRECTORY is defined and is a Path."""
        self.assertIsInstance(CASES_DIRECTORY, Path)

    def test_cases_directory_is_parent_of_file(self) -> None:
        """Test that CASES_DIRECTORY points to correct location."""
        self.assertTrue(str(CASES_DIRECTORY).endswith('cases'))

    def test_methods_list_defined(self) -> None:
        """Test that METHODS list is defined."""
        self.assertIsInstance(METHODS, list)
        self.assertIn('CFOP', METHODS)

    def test_collections_dict_defined(self) -> None:
        """Test that COLLECTIONS dict is defined."""
        self.assertIsInstance(COLLECTIONS, dict)

    def test_collections_populated_from_real_files(self) -> None:
        """Test that COLLECTIONS dict is populated with real data."""
        self.assertGreater(len(COLLECTIONS), 0)

        for key, collection in COLLECTIONS.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(collection, CaseCollection)
            self.assertIn('/', key)

    def test_collections_keys_format(self) -> None:
        """Test that COLLECTIONS keys follow METHOD/NAME format."""
        for key in COLLECTIONS:
            self.assertIn('/', key)
            method, _ = key.split('/', 1)
            self.assertEqual(method, method.upper())

    def test_collections_contain_expected_keys(self) -> None:
        """Test that COLLECTIONS contains expected collections."""
        expected_collections = [
            'CFOP/OLL',
            'CFOP/PLL',
            'CFOP/F2L',
            'CFOP/AF2L',
        ]

        for expected in expected_collections:
            self.assertIn(expected, COLLECTIONS)

    def test_collections_values_are_case_collection_instances(self) -> None:
        """Test that all COLLECTIONS values are CaseCollection instances."""
        for collection in COLLECTIONS.values():
            self.assertIsInstance(collection, CaseCollection)

    def test_collections_source_files_exist(self) -> None:
        """Test that source files for collections exist."""
        for collection in COLLECTIONS.values():
            self.assertTrue(
                collection.source.exists(),
                f'Source file does not exist: {collection.source}',
            )


class TestCaseCollectionRealData(unittest.TestCase):
    """Test CaseCollection with real JSON files."""

    def test_load_real_oll_collection(self) -> None:
        """Test loading real OLL collection."""
        if 'CFOP/OLL' not in COLLECTIONS:
            self.skipTest('CFOP/OLL collection not available')

        collection = COLLECTIONS['CFOP/OLL']
        self.assertEqual(collection.method, 'CFOP')
        self.assertEqual(collection.name, 'OLL')
        self.assertGreater(collection.size, 0)

    def test_load_real_pll_collection(self) -> None:
        """Test loading real PLL collection."""
        if 'CFOP/PLL' not in COLLECTIONS:
            self.skipTest('CFOP/PLL collection not available')

        collection = COLLECTIONS['CFOP/PLL']
        self.assertEqual(collection.method, 'CFOP')
        self.assertEqual(collection.name, 'PLL')
        self.assertGreater(collection.size, 0)

    def test_real_collection_cases_are_case_objects(self) -> None:
        """Test that real collections contain Case objects."""
        if 'CFOP/OLL' not in COLLECTIONS:
            self.skipTest('CFOP/OLL collection not available')

        collection = COLLECTIONS['CFOP/OLL']
        cases = collection.cases

        for case in cases.values():
            self.assertIsInstance(case, Case)
