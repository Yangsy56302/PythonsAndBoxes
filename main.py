import sys
import os
import math
import random
import json
import time
import copy


if __name__ != "__main__":
    print("[ERROR] The value of __name__ is not \"__main__\".")
    sys.exit(1)


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "TRUE"
import pygame
print("Thank you for playing Pythons&Boxes!")
print("This game uses Pygame to build. Support them!")


def import_settings() -> dict:
    file = open(".\\data\\settings.json", mode="r")
    settings = json.load(file)
    file.close()
    return settings
settings = import_settings()


def print_info(*_values, _sep: str | None = " ", _end: str | None = "\n") -> bool:
    if "info" in settings["print_type"]:
        print("[INFO]", *_values, sep=_sep, end=_end)
        return True
    return False


def print_warning(*_values, _sep: str | None = " ", _end: str | None = "\n") -> bool:
    if "warning" in settings["print_type"]:
        print("[WARNING]", *_values, sep=_sep, end=_end)
        return True
    return False


def print_error(*_values, _sep: str | None = " ", _end: str | None = "\n") -> bool:
    if "error" in settings["print_type"]:
        print("[ERROR]", *_values, sep=_sep, end=_end)
        return True
    return False


def progress_bar(_finished: float, _total: float) -> str:
    finished = float(_finished)
    total = float(_total)
    percentage = finished / total
    return "{:>7.2%} |{:.<100}|".format(percentage, "#" * int(percentage * 100))


def print_progress_bar(_finished: float, _total: float, _information: str) -> None:
    print_info(_information + ": " + progress_bar(_finished, _total))


pygame.init()
window = pygame.display.set_mode((settings["window_length"], settings["window_height"]))
window.fill((0, 0, 0))
if settings["debug"] == True:
    pygame.display.set_caption("Pythons&Boxes DEBUG_MODE")
else:
    pygame.display.set_caption("Pythons&Boxes")
pygame.display.set_icon(pygame.image.load(".\\assets\\images\\icons\\main.png").convert_alpha())
screen = pygame.Surface((settings["window_length"], settings["window_height"]), pygame.SRCALPHA)


class Data:
    tile_data: dict = None
    item_data: dict = None
    mob_data: dict = None
    font_data: dict = None
    recipe_data: dict = None
    structure_data: dict = None
    def load(self) -> None:
        file = open(".\\data\\tiles.json", mode="r")
        self.tile_data = json.load(file)
        file.close()
        file = open(".\\data\\items.json", mode="r")
        self.item_data = json.load(file)
        file.close()
        file = open(".\\data\\mobs.json", mode="r")
        self.mob_data = json.load(file)
        file.close()
        file = open(".\\data\\fonts.json", mode="r")
        self.font_data = json.load(file)
        file.close()
        file = open(".\\data\\recipes.json", mode="r")
        self.recipe_data = json.load(file)
        file.close()
        file = open(".\\data\\structures.json", mode="r")
        self.structure_data = json.load(file)
        file.close()
    def __init__(self) -> None:
        print_info("Loading Data...")
        self.load()
        print_info("Done.")
data = Data()


class Assets:
    tile_images: dict = None
    item_images: dict = None
    mob_images: dict = None
    font_images: dict = None
    def load(self) -> None:
        self.tile_images = {}
        self.item_images = {}
        self.mob_images = {}
        self.font_images = {}
        count = 0
        max_count = len(data.tile_data)
        for id in data.tile_data:
            self.tile_images[id] = pygame.image.load(".\\assets\\images\\tiles\\" + id + ".png").convert_alpha()
            count += 1
            print_progress_bar(count, max_count, "Loading Tile Images")
        count = 0
        max_count = len(data.item_data)
        for id in data.item_data:
            self.item_images[id] = pygame.image.load(".\\assets\\images\\items\\" + id + ".png").convert_alpha()
            count += 1
            print_progress_bar(count, max_count, "Loading Item Images")
        count = 0
        max_count = len(data.mob_data)
        for id in data.mob_data:
            self.mob_images[id] = pygame.image.load(".\\assets\\images\\mobs\\" + id + ".png").convert_alpha()
            count += 1
            print_progress_bar(count, max_count, "Loading Mob Images")
        count = 0
        max_count = len(data.font_data)
        font_image = pygame.image.load(".\\assets\\images\\fonts\\default.png").convert_alpha()
        for id in data.font_data:
            self.font_images[id] = font_image.subsurface(((data.font_data[id]["coordinate"][0] * 16, data.font_data[id]["coordinate"][1] * 16), (16, 16)))
            count += 1
            print_progress_bar(count, max_count, "Loading Font Images")
    def __init__(self) -> None:
        print_info("Loading Assets...")
        self.load()
        print_info("Done.")
assets = Assets()


class Object:
    id: str = None
    state: dict = None
    def set_to_json(self) -> dict:
        return {"id": self.id, "state": self.state}
    def get_from_json(self, _json: dict) -> None:
        self.id = _json["id"]
        self.state = _json["state"]
    def __init__(self, _json: dict) -> None:
        self.get_from_json(_json)


class Tile(Object):
    pass


class Structure(Object):
    def set_to_json(self) -> dict:
        return_value = {"id": self.id, "state": {"keys": self.keys, "tiles": self.tiles}}
        for key in self.keys:
            return_value["state"]["keys"][key] = self.state["keys"][key].set_to_json()
        return return_value
    def get_from_json(self, _json: dict) -> None:
        self.id = _json["id"]
        self.state = _json["state"]
        for key in self.keys:
            self.state["keys"][key] = Tile(_json["state"]["keys"][key])


class Item(Object):
    count: int = None
    def set_to_json(self) -> dict:
        return {"id": self.id, "count": self.count, "state": self.state}
    def get_from_json(self, _json: dict) -> None:
        self.id = _json["id"]
        self.count = _json["count"]
        self.state = _json["state"]


class Mob(Object):
    def count_item(self, _item: Item) -> bool:
        if _item.id == "empty":
            return 0
        return_value = 0
        for slot in range(len(self.state["backpack"])):
            if self.state["backpack"][slot].id == _item.id:
                if self.state["backpack"][slot].state == _item.state:
                    return_value += self.state["backpack"][slot].count
        return return_value
    def add_item(self, _item: Item) -> bool:
        for slot in range(len(self.state["backpack"])):
            if _item.id == "empty" or _item.count == 0:
                break
            if self.state["backpack"][slot].id == _item.id:
                if self.state["backpack"][slot].state == _item.state:
                    max_count = data.item_data[_item.id]["data"]["max_count"]
                    free_space = max(0, max_count - self.state["backpack"][slot].count - _item.count)
                    addition = min(free_space, _item.count)
                    if addition > 0:
                        self.state["backpack"][slot].count += addition
                        _item.count -= addition
                        if _item.count == 0:
                            _item = Item({"id": "empty", "count": 0, "state": {}})
        for slot in range(len(self.state["backpack"])):
            if _item.id == "empty" or _item.count == 0:
                break
            if self.state["backpack"][slot].id == "empty":
                self.state["backpack"][slot] = _item
                _item = Item({"id": "empty", "count": 0, "state": {}})
        if _item.id == "empty" or _item.count == 0:
            return True
        else:
            return False
    def subtract_item(self, _item: Item) -> bool:
        for slot in range(len(self.state["backpack"])):
            if _item.id == "empty" or _item.count == 0:
                break
            if self.state["backpack"][slot].id == _item.id:
                if self.state["backpack"][slot].state == _item.state:
                    subtraction = min(self.state["backpack"][slot].count, _item.count)
                    if subtraction > 0:
                        self.state["backpack"][slot].count -= subtraction
                        _item.count -= subtraction
                        if self.state["backpack"][slot].count == 0:
                            self.state["backpack"][slot] = Item({"id": "empty", "count": 0, "state": {}})
                        if _item.count == 0:
                            _item = Item({"id": "empty", "count": 0, "state": {}})
        if _item.id == "empty" or _item.count == 0:
            return True
        else:
            return False


class Player(Mob):
    def set_to_json(self) -> dict:
        return_value = {"id": self.id, "state": self.state}
        for slot_number in range(len(self.state["backpack"])):
            return_value["state"]["backpack"][slot_number] = self.state["backpack"][slot_number].set_to_json()
        return return_value
    def get_from_json(self, _json: dict) -> None:
        self.id = _json["id"]
        self.state = _json["state"]
        for slot_number in range(len(_json["state"]["backpack"])):
            self.state["backpack"][slot_number] = Item(_json["state"]["backpack"][slot_number])


def get_mouse_states(_events, _states: dict):
    states = _states
    # add the underline to the pressed button
    button_name = ["left", "middle", "right", "scroll_up", "scroll_down"]
    for button_number in range(len(button_name[0:3])):
        if "_" not in states[button_name[button_number]]:
            states[button_name[button_number]] += "_"
    # set scroll to zero
    states[button_name[3]] = 0
    states[button_name[4]] = 0
    for event in _events:
        # mouse moved
        if event.type == pygame.MOUSEMOTION:
            states["position"] = event.pos
            states["movement"] = event.rel
            for button_number in range(len(button_name[0:3])):
                if event.buttons[button_number] == 1:
                    states[button_name[button_number]] = "down"
                else:
                    states[button_name[button_number]] = "up"
        # button pressed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button - 1 in range(3):
                states[button_name[event.button - 1]] = "down"
            # special scroll detector
            elif (event.button - 1) % 2 == 0:
                states[button_name[4]] = int((event.button - 3) / 2)
            else:
                states[button_name[3]] = int((event.button - 2) / 2)
        # button released
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button - 1 in range(3):
                states[button_name[event.button - 1]] = "up"
    return states


def get_key_states(_events, _states: dict) -> dict:
    states = _states
    for state in states:
        if "_" not in states[state]:
            states[state] += "_"
    for event in _events:
        if event.type == pygame.KEYDOWN:
            states[event.key] = "down"
        if event.type == pygame.KEYUP:
            states[event.key] = "up"
    return states


def key_is_down(_states: dict, _key) -> bool:
    if _key in _states:
        if "down" in _states[_key]:
            return True
        else:
            return False
    else:
        return False


def key_is_just_down(_states: dict, _key) -> bool:
    if _key in _states:
        if _states[_key] == "down":
            return True
        else:
            return False
    else:
        return False


def key_is_up(_states: dict, _key) -> bool:
    if _key in _states:
        if "up" in _states[_key]:
            return True
        else:
            return False
    else:
        return False


def key_is_just_up(_states: dict, _key) -> bool:
    if _key in _states:
        if _states[_key] == "up":
            return True
        else:
            return False
    else:
        return False


class World:
    settings: dict = None
    map: list = None
    player: Player = None
    def set_to_json(self) -> dict:
        json_map = []
        for x in range(self.settings["world_length"]):
            json_map.append([])
            for y in range(self.settings["world_height"]):
                json_map[x].append(self.map[x][y].set_to_json())
        return {"map": json_map, "player": self.player.set_to_json(), "settings": self.settings}
    def get_from_json(self, _json: dict) -> None:
        self.settings = _json["settings"]
        self.map = []
        for x in range(self.settings["world_length"]):
            self.map.append([])
            for y in range(self.settings["world_height"]):
                self.map[x].append(Tile(_json["map"][x][y]))
        self.player = Player(_json["player"])
    def valid_coordinate(self, _coordinate: tuple) -> bool:
        return _coordinate[0] >= 0 and _coordinate[0] < self.settings["world_length"] and _coordinate[1] >= 0 and _coordinate[1] < self.settings["world_height"]
    def build_structure(self, _coordinate: tuple, _id: str) -> bool:
        structure = data.structure_data[_id]
        length = len(structure["tiles"][0])
        height = len(structure["tiles"])
        return_value = False
        for structure_x in range(length):
            for structure_y in range(height):
                map_x = structure_x + _coordinate[0] - structure["core"][0]
                map_y = height - structure_y - 1 + _coordinate[1] - structure["core"][1]
                if self.valid_coordinate((map_x, map_y)):
                    if structure["tiles"][structure_y][structure_x] != " ":
                        self.map[map_x][map_y] = Tile(structure["keys"][structure["tiles"][structure_y][structure_x]])
                        return_value = True
        return return_value
    def noise(self) -> list:
        random.seed(self.settings["seed"])
        terrain = [self.settings["world_height"] / 2 for i in range(self.settings["world_length"])]
        offset = [0 for i in range(self.settings["world_length"])]
        step_length = 1
        step_count = 0
        offset_1 = random.uniform(step_length * -0.25, step_length * 0.25)
        offset_2 = random.uniform(step_length * -0.25, step_length * 0.25)
        while step_length <= 2 ** 6:
            for x in range(self.settings["world_length"]):
                step_count += 1
                if x % step_length == 0:
                    offset_1 = offset_2
                    offset_2 = random.uniform(step_length * -0.25, step_length * 0.25)
                    step_count = 0
                offset[x] = offset_1 + (step_count * ((offset_2 - offset_1) / step_length))
            for x in range(self.settings["world_length"]):
                terrain[x] += offset[x]
            step_length *= 2
        for x in range(self.settings["world_length"]):
            terrain[x] = int(terrain[x])
        return terrain
    def create(self, _settings: dict) -> None:
        self.settings = _settings
        self.map = [[Tile({"id": "air", "state": {}}) for y in range(self.settings["world_height"])] for x in range(self.settings["world_length"])]
        terrain = self.noise()
        for x in range(self.settings["world_length"]):
            print_progress_bar(x, self.settings["world_length"], "Creating New World")
            dirt_thick = random.choice(range(3, 6))
            for y in range(terrain[x]):
                if not self.valid_coordinate((x, y)):
                    break
                if terrain[x] - y == 1:
                    self.map[x][y] = Tile({"id": "grassy_soil", "state": {}})
                    random_number = random.choice(range(64))
                    if random_number == 0:
                        if self.valid_coordinate((x, y + 1)):
                            self.map[x][y + 1] = Tile({"id": "sapling", "state": {}})
                    elif random_number == 1:
                        self.build_structure((x, y), "tree_3")
                    elif random_number == 2:
                        self.build_structure((x, y), "tree_4")
                    elif random_number == 3:
                        self.build_structure((x, y), "tree_5")
                    elif random_number <= 16:
                        if self.valid_coordinate((x, y + 1)):
                            self.map[x][y + 1] = Tile({"id": "grass", "state": {}})
                elif terrain[x] - y <= dirt_thick:
                    random_number = random.choice(range(16))
                    if random_number == 0:
                        self.map[x][y] = Tile({"id": "gravel", "state": {}})
                    else:
                        self.map[x][y] = Tile({"id": "soil", "state": {}})
                else:
                    random_number = random.choice(range(256))
                    if random_number == 0:
                        self.map[x][y] = Tile({"id": "coal_ore", "state": {}})
                    elif random_number == 1:
                        self.map[x][y] = Tile({"id": "iron_ore", "state": {}})
                    else:
                        self.map[x][y] = Tile({"id": "stone", "state": {}})
        self.player = Player({"id": "player", "state": data.mob_data["player"]["state"]})
        self.player.state["x"] = float(int(self.settings["world_length"] / 2))
        self.player.state["y"] = float(terrain[int(self.settings["world_length"] / 2)])
        self.player.state["mx"] = 0.0
        self.player.state["my"] = 0.0
        print_progress_bar(1, 1, "Creating New World")
        print_info("Done.")
    def __init__(self, _json: dict) -> None:
        if _json == {}:
            self.create(settings["default_world_settings"])
        else:
            self.get_from_json(_json)
    def mob_on_ground(self, _mob) -> bool:
        # get tile's coordinate
        tile_coordinate = [[int(_mob.state["x"] + 0.03125), int(_mob.state["y"] - 0.03125)],
                           [int(_mob.state["x"] + 0.96875), int(_mob.state["y"] - 0.03125)]]
        for coordinate in tile_coordinate:
            if self.valid_coordinate(coordinate):
                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                    return True
        return False
    def move(self, _mob) -> Mob:
        if _mob.state["mx"] == 0 and _mob.state["my"] == 0: # moving?
            return _mob
        # get player's coordinate
        max_move = int(max(abs(_mob.state["mx"]), abs(_mob.state["my"])) * 16)
        list_x = [0 for x in range(max_move + 1)]
        if _mob.state["mx"] != 0: # avoid mx / 0
            list_x = [int(x * _mob.state["mx"] * 16 / max_move) / 16 for x in range(max_move + 1)]
        list_y = [0 for y in range(max_move + 1)]
        if _mob.state["my"] != 0: # avoid my / 0
            list_y = [int(y * _mob.state["my"] * 16 / max_move) / 16 for y in range(max_move + 1)]
        # test the touch between player and tile
        for i in range(max_move + 1):
            # get tile's coordinate
            tile_coordinate = [[int(_mob.state["x"] + list_x[i] + 0.03125), int(_mob.state["y"] + list_y[i] + 0.03125)],
                               [int(_mob.state["x"] + list_x[i] + 0.03125), int(_mob.state["y"] + list_y[i] + 0.96875)],
                               [int(_mob.state["x"] + list_x[i] + 0.96875), int(_mob.state["y"] + list_y[i] + 0.03125)],
                               [int(_mob.state["x"] + list_x[i] + 0.96875), int(_mob.state["y"] + list_y[i] + 0.96875)]]
            for j in range(len(tile_coordinate)):
                if not self.valid_coordinate(tile_coordinate[j]):
                    _mob.state["x"] = float(int(self.settings["world_length"] / 2))
                    _mob.state["y"] = 250.0
                    _mob.state["mx"] = 0.0
                    _mob.state["my"] = 0.0
                    return _mob
                # collapse
                if "mob_transparent" not in data.tile_data[self.map[tile_coordinate[j][0]][tile_coordinate[j][1]].id]["tag"]:
                    if _mob.state["mx"] > 0:
                        tile_coordinate = [[int(_mob.state["x"] + list_x[i - 1] + 1.03125), int(_mob.state["y"] + list_y[i - 1] + 0.03125)],
                                           [int(_mob.state["x"] + list_x[i - 1] + 1.03125), int(_mob.state["y"] + list_y[i - 1] + 0.96875)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    _mob.state["mx"] = 0.0
                    else:
                        tile_coordinate = [[int(_mob.state["x"] + list_x[i - 1] - 0.03125), int(_mob.state["y"] + list_y[i - 1] + 0.03125)],
                                           [int(_mob.state["x"] + list_x[i - 1] - 0.03125), int(_mob.state["y"] + list_y[i - 1] + 0.96875)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    _mob.state["mx"] = 0.0
                    if _mob.state["my"] > 0:
                        tile_coordinate = [[int(_mob.state["x"] + list_x[i - 1] + 0.03125), int(_mob.state["y"] + list_y[i - 1] + 1.03125)],
                                           [int(_mob.state["x"] + list_x[i - 1] + 0.96875), int(_mob.state["y"] + list_y[i - 1] + 1.03125)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    _mob.state["my"] = 0.0
                    else:
                        tile_coordinate = [[int(_mob.state["x"] + list_x[i - 1] + 0.03125), int(_mob.state["y"] + list_y[i - 1] - 0.03125)],
                                           [int(_mob.state["x"] + list_x[i - 1] + 0.96875), int(_mob.state["y"] + list_y[i - 1] - 0.03125)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    _mob.state["my"] = 0.0
                    _mob.state["x"] += list_x[i - 1]
                    _mob.state["y"] += list_y[i - 1]
                    return _mob
        _mob.state["x"] += list_x[-1]
        _mob.state["y"] += list_y[-1]
        return _mob
    def break_tile(self, _coordinate: tuple) -> bool:
        # is this coordinate valid?
        if not self.valid_coordinate(_coordinate):
            return False
        # is this tile breakable?
        current_tile = self.map[int(_coordinate[0])][int(_coordinate[1])]
        if "unbreakable" in data.tile_data[current_tile.id]["tag"]:
            return False
        current_tool = self.player.state["backpack"][self.player.state["selected_slot"]]
        breakable_tile = False
        if data.tile_data[current_tile.id]["data"]["mining_tool"] == "none":
            breakable_tile = True
        if data.tile_data[current_tile.id]["data"]["mining_level"] <= 0:
            breakable_tile = True
        if "tool" in data.item_data[current_tool.id]["tag"]:
            if data.item_data[current_tool.id]["data"]["tool_info"]["type"] == data.tile_data[current_tile.id]["data"]["mining_tool"]:
                if data.item_data[current_tool.id]["data"]["tool_info"]["level"] >= data.tile_data[current_tile.id]["data"]["mining_level"]:
                    breakable_tile = True
        if breakable_tile == True:
            dropped_items = data.tile_data[current_tile.id]["data"]["tile_drop"]
        else:
            return False
        # get item
        for item in range(len(dropped_items)):
            self.player.add_item(Item(dropped_items[item]))
        # break tile
        self.map[int(_coordinate[0])][int(_coordinate[1])] = Tile({"id": "air", "state": {}})
        return True
    def place_tile(self, _coordinate: tuple) -> bool:
        # is this coordinate valid?
        if not self.valid_coordinate(_coordinate):
            return False
        # is this tile replaceable?
        current_tile = self.map[int(_coordinate[0])][int(_coordinate[1])]
        if "replaceable" not in data.tile_data[current_tile.id]["tag"]:
            return False
        # is this item placeable?
        current_item = self.player.state["backpack"][self.player.state["selected_slot"]]
        if "placeable" not in data.item_data[current_item.id]["tag"]:
            return False
        # subtract one item
        self.player.state["backpack"][self.player.state["selected_slot"]].count -= 1
        if self.player.state["backpack"][self.player.state["selected_slot"]].count == 0:
            self.player.state["backpack"][self.player.state["selected_slot"]] = Item({"id": "empty", "count": 0, "state": {}})
        # set tile
        self.map[int(_coordinate[0])][int(_coordinate[1])] = Tile(data.item_data[current_item.id]["data"]["to_tile"])
        return True
    def mouse_to_map(self, _mouse_position: tuple) -> tuple:
        x_coordinate = ((settings["window_length"] / 2 - _mouse_position[0]) / 16 / settings["map_scale"]) * -1 + 0.5 + self.player.state["x"]
        y_coordinate = ((settings["window_height"] / 2 - _mouse_position[1]) / 16 / settings["map_scale"]) + 0.5 + self.player.state["y"]
        return (x_coordinate, y_coordinate)
    def tick(self, _key_states: dict, _mouse_states: dict) -> str:
        if key_is_just_down(_key_states, pygame.K_DELETE):
            return "quit"
        self.player.state["mx"] = 0.0
        self.player.state["my"] += self.settings["gravity"]
        if key_is_down(_key_states, pygame.K_SPACE):
            if self.mob_on_ground(self.player):
                self.player.state["my"] += 0.75
        if key_is_down(_key_states, pygame.K_a):
            self.player.state["mx"] = -data.mob_data["player"]["data"]["speed"]
        if key_is_down(_key_states, pygame.K_d):
            self.player.state["mx"] = data.mob_data["player"]["data"]["speed"]
        if key_is_down(_key_states, pygame.K_BACKQUOTE):
            settings["map_scale"] = settings["default_map_scale"] * 2
        else:
            settings["map_scale"] = settings["default_map_scale"]
        if key_is_down(_mouse_states, "left"):
            self.break_tile(self.mouse_to_map(_mouse_states["position"]))
        if key_is_down(_mouse_states, "right"):
            self.place_tile(self.mouse_to_map(_mouse_states["position"]))
        self.player.state["selected_slot"] += _mouse_states["scroll_down"] - _mouse_states["scroll_up"]
        self.player.state["selected_slot"] %= data.mob_data["player"]["data"]["max_slot"]
        self.player = self.move(self.player)
        if key_is_just_down(_key_states, pygame.K_c):
            return "craft"
        return "do_nothing"
    def crafts(self, _key_states: dict, _mouse_states: dict) -> str:
        # is it first time?
        if "selected_recipe" not in self.player.state["temporary"]:
            self.player.state["temporary"]["selected_recipe"] = 0
        # choose the recipe
        self.player.state["temporary"]["selected_recipe"] += _mouse_states["scroll_down"] - _mouse_states["scroll_up"]
        self.player.state["temporary"]["selected_recipe"] %= len(data.recipe_data)
        self.player.state["temporary"]["successful_crafting"] = "none"
        selected_recipe = self.player.state["temporary"]["selected_recipe"]
        # craft
        if key_is_just_down(_key_states, pygame.K_SPACE):
            for material in range(len(data.recipe_data[selected_recipe]["from"])):
                if self.player.count_item(Item(data.recipe_data[selected_recipe]["from"][material])) < data.recipe_data[selected_recipe]["from"][material]["count"]:
                    self.player.state["temporary"]["successful_crafting"] = "false"
                    return "nothing"
            for material in range(len(data.recipe_data[selected_recipe]["from"])):
                self.player.subtract_item(Item(data.recipe_data[selected_recipe]["from"][material]))
            for product in range(len(data.recipe_data[selected_recipe]["to"])):
                self.player.state["temporary"]["successful_crafting"] = "true"
                self.player.add_item(Item(data.recipe_data[selected_recipe]["to"][product]))
        # exit
        if key_is_just_down(_key_states, pygame.K_c):
            return "world"
        return "nothing"
    def display_world(self, _coordinate: tuple) -> None:
        window.fill("#80C0FF")
        screen.fill("#00000000")
        # display map
        float_x = math.modf(_coordinate[0])[0]
        float_y = math.modf(_coordinate[1])[0]
        int_x = int(_coordinate[0])
        int_y = int(_coordinate[1])
        for offset_x in range(-64, 65):
            for offset_y in range(-64, 65):
                tile_x = int_x + offset_x
                tile_y = int_y + offset_y
                if not self.valid_coordinate((tile_x, tile_y)):
                    continue
                tile = self.map[tile_x][tile_y]
                tile_image_unscaled = assets.tile_images[tile.id]
                tile_image = pygame.transform.scale(tile_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
                tile_image_position = ((int((offset_x - float_x) * 16 - 8) * settings["map_scale"]) + settings["window_length"] / 2,
                                       (int((offset_y - float_y) * -16 - 8) * settings["map_scale"]) + settings["window_height"] / 2)
                screen.blit(tile_image, tile_image_position)
        # display the player in the middle
        player_image_unscaled = assets.mob_images["player"]
        player_image = pygame.transform.scale(player_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
        screen.blit(player_image, ((settings["window_length"] - 16 * settings["map_scale"]) / 2, (settings["window_height"] - 16 * settings["map_scale"]) / 2))
        # display the backpack
        backpack = self.player.state["backpack"]
        slot_image = pygame.Surface((16 * settings["gui_scale"], 16 * settings["gui_scale"])).convert_alpha()
        for slot in range(len(backpack)):
            item_image_unscaled = assets.item_images[backpack[slot].id]
            item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
            item_image_position = (int((slot * 16 - data.mob_data["player"]["data"]["max_slot"] * 8) * settings["gui_scale"] + settings["window_length"] / 2),
                                   int(settings["window_height"] - 16 * settings["gui_scale"]))
            if slot == self.player.state["selected_slot"]:
                slot_image.fill("#8000FF80")
            else:
                slot_image.fill("#8040C080")
            screen.blit(slot_image, item_image_position)
            screen.blit(item_image, item_image_position)
        # display selected item's name
        item_info = str(self.player.state["backpack"][self.player.state["selected_slot"]].count) + " " + data.item_data[self.player.state["backpack"][self.player.state["selected_slot"]].id]["name"].upper()
        for character_number in range(len(item_info)):
            character_image_unscaled = assets.font_images[item_info[character_number]]
            character_image = pygame.transform.scale(character_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
            character_image_position = (int((character_number * 16 - len(item_info) * 8) * settings["gui_scale"] + settings["window_length"] / 2),
                                        int(settings["window_height"] - 32 * settings["gui_scale"]))
            screen.blit(character_image, character_image_position)
    def display_craft(self):
        if self.player.state["temporary"]["successful_crafting"] == "true":
            window.fill("#008000")
        elif self.player.state["temporary"]["successful_crafting"] == "false":
            window.fill("#800000")
        else:
            window.fill("#000000")
        screen.fill("#00000000")
        # display all the recipes
        slot_image = pygame.Surface((16 * settings["gui_scale"], 16 * settings["gui_scale"])).convert_alpha()
        selected_recipe = self.player.state["temporary"]["selected_recipe"]
        for recipe in range(len(data.recipe_data)):
            for slot in range(len(data.recipe_data[recipe]["from"])):
                item_image_unscaled = assets.item_images[data.recipe_data[recipe]["from"][slot]["id"]]
                item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
                item_image_position = (int(((recipe - selected_recipe) * 16 - 8) * settings["gui_scale"] + settings["window_length"] / 2),
                                       int((slot + 1) * 16 * settings["gui_scale"]))
                if recipe == selected_recipe:
                    slot_image.fill("#FF000080")
                else:
                    slot_image.fill("#C0404080")
                screen.blit(slot_image, item_image_position)
                screen.blit(item_image, item_image_position)
            item_image_unscaled = assets.item_images[data.recipe_data[recipe]["to"][0]["id"]]
            item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
            item_image_position = (int(((recipe - selected_recipe) * 16 - 8) * settings["gui_scale"] + settings["window_length"] / 2), 0)
            if recipe == selected_recipe:
                slot_image.fill("#00FF0080")
            else:
                slot_image.fill("#40C04080")
            screen.blit(slot_image, item_image_position)
            screen.blit(item_image, item_image_position)
        # display the backpack
        backpack = self.player.state["backpack"]
        for slot in range(len(backpack)):
            item_image_unscaled = assets.item_images[backpack[slot].id]
            item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
            item_image_position = (int((slot * 16 - data.mob_data["player"]["data"]["max_slot"] * 8) * settings["gui_scale"] + settings["window_length"] / 2),
                                   int(settings["window_height"] - 16 * settings["gui_scale"]))
            slot_image.fill("#80808080")
            screen.blit(slot_image, item_image_position)
            screen.blit(item_image, item_image_position)
        # display selected recipe's name
        item_info = str(data.recipe_data[selected_recipe]["to"][0]["count"]) + " " + data.item_data[data.recipe_data[selected_recipe]["to"][0]["id"]]["name"].upper()
        for character_number in range(len(item_info)):
            character_image_unscaled = assets.font_images[item_info[character_number]]
            character_image = pygame.transform.scale(character_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
            character_image_position = (int((character_number * 16 - len(item_info) * 8) * settings["gui_scale"] + settings["window_length"] / 2),
                                        int(settings["window_height"] - 32 * settings["gui_scale"]))
            screen.blit(character_image, character_image_position)
if settings["read_world"] == True and os.path.exists(settings["world_directory"]):
    print_info("Reading World File...")
    file = open(settings["world_directory"], mode="r")
    world = World(json.load(file))
    file.close()
    print_info("Done.")
else:
    world = World({})


def display_world(_coordinate: tuple) -> None:
    world.display_world(_coordinate)


def display_craft() -> None:
    world.display_craft()


return_value = "do_nothing"
key_states = {}
mouse_states = {"left": "up", "middle": "up", "right": "up", "scroll_up": 0, "scroll_down": 0}
gui = "world"
while return_value != "quit":
    start_tick_time = time.time()
    events = pygame.event.get()
    key_states = get_key_states(events, key_states)
    mouse_states = get_mouse_states(events, mouse_states)
    if gui == "world":
        return_value = world.tick(key_states, mouse_states)
        display_world((world.player.state["x"], world.player.state["y"]))
        if return_value == "craft":
            gui = "craft"
    elif gui == "craft":
        return_value = world.crafts(key_states, mouse_states)
        display_craft()
        if return_value == "world":
            gui = "world"
    window.blit(screen, (0, 0))
    pygame.display.flip()
    stop_tick_time = time.time()
    while stop_tick_time - start_tick_time < 0.0625:
        stop_tick_time = time.time()
if settings["write_world"] == True:
    print_info("Writing World File...")
    file = open(settings["world_directory"], mode="w")
    json.dump(world.set_to_json(), file)
    file.close()
    print_info("Done.")
pygame.quit()
sys.exit(0)