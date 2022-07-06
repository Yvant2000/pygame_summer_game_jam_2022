from enum import Enum, auto

from pygame import K_ESCAPE
from pygame import Surface

from scripts.player import PLAYER
from scripts.splash_screen import SPLASH_SCREEN
from scripts.pause_menu import PAUSE_MENU
from scripts.display import DISPLAY
from scripts.room import Room, BedRoom


class GAME_STATE(Enum):
    SPLASH_SCREEN = auto()
    GAME = auto()
    PAUSE = auto()


class GAME:

    STATE: GAME_STATE = GAME_STATE.SPLASH_SCREEN
    SCREEN_SIZE_MULTIPLIER: float = 0.1
    SURFACE: Surface = Surface((DISPLAY.width * SCREEN_SIZE_MULTIPLIER, DISPLAY.height * SCREEN_SIZE_MULTIPLIER))
    CURRENT_ROOM: Room = BedRoom()
    ESCAPE_PRESSED: bool = False

    @classmethod
    def update(cls):
        PLAYER.update_keys()

        match cls.STATE:
            case GAME_STATE.SPLASH_SCREEN:
                if SPLASH_SCREEN.update():
                    cls.STATE = GAME_STATE.GAME

            case GAME_STATE.GAME:
                cls.run_game()

            case GAME_STATE.PAUSE:
                if PAUSE_MENU.update():
                    cls.STATE = GAME_STATE.GAME

    @classmethod
    def run_game(cls):

        cls.performance_adjustment()
        cls.SURFACE.fill((0, 0, 0))
        cls.CURRENT_ROOM.update(cls.SURFACE)
        DISPLAY.display(cls.SURFACE)

        if PLAYER.movements:
            if cls.do_pause():
                cls.STATE = GAME_STATE.PAUSE
                PAUSE_MENU.paused_surface = cls.SURFACE
                return
            PLAYER.move(cls.SCREEN_SIZE_MULTIPLIER)

    @classmethod
    def do_pause(cls) -> bool:
        """Return True if the player pressed the escape key."""
        if PLAYER.keys[K_ESCAPE]:
            if cls.ESCAPE_PRESSED:
                return False
            cls.ESCAPE_PRESSED = True
            return True
        cls.ESCAPE_PRESSED = False
        return False

    @classmethod
    def performance_adjustment(cls):
        if DISPLAY.fps < 30:
            cls.SCREEN_SIZE_MULTIPLIER *= 0.99
            cls.SCREEN_SIZE_MULTIPLIER = max(cls.SCREEN_SIZE_MULTIPLIER, 0.1)
            cls.SURFACE = Surface((DISPLAY.size[0] * cls.SCREEN_SIZE_MULTIPLIER,
                                   DISPLAY.size[1] * cls.SCREEN_SIZE_MULTIPLIER))
        elif DISPLAY.fps > 60:
            cls.SCREEN_SIZE_MULTIPLIER *= 1.01
            cls.SCREEN_SIZE_MULTIPLIER = min(cls.SCREEN_SIZE_MULTIPLIER, 1.)
            cls.SURFACE = Surface((DISPLAY.size[0] * cls.SCREEN_SIZE_MULTIPLIER,
                                   DISPLAY.size[1] * cls.SCREEN_SIZE_MULTIPLIER))
