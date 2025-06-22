import pkgutil
from typing import Callable

import orjson
from BaseClasses import CollectionState, Location
from . import items


location_name_to_id: dict[str, int] = {}


class Day:
    min_points = 0

    def __init__(self, name: str, region: str, id: int, obj: dict):
        self.name = name
        self.region = region
        self.id = id

        location_name_to_id[id] = name

        modifiers = [int(x) for x in [obj["a"], obj["b"], obj["c"]] if x]
        assert (
            len(modifiers) > 0
        ), "All routes should have at least one menu restriction."
        if modifiers[0] < 0:
            self.min_points = -modifiers[0] - 100
            modifiers = modifiers[1:]
            assert (
                len(modifiers) > 0
            ), "Routes with a score requirement should have a menu restriction."

        self.menu: set[items.Food] = set()
        for modifier in modifiers:
            self.menu |= items.food_group_id_to_food_group[modifier].contents

        self.min_prep = obj["minprep"]

        slot = obj["slot"]
        self.so = int(slot[0])
        self.hs = int(slot[1]) + int(slot[3])

    def __repr__(self):
        return f"Day({self.name} ({self.id}) = {{min_points:{self.min_points}, min_prep:{self.min_prep}, so:{self.so}, hs:{self.hs}, menu:{self.menu}}})"

    def _max_points(self, hs: bool, player: int, state: CollectionState):
        count = 0
        sum = 0
        for x in self.menu:
            if x.HS == hs and state.has(x.name, player):
                count += 1
                sum += x.difficulty
        return -1 if count < (self.hs if hs else self.so) else sum

    def is_beatable_for(self, player: int) -> Callable[[CollectionState], bool]:
        def beatable(state: CollectionState):
            extra = state.count("Extra Prep Station", player)
            if extra < self.min_prep:
                return False

            hs = self._max_points(True, player, state)
            if hs == -1:
                return False

            ps = self._max_points(False, player, state)
            if ps == -1:
                return False

            return hs + ps + extra >= self.min_points

        return beatable


class Territory:
    def __init__(self, obj: dict, index: int):
        self.name = obj["shortname"]
        self.days: list[Day] = []
        for route_no, route in enumerate(obj["routes"], 1):
            for day_no, day in enumerate(route["days"], 1):
                d = Day(
                    f"{self.name}: Route {chr(64 + route_no)} Day {day_no}",
                    self.name,
                    10000 * index + 100 * route_no + day_no,
                    day,
                )
                self.days.append(d)

    def __repr__(self):
        return f"Territory({self.name} = {self.days})"


territories: list[Territory] = [
    Territory(o, i) for i, o in enumerate(orjson.loads(pkgutil.get_data(__name__, "data/routes.json")), 1)
]


class CookServeDelicious3Location(Location):
    game = "Cook, Serve, Delicious! 3?!"

    def __init__(self, player, day: Day, parent=None):
        super().__init__(player, day.name, day.id, parent)
        self.day = day
        self.access_rule = day.is_beatable_for(player)
