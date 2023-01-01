from GameMechanics import *
from typing import Any, Optional, Literal
import sys
import os
import math
import json
import time
import copy


if __name__ != "__main__":
    print("[ERROR] The value of __name__ is not \"__main__\".")
    os._exit(1)


print("Pythons&Boxes By Yangsy56302")
window = pygame.display.set_mode((settings["window_length"], settings["window_height"]))
window.fill((0, 0, 0))
if settings["debug"] == True:
    pygame.display.set_caption("Pythons&Boxes DEBUG_MODE")
else:
    pygame.display.set_caption("Pythons&Boxes")
pygame.display.set_icon(pygame.image.load(".\\assets\\images\\icons\\PythonsAndBoxes.png").convert_alpha())
screen = pygame.Surface((settings["window_length"], settings["window_height"]), pygame.SRCALPHA)


if settings["read_world"] == True and os.path.exists(settings["world_directory"]):
    print_info("Reading World File...")
    file = open(settings["world_directory"], mode="r")
    world = World(json.load(file))
    file.close()
    print_info("Done.")
else:
    world = World({})


def display_world(_coordinate: tuple[float, float]) -> None:
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
            if not world.valid_coordinate((tile_x, tile_y)):
                continue
            tile = world.map[tile_x][tile_y]
            tile_image_unscaled = assets.tile_images[tile.id]
            tile_image = pygame.transform.scale(tile_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
            tile_image_position = ((int((offset_x - float_x) * 16 - 8) * settings["map_scale"]) + settings["window_length"] / 2,
                                   (int((offset_y - float_y) * -16 - 8) * settings["map_scale"]) + settings["window_height"] / 2)
            screen.blit(tile_image, tile_image_position)
    # display mobs
    for mob_number in range(len(world.mobs)):
        mob_image_unscaled = assets.mob_images[world.mobs[mob_number].id]
        mob_image = pygame.transform.scale(mob_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
        if world.mobs[mob_number].state.get("hurt", False):
            mob_image = tint_image(mob_image, pygame.Color(255, 0, 0, 128))
        mob_image_position = (int(((world.mobs[mob_number].state["coordinate"][0] - _coordinate[0]) * 16 - 8) * settings["map_scale"]) + settings["window_length"] / 2,
                              int(((world.mobs[mob_number].state["coordinate"][1] - _coordinate[1]) * -16 - 8) * settings["map_scale"]) + settings["window_height"] / 2)
        if mob_image_position[0] > -16 * settings["map_scale"] and mob_image_position[0] < settings["window_length"]:
            if mob_image_position[1] > -16 * settings["map_scale"] and mob_image_position[1] < settings["window_height"]:
                screen.blit(mob_image, mob_image_position)
    # display player
    player_image_unscaled = assets.mob_images["player"]
    player_image = pygame.transform.scale(player_image_unscaled, (16 * settings["map_scale"], 16 * settings["map_scale"]))
    player_image_position = (int(((world.player.state["coordinate"][0] - _coordinate[0]) * 16 - 8) * settings["map_scale"]) + settings["window_length"] / 2,
                             int(((world.player.state["coordinate"][1] - _coordinate[1]) * -16 - 8) * settings["map_scale"]) + settings["window_height"] / 2)
    screen.blit(player_image, player_image_position)
    # display the backpack
    backpack = world.player.state["backpack"]
    slot_image = pygame.Surface((16 * settings["gui_scale"], 16 * settings["gui_scale"])).convert_alpha()
    for slot in range(len(backpack)):
        item_image_unscaled = assets.item_images[backpack[slot].id]
        item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
        item_image_position = (int((slot * 16 - data.mob_data["player"]["data"]["max_slot"] * 8) * settings["gui_scale"] + settings["window_length"] / 2),
                               int(settings["window_height"] - 16 * settings["gui_scale"]))
        if slot == world.player.state["selected_slot"]:
            slot_image.fill("#8000FF80")
        else:
            slot_image.fill("#8040C080")
        screen.blit(slot_image, item_image_position)
        screen.blit(item_image, item_image_position)
    # display selected item's name
    item_info = str(world.player.state["backpack"][world.player.state["selected_slot"]].count) + "*" + data.item_data[world.player.state["backpack"][world.player.state["selected_slot"]].id]["name"]
    item_info_displayable = [Character(item_info[i]) for i in range(len(item_info))]
    display_text(item_info_displayable, (settings["window_length"] / 2, settings["window_height"] - settings["gui_scale"] * 16), settings["gui_scale"], "bottom")
    # display debug screen
    if settings["debug"] == True:
        player_coordinate = str(int(world.player.state["coordinate"][0])) + "," + str(int(world.player.state["coordinate"][1]))
        for character_number in range(len(player_coordinate)):
            character_image_unscaled = assets.font_images[player_coordinate[character_number]]
            character_image = pygame.transform.scale(character_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
            character_image_position = (int(character_number * 16 * settings["gui_scale"]), 0)
            screen.blit(character_image, character_image_position)
def display_craft() -> None:
    if world.player.state["temporary"]["successful_crafting"] == "true":
        window.fill("#008000")
    elif world.player.state["temporary"]["successful_crafting"] == "false":
        window.fill("#800000")
    else:
        window.fill("#000000")
    screen.fill("#00000000")
    # display all the recipes
    slot_image = pygame.Surface((16 * settings["gui_scale"], 16 * settings["gui_scale"])).convert_alpha()
    selected_recipe = world.player.state["temporary"]["selected_recipe"]
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
    backpack = world.player.state["backpack"]
    for slot in range(len(backpack)):
        item_image_unscaled = assets.item_images[backpack[slot].id]
        item_image = pygame.transform.scale(item_image_unscaled, (16 * settings["gui_scale"], 16 * settings["gui_scale"]))
        item_image_position = (int((slot * 16 - data.mob_data["player"]["data"]["max_slot"] * 8) * settings["gui_scale"] + settings["window_length"] / 2),
                               int(settings["window_height"] - 16 * settings["gui_scale"]))
        slot_image.fill("#80808080")
        screen.blit(slot_image, item_image_position)
        screen.blit(item_image, item_image_position)
    # display selected recipe's name
    item_info = str(data.recipe_data[selected_recipe]["to"][0]["count"]) + "*" + data.item_data[data.recipe_data[selected_recipe]["to"][0]["id"]]["name"]
    item_info_displayable = [Character(item_info[i]) for i in range(len(item_info))]
    display_text(item_info_displayable, (settings["window_length"] / 2, settings["window_height"] - settings["gui_scale"] * 16), settings["gui_scale"], "bottom")


return_value = "do_nothing"
key_states = {}
mouse_states = {"position": (0, 0), "movement": (0, 0), "left": "up", "middle": "up", "right": "up", "scroll_up": 0, "scroll_down": 0}
gui = "world"
while return_value != "quit":
    start_tick_time = time.time()
    events = pygame.event.get()
    key_states = get_key_states(events, key_states)
    mouse_states = get_mouse_states(events, mouse_states)
    if gui == "world":
        return_value = world.tick(key_states, mouse_states)
        display_world((world.player.state["coordinate"][0], world.player.state["coordinate"][1]))
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
if settings["write_world"] == True and os.path.exists(settings["world_directory"]):
    print_info("Writing World File...")
    file = open(settings["world_directory"], mode="w")
    json.dump(world.set_to_json(), file)
    file.close()
    print_info("Done.")
pygame.quit()
os._exit(0)