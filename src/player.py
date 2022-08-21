import pygame as pg
from settings import *
from utils import fib
import os
import traceback
from functools import reduce


class Segment(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        # self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()

        self.dx = 0
        self.dy = 0

        # screen position
        self.rect.x, self.rect.y = x, y

    def drawt(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.playerg
        # self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
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
            last = self
            for seg in self.segments:
                snx = last.rect.x - last.dx * TILESIZE
                sny = last.rect.y - last.dy * TILESIZE
                if last.dx != 0 or last.dy != 0:  # prevents segments moving without the head? idk if i want that
                    seg.rect.x = snx
                    seg.rect.y = sny
                    seg.dx = last.dx
                    seg.dy = last.dy
                last = seg

    def check_eat(self):
        # now check if we ate an apple
        for apple in ONSCREEN.enemies:
            if apple.gx == self.gx and apple.gy == self.gy and apple.alive:
                # eat the apple
                apple.die()
                self.add_segment()
                break

    def add_segment(self):
        if not self.segments:
            # add the first segment
            # first determine where we last were
            lastx, lasty = self.rect.x - self.dx * TILESIZE, self.rect.y - self.dy * TILESIZE
            self.segments.append(Segment(self.game, lastx, lasty))
        else:
            last_seg = self.segments[-1]
            lastx, lasty = last_seg.rect.x - last_seg.dx * TILESIZE, last_seg.rect.y - last_seg.dy * TILESIZE
            self.segments.append(Segment(self.game, lastx, lasty))

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

    def get_item(self, item):
        if len(self.state.inventory) + 1 <= self.state.Strength.value:
            self.state.inventory.append(item)
            if not self.equipped_item:
                self.equipped_item = item
            return True
        else:
            return False
    
    def use_item(self):
        if self.equipped_item:
            self.equipped_item.use()
            # if its consumable, remove it after use
            if self.equipped_item.consumable:
                self.state.inventory.remove(self.equipped_item)
                # equip the next item if there is one, or empty hands
                if len(self.state.inventory) > 0:
                    self.equipped_item = self.state.inventory[0]
                else:
                    self.equipped_item = None

    def heal_hp(self, amount_pcnt):
        max_health = self.state.Constitution.value
        cur_health = self.state.Health.value
        gained = int(max_health * amount_pcnt)
        if cur_health + gained <= max_health:
            new_health = cur_health + gained
        else:
            new_health = max_health
        new_health = int(new_health)
        self.state.Health.value = new_health
    
    def get_stats(self):
        return self.state.get_stats()
    
    def gain_xp(self, amount):
        self.state.Experience.value += amount
        if self.state.Experience.value >= self.state.next_level_xp():
            self.state.level_up()
            self.game.log.info("I leveled up!")
