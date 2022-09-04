import pygame
import math
import random
import json
import sys


def hexadecimal(_number: int):
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
    block_data = None
    def load(self) -> None:
        file = open(".\\data\\blocks.json")
        self.block_data = json.load(file)
        file.close()
    def __init__(self) -> None:
        self.load()
data = Data()


class Assets:
    block_images = None
    def load(self) -> None:
        self.block_images = {}
        print(data.block_data)
        for id in data.block_data.keys():
            self.block_images[id] = pygame.image.load(".\\assets\\images\\blocks\\" + id + ".png").convert_alpha()
    def __init__(self) -> None:
        self.load()
assets = Assets()


class Block:
    id = None
    state = None
    def __init__(self, _id: str, _state: dict = {}) -> None:
        self.id = _id
        self.state = _state
    def __str__(self) -> str:
        return str(self.id) + str(self.state)


class World:
    default_settings = {"seed": 0, "world_length": 64, "world_height": 48}
    settings = None
    map = None
    def valid_coordinate(self, _x, _y):
        return _x >= 0 and _x < self.settings["world_length"] and _y >= 0 and _y < self.settings["world_height"]
    def noise(self, _seed: int) -> list:
        random.seed(_seed)
        curve = [self.settings["world_height"] / 2 for i in range(self.settings["world_length"])]
        height_value = self.settings["world_height"] / 2
        first_step = self.settings["world_length"] / 4
        step_divider = 1
        step_length = first_step / step_divider
        while step_length >= 1:
            for x in range(self.settings["world_length"]):
                if x % step_length == 0:
                    height_value = random.uniform(self.settings["world_height"] * -0.0625 / step_divider, self.settings["world_height"] * 0.0625 / step_divider)
                curve[x] += height_value
            step_divider *= 2
            step_length = first_step / step_divider
        for x in range(self.settings["world_length"]):
            curve[x] = int(curve[x])
        return curve
    def __init__(self, _settings: dict = default_settings) -> None:
        self.settings = _settings
        self.map = [[Block("air") for j in range(self.settings["world_height"])] for i in range(self.settings["world_length"])]
        terrain = self.noise(self.settings["seed"])
        for x in range(self.settings["world_length"]):
            for y in range(terrain[x]):
                self.map[x][y] = Block("test_block")
    def __str__(self) -> str:
        return "World"
    def display(self, _x = 0, _y = 0) -> None:
        float_x = math.modf(_x)[0]
        float_y = math.modf(_y)[0]
        int_x = int(_x)
        int_y = int(_y)
        for y in range(int_x - 64, int_x + 65):
            for x in range(int_y - 64, int_y + 65):
                if not self.valid_coordinate(x, y):
                    continue
                current_block = self.map[x][y]
                current_image = assets.block_images[current_block.id]
                current_image_scaled = pygame.transform.scale(current_image, (16 * settings.scale, 16 * settings.scale))
                current_image_position = ((int((x + float_x) * 16) * settings.scale), (int((y + float_y) * 16) * settings.scale))
                window.blit(current_image_scaled, current_image_position)


def display():
    window.fill((0, 0, 0))
    world.display(32, 24.25)
    pygame.display.flip()


world = World()
return_value = -1
while return_value == -1:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            return_value = 0
    display()
    pygame.time.delay(100)
pygame.quit()
sys.exit(return_value)