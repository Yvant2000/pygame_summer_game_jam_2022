#### __IMPORTS__ ####

# STANDARD IMPORTS #

from os import environ
# disable the pygame message
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"

# THIRD PARTY IMPORTS #

import pygame
from pygame import event as pygame_event

# LOCAL IMPORTS #

from scripts.display import Display

#### __INIT__ ####

pygame.init()
display = Display()


def events() -> bool:
    """Handle the pygame events.
    :return: True if the game should continue, False otherwise.
    """
    for event in pygame_event.get():
        match event.type:
            case pygame.QUIT:
                return False
    return True


def main(debug: bool = False) -> None:
    while events():
        display.update()
        if debug:
            print(f"FPS: {display.fps}")
            print(f"Delta: {display.delta_time}")
            print(f"Caption: {display.caption}")
            print(f"Size: {display.size}")
            print()


if __name__ == '__main__':
    main(__debug__)  # Look mom ! I'm a pro at Python !
