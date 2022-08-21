import pygame as pg
from settings import *
from utils import fib
import os
import traceback
from functools import reduce


class Segment(pg.sprite.Sprite):

    def __init__(self, game, gx, gy):
        self.groups = game.all_sprites
        # self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.game = game

        self.gx = gx
        self.gy = gy

        # screen position
        x, y = self.game.current_floor.get_local_pos(gx, gy)
        self.rect.x, self.rect.y = x * TILESIZE, y * TILESIZE

    def update(self):
        x, y = self.game.current_floor.get_local_pos(self.gx, self.gy)
        self.rect.x, self.rect.y = x * TILESIZE, y * TILESIZE

    def drawt(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.playerg
        # self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()

        self.name = "Player"
        self.is_alive = True

        # position on the screen with current change
        self.dx = 0
        self.dy = 0

        # position of our head (offset by one to fit global position)
        self.rect.x = (x + 1) * TILESIZE
        self.rect.y = (y + 1) * TILESIZE

        # segments
        self.segments = []

        # position in the level
        self.gx = 0
        self.gy = 0
        self.still = True

        self.collisions = True

        # game status
        self.spells = []
        self.active_spells = []
        self.equipped_spell = None
        self.is_firing = False
        self.equipped_item = None

    def drawt(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        for seg in self.segments:
            seg.drawt(screen)

    def move(self, dx=0, dy=0):
        self.dx = dx
        self.dy = dy

    def update(self):
        self.update_segments()
        newx = self.gx + self.dx
        newy = self.gy + self.dy
        if not self.position_is_blocked(self.dx, self.dy):
            self.gx = newx
            self.gy = newy
        else:
            self.dx = 0
            self.dy = 0

    def update_segments(self):
        if self.segments:
            lastx = self.gx
            lasty = self.gy
            for seg in self.segments:
                sx, sy = seg.gx, seg.gy
                seg.gx, seg.gy = lastx, lasty
                seg.update()
                lastx, lasty = sx, sy

    def check_eat(self):
        # now check if we ate an apple
        for apple in ONSCREEN.enemies:
            if apple.gx == self.gx and apple.gy == self.gy and apple.alive:
                # eat the apple
                apple.die()
                self.add_segment()
                break

    def add_segment(self):
        # add the first segment
        # first determine where we last were
        # lastx, lasty = self.gx - self.dx, self.gy - self.dy
        # self.segments.insert(0, Segment(self.game, self.gx, self.gy))
        if self.segments:
            last = self.segments[-1]
        else:
            last = self
        self.segments.append(Segment(self.game, last.gx, last.gy))

    def is_moving(self):
        return self.dx != 0 or self.dy != 0
    
    def position_is_blocked(self, dx, dy):
        new_x = self.gx + dx
        new_y = self.gy + dy
        blocked = False
        if self.game.current_floor.layout[new_x][new_y] == 1:
            blocked = True
        # blocked if we hit something and collisions are on
        is_blocked = blocked and not self.game.godmode
        return is_blocked
