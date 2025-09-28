from pprint import pp

from cubing_algs.algorithm import Algorithm


def show_impact(algorithm: str):
    print(algorithm)
    algo = Algorithm.parse_moves(algorithm)
    pp(algo.impacts._asdict())
    algo.show()


show_impact('R')
show_impact("R'")
show_impact("R U R' U'")
