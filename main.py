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
    default_settings = {"seed": 0, "world_length": 4096, "world_height": 256}
    settings = None
    map = None
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
    def __init__(self, _settings: dict = default_settings) -> None:
        self.settings = _settings
        self.map = [[Block("air") for y in range(self.settings["world_height"])] for x in range(self.settings["world_length"])]
        terrain = self.noise()
        for x in range(self.settings["world_length"]):
            for y in range(min(terrain[x], self.settings["world_height"])):
                self.map[x][y] = Block("stone")
                if terrain[x] - y <= 4:
                    self.map[x][y] = Block("soil")
                if terrain[x] - y == 1:
                    self.map[x][y] = Block("grassy_soil")
    def __str__(self) -> str:
        return "World"
    def display(self, _x, _y) -> None:
        float_x = math.modf(_x)[0]
        float_y = math.modf(_y)[0]
        int_x = int(_x)
        int_y = int(_y)
        for offset_x in range(-64, 65):
            for offset_y in range(-64, 65):
                block_x = offset_x + int_x
                block_y = offset_y + int_y
                if not self.valid_coordinate(block_x, block_y):
                    continue
                current_block = self.map[block_x][block_y]
                current_image_unscaled = assets.block_images[current_block.id]
                current_image = pygame.transform.scale(current_image_unscaled, (16 * settings.scale, 16 * settings.scale))
                current_image_position = ((int((offset_x + float_x) * 16) * settings.scale) + 512, (int((offset_y - float_y) * -16) * settings.scale) + 384)
                window.blit(current_image, current_image_position)
world = World()


def display(_x, _y):
    window.fill((0, 0, 0))
    world.display(_x, _y)
    pygame.display.flip()


test_x = 1024
test_y = 128
return_value = -1
while return_value == -1:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            return_value = 0
    print(test_x, test_y)
    display(test_x, test_y)
    test_x += 4
    pygame.time.delay(100)
pygame.quit()
sys.exit(return_value)