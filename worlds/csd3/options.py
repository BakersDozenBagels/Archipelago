from dataclasses import dataclass
from Options import Choice, FreeText, PerGameCommonOptions, Range


class TerritoryOrder(Choice):
    """
    How to lock territories:

    - freeform = All territories are available from the start.
    - linear = Beating the last day in a territory unlocks the next one.
    - linear_shuffled = Beating the last day in a territory unlocks a random one.
    - randomized = Territory access is an item to be found. Consider starting with one as a starting_item
    """

    option_freeform = 0
    option_linear = 1
    option_linear_shuffled = 2
    option_randomized = 3


class SkipAmount(Range):
    """How many day skips should be in the pool?"""

    range_end = 50
    default = 20


class GoalLocation(FreeText):
    """Which day is your goal?"""

    default = "ICS, TN: Route J Day 3"

    def __init__(self, value: str):
        from .locations import territories

        assert any(
            any(d.name == value for d in x.days) for x in territories
        ), f"Invalid Goal Location: {value}"
        super().__init__(value)


@dataclass
class CookServeDelicious3Options(PerGameCommonOptions):
    territory_order: TerritoryOrder
    skip_amount: SkipAmount
    goal_location: GoalLocation
