from pygame import display as pygame_display
from pygame.transform import scale
from pygame import FULLSCREEN, SCALED
from pygame import Surface
from pygame.time import Clock


class Display:
    def __init__(self, title: str = "") -> None:
        self.display_info: VideoInfo = pygame_display.Info()
        self.screen: Surface = pygame_display.set_mode(
            (self.display_info.current_w, self.display_info.current_h),
            FULLSCREEN | SCALED,
            vsync=True)
        self._clock: Clock = Clock()
        self._fps: int = 0
        self._delta: float = 0.

        if title:
            pygame_display.set_caption(title)

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
        """get the time between two frames."""
        return self._delta

    def update(self) -> None:
        """Update the screen."""
        pygame_display.update()
        self._delta = self._clock.tick() / 10
        self._fps = self._clock.get_fps()

    def blit(self, surface: Surface) -> None:
        """Blit a surface on the screen.

        The surface will be scaled to the screen size.
        @param surface: The surface to display
        """
        scale(surface, self.size, self.screen)
