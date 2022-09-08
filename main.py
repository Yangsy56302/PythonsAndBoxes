import pygame
import math
import random
import json
import sys


def hexadecimal(_number: int) -> str:
    return hex(_number).upper()[2:]


class Settings:
    scale = 1
    def __init__(self) -> None:
        pass
settings = Settings()


pygame.init()
window = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("PyBox")
window.fill((0, 255, 0))


class Data:
    tile_data = None
    mob_data = None
    def load(self) -> None:
        file = open(".\\data\\tiles.json")
        self.tile_data = json.load(file)
        file = open(".\\data\\mobs.json")
        self.mob_data = json.load(file)
        file.close()
    def __init__(self) -> None:
        self.load()
data = Data()


class Assets:
    tile_images = None
    def load(self) -> None:
        self.tile_images = {}
        print(data.tile_data)
        for id in data.tile_data.keys():
            self.tile_images[id] = pygame.image.load(".\\assets\\images\\tiles\\" + id + ".png").convert_alpha()
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
    default_settings = {"seed": 0, "world_length": 4096, "world_height": 256}
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
        self.player.state["x"] = 999.0
        self.player.state["y"] = float(terrain[999])
    def tick(self, _events) -> None:
        for event in _events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.player.state["y"] += 0.25
                if event.key == pygame.K_s:
                    self.player.state["y"] -= 0.25
                if event.key == pygame.K_a:
                    self.player.state["x"] -= 0.25
                if event.key == pygame.K_d:
                    self.player.state["x"] += 0.25
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
                current_image = pygame.transform.scale(current_image_unscaled, (16 * settings.scale, 16 * settings.scale))
                current_image_position = ((int((offset_x - float_x) * 16) * settings.scale) + 512, (int((offset_y - float_y) * -16) * settings.scale) + 384)
                window.blit(current_image, current_image_position)
world = World()


def display(_x, _y):
    window.fill((0, 0, 0))
    world.display(_x, _y)
    pygame.display.flip()


return_value = -1
while return_value == -1:
    events = pygame.event.get()
    world.tick(events)
    print(world.player.state["x"], world.player.state["y"])
    display(world.player.state["x"], world.player.state["y"])
    pygame.time.delay(100)
pygame.quit()
sys.exit(return_value)