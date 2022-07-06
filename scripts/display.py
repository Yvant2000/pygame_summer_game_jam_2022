from os.path import join as join_path
from os import listdir
from typing import Generator

from pygame import display as pygame_display
from pygame.transform import scale
from pygame import FULLSCREEN, SCALED
from pygame import Surface
from pygame.time import Clock
from pygame.image import load as pygame_image_load


def load_image(*path: str) -> Surface:
    """Load an image from a path.
    @param path: The path to the image.
    :return: The loaded image.
    """
    return pygame_image_load(join_path(*path)).convert_alpha()


def lazy_load_images(*path: str) -> Generator:
    """Load images from a directory """
    path: str = join_path(*path)
    for file_path in listdir(path):
        yield load_image(path, file_path)


class Display:
    FPS_LIMIT: int = 75

    def __init__(self) -> None:
        self.display_info = pygame_display.Info()
        self.screen: Surface = pygame_display.set_mode(
            (self.display_info.current_w, self.display_info.current_h),
            FULLSCREEN | SCALED,
            vsync=True)
        self._clock: Clock = Clock()
        self._fps: int = 0
        self._delta: float = 0.

    @property
    def size(self) -> tuple[int, int]:
        """Return the screen size."""
        return self.screen.get_size()

    @property
    def caption(self) -> str:
        """Return the caption of the screen."""
        return pygame_display.get_caption()[0]

    @caption.setter
    def caption(self, title: str) -> None:
        """Set the caption of the window."""
        pygame_display.set_caption(title)

    @property
    def fps(self) -> int:
        """Return the current FPS."""
        return self._fps

    @property
    def delta_time(self) -> float:
        """get the time in seconds between two frames."""
        return self._delta

    def update(self) -> None:
        """Update the screen."""
        pygame_display.update()
        self.screen.fill((0, 0, 0))
        self._delta = self._clock.tick(Display.FPS_LIMIT) / 1000
        self._fps = self._clock.get_fps()

    def display(self, surface: Surface) -> None:
        """Display a surface on the screen.

        The surface will be scaled to the screen size.
        @param surface: The surface to display
        """
        scale(surface, self.size, self.screen)


DISPLAY: Display = Display()
