import csv
from io import StringIO
import pkgutil
from typing import Callable
import orjson
from BaseClasses import Item, ItemClassification
from .options import CookServeDelicious3Options


class CookServeDelicious3Item(Item):
    game = "Cook, Serve, Delicious! 3?!"


item_name_to_id = {}
item_name_to_classification: dict[
    str, ItemClassification | Callable[[CookServeDelicious3Options], ItemClassification]
] = {}

progressive_offset = 10000
food_offset = 20000
meta_offset = 30000

progressive_items = [
    ("Extra Prep Station", ItemClassification.progression, 7),
    ("Extra Holding Stating", ItemClassification.useful, 4),
    ("Progressive Heat Lamps", ItemClassification.useful, 3),
    ("Progressive Cooking Time Regulator", ItemClassification.useful, 3),
    ("Progressive Rejuvenator", ItemClassification.useful, 4),
    ("Progressive Special Systems Analyzer", ItemClassification.useful, 3),
    ("Progressive Serving Cloner", ItemClassification.useful, 6),
    ("Progressive Food Truck Reinforcements", ItemClassification.useful, 4),
    ("Progressive Aroma Blower", ItemClassification.filler, 4),
]

for idx, prog in enumerate(progressive_items):
    id = progressive_offset + idx
    item_name_to_id[prog[0]] = id
    item_name_to_classification[prog[0]] = prog[1]


meta_items = [
    ("Access to Boise, ID", ItemClassification.progression),
    ("Access to Moab, UT", ItemClassification.progression),
    ("Access to Wall, SD", ItemClassification.progression),
    ("Access to Wichita, KS", ItemClassification.progression),
    ("Access to Marietta, OK", ItemClassification.progression),
    ("Access to Midland, TX", ItemClassification.progression),
    ("Access to Houston, TX", ItemClassification.progression),
    ("Access to N.Orleans, LA", ItemClassification.progression),
    ("Access to Jackson, MS", ItemClassification.progression),
    ("Access to Mobile, AL", ItemClassification.progression),
    ("Access to Nashville, TN", ItemClassification.progression),
    ("Access to ICS, TN", ItemClassification.progression),
    ("Day Skip", ItemClassification.useful),
    ("Cook a meal IRL!", ItemClassification.filler),
]


for idx, meta in enumerate(meta_items):
    id = meta_offset + idx
    item_name_to_id[meta[0]] = id
    item_name_to_classification[meta[0]] = meta[1]


class Food:
    id: int
    name: str
    difficulty: int
    HS: bool
    added: int
    autoserve: bool

    def __init__(self, obj: dict[str, str]):
        self.id = obj["id"]
        self.name = obj["name"]
        self.difficulty = obj["difficulty"]
        self.HS = obj["HS"]
        self.added = obj["added"]
        self.autoserve = obj["autoserve"]

    def __repr__(self):
        return f"Food({self.name})"


food_id_to_food: dict[int, Food] = {}

foods: list[Food] = [
    Food(o) for o in orjson.loads(pkgutil.get_data(__name__, "data/foods.json"))
]

for food in foods:
    id = food.id + food_offset
    item_name_to_id[food.name] = id
    item_name_to_classification[food.name] = ItemClassification.progression
    food_id_to_food[food.id] = food


class FoodGroup:
    def __init__(self, row: list[str]):
        self.id = int(row[0])
        self.name: str = row[1]
        if row[2] == "-1002":
            if row[3] == "27":
                contents = [x.id for x in foods if x.added == int(row[0]) - 22]
            elif row[3] == "5":
                contents = [x.id for x in foods if x.difficulty == int(row[4])]
            elif row[3] == "50":
                contents = [
                    x.id for x in foods if x.autoserve == (row[4] == "autoserve")
                ]
        elif row[2] == "-1003" or row[2] == "-1005":
            contents = [x.id for x in foods]
        else:
            contents = [int(x) for x in row[2:] if x != ""]

        self.contents = {food_id_to_food[x] for x in contents}
        # self.hs = [food_id_to_food[x].name for x in contents if food_id_to_food[x].HS]
        # self.so = [
        #     food_id_to_food[x].name for x in contents if not food_id_to_food[x].HS
        # ]

    def __repr__(self):
        return f"FoodGroup({self.name} = [{repr(self.contents)}])"


food_groups: list[FoodGroup] = [
    FoodGroup(o)
    for o in csv.reader(
        StringIO(pkgutil.get_data(__name__, "data/foodGroups.csv").decode()),
        skipinitialspace=True,
    )
]

food_group_id_to_food_group = {x.id: x for x in food_groups}
