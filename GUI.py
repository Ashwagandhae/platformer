import pygame as pg
from utilities import *
from pygame.math import Vector2 as vec


class HealthBar(pg.sprite.Sprite):
    def __init__(self, size, thing, offset, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface(size)
        self.percent = 1
        self.rect = self.image.get_rect()
        self.parent = thing
        self.offset = offset
        self.rect.center = self.parent.pos + self.offset
        self.color = (0, 255, 0)
        # make healthbar image
        self.image.fill((0, 0, 0))
        pg.draw.rect(
            self.image, self.color, pg.Rect(0, 0, self.rect.width, self.rect.height)
        )

    def update(self):
        self.rect.center = self.parent.pos + self.offset
        pixel = intTuple(self.rect.midtop + vec(0, -10) + self.game.cameraOffset)
        self.image.fill(colorShade(self.game.screen.get_at(pixel), -15))
        pg.draw.rect(
            self.image,
            self.color,
            pg.Rect(0, 0, self.rect.width * self.percent, self.rect.height),
        )

    def changePercent(self, percent):
        self.percent = percent
