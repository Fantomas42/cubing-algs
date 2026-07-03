"""Common speedcubing trigger patterns and match results."""
from enum import Enum
from typing import NamedTuple


class VariationKind(Enum):
    """
    Kind of a trigger variation relative to its canonical form.

    LEFTY: mirror across the M slice, executed with the left hand.
    INVERSE: mirror across the S slice staying on comfortable faces.
    BACK: variation involving the B face, noticeably slower to execute.
    """

    LEFTY = 'lefty'
    INVERSE = 'inverse'
    BACK = 'back'


class TriggerVariation(NamedTuple):
    """A variation of a trigger pattern with its execution kind."""

    moves: str
    kind: VariationKind


class TriggerPattern(NamedTuple):
    """
    Represents a common speedcubing trigger or pattern.

    Triggers are familiar move sequences that speedcubers can execute
    efficiently due to muscle memory and ergonomic flow.

    Variations are mirror algorithms across M or S slices,
    for lefty, inverse or back versions.
    """

    name: str
    moves: str
    category: str
    ergonomic_bonus: float
    speed_multiplier: float
    variations: list[TriggerVariation]
    aliases: list[str]
    description: str


class TriggerMatch(NamedTuple):
    """Represents a detected trigger pattern in an algorithm."""

    pattern: TriggerPattern
    start_index: int
    end_index: int
    matched_moves: str
    variation: TriggerVariation | None = None  # None = canonical form

    @property
    def length(self) -> int:
        """Number of moves covered by the match."""
        return self.end_index - self.start_index + 1


TV = TriggerVariation
VK = VariationKind

TRIGGER_PATTERNS = [
    # Basic triggers (highest priority)
    TriggerPattern(
        name='Sexy Move',
        moves="R U R' U'",
        category='basic',
        ergonomic_bonus=0.17,
        speed_multiplier=1.95,
        variations=[
            TV("L' U' L U", VK.LEFTY),
            TV("R' U' R U", VK.INVERSE),
            TV("L U L' U'", VK.LEFTY),
        ],
        aliases=['Cool Move', 'Sexy'],
        description=(
            'Pure commutator [R, U]. Cycles 4 corners (2 swaps) and 3 edges'
            ' (one 3-cycle) with no orientation changes. Repeating 6 times'
            ' returns to solved. The single most common trigger in CFOP,'
            ' appearing in dozens of OLL and PLL algorithms.'
        ),
    ),
    TriggerPattern(
        name='Sledgehammer',
        moves="R' F R F'",
        category='basic',
        ergonomic_bonus=0.00,
        speed_multiplier=0.97,
        variations=[
            TV("L F' L' F", VK.LEFTY),
            TV("R B' R' B", VK.BACK),
            TV("L' B L B'", VK.BACK),
        ],
        aliases=['Sledge', 'Hammer'],
        description=(
            "Commutator [R', F]. Cycles 4 corners (2 swaps with twists)"
            ' and 3 edges (one 3-cycle with 2 flips) in the FR/UF slot area.'
            ' Commonly used in F2L to extract a piece from the FR slot'
            ' without disturbing the rest of the first two layers.'
        ),
    ),
    TriggerPattern(
        name='Hedgeslammer',
        moves="F R' F' R",
        category='basic',
        ergonomic_bonus=0.00,
        speed_multiplier=0.85,
        variations=[
            TV("F' L F L'", VK.LEFTY),
            TV("B' R B R'", VK.BACK),
            TV("B L' B' L", VK.BACK),
        ],
        aliases=['Hedge', 'Slammer'],
        description=(
            "Commutator [F, R']. Same piece set as Sledgehammer (4 corners,"
            ' 3 edges) but with reversed corner twist directions. Often'
            ' appears adjacent to Sledgehammer in OLL algorithms; the two'
            ' triggers together cancel many orientation changes.'
        ),
    ),
    TriggerPattern(
        name='Sune Trigger',
        moves="R U R' U",
        category='basic',
        ergonomic_bonus=0.03,
        speed_multiplier=1.10,
        variations=[
            TV("L' U' L U'", VK.LEFTY),
        ],
        aliases=['Su', 'Half Sune', 'Semi-Sexy', 'Homely'],
        description=(
            'First half of the Sune algorithm. Moves 5 corners and 5 edges'
            ' in 5-cycles with no orientation changes, leaving the cube in'
            ' an unsolved intermediate state. Recognized by the double U'
            ' turns when combined with its complement to complete Sune.'
        ),
    ),
    TriggerPattern(
        name='Sane Trigger',
        moves="R U' R' U'",
        category='basic',
        ergonomic_bonus=0.07,
        speed_multiplier=1.27,
        variations=[
            TV("L' U L U", VK.LEFTY),
        ],
        aliases=['Sa', 'Half Sane', 'Su backwark'],
        description=(
            "U' mirror of Sune Trigger. Moves 5 corners and 5 edges "
            'in 5-cycles with no orientation changes. Appears in OLL, '
            'and various ZZ last-layer algorithms.'
        ),
    ),
    TriggerPattern(
        name='T-Perm Trigger',
        moves="R U R' F'",
        category='basic',
        ergonomic_bonus=0.04,
        speed_multiplier=1.15,
        variations=[
            TV("L' U' L F", VK.LEFTY),
        ],
        aliases=['T-Trigger', 'T Setup'],
        description=(
            "Opening setup of the T-Perm (PLL). The F' turn at the end"
            ' connects R-face and F-face manipulation, creating the'
            ' precondition for the subsequent Sexy Move that completes'
            ' the corner 3-cycle and edge swap of the full T-Perm.'
        ),
    ),

    # Compound triggers
    TriggerPattern(
        name='Sexy + Sledge',
        moves="R U R' U' R' F R F'",
        category='compound',
        ergonomic_bonus=0.11,
        speed_multiplier=1.45,
        variations=[
            TV("L' U' L U L F' L' F", VK.LEFTY),
        ],
        aliases=['Sexy Sledge', 'OLL 33'],
        description=(
            'OLL 33: Sexy Move followed by Sledgehammer. The combination'
            ' produces a pure 3-cycle of 3 corners (with orientation changes)'
            ' and a 3-cycle of 3 edges (with 2 flips), leaving the rest of'
            ' the cube untouched. One of the most ergonomic OLL algorithms.'
        ),
    ),
    TriggerPattern(
        name='Double Sexy',
        moves="R U R' U' R U R' U'",
        category='compound',
        ergonomic_bonus=0.12,
        speed_multiplier=1.54,
        variations=[
            TV("L' U' L U L' U' L U", VK.LEFTY),
        ],
        aliases=['Double Cool', 'Sexy Sexy'],
        description=(
            'Two consecutive Sexy Moves. Leaves all 8 corners in their'
            ' original positions but twists 4 of them (net corner orientation'
            ' change only), while cycling 3 edges. Used as an OLL sub-case'
            ' recognition anchor and in intuitive corner orientation.'
        ),
    ),
    TriggerPattern(
        name='Triple Sexy',
        moves="R U R' U' R U R' U' R U R' U'",
        category='compound',
        ergonomic_bonus=0.16,
        speed_multiplier=1.88,
        variations=[
            TV("L' U' L U L' U' L U L' U' L U", VK.LEFTY),
        ],
        aliases=['Triple Cool', 'Sexy Sexy Sexy'],
        description=(
            'Three consecutive Sexy Moves. Produces a pure corner permutation:'
            ' 4 corners swap (2 two-cycles) with no orientation changes and'
            ' all edges return to their original positions. Rarely used'
            ' directly but illustrates the order-6 nature of the Sexy Move.'
        ),
    ),
    TriggerPattern(
        name='Sune',
        moves="R U R' U R U2 R'",  # Orient 3 corners
        category='OLL',
        ergonomic_bonus=0.14,
        speed_multiplier=1.3,
        variations=[
            TV("L' U' L U' L' U2 L", VK.LEFTY),
        ],
        aliases=['Anti-Chair', 'Anti-Chaise', 'OLL 27', 'OCLL 2'],
        description=(
            'OLL 27 / OCLL 2. Orients 3 last-layer corners while cycling'
            ' 4 corners (2 swaps with net twist sum of +3 mod 3) and 3 edges.'
            ' A fundamental CFOP building block: every last-layer corner'
            ' orientation case can be solved with at most two Sune/Anti-Sune'
            ' executions.'
        ),
    ),
    TriggerPattern(
        name='Anti-Sune',  # Chair
        moves="R U2 R' U' R U' R'",  # Orient 3 corners
        category='OLL',
        ergonomic_bonus=0.13,
        speed_multiplier=1.61,
        variations=[
            TV("L' U2 L U L' U L", VK.LEFTY),
        ],
        aliases=['Chair', 'Chaise', 'OLL 26', 'OCLL 3'],
        description=(
            'OLL 26 / OCLL 3. Inverse orientation effect of Sune: orients'
            ' 3 last-layer corners in the opposite twist direction (net -3'
            ' mod 3). Same piece count as Sune (4 corners, 3 edges) but'
            " undoes Sune's corner orientation when applied to the same state."
        ),
    ),
    TriggerPattern(
        name='Niklas',
        moves="R U' L' U R' U' L",   # Permute 3 corners but also reorient
        category='advanced',
        ergonomic_bonus=0.16,
        speed_multiplier=1.35,
        variations=[
            TV("L' U R U' L U R'", VK.LEFTY),
        ],
        aliases=['3-Corner Cycle'],
        description=(
            "Interleaved commutator [R U' R', L']. Cycles 4 corners in a"
            ' 4-cycle and 4 edges in a 4-cycle (odd parity), making it'
            ' self-inverse only when repeated twice. Used for intuitive'
            ' 3-corner cycles in BLD solving and advanced F2L edge insertions.'
        ),
    ),

    # Setup patterns
    TriggerPattern(
        name='Slot Extract',
        moves="R U R'",
        category='setup',
        ergonomic_bonus=0.16,
        speed_multiplier=1.87,
        variations=[
            TV("L' U' L", VK.LEFTY),
            TV("R' U' R", VK.INVERSE),
            TV("L U L'", VK.LEFTY),
        ],
        aliases=['Pull', 'Extract', 'Pick Up'],
        description=(
            'Pulls the FR slot corner-edge pair up into the U layer. Moves'
            ' 4 corners and 4 edges in 4-cycles (odd parity), so the cube'
            ' is not in a valid solved-layers state until completed with'
            ' a matching insert. The canonical F2L setup move.'
        ),
    ),
    TriggerPattern(
        name='Slot Insert',
        moves="R U' R'",
        category='setup',
        ergonomic_bonus=0.11,
        speed_multiplier=1.47,
        variations=[
            TV("L' U L", VK.LEFTY),
            TV("R' U R", VK.INVERSE),
            TV("L U' L'", VK.LEFTY),
        ],
        aliases=['Push', 'Insert', 'Put Down'],
        description=(
            'Inverse of Slot Extract: inserts a U-layer piece into the FR'
            ' slot. Moves 4 corners and 4 edges in 4-cycles (odd parity).'
            ' Combined with a U turn to align the piece, this is the'
            ' standard F2L pair insertion move.'
        ),
    ),
    TriggerPattern(
        name='Slot Extended',
        moves="R U2 R'",
        category='setup',
        ergonomic_bonus=0.00,
        speed_multiplier=0.87,
        variations=[
            TV("L' U2 L", VK.LEFTY),
            TV("R' U2 R", VK.INVERSE),
            TV("L U2 L'", VK.LEFTY),
        ],
        aliases=['Ne', 'Super', 'Double Extract', 'Long Pull'],
        description=(
            'Double-turn slot manipulation. Swaps 4 corners (2 two-cycles)'
            ' and 2 edge pairs (2 two-cycles) with no orientation changes,'
            ' making it self-inverse. Used in F2L when the slot piece needs'
            ' to be rotated 180° before reinsertion.'
        ),
    ),

    # Wide move patterns
    TriggerPattern(
        name='Wide Sexy',
        moves="r U r' U'",
        category='wide',
        ergonomic_bonus=0.12,
        speed_multiplier=1.2,
        variations=[
            TV("l' U' l U", VK.LEFTY),
            TV("r' U' r U", VK.INVERSE),
            TV("l U l' U'", VK.LEFTY),
        ],
        aliases=['Wide Cool', 'Fat Sexy'],
        description=(
            'Wide-move variant of the Sexy Move. Moves the same 4 corners'
            ' (2 swaps) as the regular Sexy Move but also cycles 6 edges'
            ' across two independent 3-cycles, including the M-slice edges.'
            ' Essential in CMLL, OLLCP, and last-layer methods that exploit'
            ' M-slice manipulation.'
        ),
    ),
]
