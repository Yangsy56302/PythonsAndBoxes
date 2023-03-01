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


tkinter_settings["world_directory"] = tkinter.StringVar(value=default_settings["world_directory"])
tkinter_settings["read_world"] = tkinter.BooleanVar(value=default_settings["read_world"])
tkinter_settings["write_world"] = tkinter.BooleanVar(value=default_settings["write_world"])
tkinter_settings["debug"] = tkinter.BooleanVar(value=default_settings["debug"])
tkinter_settings["world_settings"]["seed"] = tkinter.StringVar(value=str(default_settings["world_settings"]["seed"]))


def start_game() -> None:
    if tkinter_settings["read_world"].get() == True and os.path.exists(tkinter_settings["world_directory"].get()):
        print_info("Reading World File...")
        file = open(tkinter_settings["world_directory"].get(), mode="r")
        world = json.load(file)
        file.close()
    else:
        settings["world_settings"]["seed"] = tkinter_settings["world_settings"]["seed"].get()
        world = create_world(settings["world_settings"])
    print("Pythons&Boxes By Yangsy56302")
    key_states = {}
    mouse_states = {"position": (0, 0), "movement": (0, 0), "left": "up", "middle": "up", "right": "up", "scroll_up": 0, "scroll_down": 0}
    gui = "world"
    while not key_is_just_down(key_states, pygame.K_DELETE):
        start_tick_time = time.time()
        events = pygame.event.get()
        key_states = get_key_states(events, key_states)
        mouse_states = get_mouse_states(events, mouse_states)
        if gui == "world":
            world = tick(world, key_states, mouse_states)
            display_world(world, world["player"]["state"]["coordinate"])
            if key_is_just_down(key_states, pygame.K_c):
                gui = "craft"
        elif gui == "craft":
            world = craft(world, key_states, mouse_states)
            display_craft(world)
            if key_is_just_down(key_states, pygame.K_c):
                gui = "world"
        pygame_window.blit(screen, (0, 0))
        pygame.display.flip()
        stop_tick_time = time.time()
        while stop_tick_time - start_tick_time < 0.0625:
            stop_tick_time = time.time()
    if tkinter_settings["write_world"].get() == True and os.path.exists(tkinter_settings["world_directory"].get()):
        print_info("Writing World File...")
        file = open(tkinter_settings["world_directory"].get(), mode="w")
        json.dump(world.set_to_json(), file)
        file.close()


read_world_check_button = tkinter.Checkbutton(tkinter_window, text="Read World", variable=tkinter_settings["read_world"], onvalue=True, offvalue=False)
read_world_check_button.place(x=112, y=32, width=128, height=32)
write_world_check_button = tkinter.Checkbutton(tkinter_window, text="Write World", variable=tkinter_settings["write_world"], onvalue=True, offvalue=False)
write_world_check_button.place(x=272, y=32, width=128, height=32)
world_directory_label = tkinter.Label(tkinter_window, text="World File Location")
world_directory_label.place(x=0, y=64, width=512, height=32)
world_directory_entry = tkinter.Entry(tkinter_window, textvariable=tkinter_settings["world_directory"])
world_directory_entry.place(x=128, y=96, width=256, height=32)
world_seed_entry = tkinter.Entry(tkinter_window, textvariable=tkinter_settings["world_settings"]["seed"])
world_seed_entry.place(x=192, y=150, width=128, height=32)
debug_mode_check_button = tkinter.Checkbutton(tkinter_window, text="DEBUG MODE", variable=tkinter_settings["debug"], onvalue=True, offvalue=False)
debug_mode_check_button.place(x=192, y=288, width=128, height=32)
start_button = tkinter.Button(tkinter_window, text="Start", command=start_game)
start_button.place(x=224, y=320, width=64, height=32)
while True:
    tkinter_window.update()