from enum import Enum, auto
from math import sin, pi, cos

from pygame import Surface, transform, mouse, Rect
from pygame import K_a, K_d, K_SPACE, K_LEFT, K_RIGHT, K_UP, K_RETURN, K_e, K_ESCAPE

from scripts.display import DISPLAY, load_image
from scripts.player import PLAYER

from nostalgiaefilters import fish


class TvGame:
    def __init__(self):
        self.screen = Surface((256, 224)).convert_alpha()
        self.surface = Surface((256, 224)).convert_alpha()
        self.background = load_image("data", "mini_game", "Room.png")
        self.pause_image: Surface = load_image("data", "mini_game", "pause.png")
        self.background_deca: int = 0
        self.entities: list[Entity] = [Knight(x=100, y=160)]
        self.ev: int = 0
        self.pause: bool = True
        self.enter_key: bool = True

    def update(self):

        self.move()
        self.draw_background()
        self.draw_entities()
        if self.pause:
            self.draw_pause()
        else:
            self.update_entities()
            self.events()

        self.screen.fill((0, 0, 0, 0))
        fish(self.surface, self.screen, 0.2)

    def draw_pause(self):
        self.surface.blit(self.pause_image, (0, 0))
        if PLAYER.skip:
            if not self.enter_key:
                self.enter_key = True
                self.pause = False
        else:
            self.enter_key = False

    def events(self):
        if self.background_deca > 102 and self.ev == 0:
            self.entities.append(Bat(x=400, y=150, right=False))
            self.entities.append(Bat(x=380, y=50, speed=42, right=False))
            self.entities.append(Bat(x=90, y=80, speed=38))
            self.entities.append(Zombie(x=420, speed=18, right=False))
            self.ev += 1

        if self.background_deca > 150 and self.ev == 1:
            self.ev += 1
            self.entities.append(Zombie(x=140, speed=25))
            self.entities.append(Zombie(x=420, speed=20, right=False))

    def update_entities(self):
        knight: Knight = self.entities[0]  # type: ignore
        for entity in self.entities:
            entity.update()
            if entity is not knight and knight.attack is not None:
                if entity.attack.colliderect(knight.attack):
                    entity.damage()
            if entity.damage_anim == 0 and entity.life > 0 and entity.attack.colliderect(knight.base.get_rect(topleft=(knight.x, knight.y))):
                knight.damage()

    def draw_entities(self):
        for entity in self.entities:
            self.surface.blit(entity.draw(), (entity.x - self.background_deca, entity.y))

    def draw_background(self):
        self.surface.fill((255, 0, 0))
        deca = self.background_deca % self.background.get_width()
        self.surface.blit(self.background, (-deca, 0))
        self.surface.blit(self.background, (self.background.get_width() - deca, 0))
        self.surface.blit(self.background, (2 * self.background.get_width() - deca, 0))

    def move(self):
        self.background_deca = self.entities[0].x - 70


class Entity:
    def __init__(self, x: float = 0., y: float = 0., speed: float = 10, right: bool = True):
        self.x: float = x
        self.y: float = y
        self.right: bool = right
        self.speed: float = speed
        self.attack: Rect | None = None
        self.damage_anim = 0
        self.life = 1

    def update(self):
        ...

    def draw(self) -> Surface:
        ...

    def damage(self):
        ...


class Bat(Entity):
    def __init__(self, x: float = 0., y: float = 0., right: bool = True, speed: float = 20):
        super().__init__(x=x, y=y, speed=speed, right=right)
        self.image = load_image("data", "mini_game", "Bat", "Bat1.png")
        self.image2 = load_image("data", "mini_game", "Bat", "Bat2.png")
        self.hit1 = load_image("data", "mini_game", "Bat", "Bat1Hit.png")
        self.hit2 = load_image("data", "mini_game", "Bat", "Bat2Hit.png")
        self._anim: float = 0.
        self.death_anim = 0

    def update(self):
        self.attack = self.image.get_rect(topleft=(self.x, self.y))
        self._anim += DISPLAY.delta_time
        self.x += self.speed * DISPLAY.delta_time * ((-1) ** (not self.right))
        if self.life:
            self.y += sin(self._anim) * DISPLAY.delta_time * 15
        else:
            self.y += 40 * DISPLAY.delta_time

    def draw(self) -> Surface:
        surf = self.image if int(self._anim * 2) % 2 else self.image2
        return surf if not self.right else transform.flip(surf, True, False)

    def damage(self):
        self.life = 0
        self.damage_anim = 1
        self.image = self.hit1
        self.image2 = self.hit2


class Zombie(Entity):
    def __init__(self, x: float = 0., right: bool = True, speed: float = 15):
        super().__init__(x=x, y=160, speed=speed, right=right)
        self.image = load_image("data", "mini_game", "Zombie", "ZombieR1.png")
        self.image2 = load_image("data", "mini_game", "Zombie", "ZombieR2.png")
        self.image3 = load_image("data", "mini_game", "Zombie", "ZombieL1.png")
        self.image4 = load_image("data", "mini_game", "Zombie", "ZombieL2.png")
        self.hit1 = load_image("data", "mini_game", "Zombie", "ZombieLHit.png")
        self.hit2 = load_image("data", "mini_game", "Zombie", "ZombieRHit.png")
        self._anim: float = 0.
        self.life: int = 2
        self.damage_anim: float = 0

    def update(self):
        self.attack = self.image.get_rect(topleft=(self.x, self.y))
        self._anim += DISPLAY.delta_time
        self.x += self.speed * DISPLAY.delta_time * ((-1) ** (not self.right))
        self.y += sin(self._anim) * DISPLAY.delta_time
        self.damage_anim -= DISPLAY.delta_time
        if self.damage_anim < 0:
            if self.life <= 0:
                self.y += DISPLAY.delta_time * 30

    def draw(self) -> Surface:
        if self.damage_anim > 0:
            if self.right:
                return self.hit2
            else:
                return self.hit1
        else:
            if self.right:
                return self.image if int(self._anim * 1.5) % 2 else self.image2
            else:
                return self.image3 if int(self._anim * 1.5) % 2 else self.image4

    def damage(self):
        if self.damage_anim > 0:
            return
        self.damage_anim = 0.5
        self.life -= 1


class Knight(Entity):

    class STATE(Enum):
        WAIT = auto()
        WALK = auto()
        PRE_ATTACK = auto()
        ATTACK = auto()
        JUMP = auto()

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y, 30)
        self.base = load_image("data", "mini_game", "Character", "Main-base.png")
        self.wait = load_image("data", "mini_game", "Character", "Main-wait.png")
        self.walk = load_image("data", "mini_game", "Character", "Main-walk.png")
        self.pre_attack = load_image("data", "mini_game", "Character", "Main-cut.png")
        self.attack_surf = load_image("data", "mini_game", "Character", "Main-cutted.png")
        self.state: Knight.STATE = Knight.STATE.WAIT
        self._anim: float = 0.
        self._jump: float = 0.
        self.jump_force: float = 200

    def update(self):
        self.damage_anim -= DISPLAY.delta_time
        self._anim += DISPLAY.delta_time

        if self.y < 160 or self.state == Knight.STATE.JUMP:
            if PLAYER.keys[K_d] or PLAYER.keys[K_RIGHT]:
                self.x += DISPLAY.delta_time * self.speed
            elif (PLAYER.keys[K_a] or PLAYER.keys[K_LEFT]) and self.x > 0:
                self.x -= DISPLAY.delta_time * self.speed

            self._jump += DISPLAY.delta_time
            if self._jump < 0.5 and not (PLAYER.keys[K_SPACE] or PLAYER.keys[K_UP]):
                self._jump = 0.5
            self.y -= sin(self._jump * 2 * pi) * DISPLAY.delta_time * self.jump_force
            if self.y >= 160 or self._jump > 1.0:
                if self.state == Knight.STATE.JUMP:
                    self.state = Knight.STATE.WAIT
                self.y = 160
        else:
            self._jump = 0.

        match self.state:
            case Knight.STATE.PRE_ATTACK:
                if self._anim > 0.2:
                    self.state = Knight.STATE.ATTACK
            case Knight.STATE.ATTACK:
                self.attack = Rect(self.x + (self.base.get_width()/2 if self.right else 0), self.y,
                                   self.base.get_width()/2, self.base.get_height()/2)
                if self._anim > 0.5:
                    self.state = Knight.STATE.WAIT
                    self.attack = None
            case Knight.STATE.JUMP:
                if PLAYER.keys[K_RETURN] or mouse.get_pressed()[0] or PLAYER.keys[K_e]:
                    self.state = Knight.STATE.PRE_ATTACK
                    self._anim = 0
            case _:
                if PLAYER.keys[K_d] or PLAYER.keys[K_RIGHT]:
                    if self.state != Knight.STATE.JUMP:
                        self.state = Knight.STATE.WALK
                    self.right = True
                    self.x += DISPLAY.delta_time * self.speed
                elif (PLAYER.keys[K_a] or PLAYER.keys[K_LEFT]) and self.x > 0:
                    if self.state != Knight.STATE.JUMP:
                        self.state = Knight.STATE.WALK
                    self.right = False
                    self.x -= DISPLAY.delta_time * self.speed

                elif self.state != Knight.STATE.JUMP:
                    self.state = Knight.STATE.WAIT

                if self.state != Knight.STATE.JUMP and self.y == 160:
                    if PLAYER.keys[K_SPACE] or PLAYER.keys[K_UP]:
                        self.state = Knight.STATE.JUMP
                        self._jump = 0
                if PLAYER.keys[K_RETURN] or mouse.get_pressed()[0] or PLAYER.keys[K_e]:
                    self.state = Knight.STATE.PRE_ATTACK
                    self._anim = 0

    def draw(self) -> Surface:
        mult = (abs(cos(self._jump * pi)) + 2) / 3
        surf = transform.scale(self.get_surf(), (self.base.get_width(), self.base.get_height() * mult))
        if self.damage_anim > 0:
            surf = surf.copy().convert_alpha()
            temp = Surface(surf.get_size()).convert_alpha()
            temp.fill((255, 0, 0, 50))
            surf.blit(temp, (0, 0))

        return surf if self.right else transform.flip(surf, True, False)

    def get_surf(self) -> Surface:
        anim: int = int(self._anim * 50)
        match self.state:
            case Knight.STATE.WAIT:
                return self.wait if anim % 20 < 10 else self.base
            case Knight.STATE.WALK:
                return self.walk if anim % 10 < 5 else self.base
            case Knight.STATE.PRE_ATTACK:
                return self.pre_attack
            case Knight.STATE.ATTACK:
                return self.attack_surf
            case Knight.STATE.JUMP:
                return self.base

    def damage(self):
        self.damage_anim = 0.5
