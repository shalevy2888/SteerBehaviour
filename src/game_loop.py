import pygame
import sys
from pygame.math import Vector2
from gfx.sprite import MySprite
from steer.movable_entity import MovableEntity, Waypoint
from steer.steer_behaviour import wander
# from vmath import get_angle_from, Vector
# from math import pi, acos
# import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

class Ship(MySprite, MovableEntity):
    def __init__(self, position):
        MovableEntity.__init__(self)
        self.orig_image = pygame.image.load('images/PlayerShipBlaster1@2x.png')
        super().__init__(self.orig_image.copy(), position, True, False)
        self.fpos: Vector2 = Vector2(0.0, 0.0)
        self.movement: Vector2 = Vector2(0.0, 0.0)
        self.angle: float = 0.0
        self.rect.center = position
        
        # Moveable entity
        self.max_speed = 80.0
        self.max_force = 25.0
        self.steer_force = wander()
        self.target = Waypoint.NAWaypoint()

    def update(self, dt: float):
        global screen
        self.update_steer_behaviour(dt)
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

class Level:
    def __init__(self, surface):
        self.display_surface = surface
        self.setup_level()

    def setup_level(self):
        self.players = pygame.sprite.Group()  # GroupSingle()
        # self.background = pygame.image.load('images/space.png')
        self.players.add(Ship([100, 100]))

    def run(self, dt: float) -> None:
        # draw level
        screen.fill("black")
        # self.display_surface.blit(self.background, [0, 0])

        # player
        for player in self.players:
            player.update(dt)
            player.draw(self.display_surface)  # type: ignore


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
