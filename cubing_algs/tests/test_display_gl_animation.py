"""Tests for the animation of the GPU rendering backend."""
import math
import unittest

from cubing_algs.display.gl.animation import Animation
from cubing_algs.display.gl.animation import Turn
from cubing_algs.display.gl.animation import build_turn
from cubing_algs.display.gl.animation import ease
from cubing_algs.display.gl.animation import turn_coordinates
from cubing_algs.display.gl.animation import turned_scene
from cubing_algs.display.gl.constants import FRAME_RATE
from cubing_algs.display.gl.constants import HALF_TURN_FACTOR
from cubing_algs.display.gl.constants import MILLISECONDS
from cubing_algs.display.gl.constants import MINIMUM_MOVE_DURATION
from cubing_algs.display.gl.constants import MOVE_DURATION
from cubing_algs.display.gl.constants import MOVE_TURNS
from cubing_algs.display.gl.constants import PAUSE_DURATION
from cubing_algs.display.gl.constants import QUARTER_TURN
from cubing_algs.display.gl.geometry import FACE_BASES
from cubing_algs.display.gl.geometry import Cubie
from cubing_algs.display.gl.presentation import Presentation
from cubing_algs.display.gl.scene import SIDE_NUMBER
from cubing_algs.display.gl.scene import CubieInstance
from cubing_algs.display.gl.scene import Scene
from cubing_algs.display.gl.scene import build_scene
from cubing_algs.display.gl.transforms import Mat4
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

# How far two coordinates may differ and still be the same place.
TOLERANCE = 1e-6

# Scrambles the moves are checked on, so that no two facelets of the
# cube share a color and a wrong layer cannot go unnoticed.
SCRAMBLE_3 = "R U R' U' F2 L D' B R2 U"
SCRAMBLE_5 = "Rw U2 3Rw' F L2 Uw B' M2 D"

# Every notation a move can be written in, on a 3x3x3: the plain faces,
# the slices, the rotations and the wide moves, turned both ways.
MOVES_3 = (
    'R', "R'", 'R2', 'L', "L'", 'L2', 'U', "U'", 'U2',
    'D', "D'", 'F', "F'", 'B', "B'", 'B2',
    'M', "M'", 'M2', 'E', "E'", 'S', "S'",
    'x', "x'", 'y', "y'", 'z', "z'", 'z2',
    'Rw', "Rw'", 'Uw', 'Fw', 'Lw', 'Dw', 'Bw',
    'r', "u'", 'f2',
)

# The same on a 5x5x5, where the layer notations mean something.
MOVES_5 = (
    'R', "R'", 'L', 'U', 'D', 'F', 'B', 'M', 'M2', 'E', 'S',
    'Rw', '3Rw', "3Rw'", '3-4Rw', '2R', '2U', '3Fw2', '2-3Lw',
    'x', 'y', "z'",
)


def turn_of(notation: str, size: int) -> Turn:
    """
    Build the turn of a move, refusing one that turns nothing.

    Args:
        notation: The move to read.
        size: Size of the cube.

    Returns:
        The turn of the move.

    Raises:
        AssertionError: When the move turns nothing at all.

    """
    turn = build_turn(parse_moves(notation)[0], size)

    if turn is None:
        msg = f'{ notation } turns nothing'
        raise AssertionError(msg)

    return turn


def facelet_after(rotation: Mat4, face: int) -> int:
    """
    Tell which way a side of a cubie ends up pointing after a turn.

    Args:
        rotation: The rotation the turn applies.
        face: Index of the side, in the order of ``FACE_ORDER``.

    Returns:
        The index of the face the side has come to face.

    Raises:
        AssertionError: When the side lands on no face at all, which no
            quarter turn of a cube can do.

    """
    turned = rotation.transform_direction(FACE_BASES[face].normal)

    for index, basis in enumerate(FACE_BASES):
        if all(
                abs(left - right) < TOLERANCE
                for left, right in zip(turned, basis.normal, strict=True)
        ):
            return index

    msg = f'Face { face } lands nowhere: { turned }'
    raise AssertionError(msg)


def placed(scene: Scene) -> dict[tuple[float, ...], CubieInstance]:
    """
    Index the instances of a scene by where they stand.

    Args:
        scene: The scene to index.

    Returns:
        Mapping of rounded positions to the instance standing there.

    """
    return {
        tuple(
            round(instance.model.rows()[axis][3], 5)
            for axis in range(3)
        ): instance
        for instance in scene.instances
    }


class TestTurns(unittest.TestCase):
    """Tests for the rotation a move applies."""

    def test_every_base_move_is_known(self) -> None:
        """Test that no notation is left without an axis."""
        for move in ('R', 'L', 'U', 'D', 'F', 'B', 'M', 'E', 'S'):
            self.assertIn(move, MOVE_TURNS)

        for move in ('x', 'y', 'z'):
            self.assertIn(move, MOVE_TURNS)

    def test_quarter_turn_of_a_clockwise_move(self) -> None:
        """Test that a plain move turns a quarter of a circle."""
        turn = turn_of('R', 3)

        self.assertEqual(turn.axis, 0)
        self.assertAlmostEqual(abs(turn.angle), QUARTER_TURN)

    def test_a_double_move_turns_twice_as_far(self) -> None:
        """Test that a double move goes half way round."""
        single = turn_of('U', 3)
        double = turn_of('U2', 3)

        self.assertAlmostEqual(double.angle, 2 * single.angle)

    def test_a_counter_clockwise_move_turns_the_other_way(self) -> None:
        """Test that the prime of a move is its opposite."""
        forward = turn_of('F', 3)
        backward = turn_of("F'", 3)

        self.assertAlmostEqual(backward.angle, -forward.angle)

    def test_a_pause_turns_nothing(self) -> None:
        """Test that a pause yields no turn at all."""
        self.assertIsNone(build_turn(parse_moves('.')[0], 3))

    def test_a_face_move_takes_its_outer_layer(self) -> None:
        """Test that a face move turns the layer of its own side."""
        self.assertEqual(turn_coordinates(parse_moves('R')[0], 5), {4})
        self.assertEqual(turn_coordinates(parse_moves('L')[0], 5), {0})
        self.assertEqual(turn_coordinates(parse_moves('U')[0], 5), {4})
        self.assertEqual(turn_coordinates(parse_moves('D')[0], 5), {0})
        self.assertEqual(turn_coordinates(parse_moves('F')[0], 5), {4})
        self.assertEqual(turn_coordinates(parse_moves('B')[0], 5), {0})

    def test_a_wide_move_takes_several_layers(self) -> None:
        """Test that the layers of a wide move are counted from its side."""
        self.assertEqual(turn_coordinates(parse_moves('Rw')[0], 5), {3, 4})
        self.assertEqual(turn_coordinates(parse_moves('3Rw')[0], 5), {2, 3, 4})
        self.assertEqual(turn_coordinates(parse_moves('3-4Rw')[0], 5), {1, 2})
        self.assertEqual(turn_coordinates(parse_moves('Lw')[0], 5), {0, 1})

    def test_a_layered_move_takes_one_inner_layer(self) -> None:
        """Test that a numbered move turns that layer alone."""
        self.assertEqual(turn_coordinates(parse_moves('2R')[0], 5), {3})
        self.assertEqual(turn_coordinates(parse_moves('2L')[0], 5), {1})

    def test_a_slice_move_takes_the_middle_layer(self) -> None:
        """Test that a slice turns the middle of the cube whatever its size."""
        for size in (3, 5, 7):
            self.assertEqual(
                turn_coordinates(parse_moves('M')[0], size),
                {size // 2},
            )

    def test_a_rotation_takes_the_whole_cube(self) -> None:
        """Test that a rotation leaves no cubie behind."""
        self.assertEqual(
            turn_coordinates(parse_moves('y')[0], 4),
            {0, 1, 2, 3},
        )

    def test_a_turn_carries_the_cubies_of_its_layers(self) -> None:
        """Test that a cubie is taken along only when its layer turns."""
        turn = Turn(axis=0, angle=QUARTER_TURN, coordinates=frozenset({2}))

        self.assertTrue(turn.carries(Cubie(2, 0, 1, Vec3(0.0, 0.0, 0.0))))
        self.assertFalse(turn.carries(Cubie(1, 2, 2, Vec3(0.0, 0.0, 0.0))))


class TestTurnDuration(unittest.TestCase):
    """Tests for the beat a turn is given, quarter turn or half turn."""

    def test_a_quarter_turn_lasts_the_plain_beat(self) -> None:
        """Test that a quarter turn is given the duration it is handed."""
        self.assertEqual(turn_of('R', 3).duration(1.0), 1.0)

    def test_turning_the_other_way_changes_nothing(self) -> None:
        """Test that the beat is read on the angle, not on its sign."""
        self.assertEqual(turn_of("R'", 3).duration(1.0), 1.0)

    def test_a_half_turn_lasts_longer(self) -> None:
        """Test that a half turn is given more time than a quarter one."""
        self.assertEqual(turn_of('R2', 3).duration(1.0), HALF_TURN_FACTOR)

    def test_a_half_slice_lasts_longer(self) -> None:
        """Test that the beat follows the angle, whatever the notation."""
        self.assertEqual(turn_of('M2', 3).duration(1.0), HALF_TURN_FACTOR)

    def test_a_half_rotation_lasts_longer(self) -> None:
        """Test that a whole cube turning twice takes the longer beat."""
        self.assertEqual(turn_of('z2', 3).duration(1.0), HALF_TURN_FACTOR)


class TestEase(unittest.TestCase):
    """Tests for the easing of a turn."""

    def test_the_ends_are_left_where_they_are(self) -> None:
        """Test that easing changes neither the start nor the end."""
        self.assertAlmostEqual(ease(0.0), 0.0)
        self.assertAlmostEqual(ease(1.0), 1.0)

    def test_the_middle_is_left_where_it_is(self) -> None:
        """Test that half way through a turn is half way round."""
        self.assertAlmostEqual(ease(0.5), 0.5)

    def test_the_turn_starts_and_ends_slowly(self) -> None:
        """Test that the first tenth covers less ground than the middle."""
        self.assertLess(ease(0.1), 0.1)
        self.assertGreater(ease(0.9), 0.9)

    def test_beyond_the_ends_nothing_moves(self) -> None:
        """Test that an out of range progress is clamped."""
        self.assertAlmostEqual(ease(-1.0), 0.0)
        self.assertAlmostEqual(ease(2.0), 1.0)


class TestTurnedScene(unittest.TestCase):
    """Tests for the scene a turn has reached."""

    def test_a_turn_starting_changes_nothing(self) -> None:
        """Test that a null progress leaves every cubie where it was."""
        scene = build_scene(VCube())
        turn = turn_of('R', 3)

        started = turned_scene(scene, turn, 0.0)

        for before, after in zip(
                scene.instances, started.instances, strict=True,
        ):
            for left, right in zip(
                    before.model.values, after.model.values, strict=True,
            ):
                self.assertAlmostEqual(left, right)

    def test_the_cubies_left_alone_are_the_very_same(self) -> None:
        """Test that an untouched instance is not even rebuilt."""
        scene = build_scene(VCube())
        turn = turn_of('R', 3)

        played = turned_scene(scene, turn, 1.0)

        for before, after in zip(
                scene.instances, played.instances, strict=True,
        ):
            if not turn.carries(before.cubie):
                self.assertIs(before, after)

    def test_the_colors_of_a_cubie_follow_it(self) -> None:
        """Test that a turn moves pieces around and never repaints them."""
        scene = build_scene(VCube())
        turn = turn_of('U', 3)

        played = turned_scene(scene, turn, 0.5)

        for before, after in zip(
                scene.instances, played.instances, strict=True,
        ):
            self.assertEqual(before.colors, after.colors)

    def test_the_geometry_is_shared_with_the_scene_it_comes_from(self) -> None:
        """Test that turning a scene uploads no new mesh."""
        scene = build_scene(VCube())
        turn = turn_of('U', 3)

        self.assertIs(turned_scene(scene, turn, 0.5).geometry, scene.geometry)


class TestTurnAgreement(unittest.TestCase):
    """
    Tests that a finished turn lands exactly where ``VCube`` says.

    The one property that matters, and the one that catches an axis, a
    direction or a layer read the wrong way round: once a move is over,
    every cubie of the scene must stand where the scene built from the
    cube after that move puts it, and show the same colors.
    """

    def check(self, notation: str, size: int, scramble: str = '') -> None:
        """
        Play one move to its end and compare with the cube it lands on.

        Args:
            notation: The move to play.
            size: Size of the cube.
            scramble: Moves applied before, to tell the facelets apart.

        """
        cube = VCube(size=size)
        if scramble:
            cube.rotate(scramble)

        move = parse_moves(notation)[0]
        turn = turn_of(notation, size)

        played = turned_scene(build_scene(cube), turn, 1.0)

        cube.rotate(move)
        expected = placed(build_scene(cube))
        rotation = turn.matrix(1.0)

        for position, instance in placed(played).items():
            self.assertIn(position, expected)

            for face in range(SIDE_NUMBER):
                landed = (
                    facelet_after(rotation, face)
                    if turn.carries(instance.cubie)
                    else face
                )

                self.assertEqual(
                    instance.colors[face],
                    expected[position].colors[landed],
                    f'{ notation } on { size }x{ size }x{ size } '
                    f'at { position }, face { face }',
                )

    def test_every_move_of_a_3x3x3(self) -> None:
        """Test that every notation of a 3x3x3 lands on the right state."""
        for notation in MOVES_3:
            with self.subTest(move=notation):
                self.check(notation, 3, SCRAMBLE_3)

    def test_every_move_of_a_5x5x5(self) -> None:
        """Test that the layer notations of a 5x5x5 turn the right slices."""
        for notation in MOVES_5:
            with self.subTest(move=notation):
                self.check(notation, 5, SCRAMBLE_5)

    def test_every_move_of_a_2x2x2(self) -> None:
        """Test that a cube with no middle layer animates too."""
        for notation in ('R', "U'", 'F2', 'L', 'D', 'B', 'x', 'y', "z'"):
            with self.subTest(move=notation):
                self.check(notation, 2)


class TestAnimation(unittest.TestCase):
    """Tests for the state machine playing an algorithm."""

    def test_a_move_needs_some_time_to_happen(self) -> None:
        """Test that a null duration is refused rather than divided by."""
        with self.assertRaises(ValueError):
            Animation(VCube(), 'R', duration=0.0)

    def test_the_cube_it_is_given_is_left_alone(self) -> None:
        """Test that playing an algorithm never touches the caller cube."""
        cube = VCube()
        animation = Animation(cube, "R U R' U'")

        list(animation.play())

        self.assertTrue(cube.is_solved)
        self.assertFalse(animation.cube.is_solved)

    def test_the_final_state_is_the_one_of_the_algorithm(self) -> None:
        """Test that an animation ends exactly where VCube would."""
        for algorithm, size in (
                ("R U R' U'", 3),
                ("R U R2 U' R' U' R' U R'", 3),
                ("Rw U 3Rw' M2 x", 5),
        ):
            with self.subTest(algorithm=algorithm):
                animation = Animation(VCube(size=size), algorithm)
                list(animation.play())

                expected = VCube(size=size)
                expected.rotate(parse_moves(algorithm))

                self.assertEqual(animation.cube.state, expected.state)

    def test_an_animation_starts_at_rest(self) -> None:
        """Test that the first scene is the cube before anything happens."""
        animation = Animation(VCube(), 'R')

        self.assertFalse(animation.finished)
        self.assertEqual(
            animation.scene.instances,
            build_scene(VCube(), geometry=animation.geometry).instances,
        )

    def test_the_move_under_way_is_named(self) -> None:
        """Test that the move being turned is readable from outside."""
        animation = Animation(VCube(), "R U'", duration=0.1)

        self.assertEqual(str(animation.move), 'R')

        animation.advance(0.15)

        self.assertEqual(str(animation.move), "U'")

    def test_a_finished_animation_turns_no_move(self) -> None:
        """Test that nothing is named once every move has landed."""
        animation = Animation(VCube(), 'R', duration=0.1)
        animation.advance(0.2)

        self.assertIsNone(animation.move)

    def test_a_pause_is_never_the_move_under_way(self) -> None:
        """Test that the move named is one that truly turns something."""
        animation = Animation(VCube(), '. R', duration=0.1)

        self.assertEqual(str(animation.move), 'R')

    def test_an_empty_algorithm_is_over_before_it_starts(self) -> None:
        """Test that nothing to play is finished right away."""
        animation = Animation(VCube(), '')

        self.assertTrue(animation.finished)
        self.assertEqual(len(list(animation.play())), 1)

    def test_a_pause_never_reaches_the_cube(self) -> None:
        """Test that a pause turns nothing, however long it holds."""
        animation = Animation(VCube(), '. .')
        animation.advance(3 * PAUSE_DURATION)

        self.assertTrue(animation.finished)
        self.assertTrue(animation.cube.is_solved)

    def test_time_running_backwards_is_ignored(self) -> None:
        """Test that a negative delta leaves the animation where it is."""
        animation = Animation(VCube(), 'R')
        animation.advance(-10.0)

        self.assertEqual(animation.elapsed, 0.0)
        self.assertFalse(animation.finished)

    def test_a_long_delta_lands_several_moves_at_once(self) -> None:
        """Test that an animation catches up rather than falling behind."""
        animation = Animation(VCube(), "R U R' U'", duration=0.1)
        animation.advance(1.0)

        expected = VCube()
        expected.rotate("R U R' U'")

        self.assertTrue(animation.finished)
        self.assertEqual(animation.cube.state, expected.state)

    def test_the_clock_is_reset_once_everything_has_landed(self) -> None:
        """Test that the leftover time of the last move is dropped."""
        animation = Animation(VCube(), 'R', duration=0.1)
        animation.advance(0.75)

        self.assertEqual(animation.elapsed, 0.0)

    def test_a_move_lands_only_once_it_is_over(self) -> None:
        """Test that the cube is left alone while a move is playing."""
        animation = Animation(VCube(), 'R', duration=MOVE_DURATION)
        animation.advance(MOVE_DURATION / 2)

        self.assertTrue(animation.cube.is_solved)
        self.assertFalse(animation.finished)

    def test_the_number_of_frames_follows_the_frame_rate(self) -> None:
        """Test that an animation is sampled at the rate it is asked for."""
        frames = len(list(Animation(VCube(), 'R U', duration=0.5).play(10.0)))

        self.assertEqual(frames, 1 + math.ceil(2 * 0.5 * 10.0))

    def test_a_frame_rate_must_be_positive(self) -> None:
        """Test that an animation cannot be sampled at no rate at all."""
        with self.assertRaises(ValueError):
            list(Animation(VCube(), 'R').play(0.0))

    def test_a_mode_is_resolved_once_and_for_all(self) -> None:
        """Test that the orientation of a mode does not jump between moves."""
        animation = Animation(VCube(), "U R U' R'", Presentation(mode='f2l'))
        scenes = list(animation.play())

        self.assertEqual(
            {len(scene.instances) for scene in scenes},
            {len(scenes[0].instances)},
        )

    def test_a_mode_dims_the_pieces_it_is_not_about(self) -> None:
        """Test that a mode reaches an animation as it reaches a render."""
        plain = Animation(VCube(), 'R')
        masked = Animation(VCube(), 'R', Presentation(mode='oll'))

        self.assertEqual(
            [instance.colors for instance in masked.scene.instances],
            [
                instance.colors
                for instance in build_scene(
                    VCube(), geometry=masked.geometry, mode='oll',
                ).instances
            ],
        )
        self.assertNotEqual(
            [instance.colors for instance in masked.scene.instances],
            [instance.colors for instance in plain.scene.instances],
        )

    def test_a_mask_drops_the_cubies_nobody_may_see(self) -> None:
        """Test that a hidden piece is left out of every frame."""
        animation = Animation(
            VCube(), 'R', Presentation(mask='3' * 9 + '1' * 45),
        )

        self.assertLess(
            len(animation.scene.instances),
            len(build_scene(VCube()).instances),
        )

    def test_a_mask_overrides_the_one_of_the_mode(self) -> None:
        """Test that a mask given by hand wins over the preset."""
        animation = Animation(
            VCube(), 'R', Presentation(mode='oll', mask='1' * 54),
        )

        self.assertEqual(
            [instance.colors for instance in animation.scene.instances],
            [
                instance.colors
                for instance in build_scene(
                    VCube(), geometry=animation.geometry,
                ).instances
            ],
        )

    def test_every_frame_shares_the_geometry_of_the_animation(self) -> None:
        """Test that no scene of an animation rebuilds the mesh."""
        animation = Animation(VCube(), "R U'")

        for scene in animation.play():
            self.assertIs(scene.geometry, animation.geometry)


class TestAnimationBeat(unittest.TestCase):
    """Tests for the time an animation gives each of its moves."""

    def test_a_half_turn_is_given_a_longer_beat(self) -> None:
        """Test that a half turn does not land on the beat of a quarter."""
        animation = Animation(VCube(), 'U2', duration=0.1)

        animation.advance(0.1)
        self.assertFalse(animation.finished)
        self.assertTrue(animation.cube.is_solved)

        animation.advance(0.1 * (HALF_TURN_FACTOR - 1.0))
        self.assertTrue(animation.finished)

    def test_a_half_turn_leaves_the_next_move_its_own_beat(self) -> None:
        """Test that every move of an algorithm is timed on its own angle."""
        animation = Animation(VCube(), 'U2 R', duration=0.1)

        animation.advance(0.1 * HALF_TURN_FACTOR)
        self.assertEqual(str(animation.move), 'R')
        self.assertFalse(animation.finished)

        animation.advance(0.1)
        self.assertTrue(animation.finished)

    def test_the_beat_of_a_finished_animation_is_the_plain_one(self) -> None:
        """Test that nothing left to turn falls back on the given duration."""
        animation = Animation(VCube(), '')

        self.assertEqual(animation.step, MOVE_DURATION)

    def test_a_half_turn_takes_more_frames_than_a_quarter(self) -> None:
        """Test that the longer beat reaches the frames a GIF is made of."""
        quarter = len(list(Animation(VCube(), 'U', duration=0.5).play(20.0)))
        half = len(list(Animation(VCube(), 'U2', duration=0.5).play(20.0)))

        self.assertGreater(half, quarter)

    def test_a_turn_is_the_only_thing_moving(self) -> None:
        """Test that the cubies away from the move stand perfectly still."""
        animation = Animation(VCube(), 'R', duration=1.0)
        resting = animation.scene
        turn = turn_of('R', 3)

        moving = animation.advance(0.5)

        for before, after in zip(
                resting.instances, moving.instances, strict=True,
        ):
            if not turn.carries(before.cubie):
                self.assertEqual(before.model.values, after.model.values)


class TestAnimationSchedule(unittest.TestCase):
    """Tests for the duration the dates of the moves give a turn."""

    def setUp(self) -> None:
        """Take an animation with nothing to play, and two turns."""
        self.animation = Animation(VCube(), '', duration=0.1)
        self.quarter = turn_of('R', 3)
        self.half = turn_of('U2', 3)

    def test_a_move_with_no_date_keeps_the_beat(self) -> None:
        """Test that an ordinary algorithm is cadenced by nothing else."""
        self.assertEqual(
            self.animation.schedule(self.quarter, None, 1.0), 0.1,
        )

    def test_a_move_with_nothing_behind_it_keeps_the_beat(self) -> None:
        """Test that the last move of a stream is played at the beat."""
        self.assertEqual(
            self.animation.schedule(self.quarter, 0.5, None), 0.1,
        )

    def test_a_shorter_gap_compresses_the_turn(self) -> None:
        """Test that a move made fast is played fast."""
        self.assertAlmostEqual(
            self.animation.schedule(self.quarter, 0.0, 0.08), 0.08,
        )

    def test_a_longer_gap_leaves_the_beat_alone(self) -> None:
        """Test that a slow hand never makes a turn drag: it rests."""
        self.assertEqual(
            self.animation.schedule(self.quarter, 0.0, 1.0), 0.1,
        )

    def test_a_half_turn_is_capped_on_its_own_beat(self) -> None:
        """Test that the longer beat of a half turn is the one capping it."""
        self.assertAlmostEqual(
            self.animation.schedule(self.half, 0.0, 1.0),
            0.1 * HALF_TURN_FACTOR,
        )

    def test_two_moves_sharing_a_date_fall_on_the_floor(self) -> None:
        """Test that a burst stamped all at once still reads as turns."""
        self.assertEqual(
            self.animation.schedule(self.quarter, 0.5, 0.5),
            MINIMUM_MOVE_DURATION,
        )


class TestAnimationRetime(unittest.TestCase):
    """Tests for the duration of a turn being revised under way."""

    def test_the_angle_does_not_move(self) -> None:
        """Test that shrinking a turn never makes the layer jump."""
        animation = Animation(VCube(), 'R', duration=0.2)
        animation.advance(0.05)
        turning = animation.scene

        animation.retime(0.12)

        self.assertAlmostEqual(animation.elapsed / animation.step, 0.25)
        self.assertEqual(animation.scene.instances, turning.instances)

    def test_a_turn_well_under_way_keeps_how_far_it_has_gone(self) -> None:
        """Test that a turn cut short is not sent back to its start."""
        animation = Animation(VCube(), 'R', duration=0.2)
        animation.advance(0.15)

        animation.retime(0.05)

        self.assertEqual(animation.step, 0.05)
        self.assertAlmostEqual(animation.elapsed / animation.step, 0.75)


class TestAnimationCadence(unittest.TestCase):
    """Tests for a queue of dated moves driving the animation."""

    def test_a_timed_algorithm_lands_on_the_cube(self) -> None:
        """Test that a timestamp never reaches VCube.rotate()."""
        animation = Animation(VCube(), 'R@100 U@250', duration=0.1)
        animation.advance(10.0)

        expected = VCube()
        expected.rotate('R U')

        self.assertTrue(animation.finished)
        self.assertEqual(animation.cube.state, expected.state)

    def test_an_algorithm_pushed_whole_carries_a_single_date(self) -> None:
        """Test that a batch is one entry, hence the nominal beat behind."""
        animation = Animation(VCube(), '', duration=0.1)
        animation.extend("R U R' U'", at=0.0)

        self.assertEqual(
            [date for _move, date in animation.pending],
            [0.0, None, None, None],
        )

    def test_a_timed_algorithm_is_anchored_on_its_first_move(self) -> None:
        """Test that an algorithm starting late does not open on nothing."""
        animation = Animation(VCube(), '', duration=0.1)
        animation.extend('R@12400 U@12500')

        self.assertEqual(
            [date for _move, date in animation.pending],
            [0.0, 0.1],
        )

    def test_a_timed_batch_is_anchored_on_its_arrival(self) -> None:
        """Test that the stamps of a batch are read against when it came."""
        animation = Animation(VCube(), '', duration=0.1)
        animation.extend('R@12400 U@12500', at=2.0)

        self.assertEqual(
            [date for _move, date in animation.pending],
            [2.0, 2.0 + 0.1],
        )

    def test_a_move_starts_when_it_arrives(self) -> None:
        """Test that a move pushed into an idle animation waits for nothing."""
        animation = Animation(VCube(), '', duration=0.28)
        animation.advance(0.5)

        animation.extend('R', at=animation.clock)
        animation.advance(0.1)

        self.assertFalse(animation.finished)

        animation.advance(0.2)

        self.assertTrue(animation.finished)

    def test_the_move_behind_revises_the_one_under_way(self) -> None:
        """Test that the cadence of a producer reaches the turn playing."""
        animation = Animation(VCube(), '', duration=0.28)
        animation.extend('R', at=0.0)
        animation.advance(0.02)

        self.assertEqual(animation.step, 0.28)

        animation.extend('U', at=0.1)

        self.assertAlmostEqual(animation.step, 0.1)
        self.assertAlmostEqual(animation.elapsed / animation.step, 0.02 / 0.28)

    def test_a_move_queued_behind_another_is_scheduled_on_it(self) -> None:
        """Test that a turn started with a successor already waiting."""
        animation = Animation(VCube(), '', duration=0.2)
        animation.extend('R', at=0.0)
        animation.extend('U', at=0.1)

        animation.advance(0.05)

        self.assertAlmostEqual(animation.step, 0.1)

    def test_a_rest_holds_the_very_same_scene(self) -> None:
        """Test that the cube stands still until the next move is due."""
        animation = Animation(VCube(), 'R@0 U@1000', duration=0.1)
        animation.advance(0.2)
        resting = animation.scene

        animation.advance(0.1)

        self.assertFalse(animation.finished)
        self.assertIsNone(animation.move)
        self.assertEqual(animation.scene.instances, resting.instances)

    def test_a_rest_is_played_frame_after_frame(self) -> None:
        """Test that the wait of a replay reaches the frames of a GIF."""
        timed = len(
            list(Animation(VCube(), 'R@0 U@1000', duration=0.1).play(25.0)),
        )
        tight = len(
            list(Animation(VCube(), 'R U', duration=0.1).play(25.0)),
        )

        self.assertGreater(timed, tight)

    def test_a_timed_algorithm_plays_at_the_cadence_of_its_stamps(
            self,
    ) -> None:
        """Test that the gap between two stamps is what a turn lasts."""
        animation = Animation(VCube(), 'R@0 U@120 F@240', duration=0.28)
        animation.advance(0.01)

        self.assertAlmostEqual(animation.step, 0.12)

    def test_without_a_date_the_cadence_is_the_nominal_one(self) -> None:
        """Test that an ordinary algorithm plays exactly as it always did."""
        animation = Animation(VCube(), "R U R' U'", duration=0.1)

        for _frame in range(3):
            animation.advance(0.1)

        self.assertEqual(str(animation.move), "U'")
        self.assertEqual(animation.step, 0.1)

    def test_a_pause_holds_a_dated_move_back(self) -> None:
        """Test that a move due before the pause is over waits for it."""
        animation = Animation(VCube(), '.@0 R@100', duration=0.1)
        animation.advance(0.2)

        expected = VCube()
        expected.rotate('R')

        self.assertFalse(animation.finished)
        self.assertTrue(animation.cube.is_solved)

        animation.advance(PAUSE_DURATION)

        self.assertTrue(animation.finished)
        self.assertEqual(animation.cube.state, expected.state)


class TestAnimationPause(unittest.TestCase):
    """Tests for the time a pause holds the cube still."""

    def test_a_pause_holds_the_cube_still_for_its_beat(self) -> None:
        """Test that what follows a pause waits a whole pause duration."""
        animation = Animation(VCube(), '. R', duration=0.1)
        animation.advance(PAUSE_DURATION / 2)

        self.assertTrue(animation.cube.is_solved)
        self.assertFalse(animation.finished)

        animation.advance(PAUSE_DURATION)

        self.assertFalse(animation.cube.is_solved)

    def test_a_pause_leaves_the_scene_untouched(self) -> None:
        """Test that the move waiting behind a pause has not started."""
        animation = Animation(VCube(), '. R', duration=0.1)
        animation.advance(PAUSE_DURATION / 2)

        self.assertIs(animation.scene, animation.resting)

    def test_a_pause_closing_an_algorithm_is_not_the_end(self) -> None:
        """Test that a trailing pause is played rather than dropped."""
        animation = Animation(VCube(), 'R .', duration=0.1)
        animation.advance(0.2)

        self.assertFalse(animation.finished)

        animation.advance(PAUSE_DURATION)

        self.assertTrue(animation.finished)

    def test_pauses_add_up(self) -> None:
        """Test that two pauses hold twice as long as one."""
        animation = Animation(VCube(), '. . R', duration=0.1)
        animation.advance(1.5 * PAUSE_DURATION)

        self.assertTrue(animation.cube.is_solved)

        animation.advance(PAUSE_DURATION)

        self.assertFalse(animation.cube.is_solved)

    def test_a_rest_longer_than_a_pause_wins(self) -> None:
        """Test that a pause never shortens a rest the dates carry."""
        held = 3 * PAUSE_DURATION
        stamp = int(held * MILLISECONDS)
        animation = Animation(VCube(), f'.@0 R@{ stamp }', duration=0.1)
        animation.advance(2 * PAUSE_DURATION)

        self.assertTrue(animation.cube.is_solved)

        animation.advance(held)

        self.assertFalse(animation.cube.is_solved)

    def test_a_pause_is_drawn_as_a_rest(self) -> None:
        """Test that the frames of a pause reach a played animation."""
        without = len(list(Animation(VCube(), 'R', duration=0.1).play()))
        within = len(list(Animation(VCube(), 'R . R', duration=0.1).play()))

        self.assertGreater(within - without, PAUSE_DURATION * FRAME_RATE)


class TestTurnMatrix(unittest.TestCase):
    """Tests for the matrix a turn has reached."""

    def test_a_turn_starting_is_the_identity(self) -> None:
        """Test that nothing has happened yet at a null progress."""
        turn = Turn(axis=1, angle=QUARTER_TURN, coordinates=frozenset({0}))

        for value, expected in zip(
                turn.matrix(0.0).values,
                Mat4.identity().values,
                strict=True,
        ):
            self.assertAlmostEqual(value, expected)

    def test_each_axis_builds_its_own_rotation(self) -> None:
        """Test that the axis of a turn picks the right rotation matrix."""
        builders = (Mat4.rotation_x, Mat4.rotation_y, Mat4.rotation_z)

        for axis, builder in enumerate(builders):
            turn = Turn(
                axis=axis,
                angle=math.pi,
                coordinates=frozenset({0}),
            )

            for value, expected in zip(
                    turn.matrix(0.5).values,
                    builder(math.pi / 2).values,
                    strict=True,
            ):
                self.assertAlmostEqual(value, expected)
