from enum import Enum, auto

from pygame import K_ESCAPE
from pygame import Surface, draw, transform

from scripts.player import PLAYER
from scripts.splash_screen import SPLASH_SCREEN
from scripts.pause_menu import PAUSE_MENU
from scripts.display import DISPLAY
from scripts.room import Room, LivingRoom, LongCorridor
from scripts.text import Text
from scripts.end_screen import END_SCREEN

from nostalgiaefilters import vignette


class GAME_STATE(Enum):
    SPLASH_SCREEN = auto()
    GAME = auto()
    PAUSE = auto()
    TITLE_END = auto()


class GAME:

    STATE: GAME_STATE = GAME_STATE.SPLASH_SCREEN
    SCREEN_SIZE_MULTIPLIER: float = 0.1
    SURFACE: Surface = Surface((DISPLAY.width * SCREEN_SIZE_MULTIPLIER, DISPLAY.height * SCREEN_SIZE_MULTIPLIER))
    CURRENT_ROOM: Room = LivingRoom()  # TODO: set to LivingRoom on release
    ESCAPE_PRESSED: bool = False
    TEXT: Text | None = None
    VIGNETTE: float = 0
    BG_COLOR: tuple[int, int, int] = (0, 0, 0)

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

            case GAME_STATE.TITLE_END:
                END_SCREEN.blit()

    @classmethod
    def set_room(cls, room: Room):
        cls.CURRENT_ROOM = room

    @classmethod
    def run_game(cls):

        cls.performance_adjustment()
        cls.SURFACE.fill(cls.BG_COLOR)
        cls.CURRENT_ROOM.update(cls.SURFACE)
        vignette(cls.SURFACE, inner_radius=-cls.SURFACE.get_width()/6, strength=cls.VIGNETTE)
        cls.display_text()
        # cls.draw_collisions()
        DISPLAY.display(cls.SURFACE)

        if PLAYER.movements:
            if cls.do_pause():
                cls.STATE = GAME_STATE.PAUSE
                PAUSE_MENU.paused_surface = cls.SURFACE
                return
            PLAYER.move(cls.SCREEN_SIZE_MULTIPLIER, cls.CURRENT_ROOM.collisions)

    @classmethod
    def draw_collisions(cls):
        left = min(cls.CURRENT_ROOM.collisions, key=lambda c: c.left).left
        right = max(cls.CURRENT_ROOM.collisions, key=lambda c: c.right).right
        top = min(cls.CURRENT_ROOM.collisions, key=lambda c: c.top).top
        bottom = max(cls.CURRENT_ROOM.collisions, key=lambda c: c.bottom).bottom

        left = min(left, int(PLAYER.x * 100))
        right = max(right, int(PLAYER.x * 100 + 20))
        top = min(top, int(PLAYER.z * 100))
        bottom = max(bottom, int(PLAYER.z * 100 + 20))

        surf = Surface((right - left, bottom - top)).convert_alpha()
        surf.fill((0, 0, 0, 0))
        for collision in cls.CURRENT_ROOM.collisions:
            draw.rect(surf, (255, 0, 0, 255), (collision.left - left, collision.top - top, collision.width, collision.height), 100)
        draw.rect(surf, (0, 255, 0, 255), (PLAYER.x*100 - left, PLAYER.z*100 - top, 20, 20), 5)
        temp = transform.scale(surf, cls.SURFACE.get_size())
        cls.SURFACE.blit(temp, (0, 0))

    @classmethod
    def display_text(cls):
        if cls.TEXT is None:
            return
        if cls.TEXT.draw(cls.SURFACE, cls.SURFACE.get_rect().centerx, cls.SURFACE.get_rect().height * 0.9):
            cls.TEXT = None

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
        if DISPLAY.fps < 35:
            cls.SCREEN_SIZE_MULTIPLIER *= 0.99
            cls.SCREEN_SIZE_MULTIPLIER = max(cls.SCREEN_SIZE_MULTIPLIER, 0.1)
            cls.SURFACE = Surface((DISPLAY.size[0] * cls.SCREEN_SIZE_MULTIPLIER,
                                   DISPLAY.size[1] * cls.SCREEN_SIZE_MULTIPLIER))
        elif DISPLAY.fps > 50:
            cls.SCREEN_SIZE_MULTIPLIER *= 1.005
            cls.SCREEN_SIZE_MULTIPLIER = min(cls.SCREEN_SIZE_MULTIPLIER, 1.)
            cls.SURFACE = Surface((DISPLAY.size[0] * cls.SCREEN_SIZE_MULTIPLIER,
                                   DISPLAY.size[1] * cls.SCREEN_SIZE_MULTIPLIER))
