"""Common speedcubing trigger patterns and match results."""
from typing import NamedTuple


class TriggerPattern(NamedTuple):
    """
    Represents a common speedcubing trigger or pattern.

    Triggers are familiar move sequences that speedcubers can execute
    efficiently due to muscle memory and ergonomic flow.

    Variations are mirror algorithùs across M or S slices,
    for lefty or back versions.
    """

    name: str
    moves: str
    category: str
    ergonomic_bonus: float
    speed_multiplier: float
    variations: list[str]
    aliases: list[str]


class TriggerMatch(NamedTuple):
    """Represents a detected trigger pattern in an algorithm."""

    pattern: TriggerPattern
    start_index: int
    end_index: int
    matched_moves: str


TRIGGER_PATTERNS = [
    # Basic triggers (highest priority)
    TriggerPattern(
        name='Sexy Move',
        moves="R U R' U'",
        category='basic',
        ergonomic_bonus=0.15,
        speed_multiplier=1.3,
        variations=[
            "L' U' L U",
            "R' U' R U",
            "L U L' U'",
        ],
        aliases=['Cool Move', 'Sexy'],
    ),
    TriggerPattern(
        name='Sledgehammer',
        moves="R' F R F'",
        category='basic',
        ergonomic_bonus=0.12,
        speed_multiplier=1.25,
        variations=[
            "L F' L' F",
            "R B' R' B",
            "L' B L B'",
        ],
        aliases=['Sledge', 'Hammer'],
    ),
    TriggerPattern(
        name='Sune Trigger',
        moves="R U R' U",
        category='basic',
        ergonomic_bonus=0.10,
        speed_multiplier=1.2,
        variations=[
            "L' U' L U'",
        ],
        aliases=['Half Sune', 'Semi-Sexy', 'Homely'],
    ),
    TriggerPattern(
        name='T-Perm Trigger',
        moves="R U R' F'",
        category='basic',
        ergonomic_bonus=0.08,
        speed_multiplier=1.15,
        variations=[
            "L' U' L F",
        ],
        aliases=['T-Trigger', 'T Setup'],
    ),

    # Compound triggers
    TriggerPattern(
        name='Sexy + Sledge',
        moves="R U R' U' R' F R F'",
        category='compound',
        ergonomic_bonus=0.18,
        speed_multiplier=1.4,
        variations=[
            "L' U' L U L F' L' F",
        ],
        aliases=['Sexy Sledge', 'OLL 33'],
    ),
    TriggerPattern(
        name='Double Sexy',
        moves="R U R' U' R U R' U'",
        category='compound',
        ergonomic_bonus=0.20,
        speed_multiplier=1.45,
        variations=[
            "L' U' L U L' U' L U",
        ],
        aliases=['Double Cool', 'Sexy Sexy'],
    ),
    TriggerPattern(
        name='Triple Sexy',
        moves="R U R' U' R U R' U' R U R' U'",
        category='compound',
        ergonomic_bonus=0.20,
        speed_multiplier=1.55,
        variations=[
            "L' U' L U L' U' L U L' U' L U",
        ],
        aliases=['Triple Cool', 'Sexy Sexy Sexy'],
    ),
    TriggerPattern(
        name='Sune',
        moves="R U R' U R U2 R'",  # Orient 3 corners
        category='OLL',
        ergonomic_bonus=0.14,
        speed_multiplier=1.3,
        variations=[
            "L' U' L U' L' U2 L",
        ],
        aliases=['Anti-Chair', 'Anti-Chaise', 'OLL 27', 'OCLL 2'],
    ),
    TriggerPattern(
        name='Anti-Sune',  # Chair
        moves="R U2 R' U' R U' R'",  # Orient 3 corners
        category='OLL',
        ergonomic_bonus=0.14,
        speed_multiplier=1.3,
        variations=[
            "L' U2 L U L' U L",
        ],
        aliases=['Chair', 'Chaise', 'OLL 26', 'OCLL 3'],
    ),
    TriggerPattern(
        name='Niklas',
        moves="R U' L' U R' U' L",   # Permute 3 corners but also reorient
        category='advanced',
        ergonomic_bonus=0.16,
        speed_multiplier=1.35,
        variations=[
            "L' U R U' L U R'",
        ],
        aliases=['3-Corner Cycle'],
    ),

    # Setup patterns
    TriggerPattern(
        name='Slot Extract',
        moves="R U R'",
        category='setup',
        ergonomic_bonus=0.06,
        speed_multiplier=1.1,
        variations=[
            "L' U' L",
            "R' U' R",
            "L U L'",
        ],
        aliases=['Pull', 'Extract', 'Pick Up'],
    ),
    TriggerPattern(
        name='Slot Insert',
        moves="R U' R'",
        category='setup',
        ergonomic_bonus=0.06,
        speed_multiplier=1.1,
        variations=[
            "L' U L",
            "R' U R",
            "L U' L'",
        ],
        aliases=['Push', 'Insert', 'Put Down'],
    ),
    TriggerPattern(
        name='Slot Extended',
        moves="R U2 R'",
        category='setup',
        ergonomic_bonus=0.05,
        speed_multiplier=1.05,
        variations=[
            "L' U2 L",
            "R' U2 R",
            "L U2 L'",
        ],
        aliases=['Super', 'Double Extract', 'Long Pull'],
    ),

    # Wide move patterns
    TriggerPattern(
        name='Wide Sexy',
        moves="r U r' U'",
        category='wide',
        ergonomic_bonus=0.12,
        speed_multiplier=1.2,
        variations=[
            "l' U' l U",
            "r' U' r U",
            "l U l' U'",
        ],
        aliases=['Wide Cool', 'Fat Sexy'],
    ),
]
