import pygame
import math
import random
import json
import time
import sys


def import_settings() -> dict:
    file = open(".\\data\\settings.json")
    settings = json.load(file)
    file.close()
    return settings
settings = import_settings()


pygame.init()
window = pygame.display.set_mode((settings["window_length"], settings["window_height"]))
pygame.display.set_caption("PyBox")
pygame.display.set_icon(pygame.image.load(".\\assets\\images\\icons\\main.png").convert_alpha())
window.fill((0, 0, 0))


def get_key_states(_events, _states: dict = {}) -> dict:
    states = _states
    for event in _events:
        if event.type == pygame.KEYDOWN:
            states[event.key] = "down"
        if event.type == pygame.KEYUP:
            states[event.key] = "up"
    for state in states:
        if "_2" not in states[state]:
            states[state] += "_2"
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


class Data:
    tile_data = None
    mob_data = None
    def load(self) -> None:
        file = open(".\\data\\tiles.json")
        self.tile_data = json.load(file)
        file.close()
        file = open(".\\data\\mobs.json")
        self.mob_data = json.load(file)
        file.close()
    def __init__(self) -> None:
        self.load()
data = Data()


class Assets:
    tile_images = None
    mob_images = None
    def load(self) -> None:
        self.tile_images = {}
        self.mob_images = {}
        for id in data.tile_data.keys():
            self.tile_images[id] = pygame.image.load(".\\assets\\images\\tiles\\" + id + ".png").convert_alpha()
        for id in data.mob_data.keys():
            self.mob_images[id] = pygame.image.load(".\\assets\\images\\mobs\\" + id + ".png").convert_alpha()
    def __init__(self) -> None:
        self.load()
assets = Assets()


class Tile:
    id = None
    state = None
    def __init__(self, _id: str, _state: dict | None = None) -> None:
        self.id = _id
        if _state is None:
            self.state = data.tile_data[self.id]["state"]
        else:
            self.state = _state


class Mob:
    id = None
    state = None
    def __init__(self, _id: str, _state: dict | None = None) -> None:
        self.id = _id
        if _state is None:
            self.state = data.mob_data[self.id]["state"]
        else:
            self.state = _state


class World:
    default_settings = settings["default_world_settings"]
    settings = None
    map = None
    player = None
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
    def __init__(self, _settings: dict | None = default_settings) -> None:
        self.settings = _settings
        self.map = [[Tile("air") for y in range(self.settings["world_height"])] for x in range(self.settings["world_length"])]
        terrain = self.noise()
        for x in range(self.settings["world_length"]):
            for y in range(min(terrain[x], self.settings["world_height"])):
                self.map[x][y] = Tile("stone")
                if terrain[x] - y <= 4:
                    self.map[x][y] = Tile("soil")
                if terrain[x] - y == 1:
                    self.map[x][y] = Tile("grassy_soil")
        self.player = Mob("player")
        self.player.state["x"] = float(int(self.settings["world_length"] / 2))
        self.player.state["y"] = float(terrain[int(self.settings["world_length"] / 2)])
        self.player.state["mx"] = 0.0
        self.player.state["my"] = 0.0
    def mob_on_ground(self, _mob) -> bool:
        tile_coordinate = [[int(_mob.state["x"] + 0.03125), int(_mob.state["y"] - 0.03125)],
                            [int(_mob.state["x"] + 0.96875), int(_mob.state["y"] - 0.03125)]]
        for coordinate in tile_coordinate:
            if self.valid_coordinate(coordinate[0], coordinate[1]):
                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                    return True
        return False
    def move(self, _mob) -> Mob:
        if _mob.state["mx"] == 0 and _mob.state["my"] == 0: # move?
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
    def tick(self, _states) -> int:
        self.player.state["mx"] = 0.0
        self.player.state["my"] += self.settings["gravity"]
        if key_is_down(_states, pygame.K_SPACE):
            if self.mob_on_ground(self.player):
                self.player.state["my"] += 0.75
        if key_is_down(_states, pygame.K_a):
            self.player.state["mx"] = -data.mob_data["player"]["data"]["speed"]
        if key_is_down(_states, pygame.K_d):
            self.player.state["mx"] = data.mob_data["player"]["data"]["speed"]
        if key_is_down(_states, pygame.K_BACKQUOTE):
            settings["scale"] = 2
        else:
            settings["scale"] = 1
        if key_is_down(_states, pygame.K_DELETE):
            return 0
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
        player_image_unscaled = assets.mob_images["player"]
        player_image = pygame.transform.scale(player_image_unscaled, (16 * settings["scale"], 16 * settings["scale"]))
        window.blit(player_image, ((settings["window_length"] - 16 * settings["scale"]) / 2, (settings["window_height"] - 16 * settings["scale"]) / 2))
world = World()


def display(_x, _y):
    window.fill((0, 0, 0))
    world.display(_x, _y)
    pygame.display.flip()


return_value = -1
key_states = {}
while return_value == -1:
    start_tick_time = time.time()
    events = pygame.event.get()
    key_states = get_key_states(events, key_states)
    return_value = world.tick(key_states)
    display(world.player.state["x"], world.player.state["y"])
    stop_tick_time = time.time()
    while stop_tick_time - start_tick_time < 0.0625:
        stop_tick_time = time.time()
pygame.quit()
sys.exit(return_value)