from Resources import *
from typing import Any, Optional, Literal
import math
import random
import copy


def count_item(_mob: dict[str, Any], _item: dict[str, Any]) -> int:
    if _item["id"] == "empty":
        return 0
    return_value = 0
    for slot in range(len(_mob["state"]["backpack"])):
        if _mob["state"]["backpack"][slot]["id"] == _item["id"]:
            if _mob["state"]["backpack"][slot]["state"] == _item["state"]:
                return_value += _mob["state"]["backpack"][slot]["count"]
    return return_value


def add_item(_mob: dict[str, Any], _item: dict[str, Any]) -> dict[str, Any]:
    item = copy.deepcopy(_item)
    for slot in range(len(_mob["state"]["backpack"])):
        if item["id"] == "empty" or item["count"] == 0:
            break
        if _mob["state"]["backpack"][slot]["id"] == item["id"] and _mob["state"]["backpack"][slot]["state"] == item["state"]:
            max_count = data["item_data"][item["id"]]["data"]["max_count"]
            free_space = max(0, max_count - _mob["state"]["backpack"][slot]["count"])
            addition = min(free_space, item["count"])
            if addition > 0:
                _mob["state"]["backpack"][slot]["count"] += addition
                item["count"] -= addition
                if item["count"] == 0:
                    item = {"id": "empty", "count": 0, "state": {}}
    for slot in range(len(_mob["state"]["backpack"])):
        if item["id"] == "empty" or item["count"] == 0:
            break
        if _mob["state"]["backpack"][slot]["id"] == "empty":
            _mob["state"]["backpack"][slot] = item
            item = {"id": "empty", "count": 0, "state": {}}
    return _mob


def subtract_item(_mob: dict[str, Any], _item: dict[str, Any]) -> dict[str, Any]:
    item = copy.deepcopy(_item)
    for slot in range(len(_mob["state"]["backpack"])):
        if item["id"] == "empty" or item["count"] == 0:
            break
        if _mob["state"]["backpack"][slot]["id"] == item["id"] and _mob["state"]["backpack"][slot]["state"] == item["state"]:
            subtraction = min(_mob["state"]["backpack"][slot]["count"], item["count"])
            if subtraction > 0:
                _mob["state"]["backpack"][slot]["count"] -= subtraction
                item["count"] -= subtraction
                if _mob["state"]["backpack"][slot]["count"] == 0:
                    _mob["state"]["backpack"][slot] = {"id": "empty", "count": 0, "state": {}}
                if item["count"] == 0:
                    item = {"id": "empty", "count": 0, "state": {}}
    return _mob


def set_character(_character: dict[str, Any]) -> dict[str, Any]:
    _character.setdefault("color", (255, 255, 255, 255))
    return _character


def display_character(_character: dict[str, Any], _position: tuple[int, int], _scale: Optional[int] = 1) -> None:
    character_image_unscaled = assets["font_images"][_character["character"]]
    character_image_untinted = pygame.transform.scale(character_image_unscaled, (16 * _scale, 16 * _scale))
    character_image = change_image_color(character_image_untinted, pygame.Color(_character["color"]))
    screen.blit(character_image, _position)


def display_text(_text: list[dict[str, Any]], _position: tuple[int, int], _scale: Optional[int] = 1, _alignment: Optional[str] = "top_left") -> None:
    if _alignment == "top_left":
        for index in range(len(_text)):
            display_character(_text[index], (_position[0] + (index * _scale * 16), _position[1]), _scale)
    elif _alignment == "top":
        for index in range(len(_text)):
            display_character(_text[index], (_position[0] + (index * _scale * 16) - (len(_text) * _scale * 8), _position[1]), _scale)
    elif _alignment == "top_right":
        for index in range(len(_text)):
            display_character(_text[index], (_position[0] + (index * _scale * 16) - (len(_text) * _scale * 16), _position[1]), _scale)
    elif _alignment == "left":
        for index in range(len(_text)):
            display_character(_text[index], (_position[0] + (index * _scale * 16), _position[1] - (_scale * 8)), _scale)
    elif _alignment == "right":
        for index in range(len(_text)):
            display_character(_text[index], (_position[0] + (index * _scale * 16) - (len(_text) * _scale * 16), _position[1] - (_scale * 8)), _scale)
    elif _alignment == "bottom_left":
        for index in range(len(_text)):
            display_character(_text[index], (_position[0] + (index * _scale * 16), _position[1] - (_scale * 16)), _scale)
    elif _alignment == "bottom":
        for index in range(len(_text)):
            display_character(_text[index], (_position[0] + (index * _scale * 16) - (len(_text) * _scale * 8), _position[1] - (_scale * 16)), _scale)
    elif _alignment == "bottom_right":
        for index in range(len(_text)):
            display_character(_text[index], (_position[0] + (index * _scale * 16) - (len(_text) * _scale * 16), _position[1] - (_scale * 16)), _scale)
    else:
        for index in range(len(_text)):
            display_character(_text[index], (_position[0] + (index * _scale * 16) - (len(_text) * _scale * 8), _position[1] - (_scale * 8)), _scale)


def valid_coordinate(_world_size: tuple[int, int], _coordinate: tuple[int, int]) -> bool:
    return _coordinate[0] >= 0 and _coordinate[0] < _world_size[0] and _coordinate[1] >= 0 and _coordinate[1] < _world_size[1]


def build_structure(_world: dict[str, Any], _coordinate: tuple[int, int], _id: str) -> dict[str, Any]:
    structure = data["structure_data"][_id]
    length = len(structure["tiles"][0])
    height = len(structure["tiles"])
    for structure_x in range(length):
        for structure_y in range(height):
            map_x = structure_x + _coordinate[0] - structure["core"][0]
            map_y = height - structure_y - 1 + _coordinate[1] - structure["core"][1]
            if valid_coordinate((_world["settings"]["world_length"], _world["settings"]["world_height"]), (map_x, map_y)):
                if structure["tiles"][structure_y][structure_x] != " ":
                    _world["tiles"][map_x][map_y] = structure["keys"][structure["tiles"][structure_y][structure_x]]
    return _world


def height_map(_seed: int, _world_size: tuple[int, int]) -> list[int]:
    # generate height map
    random.seed(_seed)
    terrain = [_world_size[1] / 2 for i in range(_world_size[0])]
    offset = [0 for i in range(_world_size[0])]
    step_length = 1
    step_count = 0
    offset_1 = random.uniform(step_length * -0.25, step_length * 0.25)
    offset_2 = random.uniform(step_length * -0.25, step_length * 0.25)
    while step_length <= 2 ** 6:
        for x in range(_world_size[0]):
            step_count += 1
            if x % step_length == 0:
                offset_1 = offset_2
                offset_2 = random.uniform(step_length * -0.25, step_length * 0.25)
                step_count = 0
            offset[x] = offset_1 + (step_count * ((offset_2 - offset_1) / step_length))
        for x in range(_world_size[0]):
            terrain[x] += offset[x]
        step_length *= 2
    for x in range(_world_size[0]):
        terrain[x] = int(terrain[x])
    return terrain


def cave_line(_coordinate: tuple[int, int], _length: int) -> list[tuple[float, float]]:
    # generate cave
    cave = []
    angle = random.random()
    angle_offset = (random.random() - 0.5) / 64
    coordinate = list(_coordinate)
    for i in range(_length):
        angle_offset += (random.random() - 0.5) / 64
        angle += angle_offset
        angle %= 1
        coordinate = (coordinate[0] + math.cos(angle * 2 * math.pi), coordinate[1] + math.sin(angle * 2 * math.pi))
        cave.append(copy.deepcopy(coordinate))
    return cave


def create_world(_settings: dict[str, Any]) -> dict[str, Any]:
    # create new world
    print_info("Creating New World...")
    return_world = {}
    return_world["settings"] = _settings
    random.seed(int(return_world["settings"]["seed"]))
    print_info("Generating Terrain...")
    return_world["tiles"] = [[{"id": "air", "state": {}} for y in range(return_world["settings"]["world_height"])] for x in range(return_world["settings"]["world_length"])]
    return_world["liquids"] = [[{"id": "air", "state": {}} for y in range(return_world["settings"]["world_height"])] for x in range(return_world["settings"]["world_length"])]
    terrain = height_map(return_world["settings"]["seed"], (return_world["settings"]["world_length"], return_world["settings"]["world_height"]))
    for x in range(return_world["settings"]["world_length"]):
        dirt_thick = random.choice(range(3, 6))
        for y in range(return_world["settings"]["world_height"]):
            if not valid_coordinate((return_world["settings"]["world_length"], return_world["settings"]["world_height"]), (x, y)):
                break
            if y < terrain[x]:
                if terrain[x] - y == 1:
                    if y >= return_world["settings"]["world_height"] / 2:
                        return_world["tiles"][x][y] = {"id": "grassy_soil", "state": {}}
                        random_number = random.choice(range(64))
                        if random_number == 0:
                            if valid_coordinate((return_world["settings"]["world_length"], return_world["settings"]["world_height"]), (x, y + 1)):
                                return_world["tiles"][x][y + 1] = {"id": "sapling", "state": {}}
                        elif random_number == 1:
                            return_world = build_structure(return_world, (x, y), "tree_3")
                        elif random_number == 2:
                            return_world = build_structure(return_world, (x, y), "tree_4")
                        elif random_number == 3:
                            return_world = build_structure(return_world, (x, y), "tree_5")
                        elif random_number <= 16:
                            if valid_coordinate((return_world["settings"]["world_length"], return_world["settings"]["world_height"]), (x, y + 1)):
                                return_world["tiles"][x][y + 1] = {"id": "grass", "state": {}}
                    else:
                        return_world["tiles"][x][y] = {"id": "soil", "state": {}}
                elif terrain[x] - y <= dirt_thick:
                    random_number = random.choice(range(16))
                    if random_number == 0:
                        return_world["tiles"][x][y] = {"id": "gravel", "state": {}}
                    else:
                        return_world["tiles"][x][y] = {"id": "soil", "state": {}}
                else:
                    random_number = random.choice(range(int((y + return_world["settings"]["world_height"]) / 2)))
                    if random_number == 0:
                        return_world["tiles"][x][y] = {"id": "coal_ore", "state": {}}
                    elif random_number == 1:
                        return_world["tiles"][x][y] = {"id": "copper_ore", "state": {}}
                    elif random_number == 2:
                        return_world["tiles"][x][y] = {"id": "silver_ore", "state": {}}
                    elif random_number == 3:
                        return_world["tiles"][x][y] = {"id": "iron_ore", "state": {}}
                    elif random_number == 4:
                        return_world["tiles"][x][y] = {"id": "gold_ore", "state": {}}
                    else:
                        return_world["tiles"][x][y] = {"id": "stone", "state": {}}
            if y <= return_world["settings"]["world_height"] / 2 and "liquid_transparent" in data["tile_data"][return_world["tiles"][x][y]["id"]]["tag"]:
                return_world["liquids"][x][y] = {"id": "water", "state": {}}
    print_info("Generating Cave...")
    for _ in range(int(return_world["settings"]["world_length"] / 4)):
        cave = cave_line((random.choice(range(return_world["settings"]["world_length"])), random.choice(range(return_world["settings"]["world_height"]))), random.choice(range(16, 64)))
        for coordinate in range(len(cave)):
            for mx in range(-2, 3):
                for my in range(-2, 3):
                    if valid_coordinate((return_world["settings"]["world_length"], return_world["settings"]["world_height"]), (cave[coordinate][0] + mx, cave[coordinate][1] + my)):
                        return_world["tiles"][int(cave[coordinate][0] + mx)][int(cave[coordinate][1] + my)] = {"id": "air", "state": {}}
    print_info("Creating Player...")
    return_world["player"] = {"id": "player", "state": copy.deepcopy(data["mob_data"]["player"]["state"])}
    return_world["player"]["state"]["health"] = data["mob_data"]["player"]["data"]["max_health"]
    return_world["player"]["state"]["coordinate"] = [return_world["settings"]["world_length"] / 2, float(terrain[int(return_world["settings"]["world_length"] / 2)])]
    return_world["player"]["state"]["movement"] = [0.0, 0.0]
    print_info("Creating Mobs...")
    return_world["mobs"] = []
    animal_ids = []
    for id in data["mob_data"]:
        if "animal" in data["mob_data"][id]["tag"]:
            animal_ids.append(id)
    for mob_number in range(int(return_world["settings"]["world_length"] / 16)):
        random_animal_id = random.choice(animal_ids)
        return_world["mobs"].append({"id": random_animal_id, "state": copy.deepcopy(data["mob_data"][random_animal_id]["state"])})
        random_x = random.choice(range(return_world["settings"]["world_length"]))
        return_world["mobs"][mob_number]["state"]["health"] = data["mob_data"][return_world["mobs"][mob_number]["id"]]["data"]["max_health"]
        return_world["mobs"][mob_number]["state"]["coordinate"] = [float(random_x), float(terrain[int(random_x)])]
        return_world["mobs"][mob_number]["state"]["movement"] = [0.0, 0.0]
    return return_world


def mob_on_ground(_world: dict[str, Any], _mob: dict[str, Any]) -> bool:
    # get tile's coordinate
    tile_coordinate = [[int(_mob["state"]["coordinate"][0] + 0.03125), int(_mob["state"]["coordinate"][1] - 0.03125)],
                       [int(_mob["state"]["coordinate"][0] + 0.96875), int(_mob["state"]["coordinate"][1] - 0.03125)]]
    for coordinate in tile_coordinate:
        if valid_coordinate((_world["settings"]["world_length"], _world["settings"]["world_height"]), coordinate):
            if "mob_transparent" not in data["tile_data"][_world["tiles"][coordinate[0]][coordinate[1]]["id"]]["tag"]:
                return True
    return False


def mob_move(_world: dict[str, Any], _mob: dict[str, Any]) -> tuple[tuple[float, float], tuple[float, float]]:
    if _mob["state"]["movement"][0] == 0 and _mob["state"]["movement"][1] == 0:
        return ((_mob["state"]["coordinate"][0], _mob["state"]["coordinate"][1]), (0.0, 0.0))
    world_size = (_world["settings"]["world_length"], _world["settings"]["world_height"])
    # get _mob's coordinate
    max_move = int(max(abs(_mob["state"]["movement"][0]), abs(_mob["state"]["movement"][1])) * 16)
    list_x = [0 for x in range(max_move + 1)]
    if _mob["state"]["movement"][0] != 0: # avoid mx / 0
        list_x = [int(x * _mob["state"]["movement"][0] * 16 / max_move) / 16 for x in range(max_move + 1)]
    list_y = [0 for y in range(max_move + 1)]
    if _mob["state"]["movement"][1] != 0: # avoid my / 0
        list_y = [int(y * _mob["state"]["movement"][1] * 16 / max_move) / 16 for y in range(max_move + 1)]
    # test the touch between _mob and tile
    for i in range(max_move + 1):
        # get tile's coordinate
        tile_coordinate = [[int(_mob["state"]["coordinate"][0] + list_x[i] + 0.03125), int(_mob["state"]["coordinate"][1] + list_y[i] + 0.03125)],
                           [int(_mob["state"]["coordinate"][0] + list_x[i] + 0.03125), int(_mob["state"]["coordinate"][1] + list_y[i] + 0.96875)],
                           [int(_mob["state"]["coordinate"][0] + list_x[i] + 0.96875), int(_mob["state"]["coordinate"][1] + list_y[i] + 0.03125)],
                           [int(_mob["state"]["coordinate"][0] + list_x[i] + 0.96875), int(_mob["state"]["coordinate"][1] + list_y[i] + 0.96875)]]
        for j in range(len(tile_coordinate)):
            if not valid_coordinate(world_size, tile_coordinate[j]):
                return ((_world["settings"]["world_length"] / 2, _world["settings"]["world_height"] - 1.0), (0.0, 0.0))
            # collapse
            return_value = [[_mob["state"]["coordinate"][0], _mob["state"]["coordinate"][1]], [_mob["state"]["movement"][0], _mob["state"]["movement"][1]]]
            if "mob_transparent" not in data["tile_data"][_world["tiles"][tile_coordinate[j][0]][tile_coordinate[j][1]]["id"]]["tag"]:
                if _mob["state"]["movement"][0] > 0:
                    tile_coordinate = [[int(_mob["state"]["coordinate"][0] + list_x[i - 1] + 1.03125), int(_mob["state"]["coordinate"][1] + list_y[i - 1] + 0.03125)],
                                       [int(_mob["state"]["coordinate"][0] + list_x[i - 1] + 1.03125), int(_mob["state"]["coordinate"][1] + list_y[i - 1] + 0.96875)]]
                    for coordinate in tile_coordinate:
                        if valid_coordinate(world_size, coordinate):
                            if "mob_transparent" not in data["tile_data"][_world["tiles"][coordinate[0]][coordinate[1]]["id"]]["tag"]:
                                return_value[1][0] = 0.0
                else:
                    tile_coordinate = [[int(_mob["state"]["coordinate"][0] + list_x[i - 1] - 0.03125), int(_mob["state"]["coordinate"][1] + list_y[i - 1] + 0.03125)],
                                       [int(_mob["state"]["coordinate"][0] + list_x[i - 1] - 0.03125), int(_mob["state"]["coordinate"][1] + list_y[i - 1] + 0.96875)]]
                    for coordinate in tile_coordinate:
                        if valid_coordinate(world_size, coordinate):
                            if "mob_transparent" not in data["tile_data"][_world["tiles"][coordinate[0]][coordinate[1]]["id"]]["tag"]:
                                return_value[1][0] = 0.0
                if _mob["state"]["movement"][1] > 0:
                    tile_coordinate = [[int(_mob["state"]["coordinate"][0] + list_x[i - 1] + 0.03125), int(_mob["state"]["coordinate"][1] + list_y[i - 1] + 1.03125)],
                                       [int(_mob["state"]["coordinate"][0] + list_x[i - 1] + 0.96875), int(_mob["state"]["coordinate"][1] + list_y[i - 1] + 1.03125)]]
                    for coordinate in tile_coordinate:
                        if valid_coordinate(world_size, coordinate):
                            if "mob_transparent" not in data["tile_data"][_world["tiles"][coordinate[0]][coordinate[1]]["id"]]["tag"]:
                                return_value[1][1] = 0.0
                else:
                    tile_coordinate = [[int(_mob["state"]["coordinate"][0] + list_x[i - 1] + 0.03125), int(_mob["state"]["coordinate"][1] + list_y[i - 1] - 0.03125)],
                                       [int(_mob["state"]["coordinate"][0] + list_x[i - 1] + 0.96875), int(_mob["state"]["coordinate"][1] + list_y[i - 1] - 0.03125)]]
                    for coordinate in tile_coordinate:
                        if valid_coordinate(world_size, coordinate):
                            if "mob_transparent" not in data["tile_data"][_world["tiles"][coordinate[0]][coordinate[1]]["id"]]["tag"]:
                                return_value[1][1] = 0.0
                return_value[0][0] = _mob["state"]["coordinate"][0] + list_x[i - 1]
                return_value[0][1] = _mob["state"]["coordinate"][1] + list_y[i - 1]
                return (tuple(return_value[0]), tuple(return_value[1]))
    return_value[0][0] = _mob["state"]["coordinate"][0] + list_x[-1]
    return_value[0][1] = _mob["state"]["coordinate"][1] + list_y[-1]
    return (tuple(return_value[0]), tuple(return_value[1]))


def mouse_to_map(_mouse_position: tuple[int, int], _world_coordinate: tuple[float, float]) -> tuple[float, float]:
    x_coordinate = -((default_settings["pygame_window_length"] / 2 - _mouse_position[0]) / 16 / settings["map_scale"]) + 0.5 + _world_coordinate[0]
    y_coordinate = ((default_settings["pygame_window_height"] / 2 - _mouse_position[1]) / 16 / settings["map_scale"]) + 0.5 + _world_coordinate[1]
    return (x_coordinate, y_coordinate)


def set_tile(_world: dict[str, Any], _coordinate: tuple[int, int], _tile: dict[str, Any]) -> dict[str, Any]:
    _world["tiles"][int(_coordinate[0])][int(_coordinate[1])] = copy.deepcopy(_tile)
    return _world


def set_liquid(_world: dict[str, Any], _coordinate: tuple[int, int], _tile: dict[str, Any]) -> dict[str, Any]:
    _world["liquids"][int(_coordinate[0])][int(_coordinate[1])] = copy.deepcopy(_tile)
    return _world


def break_tile(_world: dict[str, Any], _coordinate: tuple[int, int]) -> dict[str, Any]:
    # is this coordinate valid?
    if not valid_coordinate((_world["settings"]["world_length"], _world["settings"]["world_height"]), _coordinate):
        return _world
    # is this tile breakable?
    current_tile = _world["tiles"][int(_coordinate[0])][int(_coordinate[1])]
    if "unbreakable" in data["tile_data"][current_tile["id"]]["tag"]:
        return _world
    current_tool = _world["player"]["state"]["backpack"][_world["player"]["state"]["selected_slot"]]
    breakable_tile = False
    if data["tile_data"][current_tile["id"]]["data"]["mining_tool"] == "none":
        breakable_tile = True
    if data["tile_data"][current_tile["id"]]["data"]["mining_level"] <= 0:
        breakable_tile = True
    if "tool" in data["item_data"][current_tool["id"]]["tag"]:
        if data["item_data"][current_tool["id"]]["data"]["tool_info"]["type"] == data["tile_data"][current_tile["id"]]["data"]["mining_tool"]:
            if data["item_data"][current_tool["id"]]["data"]["tool_info"]["level"] >= data["tile_data"][current_tile["id"]]["data"]["mining_level"]:
                breakable_tile = True
    if breakable_tile == True:
        dropped_items = data["tile_data"][current_tile["id"]]["data"]["tile_drop"]
    else:
        return _world
    # get item
    for item in range(len(dropped_items)):
        _world["player"] = add_item(_world["player"], dropped_items[item])
    # set tile
    _world = set_tile(_world, _coordinate, {"id": "air", "state": {}})
    return _world


def place_tile(_world: dict[str, Any], _coordinate: tuple[int, int]) -> dict[str, Any]:
    # is this coordinate valid?
    if not valid_coordinate((_world["settings"]["world_length"], _world["settings"]["world_height"]), _coordinate):
        return _world
    # is this tile replaceable?
    current_tile = _world["tiles"][int(_coordinate[0])][int(_coordinate[1])]
    if "replaceable" not in data["tile_data"][current_tile["id"]]["tag"]:
        return _world
    # is this item placeable?
    current_item = _world["player"]["state"]["backpack"][_world["player"]["state"]["selected_slot"]]
    if "placeable" not in data["item_data"][current_item["id"]]["tag"]:
        return _world
    # remove item
    _world["player"]["state"]["backpack"][_world["player"]["state"]["selected_slot"]]["count"] -= 1
    if _world["player"]["state"]["backpack"][_world["player"]["state"]["selected_slot"]]["count"] == 0:
        _world["player"]["state"]["backpack"][_world["player"]["state"]["selected_slot"]] = {"id": "empty", "count": 0, "state": {}}
    # set tile
    _world = set_tile(_world, _coordinate, data["item_data"][current_item["id"]]["data"]["to_tile"])
    return _world


def coordinate_solid_for_liquid(_world: dict[str, Any], _coordinate: tuple[int, int]) -> bool:
    if "liquid_transparent" not in data["tile_data"][_world["tiles"][_coordinate[0]][_coordinate[1]]["id"]]["tag"]:
        solid_tile = True
    else:
        solid_tile = False
    if _world["liquids"][_coordinate[0]][_coordinate[1]]["id"] != "air":
        solid_liquid = True
    else:
        solid_liquid = False
    return solid_tile or solid_liquid


def tick(_world: dict[str, Any], _key_states: dict[int, str], _mouse_states: dict[str, Any]) -> dict[str, Any]:
    # quit game
    if key_is_just_down(_key_states, pygame.K_DELETE):
        return _world
    # jump test
    if mob_on_ground(_world, _world["player"]):
        if key_is_down(_key_states, pygame.K_SPACE):
            _world["player"]["state"]["movement"][1] = _world["settings"]["jump_speed"]
        else:
            _world["player"]["state"]["movement"][1] = 0.0
    else:
        _world["player"]["state"]["movement"][1] += _world["settings"]["gravity"]
    # move left/right
    _world["player"]["state"]["movement"][0] = 0.0
    if key_is_down(_key_states, pygame.K_a):
        _world["player"]["state"]["movement"][0] = -data["mob_data"]["player"]["data"]["speed"]
    if key_is_down(_key_states, pygame.K_d):
        _world["player"]["state"]["movement"][0] = data["mob_data"]["player"]["data"]["speed"]
    # zoom
    if key_is_down(_key_states, pygame.K_BACKQUOTE):
        settings["map_scale"] = default_settings["default_map_scale"] * 2
    else:
        settings["map_scale"] = default_settings["default_map_scale"]
    # select backpack
    _world["player"]["state"]["selected_slot"] += _mouse_states["scroll_down"] - _mouse_states["scroll_up"]
    _world["player"]["state"]["selected_slot"] %= data["mob_data"]["player"]["data"]["max_slot"]
    # map changes
    mouse_in_map = mouse_to_map(_mouse_states["position"], tuple(_world["player"]["state"]["coordinate"]))
    if key_is_down(_mouse_states, "left"):
        _world = break_tile(_world, mouse_in_map)
    if key_is_down(_mouse_states, "right"):
        _world = place_tile(_world, mouse_in_map)
    new_tiles = []
    new_liquids = []
    loading_range = 64
    world_size = (_world["settings"]["world_length"], _world["settings"]["world_height"])
    # is this tile floating?
    for x in range(int(_world["player"]["state"]["coordinate"][0]) - loading_range, int(_world["player"]["state"]["coordinate"][0]) + loading_range + 1):
        for y in range(int(_world["player"]["state"]["coordinate"][1]) - loading_range, int(_world["player"]["state"]["coordinate"][1]) + loading_range + 1):
            if valid_coordinate(world_size, (x, y)) and valid_coordinate(world_size, (x, y - 1)):
                if "need_support_tile" in data["tile_data"][_world["tiles"][x][y]["id"]]["tag"]:
                    if "cant_be_support_tile" in data["tile_data"][_world["tiles"][x][y - 1]["id"]]["tag"]:
                        new_tiles.append({"coordinate": (x, y), "tile": {"id": "air", "state": {}}})
                if "falling_tile" in data["tile_data"][_world["tiles"][x][y]["id"]]["tag"]:
                    if "replaceable" in data["tile_data"][_world["tiles"][x][y - 1]["id"]]["tag"]:
                        new_tiles.append({"coordinate": (x, y - 1), "tile": _world["tiles"][x][y]})
                        new_tiles.append({"coordinate": (x, y), "tile": {"id": "air", "state": {}}})
    for index in range(len(new_tiles)):
        _world = set_tile(_world, new_tiles[index]["coordinate"], new_tiles[index]["tile"])
    new_tiles = []
    for index in range(len(new_liquids)):
        _world = set_liquid(_world, new_liquids[index]["coordinate"], new_liquids[index]["liquid"])
    new_liquids = []
    # is this liquid incorrect?
    for x in range(int(_world["player"]["state"]["coordinate"][0]) - loading_range, int(_world["player"]["state"]["coordinate"][0]) + loading_range + 1):
        for y in range(int(_world["player"]["state"]["coordinate"][1]) - loading_range, int(_world["player"]["state"]["coordinate"][1]) + loading_range + 1):
            if valid_coordinate(world_size, (x, y)):
                if _world["liquids"][x][y]["id"] != "air":
                    if "liquid_transparent" not in data["tile_data"][_world["tiles"][x][y]["id"]]["tag"]:
                        new_liquids.append({"coordinate": (x, y), "liquid": {"id": "air", "state": {}}})
                    if "liquid_breakable" in data["tile_data"][_world["tiles"][x][y]["id"]]["tag"]:
                        new_tiles.append({"coordinate": (x, y), "tile": {"id": "air", "state": {}}})
    for index in range(len(new_tiles)):
        _world = set_tile(_world, new_tiles[index]["coordinate"], new_tiles[index]["tile"])
    new_tiles = []
    for index in range(len(new_liquids)):
        _world = set_liquid(_world, new_liquids[index]["coordinate"], new_liquids[index]["liquid"])
    new_liquids = []
    # liquid flow
    for y in range(int(_world["player"]["state"]["coordinate"][1]) - loading_range, int(_world["player"]["state"]["coordinate"][1]) + loading_range + 1):
        for x in range(int(_world["player"]["state"]["coordinate"][0]) - loading_range, int(_world["player"]["state"]["coordinate"][0]) + loading_range + 1):
            if valid_coordinate(world_size, (x, y)):
                if _world["liquids"][x][y]["id"] != "air":
                    if valid_coordinate(world_size, (x, y - 1)):
                        if not coordinate_solid_for_liquid(_world, (x, y - 1)):
                            new_liquids.append({"coordinate": (x, y - 1), "liquid": _world["liquids"][x][y]})
                            new_liquids.append({"coordinate": (x, y), "liquid": {"id": "air", "state": {}}})
                    if valid_coordinate(world_size, (x - 1, y)):
                        if not coordinate_solid_for_liquid(_world, (x - 1, y)):
                            new_liquids.append({"coordinate": (x - 1, y), "liquid": _world["liquids"][x][y]})
                    if valid_coordinate(world_size, (x + 1, y)):
                        if not coordinate_solid_for_liquid(_world, (x + 1, y)):
                            new_liquids.append({"coordinate": (x + 1, y), "liquid": _world["liquids"][x][y]})
    for index in range(len(new_tiles)):
        _world = set_tile(_world, new_tiles[index]["coordinate"], new_tiles[index]["tile"])
    new_tiles = []
    for index in range(len(new_liquids)):
        _world = set_liquid(_world, new_liquids[index]["coordinate"], new_liquids[index]["liquid"])
    new_liquids = []
    # remove hurt effect
    _world["player"]["state"]["hurt"] = False
    for mob_number in range(len(_world["mobs"])):
        _world["mobs"][mob_number]["state"]["hurt"] = False
    # attack mobs
    if key_is_just_down(_mouse_states, "left"):
        if "weapon" in data["item_data"][_world["player"]["state"]["backpack"][_world["player"]["state"]["selected_slot"]]["id"]]["tag"]:
            for mob_number in range(len(_world["mobs"])):
                if abs(_world["mobs"][mob_number]["state"]["coordinate"][0] - mouse_in_map[0] + 0.5) <= 0.5 and abs(_world["mobs"][mob_number]["state"]["coordinate"][1] - mouse_in_map[1] + 0.5) <= 0.5:
                    _world["mobs"][mob_number]["state"]["health"] -= data["item_data"][_world["player"]["state"]["backpack"][_world["player"]["state"]["selected_slot"]]["id"]]["data"]["weapon_info"]["damage"]
                    _world["mobs"][mob_number]["state"]["hurt"] = True
    # player respawn
    if _world["player"]["state"]["health"] <= 0:
        top_y = _world["settings"]["world_height"] - 1
        while top_y > 0:
            if "mob_transparent" not in data["tile_data"][_world["tiles"][int(_world["settings"]["world_length"] / 2)][top_y]["id"]]["tag"]:
                break
            top_y -= 1
        _world["player"]["state"]["coordinate"] = [float(_world["settings"]["world_length"] / 2), float(top_y + 1)]
        _world["player"]["state"]["movement"] = [0.0, 0.0]
        _world["player"]["state"]["health"] = data["mob_data"]["player"]["data"]["max_health"]
        _world["player"]["state"]["hurt"] = False
    # replace no health mobs to new mobs
    animal_ids = []
    for id in data["mob_data"]:
        if "animal" in data["mob_data"][id]["tag"]:
            animal_ids.append(id)
    for mob_number in range(len(_world["mobs"])):
        if _world["mobs"][mob_number]["state"]["health"] <= 0:
            random_animal_id = random.choice(animal_ids)
            _world["mobs"][mob_number] = {"id": random_animal_id, "state": copy.deepcopy(data["mob_data"][random_animal_id]["state"])}
            random_x = random.choice(range(_world["settings"]["world_length"]))
            top_y = _world["settings"]["world_height"] - 1
            while top_y > 0:
                if "mob_transparent" not in data["tile_data"][_world["tiles"][random_x][top_y]["id"]]["tag"]:
                    break
                top_y -= 1
            _world["mobs"][mob_number]["state"]["coordinate"] = [float(random_x), float(top_y + 1)]
            _world["mobs"][mob_number]["state"]["movement"] = [0.0, 0.0]
            _world["mobs"][mob_number]["state"]["health"] = data["mob_data"][_world["mobs"][mob_number]["id"]]["data"]["max_health"]
            _world["mobs"][mob_number]["state"]["hurt"] = False
    # move player
    coordinate = mob_move(_world, _world["player"])
    _world["player"]["state"]["coordinate"][0] = coordinate[0][0]
    _world["player"]["state"]["coordinate"][1] = coordinate[0][1]
    _world["player"]["state"]["movement"][0] = coordinate[1][0]
    _world["player"]["state"]["movement"][1] = coordinate[1][1]
    if not mob_on_ground(_world, _world["player"]):
        _world["player"]["state"]["falling_time"] += 1
    else:
        if _world["player"]["state"]["falling_time"] > 24:
            _world["player"]["state"]["health"] -= _world["player"]["state"]["falling_time"] - 24
            _world["player"]["state"]["hurt"] = True
        _world["player"]["state"]["falling_time"] = 0
    # move mobs
    for mob_number in range(len(_world["mobs"])):
        if random.choice(range(16)) == 0:
            _world["mobs"][mob_number]["state"]["action"] = random.choice(data["mob_data"][_world["mobs"][mob_number]["id"]]["data"]["actions"])
        if mob_on_ground(_world, _world["mobs"][mob_number]):
            if _world["mobs"][mob_number]["state"]["action"] == "jump":
                _world["mobs"][mob_number]["state"]["movement"][1] = _world["settings"]["jump_speed"]
            else:
                _world["mobs"][mob_number]["state"]["movement"][1] = 0.0
        else:
            _world["mobs"][mob_number]["state"]["movement"][1] += _world["settings"]["gravity"]
        if _world["mobs"][mob_number]["state"]["action"] == "left":
            _world["mobs"][mob_number]["state"]["movement"][0] = -data["mob_data"][_world["mobs"][mob_number]["id"]]["data"]["speed"]
        elif _world["mobs"][mob_number]["state"]["action"] == "right":
            _world["mobs"][mob_number]["state"]["movement"][0] = data["mob_data"][_world["mobs"][mob_number]["id"]]["data"]["speed"]
        else:
            _world["mobs"][mob_number]["state"]["movement"][0] = 0.0
        coordinate = mob_move(_world, _world["mobs"][mob_number])
        _world["mobs"][mob_number]["state"]["coordinate"][0] = coordinate[0][0]
        _world["mobs"][mob_number]["state"]["coordinate"][1] = coordinate[0][1]
        _world["mobs"][mob_number]["state"]["movement"][0] = coordinate[1][0]
        _world["mobs"][mob_number]["state"]["movement"][1] = coordinate[1][1]
        if not mob_on_ground(_world, _world["mobs"][mob_number]):
            _world["mobs"][mob_number]["state"]["falling_time"] += 1
        else:
            if _world["mobs"][mob_number]["state"]["falling_time"] > 24:
                _world["mobs"][mob_number]["state"]["health"] -= _world["mobs"][mob_number]["state"]["falling_time"] - 24
                _world["mobs"][mob_number]["state"]["hurt"] = True
            _world["mobs"][mob_number]["state"]["falling_time"] = 0
    return _world


def craft(_world: dict[str, Any], _key_states: dict[int, str], _mouse_states: dict[str, Any]) -> str:
    # is it first time?
    if "selected_recipe" not in _world["player"]["state"]["temporary"]:
        _world["player"]["state"]["temporary"]["selected_recipe"] = 0
    # choose the recipe
    _world["player"]["state"]["temporary"]["selected_recipe"] += _mouse_states["scroll_down"] - _mouse_states["scroll_up"]
    _world["player"]["state"]["temporary"]["selected_recipe"] %= len(data["recipe_data"])
    _world["player"]["state"]["temporary"]["successful_crafting"] = "none"
    selected_recipe = _world["player"]["state"]["temporary"]["selected_recipe"]
    # craft
    if key_is_just_down(_key_states, pygame.K_SPACE):
        for material in range(len(data["recipe_data"][selected_recipe]["from"])):
            if count_item(_world["player"], data["recipe_data"][selected_recipe]["from"][material]) < data["recipe_data"][selected_recipe]["from"][material]["count"]:
                _world["player"]["state"]["temporary"]["successful_crafting"] = "false"
                return _world
        for material in range(len(data["recipe_data"][selected_recipe]["from"])):
            subtract_item(_world["player"], data["recipe_data"][selected_recipe]["from"][material])
        for product in range(len(data["recipe_data"][selected_recipe]["to"])):
            _world["player"]["state"]["temporary"]["successful_crafting"] = "true"
            add_item(_world["player"], data["recipe_data"][selected_recipe]["to"][product])
    return _world


def display_world(_world: dict[str, Any], _coordinate: tuple[float, float]) -> None:
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
            if not valid_coordinate((_world["settings"]["world_length"], _world["settings"]["world_height"]), (tile_x, tile_y)):
                continue
            if "display_transparent" not in data["liquid_data"][_world["liquids"][tile_x][tile_y]["id"]]["tag"]:
                liquid_image_unscaled = assets["liquid_images"][_world["liquids"][tile_x][tile_y]["id"]]
                liquid_image = pygame.transform.scale(liquid_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
                liquid_image_position = ((int((offset_x - float_x) * 16 - 8) * settings["map_scale"]) + default_settings["pygame_window_length"] / 2,
                                         (int((offset_y - float_y) * -16 - 8) * settings["map_scale"]) + default_settings["pygame_window_height"] / 2)
                screen.blit(liquid_image, liquid_image_position)
            if "display_transparent" not in data["tile_data"][_world["tiles"][tile_x][tile_y]["id"]]["tag"]:
                tile_image_unscaled = assets["tile_images"][_world["tiles"][tile_x][tile_y]["id"]]
                tile_image = pygame.transform.scale(tile_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
                tile_image_position = ((int((offset_x - float_x) * 16 - 8) * settings["map_scale"]) + default_settings["pygame_window_length"] / 2,
                                       (int((offset_y - float_y) * -16 - 8) * settings["map_scale"]) + default_settings["pygame_window_height"] / 2)
                screen.blit(tile_image, tile_image_position)
    # display mobs
    for mob_number in range(len(_world["mobs"])):
        mob_image_unscaled = assets["mob_images"][_world["mobs"][mob_number]["id"]]
        mob_image = pygame.transform.scale(mob_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
        if _world["mobs"][mob_number]["state"]["hurt"] == True:
            mob_image = tint_image(mob_image, pygame.Color(255, 0, 0, 128))
        mob_image_position = (int(((_world["mobs"][mob_number]["state"]["coordinate"][0] - _coordinate[0]) * 16 - 8) * settings["map_scale"]) + default_settings["pygame_window_length"] / 2,
                              int(((_world["mobs"][mob_number]["state"]["coordinate"][1] - _coordinate[1]) * -16 - 8) * settings["map_scale"]) + default_settings["pygame_window_height"] / 2)
        if mob_image_position[0] > -16 * settings["map_scale"] and mob_image_position[0] < default_settings["pygame_window_length"]:
            if mob_image_position[1] > -16 * settings["map_scale"] and mob_image_position[1] < default_settings["pygame_window_height"]:
                screen.blit(mob_image, mob_image_position)
    # display player
    player_image_unscaled = assets["mob_images"]["player"]
    player_image = pygame.transform.scale(player_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
    if _world["player"]["state"]["hurt"] == True:
        player_image = tint_image(player_image, pygame.Color(255, 0, 0, 128))
    player_image_position = (int(((_world["player"]["state"]["coordinate"][0] - _coordinate[0]) * 16 - 8) * settings["map_scale"]) + default_settings["pygame_window_length"] / 2,
                             int(((_world["player"]["state"]["coordinate"][1] - _coordinate[1]) * -16 - 8) * settings["map_scale"]) + default_settings["pygame_window_height"] / 2)
    screen.blit(player_image, player_image_position)
    # display health
    player_max_health = data["mob_data"]["player"]["data"]["max_health"]
    player_health = _world["player"]["state"]["health"]
    health_bar_background_image = pygame.Surface((16 * settings["gui_scale"] * data["mob_data"]["player"]["data"]["max_slot"], 16 * settings["gui_scale"])).convert_alpha()
    health_bar_background_image.fill("#80000080")
    health_bar_position = (int(default_settings["pygame_window_length"] / 2 - (8 * data["mob_data"]["player"]["data"]["max_slot"] * settings["gui_scale"])),
                           int(default_settings["pygame_window_height"] - (32 * settings["gui_scale"])))
    screen.blit(health_bar_background_image, health_bar_position)
    if player_health > 0:
        health_bar_foreground_image = pygame.Surface((int((16 * settings["gui_scale"] * data["mob_data"]["player"]["data"]["max_slot"]) / player_max_health * player_health), 16 * settings["gui_scale"])).convert_alpha()
        health_bar_foreground_image.fill("#FF0000FF")
        screen.blit(health_bar_foreground_image, health_bar_position)
    # display the backpack
    backpack = _world["player"]["state"]["backpack"]
    slot_image = pygame.Surface((16 * settings["gui_scale"], 16 * settings["gui_scale"])).convert_alpha()
    for slot in range(len(backpack)):
        item_image_unscaled = assets["item_images"][backpack[slot]["id"]]
        item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
        item_image_position = (int((slot * 16 - data["mob_data"]["player"]["data"]["max_slot"] * 8) * settings["gui_scale"] + default_settings["pygame_window_length"] / 2),
                               int(default_settings["pygame_window_height"] - 16 * settings["gui_scale"]))
        if slot == _world["player"]["state"]["selected_slot"]:
            slot_image.fill("#8000FF80")
        else:
            slot_image.fill("#8040C080")
        screen.blit(slot_image, item_image_position)
        screen.blit(item_image, item_image_position)
    # display selected item's name
    item_info = str(_world["player"]["state"]["backpack"][_world["player"]["state"]["selected_slot"]]["count"]) + "*" + data["item_data"][_world["player"]["state"]["backpack"][_world["player"]["state"]["selected_slot"]]["id"]]["name"]
    item_info_displayable = [set_character({"character": item_info[i]}) for i in range(len(item_info))]
    display_text(item_info_displayable, (default_settings["pygame_window_length"] / 2, default_settings["pygame_window_height"] - settings["gui_scale"] * 16), settings["gui_scale"], "bottom")
    # display debug screen
    if settings["debug"] == True:
        player_coordinate = str(int(_world["player"]["state"]["coordinate"][0])) + "," + str(int(_world["player"]["state"]["coordinate"][1]))
        player_coordinate_displayable = [set_character({"character": player_coordinate[i]}) for i in range(len(player_coordinate))]
        display_text(player_coordinate_displayable, (0, 0), settings["gui_scale"], "top_left")


def display_craft(_world: dict[str, Any]) -> None:
    if _world["player"]["state"]["temporary"]["successful_crafting"] == "true":
        pygame_window.fill("#008000")
    elif _world["player"]["state"]["temporary"]["successful_crafting"] == "false":
        pygame_window.fill("#800000")
    else:
        pygame_window.fill("#000000")
    screen.fill("#00000000")
    # display all the recipes
    slot_image = pygame.Surface((16 * settings["gui_scale"], 16 * settings["gui_scale"])).convert_alpha()
    selected_recipe = _world["player"]["state"]["temporary"]["selected_recipe"]
    for recipe in range(len(data["recipe_data"])):
        for slot in range(len(data["recipe_data"][recipe]["from"])):
            item_image_unscaled = assets["item_images"][data["recipe_data"][recipe]["from"][slot]["id"]]
            item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
            item_image_position = (int(((recipe - selected_recipe) * 16 - 8) * settings["gui_scale"] + default_settings["pygame_window_length"] / 2),
                                   int((slot + 1) * 16 * settings["gui_scale"]))
            if recipe == selected_recipe:
                slot_image.fill("#FF000080")
            else:
                slot_image.fill("#C0404080")
            screen.blit(slot_image, item_image_position)
            screen.blit(item_image, item_image_position)
        item_image_unscaled = assets["item_images"][data["recipe_data"][recipe]["to"][0]["id"]]
        item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
        item_image_position = (int(((recipe - selected_recipe) * 16 - 8) * settings["gui_scale"] + default_settings["pygame_window_length"] / 2), 0)
        if recipe == selected_recipe:
            slot_image.fill("#00FF0080")
        else:
            slot_image.fill("#40C04080")
        screen.blit(slot_image, item_image_position)
        screen.blit(item_image, item_image_position)
    # display the backpack
    backpack = _world["player"]["state"]["backpack"]
    for slot in range(len(backpack)):
        item_image_unscaled = assets["item_images"][backpack[slot]["id"]]
        item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
        item_image_position = (int((slot * 16 - data["mob_data"]["player"]["data"]["max_slot"] * 8) * settings["gui_scale"] + default_settings["pygame_window_length"] / 2),
                               int(default_settings["pygame_window_height"] - 16 * settings["gui_scale"]))
        slot_image.fill("#80808080")
        screen.blit(slot_image, item_image_position)
        screen.blit(item_image, item_image_position)
    # display selected recipe's name
    item_info = str(data["recipe_data"][selected_recipe]["to"][0]["count"]) + "*" + data["item_data"][data["recipe_data"][selected_recipe]["to"][0]["id"]]["name"]
    item_info_displayable = [set_character({"character": item_info[i]}) for i in range(len(item_info))]
    display_text(item_info_displayable, (default_settings["pygame_window_length"] / 2, default_settings["pygame_window_height"] - settings["gui_scale"] * 16), settings["gui_scale"], "bottom")