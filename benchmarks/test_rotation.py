"""
Benchmarks of move execution on the virtual cube.

They go through the public API only, so that the numbers stay comparable
across any rewrite of the native rotation kernel. Run them with:

    pytest benchmarks --no-cov --benchmark-autosave
    pytest benchmarks --no-cov --benchmark-compare
"""
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

T_PERM = "R U R' U' R' F R2 U' R' U' R U R' F'"
LONG = ' '.join([T_PERM] * 50)
SLICES = "M2 U M U2 M' U M2 Rw x y' S E'"
LAYERS = "3Rw U 3Rw' 2-3Lw 2U' Uw2 x"

SIZES = [2, 3, 4, 5, 7]


@pytest.mark.parametrize('size', SIZES)
def test_rotate_single_move(benchmark: BenchmarkFixture, size: int) -> None:
    """One face turn: dominated by the call overhead."""
    cube = VCube(size=size)
    benchmark(cube.rotate, 'R', history=False)


@pytest.mark.parametrize('size', SIZES)
def test_rotate_t_perm(benchmark: BenchmarkFixture, size: int) -> None:
    """A 14 moves algorithm, the typical case."""
    cube = VCube(size=size)
    benchmark(cube.rotate, T_PERM, history=False)


@pytest.mark.parametrize('size', SIZES)
def test_rotate_long(benchmark: BenchmarkFixture, size: int) -> None:
    """A 700 moves sequence: dominated by the kernel itself."""
    cube = VCube(size=size)
    benchmark(cube.rotate, LONG, history=False)


@pytest.mark.parametrize('size', [3, 5, 7])
def test_rotate_slices(benchmark: BenchmarkFixture, size: int) -> None:
    """Slice, wide and rotation moves."""
    cube = VCube(size=size)
    benchmark(cube.rotate, SLICES, history=False)


@pytest.mark.parametrize('size', [5, 7])
def test_rotate_layers(benchmark: BenchmarkFixture, size: int) -> None:
    """Moves addressing inner layers by number."""
    cube = VCube(size=size)
    benchmark(cube.rotate, LAYERS, history=False)


def test_rotate_with_history(benchmark: BenchmarkFixture) -> None:
    """The default call, recording every move in the history."""
    benchmark(lambda: VCube().rotate(T_PERM))


def test_rotate_algorithm(benchmark: BenchmarkFixture) -> None:
    """An Algorithm instance, serialized before being executed."""
    algorithm = parse_moves(T_PERM)
    benchmark(lambda: VCube().rotate(algorithm))


def test_parse_moves(benchmark: BenchmarkFixture) -> None:
    """Parsing, the usual step before any execution."""
    benchmark(parse_moves, T_PERM)


def test_cubies_to_facelets_scheme(benchmark: BenchmarkFixture) -> None:
    """Cubies to facelets with a color scheme, which rotates the scheme."""
    cube = VCube()
    cube.rotate('R U x y')
    cp, co, ep, eo, so = cube.cubies
    scheme = VCube().state
    benchmark(cubies_to_facelets, cp, co, ep, eo, so, scheme)
