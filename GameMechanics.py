from Resources import *
from typing import Any, Optional, Literal
import math
import random
import copy


class Object:
    id: str
    state: dict[str, Any]
    def set_to_json(self) -> dict:
        return {"id": self.id, "state": self.state}
    def get_from_json(self, _json: dict[str, Any]) -> None:
        self.id = _json["id"]
        self.state = _json["state"]
    def __init__(self, _json: dict[str, Any]) -> None:
        self.get_from_json(_json)


class Tile(Object):
    pass


class Liquid(Object):
    pass


class Structure(Object):
    def set_to_json(self) -> dict[str, Any]:
        return_value = {"id": self.id, "state": {"keys": self.keys, "tiles": self.tiles}}
        for key in self.keys:
            return_value["state"]["keys"][key] = self.state["keys"][key].set_to_json()
        return return_value
    def get_from_json(self, _json: dict[str, Any]) -> None:
        self.id = _json["id"]
        self.state = _json["state"]
        for key in self.keys:
            self.state["keys"][key] = Tile(_json["state"]["keys"][key])


class Item(Object):
    count: int
    def set_to_json(self) -> dict[str, Any]:
        return {"id": self.id, "count": self.count, "state": self.state}
    def get_from_json(self, _json: dict[str, Any]) -> None:
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
    def set_to_json(self) -> dict[str, Any]:
        return_value = {"id": self.id, "state": self.state}
        for slot_number in range(len(self.state["backpack"])):
            return_value["state"]["backpack"][slot_number] = self.state["backpack"][slot_number].set_to_json()
        return return_value
    def get_from_json(self, _json: dict[str, Any]) -> None:
        self.id = _json["id"]
        self.state = _json["state"]
        for slot_number in range(len(_json["state"]["backpack"])):
            self.state["backpack"][slot_number] = Item(_json["state"]["backpack"][slot_number])


class Character:
    character: str
    state: dict[str, Any]
    def set_default(self) -> None:
        self.state.setdefault("color", (255, 255, 255, 255))
    def __init__(self, _character: str, _state: Optional[dict[str, Any]] = {}) -> None:
        self.character = _character
        self.state = _state
        self.set_default()
    def display(self, _position: tuple[int, int], _scale: Optional[int] = 1) -> None:
        character_image_unscaled = assets.font_images[self.character]
        character_image_untinted = pygame.transform.scale(character_image_unscaled, (16 * _scale, 16 * _scale))
        character_image = change_image_color(character_image_untinted, pygame.Color(self.state["color"]))
        screen.blit(character_image, _position)


def display_text(_text: list[Character], _position: tuple[int, int], _scale: Optional[int] = 1, _alignment: str = "top_left") -> None:
    if _alignment == "top_left":
        for index in range(len(_text)):
            _text[index].display((_position[0] + (index * _scale * 16), _position[1]), _scale)
    elif _alignment == "top":
        for index in range(len(_text)):
            _text[index].display((_position[0] + (index * _scale * 16) - (len(_text) * _scale * 8), _position[1]), _scale)
    elif _alignment == "top_right":
        for index in range(len(_text)):
            _text[index].display((_position[0] + (index * _scale * 16) - (len(_text) * _scale * 16), _position[1]), _scale)
    elif _alignment == "left":
        for index in range(len(_text)):
            _text[index].display((_position[0] + (index * _scale * 16), _position[1] - (_scale * 8)), _scale)
    elif _alignment == "right":
        for index in range(len(_text)):
            _text[index].display((_position[0] + (index * _scale * 16) - (len(_text) * _scale * 16), _position[1] - (_scale * 8)), _scale)
    elif _alignment == "bottom_left":
        for index in range(len(_text)):
            _text[index].display((_position[0] + (index * _scale * 16), _position[1] - (_scale * 16)), _scale)
    elif _alignment == "bottom":
        for index in range(len(_text)):
            _text[index].display((_position[0] + (index * _scale * 16) - (len(_text) * _scale * 8), _position[1] - (_scale * 16)), _scale)
    elif _alignment == "bottom_right":
        for index in range(len(_text)):
            _text[index].display((_position[0] + (index * _scale * 16) - (len(_text) * _scale * 16), _position[1] - (_scale * 16)), _scale)
    else:
        for index in range(len(_text)):
            _text[index].display((_position[0] + (index * _scale * 16) - (len(_text) * _scale * 8), _position[1] - (_scale * 8)), _scale)


class World:
    settings: dict[str, Any]
    tiles: list[list[Tile]]
    liquids: list[list[Liquid]]
    player: Player
    mobs: list[Mob]
    def set_to_json(self) -> dict[str, Any]:
        json_tiles = []
        for x in range(self.settings["world_length"]):
            json_tiles.append([])
            for y in range(self.settings["world_height"]):
                json_tiles[x].append(self.tiles[x][y].set_to_json())
        json_mobs = []
        for mob_number in range(len(self.mobs)):
            json_mobs.append(self.mobs[mob_number].set_to_json())
        return {"tiles": json_tiles, "player": self.player.set_to_json(), "mobs": json_mobs, "settings": self.settings}
    def get_from_json(self, _json: dict[str, Any]) -> None:
        self.settings = _json["settings"]
        self.tiles = []
        for x in range(self.settings["world_length"]):
            self.tiles.append([])
            for y in range(self.settings["world_height"]):
                self.tiles[x].append(Tile(_json["tiles"][x][y]))
        self.player = Player(_json["player"])
        self.mobs = []
        for mob_number in range(len(_json["mobs"])):
            self.mobs.append(Mob(_json["mobs"][mob_number]))
    def valid_coordinate(self, _coordinate: tuple[int, int]) -> bool:
        return _coordinate[0] >= 0 and _coordinate[0] < self.settings["world_length"] and _coordinate[1] >= 0 and _coordinate[1] < self.settings["world_height"]
    def build_structure(self, _coordinate: tuple[int, int], _id: str) -> bool:
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
                        self.tiles[map_x][map_y] = Tile(structure["keys"][structure["tiles"][structure_y][structure_x]])
                        return_value = True
        return return_value
    def noise(self) -> list[int]:
        random.seed(int(self.settings["seed"].get()))
        terrain = [self.settings["world_height"] / 2 for i in range(self.settings["world_length"])]
        offset = [0 for i in range(self.settings["world_length"])]
        step_length = 1
        step_count = 0
        offset_1 = random.uniform(step_length * -0.25, step_length * 0.25)
        offset_2 = random.uniform(step_length * -0.25, step_length * 0.25)
        # generate height map
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
    def cave(self, _coordinate: tuple[int, int], _length: int) -> list[tuple[float, float]]:
        # generate cave
        return_value = []
        angle = random.random()
        angle_offset = (random.random() - 0.5) / 64
        coordinate = list(_coordinate)
        for i in range(_length):
            angle_offset += (random.random() - 0.5) / 64
            angle += angle_offset
            angle %= 1
            coordinate = (coordinate[0] + math.cos(angle * 2 * math.pi), coordinate[1] + math.sin(angle * 2 * math.pi))
            return_value.append(copy.deepcopy(coordinate))
        return return_value
    def create(self, _settings: dict[str, Any]) -> None:
        # create new world
        self.settings = _settings
        random.seed(int(self.settings["seed"].get()))
        print_info("Generating Terrain...")
        self.tiles = [[Tile({"id": "air", "state": {}}) for y in range(self.settings["world_height"])] for x in range(self.settings["world_length"])]
        self.liquids = [[Liquid({"id": "air", "state": {}}) for y in range(self.settings["world_height"])] for x in range(self.settings["world_length"])]
        terrain = self.noise()
        for x in range(self.settings["world_length"]):
            dirt_thick = random.choice(range(3, 6))
            for y in range(self.settings["world_height"]):
                if not self.valid_coordinate((x, y)):
                    break
                if y < terrain[x]:
                    if terrain[x] - y == 1:
                        if y >= self.settings["world_height"] / 2:
                            self.tiles[x][y] = Tile({"id": "grassy_soil", "state": {}})
                            random_number = random.choice(range(64))
                            if random_number == 0:
                                if self.valid_coordinate((x, y + 1)):
                                    self.tiles[x][y + 1] = Tile({"id": "sapling", "state": {}})
                            elif random_number == 1:
                                self.build_structure((x, y), "tree_3")
                            elif random_number == 2:
                                self.build_structure((x, y), "tree_4")
                            elif random_number == 3:
                                self.build_structure((x, y), "tree_5")
                            elif random_number <= 16:
                                if self.valid_coordinate((x, y + 1)):
                                    self.tiles[x][y + 1] = Tile({"id": "grass", "state": {}})
                        else:
                            self.tiles[x][y] = Tile({"id": "soil", "state": {}})
                    elif terrain[x] - y <= dirt_thick:
                        random_number = random.choice(range(16))
                        if random_number == 0:
                            self.tiles[x][y] = Tile({"id": "gravel", "state": {}})
                        else:
                            self.tiles[x][y] = Tile({"id": "soil", "state": {}})
                    else:
                        random_number = random.choice(range(int((y + self.settings["world_height"]) / 2)))
                        if random_number == 0:
                            self.tiles[x][y] = Tile({"id": "coal_ore", "state": {}})
                        elif random_number == 1:
                            self.tiles[x][y] = Tile({"id": "copper_ore", "state": {}})
                        elif random_number == 2:
                            self.tiles[x][y] = Tile({"id": "silver_ore", "state": {}})
                        elif random_number == 3:
                            self.tiles[x][y] = Tile({"id": "iron_ore", "state": {}})
                        elif random_number == 4:
                            self.tiles[x][y] = Tile({"id": "gold_ore", "state": {}})
                        else:
                            self.tiles[x][y] = Tile({"id": "stone", "state": {}})
                if y <= self.settings["world_height"] / 2 and "liquid_transparent" in data.tile_data[self.tiles[x][y].id]["tag"]:
                    self.liquids[x][y] = Liquid({"id": "water", "state": {"source": True}})
        print_info("Generating Cave...")
        for i in range(int(self.settings["world_length"] / 4)):
            cave_line = self.cave((random.choice(range(self.settings["world_length"])), random.choice(range(self.settings["world_height"]))), random.choice(range(16, 64)))
            for coordinate in range(len(cave_line)):
                for mx in range(-2, 3):
                    for my in range(-2, 3):
                        if self.valid_coordinate((cave_line[coordinate][0] + mx, cave_line[coordinate][1] + my)):
                            self.tiles[int(cave_line[coordinate][0] + mx)][int(cave_line[coordinate][1] + my)] = Tile({"id": "air", "state": {}})
        print_info("Creating Player...")
        self.player = Player({"id": "player", "state": copy.deepcopy(data.mob_data["player"]["state"])})
        self.player.state["health"] = data.mob_data["player"]["data"]["max_health"]
        self.player.state["coordinate"] = [self.settings["world_length"] / 2, float(terrain[int(self.settings["world_length"] / 2)])]
        self.player.state["movement"] = [0.0, 0.0]
        print_info("Creating Mobs...")
        self.mobs = []
        animal_ids = []
        for id in data.mob_data:
            if "animal" in data.mob_data[id]["tag"]:
                animal_ids.append(id)
        for mob_number in range(int(self.settings["world_length"] / 16)):
            random_animal_id = random.choice(animal_ids)
            self.mobs.append(Mob({"id": random_animal_id, "state": copy.deepcopy(data.mob_data[random_animal_id]["state"])}))
            random_x = random.choice(range(self.settings["world_length"]))
            self.mobs[mob_number].state["health"] = data.mob_data[self.mobs[mob_number].id]["data"]["max_health"]
            self.mobs[mob_number].state["coordinate"] = [float(random_x), float(terrain[int(random_x)])]
            self.mobs[mob_number].state["movement"] = [0.0, 0.0]
    def __init__(self, _json: dict[str, Any]) -> None:
        if _json["type"] == "new":
            print_info("Creating New World...")
            self.create(_json["settings"])
        elif _json["type"] == "load":
            print_info("Setting World From File...")
            self.get_from_json(_json["json"])
    def mob_on_ground(self, _mob) -> bool:
        # get tile's coordinate
        tile_coordinate = [[int(_mob.state["coordinate"][0] + 0.03125), int(_mob.state["coordinate"][1] - 0.03125)],
                           [int(_mob.state["coordinate"][0] + 0.96875), int(_mob.state["coordinate"][1] - 0.03125)]]
        for coordinate in tile_coordinate:
            if self.valid_coordinate(coordinate):
                if "mob_transparent" not in data.tile_data[self.tiles[coordinate[0]][coordinate[1]].id]["tag"]:
                    return True
        return False
    def move(self, _mob) -> tuple[float, float, float, float]:
        if _mob.state["movement"][0] == 0 and _mob.state["movement"][1] == 0:
            return (_mob.state["coordinate"][0], _mob.state["coordinate"][1], 0.0, 0.0)
        # get _mob's coordinate
        max_move = int(max(abs(_mob.state["movement"][0]), abs(_mob.state["movement"][1])) * 16)
        list_x = [0 for x in range(max_move + 1)]
        if _mob.state["movement"][0] != 0: # avoid mx / 0
            list_x = [int(x * _mob.state["movement"][0] * 16 / max_move) / 16 for x in range(max_move + 1)]
        list_y = [0 for y in range(max_move + 1)]
        if _mob.state["movement"][1] != 0: # avoid my / 0
            list_y = [int(y * _mob.state["movement"][1] * 16 / max_move) / 16 for y in range(max_move + 1)]
        # test the touch between _mob and tile
        for i in range(max_move + 1):
            # get tile's coordinate
            tile_coordinate = [[int(_mob.state["coordinate"][0] + list_x[i] + 0.03125), int(_mob.state["coordinate"][1] + list_y[i] + 0.03125)],
                               [int(_mob.state["coordinate"][0] + list_x[i] + 0.03125), int(_mob.state["coordinate"][1] + list_y[i] + 0.96875)],
                               [int(_mob.state["coordinate"][0] + list_x[i] + 0.96875), int(_mob.state["coordinate"][1] + list_y[i] + 0.03125)],
                               [int(_mob.state["coordinate"][0] + list_x[i] + 0.96875), int(_mob.state["coordinate"][1] + list_y[i] + 0.96875)]]
            for j in range(len(tile_coordinate)):
                if not self.valid_coordinate(tile_coordinate[j]):
                    return (self.settings["world_length"] / 2, self.settings["world_height"] - 1.0, 0.0, 0.0)
                # collapse
                return_value = [_mob.state["coordinate"][0], _mob.state["coordinate"][1], _mob.state["movement"][0], _mob.state["movement"][1]]
                if "mob_transparent" not in data.tile_data[self.tiles[tile_coordinate[j][0]][tile_coordinate[j][1]].id]["tag"]:
                    if _mob.state["movement"][0] > 0:
                        tile_coordinate = [[int(_mob.state["coordinate"][0] + list_x[i - 1] + 1.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 0.03125)],
                                           [int(_mob.state["coordinate"][0] + list_x[i - 1] + 1.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 0.96875)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.tiles[coordinate[0]][coordinate[1]].id]["tag"]:
                                    return_value[2] = 0.0
                    else:
                        tile_coordinate = [[int(_mob.state["coordinate"][0] + list_x[i - 1] - 0.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 0.03125)],
                                           [int(_mob.state["coordinate"][0] + list_x[i - 1] - 0.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 0.96875)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.tiles[coordinate[0]][coordinate[1]].id]["tag"]:
                                    return_value[2] = 0.0
                    if _mob.state["movement"][1] > 0:
                        tile_coordinate = [[int(_mob.state["coordinate"][0] + list_x[i - 1] + 0.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 1.03125)],
                                           [int(_mob.state["coordinate"][0] + list_x[i - 1] + 0.96875), int(_mob.state["coordinate"][1] + list_y[i - 1] + 1.03125)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.tiles[coordinate[0]][coordinate[1]].id]["tag"]:
                                    return_value[3] = 0.0
                    else:
                        tile_coordinate = [[int(_mob.state["coordinate"][0] + list_x[i - 1] + 0.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] - 0.03125)],
                                           [int(_mob.state["coordinate"][0] + list_x[i - 1] + 0.96875), int(_mob.state["coordinate"][1] + list_y[i - 1] - 0.03125)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.tiles[coordinate[0]][coordinate[1]].id]["tag"]:
                                    return_value[3] = 0.0
                    return_value[0] = _mob.state["coordinate"][0] + list_x[i - 1]
                    return_value[1] = _mob.state["coordinate"][1] + list_y[i - 1]
                    return tuple(return_value)
        return_value[0] = _mob.state["coordinate"][0] + list_x[-1]
        return_value[1] = _mob.state["coordinate"][1] + list_y[-1]
        return tuple(return_value)
    def mouse_to_map(self, _mouse_position: tuple[int, int], _world_coordinate: tuple[float, float]) -> tuple[float, float]:
        x_coordinate = -((default_settings["pygame_window_length"] / 2 - _mouse_position[0]) / 16 / settings["map_scale"]) + 0.5 + _world_coordinate[0]
        y_coordinate = ((default_settings["pygame_window_height"] / 2 - _mouse_position[1]) / 16 / settings["map_scale"]) + 0.5 + _world_coordinate[1]
        return (x_coordinate, y_coordinate)
    def break_tile(self, _coordinate: tuple[int, int]) -> bool:
        # is this coordinate valid?
        if not self.valid_coordinate(_coordinate):
            return False
        # is this tile breakable?
        current_tile = self.tiles[int(_coordinate[0])][int(_coordinate[1])]
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
        self.tiles[int(_coordinate[0])][int(_coordinate[1])] = Tile({"id": "air", "state": {}})
        return True
    def place_tile(self, _coordinate: tuple[int, int]) -> bool:
        # is this coordinate valid?
        if not self.valid_coordinate(_coordinate):
            return False
        # is this tile replaceable?
        current_tile = self.tiles[int(_coordinate[0])][int(_coordinate[1])]
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
        self.tiles[int(_coordinate[0])][int(_coordinate[1])] = Tile(data.item_data[current_item.id]["data"]["to_tile"])
        return True
    def tick(self, _key_states: dict[int, str], _mouse_states: dict[str, Any]) -> str:
        # quit game
        if key_is_just_down(_key_states, pygame.K_DELETE):
            return "quit"
        # jump test
        if self.mob_on_ground(self.player):
            if key_is_down(_key_states, pygame.K_SPACE):
                self.player.state["movement"][1] = self.settings["jump_speed"]
            else:
                self.player.state["movement"][1] = 0.0
        else:
            self.player.state["movement"][1] += self.settings["gravity"]
        # move left/right
        self.player.state["movement"][0] = 0.0
        if key_is_down(_key_states, pygame.K_a):
            self.player.state["movement"][0] = -data.mob_data["player"]["data"]["speed"]
        if key_is_down(_key_states, pygame.K_d):
            self.player.state["movement"][0] = data.mob_data["player"]["data"]["speed"]
        # zoom
        if key_is_down(_key_states, pygame.K_BACKQUOTE):
            settings["map_scale"] = default_settings["default_map_scale"] * 2
        else:
            settings["map_scale"] = default_settings["default_map_scale"]
        # select backpack
        self.player.state["selected_slot"] += _mouse_states["scroll_down"] - _mouse_states["scroll_up"]
        self.player.state["selected_slot"] %= data.mob_data["player"]["data"]["max_slot"]
        # map changes
        mouse_in_map = self.mouse_to_map(_mouse_states["position"], tuple(self.player.state["coordinate"]))
        if key_is_down(_mouse_states, "left"):
            self.break_tile(mouse_in_map)
        if key_is_down(_mouse_states, "right"):
            self.place_tile(mouse_in_map)
        new_tiles = copy.deepcopy(self.tiles)
        print("copy good")
        new_liquids = copy.deepcopy(self.liquids)
        loading_range = 64
        for x in range(int(self.player.state["coordinate"][0]) - loading_range, int(self.player.state["coordinate"][0]) + loading_range + 1):
            for y in range(int(self.player.state["coordinate"][1]) - loading_range, int(self.player.state["coordinate"][1]) + loading_range + 1):
                if self.valid_coordinate((x, y)):
                    if "need_support_tile" in data.tile_data[self.tiles[x][y].id]["tag"]:
                        if self.valid_coordinate((x, y - 1)):
                            if "cant_be_support_tile" in data.tile_data[self.tiles[x][y - 1].id]["tag"]:
                                new_tiles[x][y] = Tile({"id": "air", "state": {}})
                    if "falling_tile" in data.tile_data[self.tiles[x][y].id]["tag"]:
                        if self.valid_coordinate((x, y - 1)):
                            if "replaceable" in data.tile_data[self.tiles[x][y - 1].id]["tag"]:
                                new_tiles[x][y - 1] = self.tiles[x][y]
                                new_tiles[x][y] = Tile({"id": "air", "state": {}})
        for x in range(int(self.player.state["coordinate"][0]) - loading_range, int(self.player.state["coordinate"][0]) + loading_range + 1):
            for y in range(int(self.player.state["coordinate"][1]) - loading_range, int(self.player.state["coordinate"][1]) + loading_range + 1):
                if self.valid_coordinate((x, y)):
                    if self.liquids[x][y].id != "air":
                        if "liquid_transparent" not in data.tile_data[self.tiles[x][y].id]["tag"]:
                            new_liquids[x][y] = Liquid({"id": "air", "state": {}})
                        if "liquid_breakable" in data.tile_data[self.tiles[x][y].id]["tag"]:
                            new_tiles[x][y] = Tile({"id": "air", "state": {}})
        for x in range(int(self.player.state["coordinate"][0]) - loading_range, int(self.player.state["coordinate"][0]) + loading_range + 1):
            for y in range(int(self.player.state["coordinate"][1]) - loading_range, int(self.player.state["coordinate"][1]) + loading_range + 1):
                if self.valid_coordinate((x, y)):
                    if self.liquids[x][y].id != "air":
                        current_liquid_id = self.liquids[x][y].id
                        if self.valid_coordinate((x, y - 1)):
                            liquid_fall = False
                            if "liquid_transparent" in data.tile_data[self.tiles[x][y - 1].id]["tag"]:
                                liquid_fall = True
                            if "liquid_breakable" in data.tile_data[self.tiles[x][y - 1].id]["tag"]:
                                new_tiles[x][y - 1] = Tile({"id": "air", "state": {}})
                                liquid_fall = True
                            if self.liquids[x][y].state["source"] == False:
                                if self.liquids[x][y - 1].id != "air" and self.liquids[x][y - 1].state["source"] == True:
                                    liquid_fall = True
                            if liquid_fall == True:
                                if self.liquids[x][y].state["source"] == False:
                                    new_liquids[x][y] = Liquid({"id": "air", "state": {}})
                                new_liquids[x][y - 1] = Liquid({"id": current_liquid_id, "state": {"source": False}})
        for x in range(int(self.player.state["coordinate"][0]) - loading_range, int(self.player.state["coordinate"][0]) + loading_range + 1):
            for y in range(int(self.player.state["coordinate"][1]) - loading_range, int(self.player.state["coordinate"][1]) + loading_range + 1):
                if self.valid_coordinate((x, y)):
                    if self.liquids[x][y].id != "air":
                        current_liquid_id = self.liquids[x][y].id
                        if self.valid_coordinate((x, y - 1)):
                            liquid_spread = False
                            if "liquid_transparent" not in data.tile_data[self.tiles[x][y - 1].id]["tag"]:
                                liquid_spread = True
                            if self.liquids[x][y].state["source"] == True:
                                if self.liquids[x][y - 1].id != "air" and self.liquids[x][y - 1].state["source"] == True:
                                    liquid_spread = True
                            if liquid_spread == True:
                                if self.liquids[x][y].state["source"] == False:
                                    new_liquids[x][y] = Liquid({"id": "air", "state": {}})
                                if self.valid_coordinate((x - 1, y)):
                                    if "liquid_transparent" in data.tile_data[self.tiles[x - 1][y].id]["tag"]:
                                        new_liquids[x - 1][y] = Liquid({"id": current_liquid_id, "state": {"source": False}})
                                    if "liquid_breakable" in data.tile_data[self.tiles[x - 1][y].id]["tag"]:
                                        new_tiles[x - 1][y] = Tile({"id": "air", "state": {}})
                                        new_liquids[x - 1][y] = Liquid({"id": current_liquid_id, "state": {"source": False}})
                                if self.valid_coordinate((x + 1, y)):
                                    if "liquid_transparent" in data.tile_data[self.tiles[x + 1][y].id]["tag"]:
                                        new_liquids[x + 1][y] = Liquid({"id": current_liquid_id, "state": {"source": False}})
                                    if "liquid_breakable" in data.tile_data[self.tiles[x + 1][y].id]["tag"]:
                                        new_tiles[x + 1][y] = Tile({"id": "air", "state": {}})
                                        new_liquids[x + 1][y] = Liquid({"id": current_liquid_id, "state": {"source": False}})
        self.tiles = copy.deepcopy(new_tiles)
        self.liquids = copy.deepcopy(new_liquids)
        # remove hurt effect
        self.player.state["hurt"] = False
        for mob_number in range(len(self.mobs)):
            self.mobs[mob_number].state["hurt"] = False
        # attack mobs
        if key_is_just_down(_mouse_states, "left"):
            if "weapon" in data.item_data[self.player.state["backpack"][self.player.state["selected_slot"]].id]["tag"]:
                for mob_number in range(len(self.mobs)):
                    if abs(self.mobs[mob_number].state["coordinate"][0] - mouse_in_map[0] + 0.5) <= 0.5 and abs(self.mobs[mob_number].state["coordinate"][1] - mouse_in_map[1] + 0.5) <= 0.5:
                        self.mobs[mob_number].state["health"] -= data.item_data[self.player.state["backpack"][self.player.state["selected_slot"]].id]["data"]["weapon_info"]["damage"]
                        self.mobs[mob_number].state["hurt"] = True
        # player respawn
        if self.player.state["health"] <= 0:
            top_y = self.settings["world_height"] - 1
            while top_y > 0:
                if "mob_transparent" not in data.tile_data[self.tiles[int(self.settings["world_length"] / 2)][top_y].id]["tag"]:
                    break
                top_y -= 1
            self.player.state["coordinate"] = [float(self.settings["world_length"] / 2), float(top_y + 1)]
            self.player.state["movement"] = [0.0, 0.0]
            self.player.state["health"] = data.mob_data["player"]["data"]["max_health"]
        # replace no health mobs to new mobs
        animal_ids = []
        for id in data.mob_data:
            if "animal" in data.mob_data[id]["tag"]:
                animal_ids.append(id)
        for mob_number in range(len(self.mobs)):
            if self.mobs[mob_number].state["health"] <= 0:
                random_animal_id = random.choice(animal_ids)
                self.mobs[mob_number] = Mob({"id": random_animal_id, "state": copy.deepcopy(data.mob_data[random_animal_id]["state"])})
                random_x = random.choice(range(self.settings["world_length"]))
                top_y = self.settings["world_height"] - 1
                while top_y > 0:
                    if "mob_transparent" not in data.tile_data[self.tiles[random_x][top_y].id]["tag"]:
                        break
                    top_y -= 1
                self.mobs[mob_number].state["coordinate"] = [float(random_x), float(top_y + 1)]
                self.mobs[mob_number].state["movement"] = [0.0, 0.0]
                self.mobs[mob_number].state["health"] = data.mob_data[self.mobs[mob_number].id]["data"]["max_health"]
        # move player
        coordinate = self.move(self.player)
        self.player.state["coordinate"][0] = coordinate[0]
        self.player.state["coordinate"][1] = coordinate[1]
        self.player.state["movement"][0] = coordinate[2]
        self.player.state["movement"][1] = coordinate[3]
        if not self.mob_on_ground(self.player):
            self.player.state["falling_time"] += 1
        else:
            if self.player.state["falling_time"] > 24:
                self.player.state["health"] -= self.player.state["falling_time"] - 24
                self.player.state["hurt"] = True
            self.player.state["falling_time"] = 0
        # move mobs
        for mob_number in range(len(self.mobs)):
            if random.choice(range(16)) == 0:
                self.mobs[mob_number].state["action"] = random.choice(data.mob_data[self.mobs[mob_number].id]["data"]["actions"])
            if self.mob_on_ground(self.mobs[mob_number]):
                if self.mobs[mob_number].state["action"] == "jump":
                    self.mobs[mob_number].state["movement"][1] = self.settings["jump_speed"]
                else:
                    self.mobs[mob_number].state["movement"][1] = 0.0
            else:
                self.mobs[mob_number].state["movement"][1] += self.settings["gravity"]
            if self.mobs[mob_number].state["action"] == "left":
                self.mobs[mob_number].state["movement"][0] = -data.mob_data[self.mobs[mob_number].id]["data"]["speed"]
            elif self.mobs[mob_number].state["action"] == "right":
                self.mobs[mob_number].state["movement"][0] = data.mob_data[self.mobs[mob_number].id]["data"]["speed"]
            else:
                self.mobs[mob_number].state["movement"][0] = 0.0
            coordinate = self.move(self.mobs[mob_number])
            self.mobs[mob_number].state["coordinate"][0] = coordinate[0]
            self.mobs[mob_number].state["coordinate"][1] = coordinate[1]
            self.mobs[mob_number].state["movement"][0] = coordinate[2]
            self.mobs[mob_number].state["movement"][1] = coordinate[3]
            if not self.mob_on_ground(self.mobs[mob_number]):
                self.mobs[mob_number].state["falling_time"] += 1
            else:
                if self.mobs[mob_number].state["falling_time"] > 24:
                    self.mobs[mob_number].state["health"] -= self.mobs[mob_number].state["falling_time"] - 24
                    self.mobs[mob_number].state["hurt"] = True
                self.mobs[mob_number].state["falling_time"] = 0
        if key_is_just_down(_key_states, pygame.K_c):
            return "craft"
        return "do_nothing"
    def crafts(self, _key_states: dict[int, str], _mouse_states: dict[str, Any]) -> str:
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


def display_world(_world: World, _coordinate: tuple[float, float]) -> None:
    pygame_window.fill("#80C0FF")
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
            if not _world.valid_coordinate((tile_x, tile_y)):
                continue
            if "display_transparent" not in data.liquid_data[_world.liquids[tile_x][tile_y].id]["tag"]:
                liquid_image_unscaled = assets.liquid_images[_world.liquids[tile_x][tile_y].id]
                liquid_image = pygame.transform.scale(liquid_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
                liquid_image_position = ((int((offset_x - float_x) * 16 - 8) * settings["map_scale"]) + default_settings["pygame_window_length"] / 2,
                                         (int((offset_y - float_y) * -16 - 8) * settings["map_scale"]) + default_settings["pygame_window_height"] / 2)
                screen.blit(liquid_image, liquid_image_position)
            if "display_transparent" not in data.tile_data[_world.tiles[tile_x][tile_y].id]["tag"]:
                tile_image_unscaled = assets.tile_images[_world.tiles[tile_x][tile_y].id]
                tile_image = pygame.transform.scale(tile_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
                tile_image_position = ((int((offset_x - float_x) * 16 - 8) * settings["map_scale"]) + default_settings["pygame_window_length"] / 2,
                                       (int((offset_y - float_y) * -16 - 8) * settings["map_scale"]) + default_settings["pygame_window_height"] / 2)
                screen.blit(tile_image, tile_image_position)
    # display mobs
    for mob_number in range(len(_world.mobs)):
        mob_image_unscaled = assets.mob_images[_world.mobs[mob_number].id]
        mob_image = pygame.transform.scale(mob_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
        if _world.mobs[mob_number].state["hurt"] == True:
            mob_image = tint_image(mob_image, pygame.Color(255, 0, 0, 128))
        mob_image_position = (int(((_world.mobs[mob_number].state["coordinate"][0] - _coordinate[0]) * 16 - 8) * settings["map_scale"]) + default_settings["pygame_window_length"] / 2,
                              int(((_world.mobs[mob_number].state["coordinate"][1] - _coordinate[1]) * -16 - 8) * settings["map_scale"]) + default_settings["pygame_window_height"] / 2)
        if mob_image_position[0] > -16 * settings["map_scale"] and mob_image_position[0] < default_settings["pygame_window_length"]:
            if mob_image_position[1] > -16 * settings["map_scale"] and mob_image_position[1] < default_settings["pygame_window_height"]:
                screen.blit(mob_image, mob_image_position)
    # display player
    player_image_unscaled = assets.mob_images["player"]
    player_image = pygame.transform.scale(player_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
    if _world.player.state["hurt"] == True:
        player_image = tint_image(player_image, pygame.Color(255, 0, 0, 128))
    player_image_position = (int(((_world.player.state["coordinate"][0] - _coordinate[0]) * 16 - 8) * settings["map_scale"]) + default_settings["pygame_window_length"] / 2,
                             int(((_world.player.state["coordinate"][1] - _coordinate[1]) * -16 - 8) * settings["map_scale"]) + default_settings["pygame_window_height"] / 2)
    screen.blit(player_image, player_image_position)
    # display health
    player_max_health = data.mob_data["player"]["data"]["max_health"]
    player_health = _world.player.state["health"]
    health_bar_background_image = pygame.Surface((16 * settings["gui_scale"] * data.mob_data["player"]["data"]["max_slot"], 16 * settings["gui_scale"])).convert_alpha()
    health_bar_foreground_image = pygame.Surface((int((16 * settings["gui_scale"] * data.mob_data["player"]["data"]["max_slot"]) / player_max_health * player_health), 16 * settings["gui_scale"])).convert_alpha()
    health_bar_background_image.fill("#80000080")
    health_bar_foreground_image.fill("#FF0000FF")
    health_bar_position = (int(default_settings["pygame_window_length"] / 2 - (8 * data.mob_data["player"]["data"]["max_slot"] * settings["gui_scale"])),
                           int(default_settings["pygame_window_height"] - (32 * settings["gui_scale"])))
    screen.blit(health_bar_background_image, health_bar_position)
    screen.blit(health_bar_foreground_image, health_bar_position)
    # display the backpack
    backpack = _world.player.state["backpack"]
    slot_image = pygame.Surface((16 * settings["gui_scale"], 16 * settings["gui_scale"])).convert_alpha()
    for slot in range(len(backpack)):
        item_image_unscaled = assets.item_images[backpack[slot].id]
        item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
        item_image_position = (int((slot * 16 - data.mob_data["player"]["data"]["max_slot"] * 8) * settings["gui_scale"] + default_settings["pygame_window_length"] / 2),
                               int(default_settings["pygame_window_height"] - 16 * settings["gui_scale"]))
        if slot == _world.player.state["selected_slot"]:
            slot_image.fill("#8000FF80")
        else:
            slot_image.fill("#8040C080")
        screen.blit(slot_image, item_image_position)
        screen.blit(item_image, item_image_position)
    # display selected item's name
    item_info = str(_world.player.state["backpack"][_world.player.state["selected_slot"]].count) + "*" + data.item_data[_world.player.state["backpack"][_world.player.state["selected_slot"]].id]["name"]
    item_info_displayable = [Character(item_info[i]) for i in range(len(item_info))]
    display_text(item_info_displayable, (default_settings["pygame_window_length"] / 2, default_settings["pygame_window_height"] - settings["gui_scale"] * 16), settings["gui_scale"], "bottom")
    # display debug screen
    if settings["debug"] == True:
        player_coordinate = str(int(_world.player.state["coordinate"][0])) + "," + str(int(_world.player.state["coordinate"][1]))
        for character_number in range(len(player_coordinate)):
            character_image_unscaled = assets.font_images[player_coordinate[character_number]]
            character_image = pygame.transform.scale(character_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
            character_image_position = (int(character_number * 16 * settings["gui_scale"]), 0)
            screen.blit(character_image, character_image_position)


def display_craft(_world: World) -> None:
    if _world.player.state["temporary"]["successful_crafting"] == "true":
        pygame_window.fill("#008000")
    elif _world.player.state["temporary"]["successful_crafting"] == "false":
        pygame_window.fill("#800000")
    else:
        pygame_window.fill("#000000")
    screen.fill("#00000000")
    # display all the recipes
    slot_image = pygame.Surface((16 * settings["gui_scale"], 16 * settings["gui_scale"])).convert_alpha()
    selected_recipe = _world.player.state["temporary"]["selected_recipe"]
    for recipe in range(len(data.recipe_data)):
        for slot in range(len(data.recipe_data[recipe]["from"])):
            item_image_unscaled = assets.item_images[data.recipe_data[recipe]["from"][slot]["id"]]
            item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
            item_image_position = (int(((recipe - selected_recipe) * 16 - 8) * settings["gui_scale"] + default_settings["pygame_window_length"] / 2),
                                   int((slot + 1) * 16 * settings["gui_scale"]))
            if recipe == selected_recipe:
                slot_image.fill("#FF000080")
            else:
                slot_image.fill("#C0404080")
            screen.blit(slot_image, item_image_position)
            screen.blit(item_image, item_image_position)
        item_image_unscaled = assets.item_images[data.recipe_data[recipe]["to"][0]["id"]]
        item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
        item_image_position = (int(((recipe - selected_recipe) * 16 - 8) * settings["gui_scale"] + default_settings["pygame_window_length"] / 2), 0)
        if recipe == selected_recipe:
            slot_image.fill("#00FF0080")
        else:
            slot_image.fill("#40C04080")
        screen.blit(slot_image, item_image_position)
        screen.blit(item_image, item_image_position)
    # display the backpack
    backpack = _world.player.state["backpack"]
    for slot in range(len(backpack)):
        item_image_unscaled = assets.item_images[backpack[slot].id]
        item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
        item_image_position = (int((slot * 16 - data.mob_data["player"]["data"]["max_slot"] * 8) * settings["gui_scale"] + default_settings["pygame_window_length"] / 2),
                               int(default_settings["pygame_window_height"] - 16 * settings["gui_scale"]))
        slot_image.fill("#80808080")
        screen.blit(slot_image, item_image_position)
        screen.blit(item_image, item_image_position)
    # display selected recipe's name
    item_info = str(data.recipe_data[selected_recipe]["to"][0]["count"]) + "*" + data.item_data[data.recipe_data[selected_recipe]["to"][0]["id"]]["name"]
    item_info_displayable = [Character(item_info[i]) for i in range(len(item_info))]
    display_text(item_info_displayable, (default_settings["pygame_window_length"] / 2, default_settings["pygame_window_height"] - settings["gui_scale"] * 16), settings["gui_scale"], "bottom")