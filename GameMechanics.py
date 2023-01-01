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
    map: list[list[Tile]]
    player: Player
    mobs: list[Mob]
    def set_to_json(self) -> dict[str, Any]:
        json_map = []
        for x in range(self.settings["world_length"]):
            json_map.append([])
            for y in range(self.settings["world_height"]):
                json_map[x].append(self.map[x][y].set_to_json())
        json_mobs = []
        for mob_number in range(len(self.mobs)):
            json_mobs.append(self.mobs[mob_number].set_to_json())
        return {"map": json_map, "player": self.player.set_to_json(), "mobs": json_mobs, "settings": self.settings}
    def get_from_json(self, _json: dict[str, Any]) -> None:
        self.settings = _json["settings"]
        self.map = []
        for x in range(self.settings["world_length"]):
            self.map.append([])
            for y in range(self.settings["world_height"]):
                self.map[x].append(Tile(_json["map"][x][y]))
        self.player = Player(_json["player"])
        for mob_number in range(len(_json.mobs)):
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
                        self.map[map_x][map_y] = Tile(structure["keys"][structure["tiles"][structure_y][structure_x]])
                        return_value = True
        return return_value
    def noise(self) -> list[int]:
        random.seed(self.settings["seed"])
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
        # create new self
        self.settings = _settings
        print_info("Generating Terrain...")
        self.map = [[Tile({"id": "air", "state": {}}) for y in range(self.settings["world_height"])] for x in range(self.settings["world_length"])]
        terrain = self.noise()
        for x in range(self.settings["world_length"]):
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
                    random_number = random.choice(range(int((y + self.settings["world_height"]) / 2)))
                    if random_number == 0:
                        self.map[x][y] = Tile({"id": "coal_ore", "state": {}})
                    elif random_number == 1:
                        self.map[x][y] = Tile({"id": "copper_ore", "state": {}})
                    elif random_number == 2:
                        self.map[x][y] = Tile({"id": "silver_ore", "state": {}})
                    elif random_number == 3:
                        self.map[x][y] = Tile({"id": "iron_ore", "state": {}})
                    elif random_number == 4:
                        self.map[x][y] = Tile({"id": "gold_ore", "state": {}})
                    else:
                        self.map[x][y] = Tile({"id": "stone", "state": {}})
        print_info("Generating Cave...")
        for i in range(int(self.settings["world_length"] / 4)):
            cave_line = self.cave((random.choice(range(self.settings["world_length"])), random.choice(range(self.settings["world_height"]))), random.choice(range(16, 64)))
            for coordinate in range(len(cave_line)):
                for mx in range(-2, 3):
                    for my in range(-2, 3):
                        if self.valid_coordinate((cave_line[coordinate][0] + mx, cave_line[coordinate][1] + my)):
                            self.map[int(cave_line[coordinate][0] + mx)][int(cave_line[coordinate][1] + my)] = Tile({"id": "air", "state": {}})
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
        if _json == {}:
            print_info("Creating New World...")
            self.create(settings["default_world_settings"])
        else:
            print_info("Loading World File...")
            self.get_from_json(_json)
    def mob_on_ground(self, _mob) -> bool:
        # get tile's coordinate
        tile_coordinate = [[int(_mob.state["coordinate"][0] + 0.03125), int(_mob.state["coordinate"][1] - 0.03125)],
                           [int(_mob.state["coordinate"][0] + 0.96875), int(_mob.state["coordinate"][1] - 0.03125)]]
        for coordinate in tile_coordinate:
            if self.valid_coordinate(coordinate):
                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
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
                if "mob_transparent" not in data.tile_data[self.map[tile_coordinate[j][0]][tile_coordinate[j][1]].id]["tag"]:
                    if _mob.state["movement"][0] > 0:
                        tile_coordinate = [[int(_mob.state["coordinate"][0] + list_x[i - 1] + 1.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 0.03125)],
                                           [int(_mob.state["coordinate"][0] + list_x[i - 1] + 1.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 0.96875)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    return_value[2] = 0.0
                    else:
                        tile_coordinate = [[int(_mob.state["coordinate"][0] + list_x[i - 1] - 0.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 0.03125)],
                                           [int(_mob.state["coordinate"][0] + list_x[i - 1] - 0.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 0.96875)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    return_value[2] = 0.0
                    if _mob.state["movement"][1] > 0:
                        tile_coordinate = [[int(_mob.state["coordinate"][0] + list_x[i - 1] + 0.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] + 1.03125)],
                                           [int(_mob.state["coordinate"][0] + list_x[i - 1] + 0.96875), int(_mob.state["coordinate"][1] + list_y[i - 1] + 1.03125)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    return_value[3] = 0.0
                    else:
                        tile_coordinate = [[int(_mob.state["coordinate"][0] + list_x[i - 1] + 0.03125), int(_mob.state["coordinate"][1] + list_y[i - 1] - 0.03125)],
                                           [int(_mob.state["coordinate"][0] + list_x[i - 1] + 0.96875), int(_mob.state["coordinate"][1] + list_y[i - 1] - 0.03125)]]
                        for coordinate in tile_coordinate:
                            if self.valid_coordinate(coordinate):
                                if "mob_transparent" not in data.tile_data[self.map[coordinate[0]][coordinate[1]].id]["tag"]:
                                    return_value[3] = 0.0
                    return_value[0] = _mob.state["coordinate"][0] + list_x[i - 1]
                    return_value[1] = _mob.state["coordinate"][1] + list_y[i - 1]
                    return tuple(return_value)
        return_value[0] = _mob.state["coordinate"][0] + list_x[-1]
        return_value[1] = _mob.state["coordinate"][1] + list_y[-1]
        return tuple(return_value)
    def mouse_to_map(self, _mouse_position: tuple[int, int], _world_coordinate: tuple[float, float]) -> tuple[float, float]:
        x_coordinate = -((settings["window_length"] / 2 - _mouse_position[0]) / 16 / settings["map_scale"]) + 0.5 + _world_coordinate[0]
        y_coordinate = ((settings["window_height"] / 2 - _mouse_position[1]) / 16 / settings["map_scale"]) + 0.5 + _world_coordinate[1]
        return (x_coordinate, y_coordinate)
    def break_tile(self, _coordinate: tuple[int, int]) -> bool:
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
    def place_tile(self, _coordinate: tuple[int, int]) -> bool:
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
            settings["map_scale"] = settings["default_map_scale"] * 2
        else:
            settings["map_scale"] = settings["default_map_scale"]
        # break/place tile
        mouse_in_map = self.mouse_to_map(_mouse_states["position"], tuple(self.player.state["coordinate"]))
        if key_is_down(_mouse_states, "left"):
            self.break_tile(mouse_in_map)
        if key_is_down(_mouse_states, "right"):
            self.place_tile(mouse_in_map)
        for x in range(int(self.player.state["coordinate"][0]) - 64, int(self.player.state["coordinate"][0]) + 65):
            for y in range(int(self.player.state["coordinate"][1]) - 64, int(self.player.state["coordinate"][1]) + 65):
                if self.valid_coordinate((x, y)):
                    if "need_support_tile" in data.tile_data[self.map[x][y].id]["tag"]:
                        if self.valid_coordinate((x, y - 1)):
                            if "cant_be_support_tile" in data.tile_data[self.map[x][y - 1].id]["tag"]:
                                self.map[x][y] = Tile({"id": "air", "state": {}})
                    if "falling_tile" in data.tile_data[self.map[x][y].id]["tag"]:
                        if self.valid_coordinate((x, y - 1)):
                            if "replaceable" in data.tile_data[self.map[x][y - 1].id]["tag"]:
                                self.map[x][y - 1] = self.map[x][y]
                                self.map[x][y] = Tile({"id": "air", "state": {}})
        # remove mob hurt effect
        for mob_number in range(len(self.mobs)):
            self.mobs[mob_number].state["hurt"] = False
        # attack mobs
        if key_is_just_down(_mouse_states, "left"):
            if "weapon" in data.item_data[self.player.state["backpack"][self.player.state["selected_slot"]].id]["tag"]:
                for mob_number in range(len(self.mobs)):
                    if abs(self.mobs[mob_number].state["coordinate"][0] - mouse_in_map[0] + 0.5) <= 0.5 and abs(self.mobs[mob_number].state["coordinate"][1] - mouse_in_map[1] + 0.5) <= 0.5:
                        self.mobs[mob_number].state["health"] -= data.item_data[self.player.state["backpack"][self.player.state["selected_slot"]].id]["data"]["weapon_info"]["damage"]
                        self.mobs[mob_number].state["hurt"] = True
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
                while top_y >= 0:
                    if "mob_transparent" not in data.tile_data[self.map[random_x][top_y].id]["tag"]:
                        break
                    top_y -= 1
                self.mobs[mob_number].state["health"] = data.mob_data[self.mobs[mob_number].id]["data"]["max_health"]
                self.mobs[mob_number].state["coordinate"] = [float(random_x), float(top_y + 1)]
                self.mobs[mob_number].state["movement"] = [0.0, 0.0]
        # select backpack
        self.player.state["selected_slot"] += _mouse_states["scroll_down"] - _mouse_states["scroll_up"]
        self.player.state["selected_slot"] %= data.mob_data["player"]["data"]["max_slot"]
        # move player
        coordinate = self.move(self.player)
        self.player.state["coordinate"][0] = coordinate[0]
        self.player.state["coordinate"][1] = coordinate[1]
        self.player.state["movement"][0] = coordinate[2]
        self.player.state["movement"][1] = coordinate[3]
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