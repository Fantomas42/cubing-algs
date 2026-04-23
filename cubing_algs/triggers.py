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
    ),
    TriggerPattern(
        name='Sune Trigger',
        moves="R U R' U",
        category='basic',
        ergonomic_bonus=0.10,
        speed_multiplier=1.2,
        variations=["L U L' U", "L U' L' U'"],
    ),
    TriggerPattern(
        name='Anti-Sune Trigger',
        moves="R U' R' U'",
        category='basic',
        ergonomic_bonus=0.10,
        speed_multiplier=1.2,
        variations=["L U' L' U'"],
    ),

    # Compound triggers
    TriggerPattern(
        name='Sexy + Sledge',
        moves="R U R' U' R' F R F'",
        category='compound',
        ergonomic_bonus=0.18,
        speed_multiplier=1.4,
        variations=["L U L' U' L' F L F'"],
    ),
    TriggerPattern(
        name='Double Sexy',
        moves="R U R' U' R U R' U'",
        category='compound',
        ergonomic_bonus=0.20,
        speed_multiplier=1.45,
        variations=["L U L' U' L U L' U'"],
    ),
    TriggerPattern(
        name='Sune',  # Anti-Chair
        moves="R U R' U R U2 R'",
        category='OLL',
        ergonomic_bonus=0.14,
        speed_multiplier=1.3,
        variations=[
            "L' U' L U' L' U2 L",
        ],
    ),
    TriggerPattern(
        name='Anti-Sune',  # Chair
        moves="R U2 R' U' R U' R'",
        category='OLL',
        ergonomic_bonus=0.14,
        speed_multiplier=1.3,
        variations=[
            "L' U2 L U L' U L",
        ],
    ),
    TriggerPattern(
        name='T-Perm Trigger',
        moves="R U R' F'",
        category='basic',
        ergonomic_bonus=0.08,
        speed_multiplier=1.15,
        variations=["L U L' F"],
    ),
    TriggerPattern(
        name='Niklas',
        moves="R U' L' U R' U' L U",
        category='advanced',
        ergonomic_bonus=0.16,
        speed_multiplier=1.35,
        variations=["L U' R' U L' U' R U"],
    ),

    # Setup patterns
    TriggerPattern(
        name='Right Insert',
        moves="R U R'",
        category='setup',
        ergonomic_bonus=0.06,
        speed_multiplier=1.1,
        variations=["L U L'", "R U' R'", "L U' L'"],
    ),
    TriggerPattern(
        name='Extended Insert',
        moves="R U2 R'",
        category='setup',
        ergonomic_bonus=0.05,
        speed_multiplier=1.05,
        variations=["L U2 L'"],
    ),

    # Wide move patterns
    TriggerPattern(
        name='Wide Sexy',
        moves="r U r' U'",
        category='wide',
        ergonomic_bonus=0.12,
        speed_multiplier=1.2,
        variations=["l U l' U'", "r U' r' U"],
    ),
]
