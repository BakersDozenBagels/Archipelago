from typing import Any
from BaseClasses import ItemClassification, Location, Region
from Utils import visualize_regions
from entrance_rando import disconnect_entrance_for_randomization, randomize_entrances
from worlds.AutoWorld import World

from .items import CookServeDelicious3Item, item_name_to_id, item_name_to_classification
from .locations import CookServeDelicious3Location, Territory, location_name_to_id
from .options import CookServeDelicious3Options
from . import items, locations, options


class CookServeDelicious3World(World):
    game = "Cook, Serve, Delicious! 3?!"
    options_dataclass = CookServeDelicious3Options
    options: CookServeDelicious3Options

    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id

    def create_item(self, name: str, classification: ItemClassification | None = None):
        if classification == None:
            classification = item_name_to_classification[name]
        if callable(classification):
            classification = classification(self.options)
        return CookServeDelicious3Item(
            name, classification, self.item_name_to_id[name], self.player
        )

    def create_event(self, name: str):
        return CookServeDelicious3Item(
            name, ItemClassification.progression, None, self.player
        )

    def generate_early(self):
        self.territory_order = self.options.territory_order

    def create_regions(self):
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)

        prev_region: Region = menu_region
        prev: Territory | None = None
        for territory in locations.territories:
            region = Region(territory.name, self.player, self.multiworld)
            self.multiworld.regions.append(region)
            region.locations = [
                CookServeDelicious3Location(self.player, day, region)
                for day in territory.days
            ]
            if self.territory_order == options.TerritoryOrder.option_freeform:
                menu_region.connect(region)
            elif (
                self.territory_order == options.TerritoryOrder.option_linear
                or self.territory_order == options.TerritoryOrder.option_linear_shuffled
            ):
                if not prev:
                    entrance = prev_region.connect(region)
                else:
                    entrance = prev_region.connect(
                        region,
                        f"Beat {territory.days[-1].name}",
                        prev.days[-1].is_beatable_for(self.player),
                    )
                if (
                    self.territory_order
                    == options.TerritoryOrder.option_linear_shuffled
                ):
                    disconnect_entrance_for_randomization(
                        entrance, None, f"Access to {territory.name}"
                    )
                prev_region = region
                prev = territory
            elif self.territory_order == options.TerritoryOrder.option_randomized:
                menu_region.connect(
                    region,
                    None,
                    lambda state: state.has(f"Access to {territory.name}", self.player),
                )
            else:
                raise NotImplemented

        win_loc: CookServeDelicious3Location = self.multiworld.get_location(
            self.options.goal_location.value, self.player
        )
        win_region = self.get_region(win_loc.day.region)
        loc = Location(
            self.player, f"Complete {self.options.goal_location.value}", None, win_region
        )
        loc.access_rule = win_loc.access_rule
        win_region.locations.append(loc)
        loc.place_locked_item(self.create_event("Victory"))

        self.multiworld.completion_condition[self.player] = lambda state: state.has(
            "Victory", self.player
        )

    def connect_entrances(self):
        if self.territory_order == options.TerritoryOrder.option_linear_shuffled:
            randomize_entrances(self, False, {0: [0]})
        # print("========================================")
        # visualize_regions(self.get_region("Menu"), "my_world.puml")

    def create_items(self):
        self.multiworld.itempool += [
            self.create_item(x.name) for x in items.foods if x.difficulty != 0
        ]
        for x in items.progressive_items:
            self.multiworld.itempool += [self.create_item(x[0]) for _ in range(x[2])]

        for x in items.foods:
            if x.difficulty == 0:
                item = self.create_item(x.name)
                # self.multiworld.itempool += [item]
                self.multiworld.push_precollected(item)

        extra = 0

        if self.territory_order == options.TerritoryOrder.option_randomized:
            for territory in locations.territories:
                self.multiworld.itempool += [
                    self.create_item(f"Access to {territory.name}")
                ]
            extra = len(locations.territories)

        self.multiworld.itempool += [
            self.create_item("Day Skip") for _ in range(self.options.skip_amount)
        ]
        extra += self.options.skip_amount

        junk = (
            len(location_name_to_id)
            - len(items.foods)
            - sum(x[2] for x in items.progressive_items)
            + len([x for x in items.foods if x.difficulty == 0])
            - extra
        )
        self.multiworld.itempool += [
            self.create_item("Cook a meal IRL!", ItemClassification.filler)
            for _ in range(junk)
        ]

    def fill_slot_data(self) -> dict[str, Any]:
        return {
            "territory_access": (
                "item"
                if self.territory_order == options.TerritoryOrder.option_randomized
                else (
                    "freeform"
                    if self.territory_order == options.TerritoryOrder.option_freeform
                    else "region"
                )
            )
        }
