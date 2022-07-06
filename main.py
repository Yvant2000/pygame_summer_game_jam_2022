#### __IMPORTS__ ####

# STANDARD IMPORTS #

from os import environ
# disable the pygame message
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"

# THIRD PARTY IMPORTS #

import pygame
from pygame import event as pygame_event
pygame.init()

# LOCAL IMPORTS #

from scripts.display import DISPLAY


# EVENT LOOP #

def events() -> bool:
    """Handle the pygame events.
    :return: True if the game should continue, False otherwise.
    """
    for event in pygame_event.get():
        match event.type:
            case pygame.QUIT:
                return False
    return True


# MAIN LOOP #

def debug_print() -> None:
    print(f"FPS: {DISPLAY.fps}")
    print(f"Delta: {DISPLAY.delta_time}")
    print(f"Caption: {DISPLAY.caption}")
    print(f"Size: {DISPLAY.size}")
    print()


def main(debug: bool = False) -> None:
    while events():
        DISPLAY.update()
        if debug:
            debug_print()


if __name__ == '__main__':
    main(__debug__)  # Look mom ! I'm a pro at Python !
