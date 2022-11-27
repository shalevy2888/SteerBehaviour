import sys

import pygame
from pygame.math import Vector2

from gfx.sprite import MySprite
from infra.vmath import Vector
from steer.formation import FormationArrowHead
from steer.movable_entity import MovableEntity
from steer.movable_entity import Waypoint
from steer.path import circle_path
from steer.path import Path
from steer.path import shift_path
from steer.squad import Squad
from steer.squad_behaviour import path
from steer.squad_behaviour_condition import infinite_behaviour_condition

# from steer.steer_behaviour import wander

# from math import pi, acos
# import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800


class Ship(MySprite, MovableEntity):
    def __init__(self, position):
        MovableEntity.__init__(self, Vector(position[0], position[1]))
        self.orig_image = pygame.image.load('images/PlayerShipBlaster1.png')
        super().__init__(self.orig_image.copy(), position, True, False)
        self.fpos: Vector2 = Vector2(0.0, 0.0)
        self.movement: Vector2 = Vector2(0.0, 0.0)
        self.angle: float = 0.0
        self.rect.center = position

        # Moveable entity
        self.max_speed = 80.0
        self.max_force = 25.0
        # self.steer_force = wander()
        self.target = Waypoint.NAWaypoint()
        self.lead = False

    def update(self, dt: float):
        global screen
        # self.update_steer_behaviour(dt)
        # self.movement = Vector2(self.velocity.x, self.velocity.y)

        # self.get_input()
        velocity_vector2 = Vector2(self.velocity.x, self.velocity.y)
        angle_to: float = velocity_vector2.angle_to(Vector2(0, 1))
        self.angle = angle_to + 180
        # print(velocity_vector2, self.angle)

        # print(self.angle, self.forward, self.movement)
        rot_image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = rot_image.get_rect(center=self.fpos)
        # self.fpos = self.fpos + self.movement
        self.fpos = Vector2(self.pos.x, self.pos.y)

        # vertical correction to screen height
        if self.fpos.y < (-self.rect.height / 2):
            self.fpos.y = screen.get_height() + self.fpos.y
        if self.fpos.y > screen.get_height() + self.rect.height / 2:
            self.fpos.y -= screen.get_height()
        # horizontal correction to screen width
        if self.fpos.x < (-self.rect.width / 2):
            self.fpos.x = screen.get_width() + self.fpos.x
        if self.fpos.x > screen.get_width() + self.rect.width / 2:
            self.fpos.x -= screen.get_width()

        self.rect.center = (int(self.fpos.x), int(self.fpos.y))
        self.image = rot_image
        if self.lead is True:
            self.image.fill((0, 230, 0, 230), special_flags=pygame.BLEND_RGBA_MULT)

    def draw(self, screen: pygame.Surface):
        if self.lead is True:
            # self.image.fill((0, 190, 0, 100), special_flags=pygame.BLEND_ADD)
            pygame.draw.rect(
                screen, 'green', pygame.Rect(self.target.pos.x, self.target.pos.y, 3, 3)
            )
        if self.target is not None:
            pygame.draw.line(
                screen,
                'yellow',
                (self.pos.x, self.pos.y),
                (self.target.pos.x, self.target.pos.y),
            )
        super().draw(screen)


class VisiblePath:
    def __init__(self, p: Path) -> None:
        self.path = p

    def draw(self, screen: pygame.Surface):
        for idx, v in enumerate(self.path):
            print(idx, v)
            pygame.draw.rect(screen, 'red', pygame.Rect(v.x, v.y, 5, 5))


class Level:
    def __init__(self, surface):
        self.display_surface = surface
        self.setup_level()
        self.leader = None

    def setup_level(self):
        self.players = pygame.sprite.Group()  # GroupSingle()
        # self.background = pygame.image.load('images/space.png')

        # self.path = VisiblePath(shift_path(patrol_path(8, False, 450, 300, True, False), Vector(100, 100)))
        self.path = VisiblePath(
            shift_path(circle_path(250, 0, 20, 1), Vector(350, 350))
        )

        self.s1 = Squad()
        self.s1.entities = [Ship([100, 100]) for _ in range(8)]
        self.s1.formation = FormationArrowHead()
        self.s1.formation.scale = 0.7
        self.s1.squad_behaviour = path(
            infinite_behaviour_condition(), self.path.path, self.s1, True
        )
        # squad_wander(self.s1, 30, SCREEN_WIDTH, SCREEN_HEIGHT)
        for e in self.s1.entities:
            self.players.add(e)
        self.leader = self.s1.get_leader()
        self.leader.max_force = 65
        self.leader.lead = True

    def run(self, dt: float) -> None:
        # draw level
        screen.fill("black")
        self.path.draw(self.display_surface)
        # self.display_surface.blit(self.background, [0, 0])
        self.s1.update_squad_behaviour(dt)

        new_leader = self.s1.get_leader()
        if new_leader != self.leader:
            if self.leader is not None:
                self.leader.lead = False
            self.leader = new_leader
            self.leader.lead = True
        # player
        player: MySprite
        for player in self.players:
            player.update(dt)
            player.draw(self.display_surface)


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Steer Behaviour")
clock = pygame.time.Clock()
level = Level(screen)


def game_loop():
    game_over = False
    ticks_last_frame: float = pygame.time.get_ticks()

    while not game_over:
        # check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        t = pygame.time.get_ticks()
        dt = (t - ticks_last_frame) / 1000.0
        ticks_last_frame = t

        level.run(dt)

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    game_loop()
    pygame.quit()
    sys.exit()
