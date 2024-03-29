from typing import Any, Optional, Literal
import sys
import os
import math
import json
import copy


def import_settings() -> dict[str, Any]:
    file = open(".\\data\\settings.json", mode="r")
    return_value = json.load(file)
    file.close()
    return return_value
default_settings = import_settings()
settings = copy.deepcopy(default_settings)
tkinter_settings = copy.deepcopy(default_settings)


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "TRUE"
import pygame
pygame.init()
pygame_window = pygame.display.set_mode((default_settings["pygame_window_length"], default_settings["pygame_window_height"]))
pygame_window.fill((0, 0, 0))
pygame.display.set_caption("Pythons&Boxes")
pygame.display.set_icon(pygame.image.load(".\\assets\\images\\icons\\PythonsAndBoxes.png").convert_alpha())
pygame.display.flip()
screen = pygame.Surface((default_settings["pygame_window_length"], default_settings["pygame_window_height"]), pygame.SRCALPHA)


def exit_0() -> None:
    pygame.quit()
    os._exit(0)


def exit_1() -> None:
    pygame.quit()
    os._exit(1)


import tkinter
tkinter_window = tkinter.Tk()
tkinter_window.geometry("512x384")
tkinter_window.resizable(False, False)
tkinter_window.title("Pythons&Boxes")
tkinter_window.iconbitmap(".\\assets\\images\\icons\\PythonsAndBoxes.ico")
tkinter_window.protocol('WM_DELETE_WINDOW', exit_0)
tkinter_window.update()


def print_info(*_values, _sep: Optional[str] = " ", _end: Optional[str] = "\n") -> bool:
    if "info" in default_settings["print_type"]:
        print("[INFO]", *_values, sep=_sep, end=_end)
        return True
    return False


def print_warning(*_values, _sep: Optional[str] = " ", _end: Optional[str] = "\n") -> bool:
    if "warning" in default_settings["print_type"]:
        print("[WARNING]", *_values, sep=_sep, end=_end)
        return True
    return False


def print_error(*_values, _sep: Optional[str] = " ", _end: Optional[str] = "\n") -> bool:
    if "error" in default_settings["print_type"]:
        print("[ERROR]", *_values, sep=_sep, end=_end)
        return True
    return False


def import_data() -> dict[str, Any]:
    return_data = {}
    print_info("Loading Tile Data...")
    file = open(".\\data\\tiles.json", mode="r")
    return_data["tile_data"] = json.load(file)
    file.close()
    print_info("Loading Liquid Data...")
    file = open(".\\data\\liquids.json", mode="r")
    return_data["liquid_data"] = json.load(file)
    file.close()
    print_info("Loading Item Data...")
    file = open(".\\data\\items.json", mode="r")
    return_data["item_data"] = json.load(file)
    file.close()
    print_info("Loading Mob Data...")
    file = open(".\\data\\mobs.json", mode="r")
    return_data["mob_data"] = json.load(file)
    file.close()
    print_info("Loading Font Data...")
    file = open(".\\data\\fonts.json", mode="r")
    return_data["font_data"] = json.load(file)
    file.close()
    print_info("Loading Recipe Data...")
    file = open(".\\data\\recipes.json", mode="r")
    return_data["recipe_data"] = json.load(file)
    file.close()
    print_info("Loading Structure Data...")
    file = open(".\\data\\structures.json", mode="r")
    return_data["structure_data"] = json.load(file)
    file.close()
    return return_data
data = import_data()


def import_assets() -> dict[str, Any]:
    return_assets = {}
    return_assets["tile_images"] = {}
    return_assets["liquid_images"] = {}
    return_assets["item_images"] = {}
    return_assets["mob_images"] = {}
    return_assets["font_images"] = {}
    print_info("Loading Tile Images...")
    for id in data["tile_data"]:
        return_assets["tile_images"][id] = pygame.image.load(".\\assets\\images\\tiles\\" + id + ".png").convert_alpha()
    print_info("Loading Liquid Images...")
    for id in data["liquid_data"]:
        return_assets["liquid_images"][id] = pygame.image.load(".\\assets\\images\\liquids\\" + id + ".png").convert_alpha()
    print_info("Loading Item Images...")
    for id in data["item_data"]:
        return_assets["item_images"][id] = pygame.image.load(".\\assets\\images\\items\\" + id + ".png").convert_alpha()
    print_info("Loading Mob Images...")
    for id in data["mob_data"]:
        return_assets["mob_images"][id] = pygame.image.load(".\\assets\\images\\mobs\\" + id + ".png").convert_alpha()
    print_info("Loading Font Images...")
    font_image = pygame.image.load(".\\assets\\images\\fonts\\default.png").convert_alpha()
    for id in data["font_data"]:
        return_assets["font_images"][id] = font_image.subsurface(((data["font_data"][id]["coordinate"][0] * 16, data["font_data"][id]["coordinate"][1] * 16), (16, 16)))
    return return_assets
assets = import_assets()


def tint_image(_image: pygame.Surface, _color: Optional[pygame.Color] = pygame.Color(255, 255, 255, 255)) -> pygame.Surface:
    return_image = _image.copy()
    for x in range(_image.get_width()):
        for y in range(_image.get_height()):
            old_color = pygame.Color(_image.get_at((x, y)))
            new_color = pygame.Color(int((old_color.r * (1 - (_color.a / 255))) + (_color.r * (_color.a / 255))),
                                     int((old_color.g * (1 - (_color.a / 255))) + (_color.g * (_color.a / 255))),
                                     int((old_color.b * (1 - (_color.a / 255))) + (_color.b * (_color.a / 255))), old_color.a)
            return_image.set_at((x, y), new_color)
    return return_image


def change_image_color(_image: pygame.Surface, _color: Optional[pygame.Color] = pygame.Color(255, 255, 255, 255)) -> pygame.Surface:
    return_image = _image.copy()
    for x in range(_image.get_width()):
        for y in range(_image.get_height()):
            old_color = pygame.Color(_image.get_at((x, y)))
            new_color = pygame.Color(_color.r, _color.g, _color.b, int(_color.a * old_color.a / 255))
            return_image.set_at((x, y), new_color)
    return return_image


def get_mouse_states(_events: Any, _states: dict[str, Any]) -> dict[str, Any]:
    states = _states
    # add the underline to the pressed button
    button_name = ["left", "middle", "right", "scroll_up", "scroll_down"]
    for button_number in range(len(button_name[0:3])):
        if "_" not in states[button_name[button_number]]:
            states[button_name[button_number]] += "_"
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
                    states[button_name[button_number]] = "down"
                else:
                    states[button_name[button_number]] = "up"
        # button pressed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button - 1 in range(3):
                states[button_name[event.button - 1]] = "down"
            # special scroll detector
            elif (event.button - 1) % 2 == 0:
                states[button_name[4]] = int((event.button - 3) / 2)
            else:
                states[button_name[3]] = int((event.button - 2) / 2)
        # button released
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button - 1 in range(3):
                states[button_name[event.button - 1]] = "up"
    return states


def get_key_states(_events: Any, _states: dict[int, str]) -> dict[int, str]:
    states = _states
    for state in states:
        if "_" not in states[state]:
            states[state] += "_"
    for event in _events:
        if event.type == pygame.KEYDOWN:
            states[event.key] = "down"
        if event.type == pygame.KEYUP:
            states[event.key] = "up"
    return states


def key_is_down(_states: dict, _key: Any) -> bool:
    if _key in _states:
        if "down" in _states[_key]:
            return True
        else:
            return False
    else:
        return False


def key_is_just_down(_states: dict, _key: Any) -> bool:
    if _key in _states:
        if _states[_key] == "down":
            return True
        else:
            return False
    else:
        return False


def key_is_up(_states: dict, _key: Any) -> bool:
    if _key in _states:
        if "up" in _states[_key]:
            return True
        else:
            return False
    else:
        return False


def key_is_just_up(_states: dict, _key: Any) -> bool:
    if _key in _states:
        if _states[_key] == "up":
            return True
        else:
            return False
    else:
        return False