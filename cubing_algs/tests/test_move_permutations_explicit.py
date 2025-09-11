import unittest

from cubing_algs.vcube import VCube


class TestExplicitMovePermutations(unittest.TestCase):
    @staticmethod
    def create_numbered_cube():
        state = ''.join([chr(ord('A') + i) for i in range(54)])
        return VCube(initial=state, check=False)

    @staticmethod
    def get_permutations(initial_state, final_state):
        permutations = {}
        for dest_pos in range(54):
            dest_char = final_state[dest_pos]
            src_pos = initial_state.index(dest_char)
            if dest_pos != src_pos:
                permutations[dest_pos] = src_pos
        return permutations

    def test_U_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move U."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('U')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 6,
            1: 3,
            2: 0,
            3: 7,
            5: 1,
            6: 8,
            7: 5,
            8: 2,
            9: 45,
            10: 46,
            11: 47,
            18: 9,
            19: 10,
            20: 11,
            36: 18,
            37: 19,
            38: 20,
            45: 36,
            46: 37,
            47: 38,
        }

        self.assertEqual(permutations, expected_perms)

    def test_U_prime_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move U'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("U'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 2,
            1: 5,
            2: 8,
            3: 1,
            5: 7,
            6: 0,
            7: 3,
            8: 6,
            9: 18,
            10: 19,
            11: 20,
            18: 36,
            19: 37,
            20: 38,
            36: 45,
            37: 46,
            38: 47,
            45: 9,
            46: 10,
            47: 11,
        }

        self.assertEqual(permutations, expected_perms)

    def test_U_2_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move U2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('U2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 8,
            1: 7,
            2: 6,
            3: 5,
            5: 3,
            6: 2,
            7: 1,
            8: 0,
            9: 36,
            10: 37,
            11: 38,
            18: 45,
            19: 46,
            20: 47,
            36: 9,
            37: 10,
            38: 11,
            45: 18,
            46: 19,
            47: 20,
        }

        self.assertEqual(permutations, expected_perms)

    def test_R_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move R."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('R')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            2: 20,
            5: 23,
            8: 26,
            9: 15,
            10: 12,
            11: 9,
            12: 16,
            14: 10,
            15: 17,
            16: 14,
            17: 11,
            20: 29,
            23: 32,
            26: 35,
            29: 51,
            32: 48,
            35: 45,
            45: 8,
            48: 5,
            51: 2,
        }

        self.assertEqual(permutations, expected_perms)

    def test_R_prime_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move R'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("R'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            2: 51,
            5: 48,
            8: 45,
            9: 11,
            10: 14,
            11: 17,
            12: 10,
            14: 16,
            15: 9,
            16: 12,
            17: 15,
            20: 2,
            23: 5,
            26: 8,
            29: 20,
            32: 23,
            35: 26,
            45: 35,
            48: 32,
            51: 29,
        }

        self.assertEqual(permutations, expected_perms)

    def test_R_2_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move R2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('R2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            2: 29,
            5: 32,
            8: 35,
            9: 17,
            10: 16,
            11: 15,
            12: 14,
            14: 12,
            15: 11,
            16: 10,
            17: 9,
            20: 51,
            23: 48,
            26: 45,
            29: 2,
            32: 5,
            35: 8,
            45: 26,
            48: 23,
            51: 20,
        }

        self.assertEqual(permutations, expected_perms)

    def test_F_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move F."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('F')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            6: 44,
            7: 41,
            8: 38,
            9: 6,
            12: 7,
            15: 8,
            18: 24,
            19: 21,
            20: 18,
            21: 25,
            23: 19,
            24: 26,
            25: 23,
            26: 20,
            27: 15,
            28: 12,
            29: 9,
            38: 27,
            41: 28,
            44: 29,
        }

        self.assertEqual(permutations, expected_perms)

    def test_F_prime_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move F'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("F'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            6: 9,
            7: 12,
            8: 15,
            9: 29,
            12: 28,
            15: 27,
            18: 20,
            19: 23,
            20: 26,
            21: 19,
            23: 25,
            24: 18,
            25: 21,
            26: 24,
            27: 38,
            28: 41,
            29: 44,
            38: 8,
            41: 7,
            44: 6,
        }

        self.assertEqual(permutations, expected_perms)

    def test_F_2_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move F2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('F2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            6: 29,
            7: 28,
            8: 27,
            9: 44,
            12: 41,
            15: 38,
            18: 26,
            19: 25,
            20: 24,
            21: 23,
            23: 21,
            24: 20,
            25: 19,
            26: 18,
            27: 8,
            28: 7,
            29: 6,
            38: 15,
            41: 12,
            44: 9,
        }

        self.assertEqual(permutations, expected_perms)

    def test_D_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move D."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('D')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            15: 24,
            16: 25,
            17: 26,
            24: 42,
            25: 43,
            26: 44,
            27: 33,
            28: 30,
            29: 27,
            30: 34,
            32: 28,
            33: 35,
            34: 32,
            35: 29,
            42: 51,
            43: 52,
            44: 53,
            51: 15,
            52: 16,
            53: 17,
        }

        self.assertEqual(permutations, expected_perms)

    def test_D_prime_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move D'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("D'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            15: 51,
            16: 52,
            17: 53,
            24: 15,
            25: 16,
            26: 17,
            27: 29,
            28: 32,
            29: 35,
            30: 28,
            32: 34,
            33: 27,
            34: 30,
            35: 33,
            42: 24,
            43: 25,
            44: 26,
            51: 42,
            52: 43,
            53: 44,
        }

        self.assertEqual(permutations, expected_perms)

    def test_D_2_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move D2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('D2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            15: 42,
            16: 43,
            17: 44,
            24: 51,
            25: 52,
            26: 53,
            27: 35,
            28: 34,
            29: 33,
            30: 32,
            32: 30,
            33: 29,
            34: 28,
            35: 27,
            42: 15,
            43: 16,
            44: 17,
            51: 24,
            52: 25,
            53: 26,
        }

        self.assertEqual(permutations, expected_perms)

    def test_L_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move L."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('L')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 53,
            3: 50,
            6: 47,
            18: 0,
            21: 3,
            24: 6,
            27: 18,
            30: 21,
            33: 24,
            36: 42,
            37: 39,
            38: 36,
            39: 43,
            41: 37,
            42: 44,
            43: 41,
            44: 38,
            47: 33,
            50: 30,
            53: 27,
        }

        self.assertEqual(permutations, expected_perms)

    def test_L_prime_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move L'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("L'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 18,
            3: 21,
            6: 24,
            18: 27,
            21: 30,
            24: 33,
            27: 53,
            30: 50,
            33: 47,
            36: 38,
            37: 41,
            38: 44,
            39: 37,
            41: 43,
            42: 36,
            43: 39,
            44: 42,
            47: 6,
            50: 3,
            53: 0,
        }

        self.assertEqual(permutations, expected_perms)

    def test_L_2_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move L2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('L2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 27,
            3: 30,
            6: 33,
            18: 53,
            21: 50,
            24: 47,
            27: 0,
            30: 3,
            33: 6,
            36: 44,
            37: 43,
            38: 42,
            39: 41,
            41: 39,
            42: 38,
            43: 37,
            44: 36,
            47: 24,
            50: 21,
            53: 18,
        }

        self.assertEqual(permutations, expected_perms)

    def test_B_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move B."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('B')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 11,
            1: 14,
            2: 17,
            11: 35,
            14: 34,
            17: 33,
            33: 36,
            34: 39,
            35: 42,
            36: 2,
            39: 1,
            42: 0,
            45: 51,
            46: 48,
            47: 45,
            48: 52,
            50: 46,
            51: 53,
            52: 50,
            53: 47,
        }

        self.assertEqual(permutations, expected_perms)

    def test_B_prime_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move B'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("B'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 42,
            1: 39,
            2: 36,
            11: 0,
            14: 1,
            17: 2,
            33: 17,
            34: 14,
            35: 11,
            36: 33,
            39: 34,
            42: 35,
            45: 47,
            46: 50,
            47: 53,
            48: 46,
            50: 52,
            51: 45,
            52: 48,
            53: 51,
        }

        self.assertEqual(permutations, expected_perms)

    def test_B_2_move_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move B2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('B2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 35,
            1: 34,
            2: 33,
            11: 42,
            14: 39,
            17: 36,
            33: 2,
            34: 1,
            35: 0,
            36: 17,
            39: 14,
            42: 11,
            45: 53,
            46: 52,
            47: 51,
            48: 50,
            50: 48,
            51: 47,
            52: 46,
            53: 45,
        }

        self.assertEqual(permutations, expected_perms)

    def test_x_rotation_explicit_permutations(self):
        """Test explicit permutations for move x."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('x')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 18,
            1: 19,
            2: 20,
            3: 21,
            4: 22,
            5: 23,
            6: 24,
            7: 25,
            8: 26,
            9: 15,
            10: 12,
            11: 9,
            12: 16,
            14: 10,
            15: 17,
            16: 14,
            17: 11,
            18: 27,
            19: 28,
            20: 29,
            21: 30,
            22: 31,
            23: 32,
            24: 33,
            25: 34,
            26: 35,
            27: 53,
            28: 52,
            29: 51,
            30: 50,
            31: 49,
            32: 48,
            33: 47,
            34: 46,
            35: 45,
            36: 38,
            37: 41,
            38: 44,
            39: 37,
            41: 43,
            42: 36,
            43: 39,
            44: 42,
            45: 8,
            46: 7,
            47: 6,
            48: 5,
            49: 4,
            50: 3,
            51: 2,
            52: 1,
            53: 0,
        }

        self.assertEqual(permutations, expected_perms)

    def test_x_prime_rotation_explicit_permutations(self):
        """Test explicit permutations for move x'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("x'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 53,
            1: 52,
            2: 51,
            3: 50,
            4: 49,
            5: 48,
            6: 47,
            7: 46,
            8: 45,
            9: 11,
            10: 14,
            11: 17,
            12: 10,
            14: 16,
            15: 9,
            16: 12,
            17: 15,
            18: 0,
            19: 1,
            20: 2,
            21: 3,
            22: 4,
            23: 5,
            24: 6,
            25: 7,
            26: 8,
            27: 18,
            28: 19,
            29: 20,
            30: 21,
            31: 22,
            32: 23,
            33: 24,
            34: 25,
            35: 26,
            36: 42,
            37: 39,
            38: 36,
            39: 43,
            41: 37,
            42: 44,
            43: 41,
            44: 38,
            45: 35,
            46: 34,
            47: 33,
            48: 32,
            49: 31,
            50: 30,
            51: 29,
            52: 28,
            53: 27,
        }

        self.assertEqual(permutations, expected_perms)

    def test_x_2_rotation_explicit_permutations(self):
        """Test explicit permutations for move x2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('x2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 27,
            1: 28,
            2: 29,
            3: 30,
            4: 31,
            5: 32,
            6: 33,
            7: 34,
            8: 35,
            9: 17,
            10: 16,
            11: 15,
            12: 14,
            14: 12,
            15: 11,
            16: 10,
            17: 9,
            18: 53,
            19: 52,
            20: 51,
            21: 50,
            22: 49,
            23: 48,
            24: 47,
            25: 46,
            26: 45,
            27: 0,
            28: 1,
            29: 2,
            30: 3,
            31: 4,
            32: 5,
            33: 6,
            34: 7,
            35: 8,
            36: 44,
            37: 43,
            38: 42,
            39: 41,
            41: 39,
            42: 38,
            43: 37,
            44: 36,
            45: 26,
            46: 25,
            47: 24,
            48: 23,
            49: 22,
            50: 21,
            51: 20,
            52: 19,
            53: 18,
        }

        self.assertEqual(permutations, expected_perms)

    def test_y_rotation_explicit_permutations(self):
        """Test explicit permutations for move y."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('y')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 6,
            1: 3,
            2: 0,
            3: 7,
            5: 1,
            6: 8,
            7: 5,
            8: 2,
            9: 45,
            10: 46,
            11: 47,
            12: 48,
            13: 49,
            14: 50,
            15: 51,
            16: 52,
            17: 53,
            18: 9,
            19: 10,
            20: 11,
            21: 12,
            22: 13,
            23: 14,
            24: 15,
            25: 16,
            26: 17,
            27: 29,
            28: 32,
            29: 35,
            30: 28,
            32: 34,
            33: 27,
            34: 30,
            35: 33,
            36: 18,
            37: 19,
            38: 20,
            39: 21,
            40: 22,
            41: 23,
            42: 24,
            43: 25,
            44: 26,
            45: 36,
            46: 37,
            47: 38,
            48: 39,
            49: 40,
            50: 41,
            51: 42,
            52: 43,
            53: 44,
        }

        self.assertEqual(permutations, expected_perms)

    def test_y_prime_rotation_explicit_permutations(self):
        """Test explicit permutations for move y'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("y'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 2,
            1: 5,
            2: 8,
            3: 1,
            5: 7,
            6: 0,
            7: 3,
            8: 6,
            9: 18,
            10: 19,
            11: 20,
            12: 21,
            13: 22,
            14: 23,
            15: 24,
            16: 25,
            17: 26,
            18: 36,
            19: 37,
            20: 38,
            21: 39,
            22: 40,
            23: 41,
            24: 42,
            25: 43,
            26: 44,
            27: 33,
            28: 30,
            29: 27,
            30: 34,
            32: 28,
            33: 35,
            34: 32,
            35: 29,
            36: 45,
            37: 46,
            38: 47,
            39: 48,
            40: 49,
            41: 50,
            42: 51,
            43: 52,
            44: 53,
            45: 9,
            46: 10,
            47: 11,
            48: 12,
            49: 13,
            50: 14,
            51: 15,
            52: 16,
            53: 17,
        }

        self.assertEqual(permutations, expected_perms)

    def test_y_2_rotation_explicit_permutations(self):
        """Test explicit permutations for move y2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('y2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 8,
            1: 7,
            2: 6,
            3: 5,
            5: 3,
            6: 2,
            7: 1,
            8: 0,
            9: 36,
            10: 37,
            11: 38,
            12: 39,
            13: 40,
            14: 41,
            15: 42,
            16: 43,
            17: 44,
            18: 45,
            19: 46,
            20: 47,
            21: 48,
            22: 49,
            23: 50,
            24: 51,
            25: 52,
            26: 53,
            27: 35,
            28: 34,
            29: 33,
            30: 32,
            32: 30,
            33: 29,
            34: 28,
            35: 27,
            36: 9,
            37: 10,
            38: 11,
            39: 12,
            40: 13,
            41: 14,
            42: 15,
            43: 16,
            44: 17,
            45: 18,
            46: 19,
            47: 20,
            48: 21,
            49: 22,
            50: 23,
            51: 24,
            52: 25,
            53: 26,
        }

        self.assertEqual(permutations, expected_perms)

    def test_z_rotation_explicit_permutations(self):
        """Test explicit permutations for move z."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('z')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 42,
            1: 39,
            2: 36,
            3: 43,
            4: 40,
            5: 37,
            6: 44,
            7: 41,
            8: 38,
            9: 6,
            10: 3,
            11: 0,
            12: 7,
            13: 4,
            14: 1,
            15: 8,
            16: 5,
            17: 2,
            18: 24,
            19: 21,
            20: 18,
            21: 25,
            23: 19,
            24: 26,
            25: 23,
            26: 20,
            27: 15,
            28: 12,
            29: 9,
            30: 16,
            31: 13,
            32: 10,
            33: 17,
            34: 14,
            35: 11,
            36: 33,
            37: 30,
            38: 27,
            39: 34,
            40: 31,
            41: 28,
            42: 35,
            43: 32,
            44: 29,
            45: 47,
            46: 50,
            47: 53,
            48: 46,
            50: 52,
            51: 45,
            52: 48,
            53: 51,
        }

        self.assertEqual(permutations, expected_perms)

    def test_z_prime_rotation_explicit_permutations(self):
        """Test explicit permutations for move z'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("z'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 11,
            1: 14,
            2: 17,
            3: 10,
            4: 13,
            5: 16,
            6: 9,
            7: 12,
            8: 15,
            9: 29,
            10: 32,
            11: 35,
            12: 28,
            13: 31,
            14: 34,
            15: 27,
            16: 30,
            17: 33,
            18: 20,
            19: 23,
            20: 26,
            21: 19,
            23: 25,
            24: 18,
            25: 21,
            26: 24,
            27: 38,
            28: 41,
            29: 44,
            30: 37,
            31: 40,
            32: 43,
            33: 36,
            34: 39,
            35: 42,
            36: 2,
            37: 5,
            38: 8,
            39: 1,
            40: 4,
            41: 7,
            42: 0,
            43: 3,
            44: 6,
            45: 51,
            46: 48,
            47: 45,
            48: 52,
            50: 46,
            51: 53,
            52: 50,
            53: 47,
        }

        self.assertEqual(permutations, expected_perms)

    def test_z_2_rotation_explicit_permutations(self):
        """Test explicit permutations for move z2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('z2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 35,
            1: 34,
            2: 33,
            3: 32,
            4: 31,
            5: 30,
            6: 29,
            7: 28,
            8: 27,
            9: 44,
            10: 43,
            11: 42,
            12: 41,
            13: 40,
            14: 39,
            15: 38,
            16: 37,
            17: 36,
            18: 26,
            19: 25,
            20: 24,
            21: 23,
            23: 21,
            24: 20,
            25: 19,
            26: 18,
            27: 8,
            28: 7,
            29: 6,
            30: 5,
            31: 4,
            32: 3,
            33: 2,
            34: 1,
            35: 0,
            36: 17,
            37: 16,
            38: 15,
            39: 14,
            40: 13,
            41: 12,
            42: 11,
            43: 10,
            44: 9,
            45: 53,
            46: 52,
            47: 51,
            48: 50,
            50: 48,
            51: 47,
            52: 46,
            53: 45,
        }

        self.assertEqual(permutations, expected_perms)

    def test_M_slice_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move M."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('M')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            1: 52,
            4: 49,
            7: 46,
            19: 1,
            22: 4,
            25: 7,
            28: 19,
            31: 22,
            34: 25,
            46: 34,
            49: 31,
            52: 28,
        }

        self.assertEqual(permutations, expected_perms)

    def test_M_prime_slice_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move M'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("M'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            1: 19,
            4: 22,
            7: 25,
            19: 28,
            22: 31,
            25: 34,
            28: 52,
            31: 49,
            34: 46,
            46: 7,
            49: 4,
            52: 1,
        }

        self.assertEqual(permutations, expected_perms)

    def test_M_2_slice_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move M2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('M2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            1: 28,
            4: 31,
            7: 34,
            19: 52,
            22: 49,
            25: 46,
            28: 1,
            31: 4,
            34: 7,
            46: 25,
            49: 22,
            52: 19,
        }

        self.assertEqual(permutations, expected_perms)

    def test_E_slice_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move E."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('E')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            12: 21,
            13: 22,
            14: 23,
            21: 39,
            22: 40,
            23: 41,
            39: 48,
            40: 49,
            41: 50,
            48: 12,
            49: 13,
            50: 14,
        }

        self.assertEqual(permutations, expected_perms)

    def test_E_prime_slice_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move E'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("E'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            12: 48,
            13: 49,
            14: 50,
            21: 12,
            22: 13,
            23: 14,
            39: 21,
            40: 22,
            41: 23,
            48: 39,
            49: 40,
            50: 41,
        }

        self.assertEqual(permutations, expected_perms)

    def test_E_2_slice_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move E2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('E2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            12: 39,
            13: 40,
            14: 41,
            21: 48,
            22: 49,
            23: 50,
            39: 12,
            40: 13,
            41: 14,
            48: 21,
            49: 22,
            50: 23,
        }

        self.assertEqual(permutations, expected_perms)

    def test_S_slice_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move S."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('S')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            3: 43,
            4: 40,
            5: 37,
            10: 3,
            13: 4,
            16: 5,
            30: 16,
            31: 13,
            32: 10,
            37: 30,
            40: 31,
            43: 32,
        }

        self.assertEqual(permutations, expected_perms)

    def test_S_prime_slice_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move S'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("S'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            3: 10,
            4: 13,
            5: 16,
            10: 32,
            13: 31,
            16: 30,
            30: 37,
            31: 40,
            32: 43,
            37: 5,
            40: 4,
            43: 3,
        }

        self.assertEqual(permutations, expected_perms)

    def test_S_2_slice_explicit_permutations(self):  # noqa: N802
        """Test explicit permutations for move S2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('S2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            3: 32,
            4: 31,
            5: 30,
            10: 43,
            13: 40,
            16: 37,
            30: 5,
            31: 4,
            32: 3,
            37: 16,
            40: 13,
            43: 10,
        }

        self.assertEqual(permutations, expected_perms)

    def test_u_wide_explicit_permutations(self):
        """Test explicit permutations for move u."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('u')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 6,
            1: 3,
            2: 0,
            3: 7,
            5: 1,
            6: 8,
            7: 5,
            8: 2,
            9: 45,
            10: 46,
            11: 47,
            12: 48,
            13: 49,
            14: 50,
            18: 9,
            19: 10,
            20: 11,
            21: 12,
            22: 13,
            23: 14,
            36: 18,
            37: 19,
            38: 20,
            39: 21,
            40: 22,
            41: 23,
            45: 36,
            46: 37,
            47: 38,
            48: 39,
            49: 40,
            50: 41,
        }

        self.assertEqual(permutations, expected_perms)

    def test_u_prime_wide_explicit_permutations(self):
        """Test explicit permutations for move u'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("u'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 2,
            1: 5,
            2: 8,
            3: 1,
            5: 7,
            6: 0,
            7: 3,
            8: 6,
            9: 18,
            10: 19,
            11: 20,
            12: 21,
            13: 22,
            14: 23,
            18: 36,
            19: 37,
            20: 38,
            21: 39,
            22: 40,
            23: 41,
            36: 45,
            37: 46,
            38: 47,
            39: 48,
            40: 49,
            41: 50,
            45: 9,
            46: 10,
            47: 11,
            48: 12,
            49: 13,
            50: 14,
        }

        self.assertEqual(permutations, expected_perms)

    def test_u_2_wide_explicit_permutations(self):
        """Test explicit permutations for move u2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('u2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 8,
            1: 7,
            2: 6,
            3: 5,
            5: 3,
            6: 2,
            7: 1,
            8: 0,
            9: 36,
            10: 37,
            11: 38,
            12: 39,
            13: 40,
            14: 41,
            18: 45,
            19: 46,
            20: 47,
            21: 48,
            22: 49,
            23: 50,
            36: 9,
            37: 10,
            38: 11,
            39: 12,
            40: 13,
            41: 14,
            45: 18,
            46: 19,
            47: 20,
            48: 21,
            49: 22,
            50: 23,
        }

        self.assertEqual(permutations, expected_perms)

    def test_r_wide_explicit_permutations(self):
        """Test explicit permutations for move r."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('r')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            1: 19,
            2: 20,
            4: 22,
            5: 23,
            7: 25,
            8: 26,
            9: 15,
            10: 12,
            11: 9,
            12: 16,
            14: 10,
            15: 17,
            16: 14,
            17: 11,
            19: 28,
            20: 29,
            22: 31,
            23: 32,
            25: 34,
            26: 35,
            28: 52,
            29: 51,
            31: 49,
            32: 48,
            34: 46,
            35: 45,
            45: 8,
            46: 7,
            48: 5,
            49: 4,
            51: 2,
            52: 1,
        }

        self.assertEqual(permutations, expected_perms)

    def test_r_prime_wide_explicit_permutations(self):
        """Test explicit permutations for move r'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("r'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            1: 52,
            2: 51,
            4: 49,
            5: 48,
            7: 46,
            8: 45,
            9: 11,
            10: 14,
            11: 17,
            12: 10,
            14: 16,
            15: 9,
            16: 12,
            17: 15,
            19: 1,
            20: 2,
            22: 4,
            23: 5,
            25: 7,
            26: 8,
            28: 19,
            29: 20,
            31: 22,
            32: 23,
            34: 25,
            35: 26,
            45: 35,
            46: 34,
            48: 32,
            49: 31,
            51: 29,
            52: 28,
        }

        self.assertEqual(permutations, expected_perms)

    def test_r_2_wide_explicit_permutations(self):
        """Test explicit permutations for move r2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('r2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            1: 28,
            2: 29,
            4: 31,
            5: 32,
            7: 34,
            8: 35,
            9: 17,
            10: 16,
            11: 15,
            12: 14,
            14: 12,
            15: 11,
            16: 10,
            17: 9,
            19: 52,
            20: 51,
            22: 49,
            23: 48,
            25: 46,
            26: 45,
            28: 1,
            29: 2,
            31: 4,
            32: 5,
            34: 7,
            35: 8,
            45: 26,
            46: 25,
            48: 23,
            49: 22,
            51: 20,
            52: 19,
        }

        self.assertEqual(permutations, expected_perms)

    def test_f_wide_explicit_permutations(self):
        """Test explicit permutations for move f."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('f')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            3: 43,
            4: 40,
            5: 37,
            6: 44,
            7: 41,
            8: 38,
            9: 6,
            10: 3,
            12: 7,
            13: 4,
            15: 8,
            16: 5,
            18: 24,
            19: 21,
            20: 18,
            21: 25,
            23: 19,
            24: 26,
            25: 23,
            26: 20,
            27: 15,
            28: 12,
            29: 9,
            30: 16,
            31: 13,
            32: 10,
            37: 30,
            38: 27,
            40: 31,
            41: 28,
            43: 32,
            44: 29,
        }

        self.assertEqual(permutations, expected_perms)

    def test_f_prime_wide_explicit_permutations(self):
        """Test explicit permutations for move f'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("f'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            3: 10,
            4: 13,
            5: 16,
            6: 9,
            7: 12,
            8: 15,
            9: 29,
            10: 32,
            12: 28,
            13: 31,
            15: 27,
            16: 30,
            18: 20,
            19: 23,
            20: 26,
            21: 19,
            23: 25,
            24: 18,
            25: 21,
            26: 24,
            27: 38,
            28: 41,
            29: 44,
            30: 37,
            31: 40,
            32: 43,
            37: 5,
            38: 8,
            40: 4,
            41: 7,
            43: 3,
            44: 6,
        }

        self.assertEqual(permutations, expected_perms)

    def test_f_2_wide_explicit_permutations(self):
        """Test explicit permutations for move f2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('f2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            3: 32,
            4: 31,
            5: 30,
            6: 29,
            7: 28,
            8: 27,
            9: 44,
            10: 43,
            12: 41,
            13: 40,
            15: 38,
            16: 37,
            18: 26,
            19: 25,
            20: 24,
            21: 23,
            23: 21,
            24: 20,
            25: 19,
            26: 18,
            27: 8,
            28: 7,
            29: 6,
            30: 5,
            31: 4,
            32: 3,
            37: 16,
            38: 15,
            40: 13,
            41: 12,
            43: 10,
            44: 9,
        }

        self.assertEqual(permutations, expected_perms)

    def test_d_wide_explicit_permutations(self):
        """Test explicit permutations for move d."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('d')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            12: 21,
            13: 22,
            14: 23,
            15: 24,
            16: 25,
            17: 26,
            21: 39,
            22: 40,
            23: 41,
            24: 42,
            25: 43,
            26: 44,
            27: 33,
            28: 30,
            29: 27,
            30: 34,
            32: 28,
            33: 35,
            34: 32,
            35: 29,
            39: 48,
            40: 49,
            41: 50,
            42: 51,
            43: 52,
            44: 53,
            48: 12,
            49: 13,
            50: 14,
            51: 15,
            52: 16,
            53: 17,
        }

        self.assertEqual(permutations, expected_perms)

    def test_d_prime_wide_explicit_permutations(self):
        """Test explicit permutations for move d'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("d'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            12: 48,
            13: 49,
            14: 50,
            15: 51,
            16: 52,
            17: 53,
            21: 12,
            22: 13,
            23: 14,
            24: 15,
            25: 16,
            26: 17,
            27: 29,
            28: 32,
            29: 35,
            30: 28,
            32: 34,
            33: 27,
            34: 30,
            35: 33,
            39: 21,
            40: 22,
            41: 23,
            42: 24,
            43: 25,
            44: 26,
            48: 39,
            49: 40,
            50: 41,
            51: 42,
            52: 43,
            53: 44,
        }

        self.assertEqual(permutations, expected_perms)

    def test_d_2_wide_explicit_permutations(self):
        """Test explicit permutations for move d2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('d2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            12: 39,
            13: 40,
            14: 41,
            15: 42,
            16: 43,
            17: 44,
            21: 48,
            22: 49,
            23: 50,
            24: 51,
            25: 52,
            26: 53,
            27: 35,
            28: 34,
            29: 33,
            30: 32,
            32: 30,
            33: 29,
            34: 28,
            35: 27,
            39: 12,
            40: 13,
            41: 14,
            42: 15,
            43: 16,
            44: 17,
            48: 21,
            49: 22,
            50: 23,
            51: 24,
            52: 25,
            53: 26,
        }

        self.assertEqual(permutations, expected_perms)

    def test_l_wide_explicit_permutations(self):
        """Test explicit permutations for move l."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('l')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 53,
            1: 52,
            3: 50,
            4: 49,
            6: 47,
            7: 46,
            18: 0,
            19: 1,
            21: 3,
            22: 4,
            24: 6,
            25: 7,
            27: 18,
            28: 19,
            30: 21,
            31: 22,
            33: 24,
            34: 25,
            36: 42,
            37: 39,
            38: 36,
            39: 43,
            41: 37,
            42: 44,
            43: 41,
            44: 38,
            46: 34,
            47: 33,
            49: 31,
            50: 30,
            52: 28,
            53: 27,
        }

        self.assertEqual(permutations, expected_perms)

    def test_l_prime_wide_explicit_permutations(self):
        """Test explicit permutations for move l'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("l'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 18,
            1: 19,
            3: 21,
            4: 22,
            6: 24,
            7: 25,
            18: 27,
            19: 28,
            21: 30,
            22: 31,
            24: 33,
            25: 34,
            27: 53,
            28: 52,
            30: 50,
            31: 49,
            33: 47,
            34: 46,
            36: 38,
            37: 41,
            38: 44,
            39: 37,
            41: 43,
            42: 36,
            43: 39,
            44: 42,
            46: 7,
            47: 6,
            49: 4,
            50: 3,
            52: 1,
            53: 0,
        }

        self.assertEqual(permutations, expected_perms)

    def test_l_2_wide_explicit_permutations(self):
        """Test explicit permutations for move l2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('l2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 27,
            1: 28,
            3: 30,
            4: 31,
            6: 33,
            7: 34,
            18: 53,
            19: 52,
            21: 50,
            22: 49,
            24: 47,
            25: 46,
            27: 0,
            28: 1,
            30: 3,
            31: 4,
            33: 6,
            34: 7,
            36: 44,
            37: 43,
            38: 42,
            39: 41,
            41: 39,
            42: 38,
            43: 37,
            44: 36,
            46: 25,
            47: 24,
            49: 22,
            50: 21,
            52: 19,
            53: 18,
        }

        self.assertEqual(permutations, expected_perms)

    def test_b_wide_explicit_permutations(self):
        """Test explicit permutations for move b."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('b')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 11,
            1: 14,
            2: 17,
            3: 10,
            4: 13,
            5: 16,
            10: 32,
            11: 35,
            13: 31,
            14: 34,
            16: 30,
            17: 33,
            30: 37,
            31: 40,
            32: 43,
            33: 36,
            34: 39,
            35: 42,
            36: 2,
            37: 5,
            39: 1,
            40: 4,
            42: 0,
            43: 3,
            45: 51,
            46: 48,
            47: 45,
            48: 52,
            50: 46,
            51: 53,
            52: 50,
            53: 47,
        }

        self.assertEqual(permutations, expected_perms)

    def test_b_prime_wide_explicit_permutations(self):
        """Test explicit permutations for move b'."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate("b'")
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 42,
            1: 39,
            2: 36,
            3: 43,
            4: 40,
            5: 37,
            10: 3,
            11: 0,
            13: 4,
            14: 1,
            16: 5,
            17: 2,
            30: 16,
            31: 13,
            32: 10,
            33: 17,
            34: 14,
            35: 11,
            36: 33,
            37: 30,
            39: 34,
            40: 31,
            42: 35,
            43: 32,
            45: 47,
            46: 50,
            47: 53,
            48: 46,
            50: 52,
            51: 45,
            52: 48,
            53: 51,
        }

        self.assertEqual(permutations, expected_perms)

    def test_b_2_wide_explicit_permutations(self):
        """Test explicit permutations for move b2."""
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('b2')
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        expected_perms = {
            0: 35,
            1: 34,
            2: 33,
            3: 32,
            4: 31,
            5: 30,
            10: 43,
            11: 42,
            13: 40,
            14: 39,
            16: 37,
            17: 36,
            30: 5,
            31: 4,
            32: 3,
            33: 2,
            34: 1,
            35: 0,
            36: 17,
            37: 16,
            39: 14,
            40: 13,
            42: 11,
            43: 10,
            45: 53,
            46: 52,
            47: 51,
            48: 50,
            50: 48,
            51: 47,
            52: 46,
            53: 45,
        }

        self.assertEqual(permutations, expected_perms)
