import unittest

from cubing_algs.vcube import VCube


class TestMovePermutations(unittest.TestCase):

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

    def test_permutation_correctness(self):
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate('U')
        u_state = cube.state
        u_perms = self.get_permutations(initial_state, u_state)

        self.assertGreater(
            len(u_perms), 0,
            'U must produce permutations',
        )

        for dest, src in u_perms.items():
            self.assertIn(
                dest, range(54),
                f'Destination position { dest } invalid',
            )
            self.assertIn(
                src, range(54),
                f'Source position { src } invalid',
            )

    def analyze_move_permutations(self, move_name):
        cube = self.create_numbered_cube()
        initial_state = cube.state

        cube.rotate(move_name)
        after_state = cube.state
        permutations = self.get_permutations(initial_state, after_state)

        return {
            'move': move_name,
            'permutation_count': len(permutations),
            'permutations': permutations,
            'cycles': self.find_cycles(permutations),
        }

    @staticmethod
    def find_cycles(permutations):
        visited = set()
        cycles = []

        for start in permutations:
            if start in visited:
                continue

            cycle = []
            current = start

            while current not in visited:
                visited.add(current)
                cycle.append(current)
                current = permutations.get(current, current)

                if current == start:
                    break

            if len(cycle) > 1:
                cycles.append(cycle)

        return cycles

    def test_cancellation_all_moves(self):
        moves = [
            'U', 'R', 'F', 'D', 'L', 'B',
            'x', 'y', 'z', 'M', 'E', 'S',
            'u', 'r', 'f', 'd', 'l', 'b',
        ]

        for move in moves:
            with self.subTest(move=move):
                cube = self.create_numbered_cube()
                initial_state = cube.state

                cube.rotate(move)
                cube.rotate(f"{ move }'")

                self.assertEqual(
                    cube.state, initial_state,
                    f"The move { move } does not cancel with { move }'",
                )

    def test_double_moves_cancellation(self):
        moves = [
            'U', 'R', 'F', 'D', 'L', 'B',
            'x', 'y', 'z', 'M', 'E', 'S',
            'u', 'r', 'f', 'd', 'l', 'b',
        ]

        for move in moves:
            with self.subTest(move=move):
                cube = self.create_numbered_cube()
                initial_state = cube.state

                cube.rotate(f'{ move }2')
                cube.rotate(f'{ move }2')

                self.assertEqual(
                    cube.state, initial_state,
                    f'The move { move }2 does not cancel with himself',
                )

    def test_all_basic_moves_produce_permutations(self):
        moves = ['U', 'R', 'F', 'D', 'L', 'B', 'M', 'E', 'S']

        for move in moves:
            with self.subTest(move=move):
                analysis = self.analyze_move_permutations(move)

                self.assertGreater(
                    analysis['permutation_count'], 0,
                    f'The move { move } does not produce permutation',
                )

                cycles = analysis['cycles']
                self.assertGreater(
                    len(cycles), 0,
                    f'The move { move } do not produce cycle',
                )

    def test_rotations_permutations(self):
        rotations = ['x', 'y', 'z']

        for rotation in rotations:
            with self.subTest(rotation=rotation):
                analysis = self.analyze_move_permutations(rotation)

                self.assertGreaterEqual(
                    analysis['permutation_count'], 24,
                    f'The rotation { rotation } affects too few positions',
                )

                cube = self.create_numbered_cube()
                initial_state = cube.state

                cube.rotate(rotation)
                cube.rotate(f"{rotation}'")

                self.assertEqual(
                    cube.state, initial_state,
                    f'The rotation { rotation } is not reversible',
                )

    def test_wide_moves_permutations(self):
        wide_moves = ['u', 'r', 'f', 'd', 'l', 'b']

        for move in wide_moves:
            with self.subTest(move=move):
                analysis = self.analyze_move_permutations(move)

                self.assertGreaterEqual(
                    analysis['permutation_count'], 16,
                    f'The wide move { move } affects too few positions',
                )

                cube = self.create_numbered_cube()
                initial_state = cube.state

                cube.rotate(move)
                cube.rotate(f"{ move }'")

                self.assertEqual(
                    cube.state, initial_state,
                    f'The move { move } is not reversible',
                )

    def test_all_move_variants(self):
        base_moves = [
            'U', 'R', 'F', 'D', 'L', 'B',
            'x', 'y', 'z', 'M', 'E', 'S',
            'u', 'r', 'f', 'd', 'l', 'b',
        ]

        for base_move in base_moves:
            for suffix in ['', "'", '2']:
                move = f'{ base_move }{ suffix }'
                with self.subTest(move=move):
                    cube = self.create_numbered_cube()

                    try:
                        cube.rotate(move)
                        after_state = cube.state

                        self.assertIsNotNone(
                            after_state,
                            f'The move { move } has failed',
                        )

                        if suffix != '2':
                            pass

                    except Exception as e:  # noqa: BLE001
                        self.fail(f'The move { move } has failed: { e }')

    def test_specific_move_permutations_u(self):
        analysis = self.analyze_move_permutations('U')

        self.assertEqual(
            analysis['permutation_count'], 20,
            'The move U must affect exactly 20 positions',
        )

        cycles = analysis['cycles']
        self.assertGreater(len(cycles), 0, 'U must produce cycles')

    def test_specific_move_permutations_m(self):
        analysis = self.analyze_move_permutations('M')

        self.assertEqual(
            analysis['permutation_count'], 12,
            'The move M must affect exactly 12 positions',
        )

        cycles = analysis['cycles']
        self.assertGreater(len(cycles), 0, 'M must produce cycles')

    def test_permutation_bijectivity(self):
        moves = [
            'U', 'R', 'F', 'D', 'L', 'B',
            'x', 'y', 'z', 'M', 'E', 'S',
        ]

        for move in moves:
            with self.subTest(move=move):
                analysis = self.analyze_move_permutations(move)
                permutations = analysis['permutations']

                sources = list(permutations.values())
                unique_sources = set(sources)

                self.assertEqual(
                    len(sources), len(unique_sources),
                    f'The move { move } has duplicated sources',
                )

                for dest, src in permutations.items():
                    self.assertIn(
                        dest, range(54),
                        f'Destination position { dest } invalid',
                    )
                    self.assertIn(
                        src, range(54),
                        f'Source position { src } invalid',
                    )
