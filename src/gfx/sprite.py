import pygame
from pygame import Vector2
from typing import List

class MySprite(pygame.sprite.Sprite):
    def __init__(self, surface: pygame.Surface, pos: List[float], wrap_around=False, debug_print=False):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(center=pos)
        self.fpos = Vector2(pos)
        self.wrap_around = wrap_around
        self.collision_rect: List[pygame.Rect] = []
        self.debug_print = debug_print

    def update(self):
        pass

    def create_rect(self, x, y, w=64, h=64):
        return pygame.Rect(x - w / 2, y - h / 2, w, h)

    def draw(self, screen: pygame.Surface):
        if self.rect is None or self.image is None:
            return
        x, y = self.rect.topleft
        cx, cy = self.rect.center
        self.collision_rect.clear()
        self.collision_rect.append(self.create_rect(
                                   self.rect.centerx, self.rect.centery))
        if self.wrap_around:
            # Find the portion of the sprite that is above the screen (y<0)
            # and draw it on the bottom of the screen
            sh = screen.get_height()
            sw = screen.get_width()
            h = self.rect.height
            w = self.rect.width
            additional_blit = Vector2(0, 0)
            # vertical blit
            if y < 0 and abs(y) <= h:
                screen.blit(self.image, (x, sh + y))
                self.collision_rect.append(
                    self.create_rect(cx, sh + cy))
                # pygame.Rect(x, sh+y, self.rect.width, self.rect.height)
                # .inflate(inflate_by, inflate_by))
                additional_blit.y = sh + cy
            if y + h > sh and sh - y < h:
                screen.blit(self.image, (x, y - sh))
                self.collision_rect.append(
                    self.create_rect(cx, cy - sh))
                # pygame.Rect(x, y-sh, self.rect.width, self.rect.height)
                # .inflate(inflate_by, inflate_by))
                additional_blit.y = cy - sh
            # horizontal blit
            if x < 0 and abs(x) <= w:
                screen.blit(self.image, (sw + x, y))
                self.collision_rect.append(
                    self.create_rect(sw + cx, cy))
                # pygame.Rect(sw+x, y, self.rect.width, self.rect.height))
                additional_blit.x = sw + cx
            if x + w > sw and sw - x < w:
                screen.blit(self.image, (x - sw, y))
                self.collision_rect.append(
                    self.create_rect(cx - sw, cy))
                # pygame.Rect(x-sw, y, self.rect.width, self.rect.height)
                # .inflate(inflate_by, inflate_by))
                additional_blit.x = cx - sw
            if additional_blit.x != 0 and additional_blit.y != 0:
                screen.blit(self.image, additional_blit)
                self.collision_rect.append(
                    self.create_rect(additional_blit.x, additional_blit.y))
                # self.CreateRect(cx-sw, cy))
                # pygame.Rect(additional_blit.x, additional_blit.y,
                #             self.rect.width, self.rect.height)
                # .inflate(inflate_by, inflate_by))
        screen.blit(self.image, (x, y))
        if self.debug_print:
            print(self.collision_rect)
            for r in self.collision_rect:
                pygame.draw.rect(screen, (255, 0, 0),
                                 r,
                                 width=1)
                # pygame.draw.rect(screen, (0, 0, 255),
                #                  pygame.Rect(r.centerx, r.centery, 5, 5),
                #                  width=2)
