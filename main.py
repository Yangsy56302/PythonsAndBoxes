import sys
import os
import math
import random
import json
import time
import threading


if __name__ != "__main__":
    print("[ERROR] Please don't import main.py as a module or run main.exe indirectly.")
    print("[ERROR] Program will close in 10 seconds...")
    time.sleep(10)
    sys.exit(1)


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "TRUE"
import pygame


def import_settings() -> dict:
    file = open(".\\data\\settings.json", mode="r")
    settings = json.load(file)
    file.close()
    return settings
settings = import_settings()


def print_info(*_values, _sep: str | None = " ", _end: str | None = "\n") -> bool:
    if "info" in settings["print_type"]:
        print("[INFO]", end=" ")
        print(*_values, sep=_sep, end=_end)
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
pygame.display.set_caption("PyBox")
pygame.display.set_icon(pygame.image.load(".\\assets\\images\\icons\\main.png").convert_alpha())
window.fill((0, 0, 0))


class Data:
    tile_data = None
    item_data = None
    mob_data = None
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
        self.load()
data = Data()


class Assets:
    tile_images = None
    item_images = None
    mob_images = None
    def load(self) -> None:
        self.tile_images = {}
        self.item_images = {}
        self.mob_images = {}
        for id in data.tile_data.keys():
            self.tile_images[id] = pygame.image.load(".\\assets\\images\\tiles\\" + id + ".png").convert_alpha()
        for id in data.item_data.keys():
            self.item_images[id] = pygame.image.load(".\\assets\\images\\items\\" + id + ".png").convert_alpha()
        for id in data.mob_data.keys():
            self.mob_images[id] = pygame.image.load(".\\assets\\images\\mobs\\" + id + ".png").convert_alpha()
    def __init__(self) -> None:
        self.load()
assets = Assets()


class Object:
    id = None
    state = None
    def set_to_json(self) -> dict:
        return {"id": self.id, "state": self.state}
    def get_from_json(self, _json: dict) -> None:
        self.id = _json["id"]
        self.state = _json["state"]
    def __init__(self, _json: dict) -> None:
        self.get_from_json(_json)


class Tile(Object):
    pass


class Mob(Object):
    pass


class Item(Object):
    pass


def get_mouse_states(_events, _states: dict):
    states = _states
    button_name = ["left", "middle", "right"]
    for event in _events:
        if event.type == pygame.MOUSEMOTION:
            states["position"] = event.pos
            states["movement"] = event.rel
            for button_number in range(len(button_name)):
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            states["position"] = event.pos
            states["movement"] = (event.pos[0] - _states["position"][0], event.pos[1] - _states["position"][1])
            if "down" not in _states[button_name[event.button - 1]]:
                states[button_name[event.button - 1]] = "down"
            else:
                states[button_name[event.button - 1]] = "down_2"
        elif event.type == pygame.MOUSEBUTTONUP:
            states["position"] = event.pos
            states["movement"] = (event.pos[0] - _states["position"][0], event.pos[1] - _states["position"][1])
            if "up" not in _states[button_name[event.button - 1]]:
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
    settings = None
    map = None
    player = None
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
        self.player = Mob(_json["player"])
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
        self.player = Mob({"id": "player", "state": {}})
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
        if self.valid_coordinate(_coordinate[0], _coordinate[1]):
            if "unbreakable" not in data.tile_data[self.map[int(_coordinate[0])][int(_coordinate[1])].id]["tag"]:
                self.map[int(_coordinate[0])][int(_coordinate[1])] = Tile({"id": "air", "state": {}})
                return True
        return False
    def place_tile(self, _coordinate: tuple) -> bool:
        if self.valid_coordinate(_coordinate[0], _coordinate[1]):
            if "replaceable" in data.tile_data[self.map[int(_coordinate[0])][int(_coordinate[1])].id]["tag"]:
                self.map[int(_coordinate[0])][int(_coordinate[1])] = Tile({"id": "test_tile", "state": {}})
                return True
        return False
    def mouse_to_map(self, _mouse_position: tuple) -> tuple:
        x_coordinate = ((settings["window_length"] / 2 - _mouse_position[0]) / 16 / settings["scale"]) * -1 + 0.5 + self.player.state["x"]
        y_coordinate = ((settings["window_height"] / 2 - _mouse_position[1]) / 16 / settings["scale"]) + 0.5 + self.player.state["y"]
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
            settings["scale"] = 2
        else:
            settings["scale"] = 1
        if key_is_down(_key_states, pygame.K_DELETE):
            return 0
        if key_is_down(_mouse_states, "left"):
            self.break_tile(self.mouse_to_map(_mouse_states["position"]))
        if key_is_down(_mouse_states, "right"):
            self.place_tile(self.mouse_to_map(_mouse_states["position"]))
        self.player = self.move(self.player)
        return -1
    def display(self, _x, _y) -> None:
        float_x = math.modf(_x)[0]
        float_y = math.modf(_y)[0]
        int_x = int(_x)
        int_y = int(_y)
        for offset_x in range(-64, 65):
            for offset_y in range(-64, 65):
                tile_x = int_x + offset_x
                tile_y = int_y + offset_y
                if not self.valid_coordinate(tile_x, tile_y):
                    continue
                current_tile = self.map[tile_x][tile_y]
                current_image_unscaled = assets.tile_images[current_tile.id]
                current_image = pygame.transform.scale(current_image_unscaled, (16 * settings["scale"], 16 * settings["scale"]))
                current_image_position = ((int((offset_x - float_x) * 16 - 8) * settings["scale"]) + settings["window_length"] / 2,
                                          (int((offset_y - float_y) * -16 - 8) * settings["scale"]) + settings["window_height"] / 2)
                window.blit(current_image, current_image_position)
        # display the player in the middle
        player_image_unscaled = assets.mob_images["player"]
        player_image = pygame.transform.scale(player_image_unscaled, (16 * settings["scale"], 16 * settings["scale"]))
        window.blit(player_image, ((settings["window_length"] - 16 * settings["scale"]) / 2, (settings["window_height"] - 16 * settings["scale"]) / 2))
if settings["read_world"] == True and os.path.exists(settings["world_directory"]):
    print_info("Reading World File...")
    file = open(settings["world_directory"], mode="r")
    world = World(json.load(file))
    file.close()
    print_info("Done.")
else:
    world = World({})


def display(_x, _y):
    window.fill((0, 0, 0))
    world.display(_x, _y)
    pygame.display.flip()


return_value = -1
key_states = {}
mouse_states = {}
while return_value == -1:
    start_tick_time = time.time()
    events = pygame.event.get()
    key_states = get_key_states(events, key_states)
    mouse_states = get_mouse_states(events, mouse_states)
    return_value = world.tick(key_states, mouse_states)
    display(world.player.state["x"], world.player.state["y"])
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