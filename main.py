import sys
import os
import math
import random
import json
import time
import copy


class Error(Exception):
    info: str = ""
    def __init__(self, _info: str = "No Info."):
        self.info = _info
    def __str__(self):
        return self.info


class NameIsNotMainError(Error):
    def __init__(self):
        Error.__init__(self, "The value of __name__ is not \"__main__\".")


try:
    if __name__ != "__main__":
        raise NameIsNotMainError()
except NameIsNotMainError as error:
    print("[ERROR]", str(error))
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
        print("[WARNING]", end=" ")
        print(*_values, sep=_sep, end=_end)
        return True
    return False


def print_error(*_values, _sep: str | None = " ", _end: str | None = "\n") -> bool:
    if "error" in settings["print_type"]:
        print("[ERROR]", end=" ")
        print(*_values, sep=_sep, end=_end)
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
pygame.display.set_caption("Pythons&Boxes")
pygame.display.set_icon(pygame.image.load(".\\assets\\images\\icons\\main.png").convert_alpha())
window.fill((0, 0, 0))
screen = pygame.Surface((settings["window_length"], settings["window_height"]), pygame.SRCALPHA)


class Data:
    tile_data: dict = None
    item_data: dict = None
    mob_data: dict = None
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
    def __init__(self) -> None:
        print_info("Loading Data...")
        self.load()
        print_info("Done.")
data = Data()


class Assets:
    tile_images: dict = None
    item_images: dict = None
    mob_images: dict = None
    def load(self) -> None:
        self.tile_images = {}
        self.item_images = {}
        self.mob_images = {}
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


class Item(Object):
    count: int = None
    def set_to_json(self) -> dict:
        return {"id": self.id, "count": self.count, "state": self.state}
    def get_from_json(self, _json: dict) -> None:
        self.id = _json["id"]
        self.count = _json["count"]
        self.state = _json["state"]


class Mob(Object):
    pass


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
            self.state["backpack"][slot_number] = Item({"id": _json["state"]["backpack"][slot_number]["id"],
                                                        "count": _json["state"]["backpack"][slot_number]["count"],
                                                        "state": _json["state"]["backpack"][slot_number]["state"]})


def get_mouse_states(_events, _states: dict):
    states = _states
    button_name = ["left", "middle", "right", "scroll_up", "scroll_down"]
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
                    if button_name[button_number] not in _states:
                        states[button_name[button_number]] = "down"
                    elif "down" not in _states[button_name[button_number]]:
                        states[button_name[button_number]] = "down"
                    else:
                        states[button_name[button_number]] = "down_2"
                else:
                    if button_name[button_number] not in _states:
                        states[button_name[button_number]] = "up"
                    elif "up" not in _states[button_name[button_number]]:
                        states[button_name[button_number]] = "up"
                    else:
                        states[button_name[button_number]] = "up_2"
        # button pressed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button - 1 in range(3):
                if button_name[event.button - 1] not in _states:
                    states[button_name[event.button - 1]] = "down"
                elif "down" not in _states[button_name[event.button - 1]]:
                    states[button_name[event.button - 1]] = "down"
                else:
                    states[button_name[event.button - 1]] = "down_2"
            # special scroll detector
            elif (event.button - 1) % 2 == 0:
                states[button_name[4]] = int((event.button - 3) / 2)
            else:
                states[button_name[3]] = int((event.button - 2) / 2)
        # button released
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button - 1 in range(3):
                if button_name[event.button - 1] not in _states:
                    states[button_name[event.button - 1]] = "up"
                elif "up" not in _states[button_name[event.button - 1]]:
                    states[button_name[event.button - 1]] = "up"
                else:
                    states[button_name[event.button - 1]] = "up_2"
    return states


def get_key_states(_events, _states: dict) -> dict:
    states = _states
    for event in _events:
        if event.type == pygame.KEYDOWN:
            if event.key not in _states:
                states[event.key] = "down"
            elif "down" not in _states[event.key]:
                states[event.key] = "down"
            else:
                states[event.key] = "down_2"
        if event.type == pygame.KEYUP:
            if event.key not in _states:
                states[event.key] = "up"
            elif "up" not in _states[event.key]:
                states[event.key] = "up"
            else:
                states[event.key] = "up_2"
    return states


def key_is_down(_states: dict, _key) -> bool:
    if _key in _states:
        if "down" in _states[_key]:
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
    def valid_coordinate(self, _x, _y) -> bool:
        return _x >= 0 and _x < self.settings["world_length"] and _y >= 0 and _y < self.settings["world_height"]
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
            for y in range(min(terrain[x], self.settings["world_height"])):
                self.map[x][y] = Tile({"id": "stone", "state": {}})
                if terrain[x] - y <= 4:
                    self.map[x][y] = Tile({"id": "soil", "state": {}})
                if terrain[x] - y == 1:
                    self.map[x][y] = Tile({"id": "grassy_soil", "state": {}})
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
            if self.valid_coordinate(coordinate[0], coordinate[1]):
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
                if not self.valid_coordinate(tile_coordinate[j][0], tile_coordinate[j][1]):
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
                            if self.valid_coordinate(coordinate[0], coordinate[1]):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    _mob.state["mx"] = 0.0
                    else:
                        tile_coordinate = [[int(_mob.state["x"] + list_x[i - 1] - 0.03125), int(_mob.state["y"] + list_y[i - 1] + 0.03125)],
                                           [int(_mob.state["x"] + list_x[i - 1] - 0.03125), int(_mob.state["y"] + list_y[i - 1] + 0.96875)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate[0], coordinate[1]):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    _mob.state["mx"] = 0.0
                    if _mob.state["my"] > 0:
                        tile_coordinate = [[int(_mob.state["x"] + list_x[i - 1] + 0.03125), int(_mob.state["y"] + list_y[i - 1] + 1.03125)],
                                           [int(_mob.state["x"] + list_x[i - 1] + 0.96875), int(_mob.state["y"] + list_y[i - 1] + 1.03125)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate[0], coordinate[1]):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    _mob.state["my"] = 0.0
                    else:
                        tile_coordinate = [[int(_mob.state["x"] + list_x[i - 1] + 0.03125), int(_mob.state["y"] + list_y[i - 1] - 0.03125)],
                                           [int(_mob.state["x"] + list_x[i - 1] + 0.96875), int(_mob.state["y"] + list_y[i - 1] - 0.03125)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate[0], coordinate[1]):
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
        if not self.valid_coordinate(_coordinate[0], _coordinate[1]):
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
            dropped_items = copy.deepcopy(data.tile_data[current_tile.id]["data"]["tile_drop"])
        else:
            return False
        # get item
        for slot in range(len(self.player.state["backpack"])):
            for item in range(len(dropped_items)):
                if dropped_items[item]["id"] == "empty" or dropped_items[item]["count"] == 0:
                    continue
                if self.player.state["backpack"][slot].id == dropped_items[item]["id"]:
                    if self.player.state["backpack"][slot].state == dropped_items[item]["state"]:
                        max_count = data.item_data[dropped_items[item]["id"]]["data"]["max_count"]
                        free_space = max(0, max_count - self.player.state["backpack"][slot].count - dropped_items[item]["count"])
                        addition = min(free_space, dropped_items[item]["count"])
                        if addition > 0:
                            self.player.state["backpack"][slot].count += addition
                            dropped_items[item]["count"] -= addition
                            if dropped_items[item]["count"] == 0:
                                dropped_items[item] = {"id": "empty", "count": 0, "state": {}}
        for slot in range(len(self.player.state["backpack"])):
            for item in range(len(dropped_items)):
                if dropped_items[item]["id"] == "empty" or dropped_items[item]["count"] == 0:
                    continue
                if self.player.state["backpack"][slot].id == "empty":
                    self.player.state["backpack"][slot] = Item(dropped_items[item])
                    dropped_items[item] = {"id": "empty", "count": 0, "state": {}}
        # break tile
        self.map[int(_coordinate[0])][int(_coordinate[1])] = Tile({"id": "air", "state": {}})
        return True
    def place_tile(self, _coordinate: tuple) -> bool:
        if self.valid_coordinate(_coordinate[0], _coordinate[1]):
            if "replaceable" in data.tile_data[self.map[int(_coordinate[0])][int(_coordinate[1])].id]["tag"]:
                self.map[int(_coordinate[0])][int(_coordinate[1])] = Tile({"id": "test_tile", "state": {}})
                return True
        return False
    def place_tile(self, _coordinate: tuple) -> bool:
        # is this coordinate valid?
        if not self.valid_coordinate(_coordinate[0], _coordinate[1]):
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
    def tick(self, _key_states: dict, _mouse_states: dict) -> int:
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
            settings["map_scale"] = 2
        else:
            settings["map_scale"] = 1
        if key_is_down(_key_states, pygame.K_DELETE):
            return 0
        if key_is_down(_mouse_states, "left"):
            self.break_tile(self.mouse_to_map(_mouse_states["position"]))
        if key_is_down(_mouse_states, "right"):
            self.place_tile(self.mouse_to_map(_mouse_states["position"]))
        self.player.state["selected_slot"] += _mouse_states["scroll_down"] - _mouse_states["scroll_up"]
        self.player.state["selected_slot"] %= data.mob_data["player"]["data"]["max_slot"]
        self.player = self.move(self.player)
        return -1
    def display(self, _coordinate: tuple) -> None:
        # display map
        float_x = math.modf(_coordinate[0])[0]
        float_y = math.modf(_coordinate[1])[0]
        int_x = int(_coordinate[0])
        int_y = int(_coordinate[1])
        for offset_x in range(-64, 65):
            for offset_y in range(-64, 65):
                tile_x = int_x + offset_x
                tile_y = int_y + offset_y
                if not self.valid_coordinate(tile_x, tile_y):
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
            item_image_position = (int((slot * 16 - data.mob_data["player"]["data"]["max_slot"] * 8) * settings["gui_scale"] + settings["window_length"] / 2), int(settings["window_height"] - 16 * settings["gui_scale"]))
            if slot == self.player.state["selected_slot"]:
                slot_image.fill("#8000FF80")
            else:
                slot_image.fill("#8040C080")
            screen.blit(slot_image, item_image_position)
            screen.blit(item_image, item_image_position)
if settings["read_world"] == True and os.path.exists(settings["world_directory"]):
    print_info("Reading World File...")
    file = open(settings["world_directory"], mode="r")
    world = World(json.load(file))
    file.close()
    print_info("Done.")
else:
    world = World({})


def display(_coordinate: tuple):
    window.fill("#000000")
    screen.fill("#00000000")
    world.display(_coordinate)
    window.blit(screen, (0, 0))
    pygame.display.flip()


return_value = -1
key_states = {}
mouse_states = {"left": "up", "middle": "up", "right": "up", "scroll_up": 0, "scroll_down": 0}
while return_value == -1:
    start_tick_time = time.time()
    events = pygame.event.get()
    key_states = get_key_states(events, key_states)
    mouse_states = get_mouse_states(events, mouse_states)
    return_value = world.tick(key_states, mouse_states)
    display((world.player.state["x"], world.player.state["y"]))
    stop_tick_time = time.time()
    while stop_tick_time - start_tick_time < 0.0625:
        stop_tick_time = time.time()
pygame.quit()
if settings["write_world"] == True:
    print_info("Writing World File...")
    file = open(settings["world_directory"], mode="w")
    json.dump(world.set_to_json(), file)
    file.close()
    print_info("Done.")
sys.exit(return_value)