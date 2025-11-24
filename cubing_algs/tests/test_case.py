"""Tests for the Case class."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.cases.case import Case
from cubing_algs.cases.case import CaseData


class TestCaseInitialization(unittest.TestCase):
    """Test Case initialization."""

    def test_init_with_valid_data(self) -> None:
        """Test Case initialization with valid data."""
        data: CaseData = {
            'name': 'OLL 01',
            'code': '01',
            'description': 'Test case',
            'aliases': ['Runway', 'Blank'],
            'arrows': '',
            'symmetry': 'double',
            'family': 'Point',
            'groups': ['OLL'],
            'status': 'OK',
            'recognition': {'cases': [], 'moves': []},
            'optimal_cycles': 3,
            'optimal_htm': 11,
            'optimal_stm': 11,
            'probability': 0.009259259,
            'probability_label': '1/108',
            'main': "R U R' U'",
            'algorithms': ["R U R' U'", "F R U R' U' F'"],
        }

        case = Case('CFOP', 'OLL', data)

        self.assertEqual(case.method, 'CFOP')
        self.assertEqual(case.step, 'OLL')
        self.assertEqual(case.data, data)

    def test_init_with_empty_method_step(self) -> None:
        """Test Case initialization with empty method and step."""
        data: CaseData = {
            'name': 'Test',
            'code': '00',
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

        case = Case('', '', data)

        self.assertEqual(case.method, '')
        self.assertEqual(case.step, '')


class TestCaseProperties(unittest.TestCase):
    """Test Case cached properties."""

    def setUp(self) -> None:
        """Set up test case with sample data."""
        self.data: CaseData = {
            'name': 'OLL 27',
            'code': '27',
            'description': 'Sune pattern',
            'aliases': ['Sune', 'Anti-Bruno'],
            'arrows': '↻U',
            'symmetry': 'single',
            'family': 'Corner',
            'groups': ['OLL', 'COLL'],
            'status': 'OK',
            'recognition': {
                'cases': [],
                'moves': ['U', 'U2', "U'"],
            },
            'optimal_cycles': 2,
            'optimal_htm': 6,
            'optimal_stm': 6,
            'probability': 0.037037037,
            'probability_label': '1/27',
            'main': "R U R' U R U2 R'",
            'algorithms': [
                "R U R' U R U2 R'",
                "L' U' L U' L' U2 L",
                "y R U R' U R U2 R'",
            ],
        }
        self.case = Case('CFOP', 'OLL', self.data)

    def test_name_property(self) -> None:
        """Test name property returns correct value."""
        self.assertEqual(self.case.name, 'OLL 27')

    def test_code_property(self) -> None:
        """Test code property returns correct value."""
        self.assertEqual(self.case.code, '27')

    def test_description_property(self) -> None:
        """Test description property returns correct value."""
        self.assertEqual(self.case.description, 'Sune pattern')

    def test_aliases_property(self) -> None:
        """Test aliases property returns correct list."""
        self.assertEqual(self.case.aliases, ['Sune', 'Anti-Bruno'])
        self.assertIsInstance(self.case.aliases, list)

    def test_arrows_property(self) -> None:
        """Test arrows property returns correct value."""
        self.assertEqual(self.case.arrows, '↻U')

    def test_symmetry_property(self) -> None:
        """Test symmetry property returns correct value."""
        self.assertEqual(self.case.symmetry, 'single')

    def test_family_property(self) -> None:
        """Test family property returns correct value."""
        self.assertEqual(self.case.family, 'Corner')

    def test_groups_property(self) -> None:
        """Test groups property returns correct list."""
        self.assertEqual(self.case.groups, ['OLL', 'COLL'])
        self.assertIsInstance(self.case.groups, list)

    def test_status_property(self) -> None:
        """Test status property returns correct value."""
        self.assertEqual(self.case.status, 'OK')

    def test_recognition_property(self) -> None:
        """Test recognition property returns correct data."""
        recognition = self.case.recognition
        self.assertIsInstance(recognition, dict)
        self.assertIn('cases', recognition)
        self.assertIn('moves', recognition)
        self.assertEqual(recognition['moves'], ['U', 'U2', "U'"])

    def test_optimal_cycles_property(self) -> None:
        """Test optimal_cycles property returns correct value."""
        self.assertEqual(self.case.optimal_cycles, 2)
        self.assertIsInstance(self.case.optimal_cycles, int)

    def test_optimal_htm_property(self) -> None:
        """Test optimal_htm property returns correct value."""
        self.assertEqual(self.case.optimal_htm, 6)
        self.assertIsInstance(self.case.optimal_htm, int)

    def test_optimal_stm_property(self) -> None:
        """Test optimal_stm property returns correct value."""
        self.assertEqual(self.case.optimal_stm, 6)
        self.assertIsInstance(self.case.optimal_stm, int)

    def test_probability_property(self) -> None:
        """Test probability property returns correct value."""
        self.assertAlmostEqual(self.case.probability, 0.037037037, places=6)
        self.assertIsInstance(self.case.probability, float)

    def test_probability_label_property(self) -> None:
        """Test probability_label property returns correct value."""
        self.assertEqual(self.case.probability_label, '1/27')


class TestCaseAlgorithmProperties(unittest.TestCase):
    """Test Case algorithm-related properties."""

    def setUp(self) -> None:
        """Set up test case with sample data."""
        self.data: CaseData = {
            'name': 'Test Case',
            'code': '01',
            'description': 'Test',
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
            'main': "R U R' U'",
            'algorithms': [
                "R U R' U'",
                "F R U R' U' F'",
                'R U2 R2 F R F2 U2 F',
            ],
        }
        self.case = Case('CFOP', 'OLL', self.data)

    def test_main_algorithm_property(self) -> None:
        """Test main_algorithm property returns Algorithm."""
        main_algo = self.case.main_algorithm
        self.assertIsInstance(main_algo, Algorithm)
        self.assertEqual(str(main_algo), "R U R' U'")

    def test_algorithms_property(self) -> None:
        """Test algorithms property returns list of Algorithms."""
        algorithms = self.case.algorithms
        self.assertIsInstance(algorithms, list)
        self.assertEqual(len(algorithms), 3)

        for algo in algorithms:
            self.assertIsInstance(algo, Algorithm)

        self.assertEqual(str(algorithms[0]), "R U R' U'")
        self.assertEqual(str(algorithms[1]), "F R U R' U' F'")
        self.assertEqual(str(algorithms[2]), 'R U2 R2 F R F2 U2 F')

    def test_algorithms_property_empty_list(self) -> None:
        """Test algorithms property with empty algorithms list."""
        data: CaseData = {
            'name': 'Empty',
            'code': '00',
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
        case = Case('CFOP', 'OLL', data)

        algorithms = case.algorithms
        self.assertIsInstance(algorithms, list)
        self.assertEqual(len(algorithms), 0)


class TestCaseStringMethods(unittest.TestCase):
    """Test Case string representation methods."""

    def test_str_method(self) -> None:
        """Test __str__ returns correct format."""
        data: CaseData = {
            'name': 'OLL 27',
            'code': '27',
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
        case = Case('CFOP', 'OLL', data)

        self.assertEqual(str(case), 'Case OLL 27')

    def test_str_with_different_names(self) -> None:
        """Test __str__ with different case names."""
        data: CaseData = {
            'name': 'PLL Ja',
            'code': 'Ja',
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
        case = Case('CFOP', 'PLL', data)

        self.assertEqual(str(case), 'Case PLL Ja')

    def test_repr_method(self) -> None:
        """Test __repr__ returns correct format."""
        data: CaseData = {
            'name': 'OLL 27',
            'code': '27',
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
        case = Case('CFOP', 'OLL', data)

        expected = "Case('CFOP', 'OLL', {'name': 'OLL 27'})"
        self.assertEqual(repr(case), expected)

    def test_repr_with_different_method_step(self) -> None:
        """Test __repr__ with different method and step."""
        data: CaseData = {
            'name': 'Test Name',
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
        }
        case = Case('Roux', 'CMLL', data)

        expected = "Case('Roux', 'CMLL', {'name': 'Test Name'})"
        self.assertEqual(repr(case), expected)


class TestCaseEdgeCases(unittest.TestCase):
    """Test Case edge cases and boundary conditions."""

    def test_empty_aliases_list(self) -> None:
        """Test case with empty aliases list."""
        data: CaseData = {
            'name': 'No Aliases',
            'code': '00',
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
        case = Case('CFOP', 'OLL', data)

        self.assertEqual(case.aliases, [])
        self.assertIsInstance(case.aliases, list)

    def test_empty_groups_list(self) -> None:
        """Test case with empty groups list."""
        data: CaseData = {
            'name': 'No Groups',
            'code': '00',
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
        case = Case('CFOP', 'OLL', data)

        self.assertEqual(case.groups, [])
        self.assertIsInstance(case.groups, list)

    def test_zero_probability(self) -> None:
        """Test case with zero probability."""
        data: CaseData = {
            'name': 'Zero Prob',
            'code': '00',
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
            'probability_label': '0',
            'main': '',
            'algorithms': [],
        }
        case = Case('CFOP', 'OLL', data)

        self.assertEqual(case.probability, 0.0)
        self.assertEqual(case.probability_label, '0')

    def test_high_optimal_values(self) -> None:
        """Test case with high optimal values."""
        data: CaseData = {
            'name': 'High Values',
            'code': '00',
            'description': '',
            'aliases': [],
            'arrows': '',
            'symmetry': '',
            'family': '',
            'groups': [],
            'status': '',
            'recognition': {'cases': [], 'moves': []},
            'optimal_cycles': 100,
            'optimal_htm': 50,
            'optimal_stm': 45,
            'probability': 0.0,
            'probability_label': '',
            'main': '',
            'algorithms': [],
        }
        case = Case('CFOP', 'OLL', data)

        self.assertEqual(case.optimal_cycles, 100)
        self.assertEqual(case.optimal_htm, 50)
        self.assertEqual(case.optimal_stm, 45)

    def test_empty_recognition_data(self) -> None:
        """Test case with empty recognition data."""
        data: CaseData = {
            'name': 'Empty Recognition',
            'code': '00',
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
        case = Case('CFOP', 'OLL', data)

        recognition = case.recognition
        self.assertEqual(recognition['cases'], [])
        self.assertEqual(recognition['moves'], [])

    def test_empty_string_fields(self) -> None:
        """Test case with empty string fields."""
        data: CaseData = {
            'name': '',
            'code': '',
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
        case = Case('', '', data)

        self.assertEqual(case.name, '')
        self.assertEqual(case.code, '')
        self.assertEqual(case.description, '')
        self.assertEqual(case.arrows, '')
        self.assertEqual(case.symmetry, '')
        self.assertEqual(case.family, '')
        self.assertEqual(case.status, '')

    def test_cached_property_accessed_multiple_times(self) -> None:
        """Test cached properties return same value on multiple accesses."""
        data: CaseData = {
            'name': 'Cached Test',
            'code': '01',
            'description': 'Testing caching',
            'aliases': ['Alias1'],
            'arrows': '',
            'symmetry': '',
            'family': '',
            'groups': [],
            'status': '',
            'recognition': {'cases': [], 'moves': []},
            'optimal_cycles': 5,
            'optimal_htm': 10,
            'optimal_stm': 8,
            'probability': 0.5,
            'probability_label': '1/2',
            'main': 'R U R',
            'algorithms': ['R U R', 'F U F'],
        }
        case = Case('CFOP', 'OLL', data)

        name1 = case.name
        name2 = case.name
        self.assertIs(name1, name2)

        algo1 = case.main_algorithm
        algo2 = case.main_algorithm
        self.assertIs(algo1, algo2)

        algos1 = case.algorithms
        algos2 = case.algorithms
        self.assertIs(algos1, algos2)
