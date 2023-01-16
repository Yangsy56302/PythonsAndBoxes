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


settings["world_directory"] = tkinter.StringVar(value=default_settings["world_directory"])
settings["read_world"] = tkinter.BooleanVar(value=default_settings["read_world"])
settings["write_world"] = tkinter.BooleanVar(value=default_settings["write_world"])
settings["debug"] = tkinter.BooleanVar(value=default_settings["debug"])


game_running = False
def start_game() -> None:
    global game_running
    game_running = True
    if settings["read_world"].get() == True and os.path.exists(settings["world_directory"].get()):
        print_info("Reading World File...")
        file = open(settings["world_directory"].get(), mode="r")
        world = World({"type": "load", "json": json.load(file)})
        file.close()
    else:
        world = World({"type": "new", "settings": settings["world_settings"]})
    print("Pythons&Boxes By Yangsy56302")
    key_states = {}
    mouse_states = {"position": (0, 0), "movement": (0, 0), "left": "up", "middle": "up", "right": "up", "scroll_up": 0, "scroll_down": 0}
    gui = "world"
    return_value = "do_nothing"
    while return_value != "quit":
        start_tick_time = time.time()
        events = pygame.event.get()
        key_states = get_key_states(events, key_states)
        mouse_states = get_mouse_states(events, mouse_states)
        if gui == "world":
            return_value = world.tick(key_states, mouse_states)
            display_world(world, (world.player.state["coordinate"][0], world.player.state["coordinate"][1]))
            if return_value == "craft":
                gui = "craft"
        elif gui == "craft":
            return_value = world.crafts(key_states, mouse_states)
            display_craft(world)
            if return_value == "world":
                gui = "world"
        pygame_window.blit(screen, (0, 0))
        pygame.display.flip()
        stop_tick_time = time.time()
        while stop_tick_time - start_tick_time < 0.0625:
            stop_tick_time = time.time()
    if settings["write_world"].get() == True and os.path.exists(settings["world_directory"].get()):
        print_info("Writing World File...")
        file = open(settings["world_directory"].get(), mode="w")
        json.dump(world.set_to_json(), file)
        file.close()
    game_running = False


read_world_check_button = tkinter.Checkbutton(tkinter_window, text="Read World", variable=settings["read_world"], onvalue=True, offvalue=False)
read_world_check_button.place(x=112, y=32, width=128, height=32)
write_world_check_button = tkinter.Checkbutton(tkinter_window, text="Write World", variable=settings["write_world"], onvalue=True, offvalue=False)
write_world_check_button.place(x=272, y=32, width=128, height=32)
world_directory_label = tkinter.Label(tkinter_window, text="World File Location")
world_directory_label.place(x=0, y=64, width=512, height=32)
world_directory_entry = tkinter.Entry(tkinter_window, textvariable=settings["world_directory"])
world_directory_entry.place(x=128, y=96, width=256, height=32)
debug_mode_check_button = tkinter.Checkbutton(tkinter_window, text="DEBUG MODE", variable=settings["debug"], onvalue=True, offvalue=False)
debug_mode_check_button.place(x=192, y=288, width=128, height=32)
start_button = tkinter.Button(tkinter_window, text="Start", command=start_game)
start_button.place(x=224, y=320, width=64, height=32)
while True:
    tkinter_window.update()