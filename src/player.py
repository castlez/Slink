import pygame as pg
from settings import *
from utils import fib
import os
import traceback
from functools import reduce

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.playerg
        # self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        # self.image = pg.image.load(os.path.join("assets", "wiz_up.png"))
        # self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        # TODO: use rotozoom to rotate 
        # self.image = pg.Surface(self.image.get_size()).convert_alpha()
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()

        self.state = PlayerState()
        self.name = "Player"

        # position on the screen with current change
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0

        # position of our head
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE
        
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
    
    def take_damage(self, source, amount):
        if self.game.godmode:
            self.game.log.info(f"Woulda taken {amount} dmg if not for godmode")
            return
        self.state.Health.value -= amount
        self.game.log.info(f"Hit by {source.name} for {amount} damage")
        self.game.log.info(f"Remaining health: {self.state.Health.value}")
        if self.state.Health.value <= 0:
            self.state.alive = False
    
    def inspect(self):
        return "I am badass, swagass, Wizrad"

    def update_global_position(self, x, y):
        self.gx = x
        self.gy = y

    def move(self, dx=0, dy=0):
        blocked = self.check_collision(dx, dy)
        if not blocked:
            self.dx = dx
            self.dy = dy
            self.gx += dx
            self.gy += dy
            self.still = False

    def update(self):
        self.check_spells()

    def check_spells(self):
        for i, spell in enumerate(self.active_spells):
            if not spell.active:
                spell.kill()
                del self.active_spells[i]
    
    def is_moving(self):
        return self.dx != 0 and self.dy != 0
    
    def check_collision(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        blocked = False
        for sprite in self.game.all_sprites:
            if new_x == sprite.x and new_y == sprite.y and sprite.blocking:
                blocked = True
        # blocked if we hit something and collisions are on
        is_blocked = blocked and not self.game.godmode
        return is_blocked
    
    def inspect_space(self, mouse_pos):
        message = ""
        for sprite in self.game.all_sprites:
            try:
                if sprite.rect.collidepoint(mouse_pos):
                    message = sprite.inspect()
                    break
            except Exception as e:
                # self.game.log.info(e)
                continue
        # if message == "" or message == None:
        #     message = "Its the floor. Im looking at the floor... "\
        #               "Maybe i should look at other things"

    def interact_space(self, mouse_pos):        
        message = ""
        for sprite in self.game.all_sprites:
            try:
                if sprite.rect.collidepoint(mouse_pos):
                    message = sprite.interact(self)
                    break
            except Exception as e:
                self.game.log.info(e)
                continue
        if message == "" or message == None:
            message = "Not much to do with the floor really.."
        self.game.log.info(message)
    
    def has_element(self, element):
        has_ele = False
        for spell in self.spells:
            if element in spell.elements:
                has_ele = True
        return has_ele
    
    def get_spells(self):
        return [s.name for s in self.spells]
    
    def add_spell(self, spell):
        if len(self.spells) + 1 <= self.state.Intelligence.value:
            self.spells.append(spell)
            if not self.equipped_spell:
                self.equipped_spell = spell
            return True
        else:
            self.game.log.info("My mind is full, I cannot learn more spells till I level up :(")
            return False
    
    def fire_spell(self, mouse_pos):
        if self.equipped_spell:
            self.is_firing = True
            spell = self.equipped_spell(self.game, mouse_pos)
            self.active_spells.append(spell)
    
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

class PlayerState:
    known_spells = None
    alive = True
    inventory = []
    
    @classmethod
    def next_level_xp(cls):
        """
        xp needed == sum(fib(next_level))*10
        """
        next_level = cls.Level.value + 1
        if next_level == 1:
            return 10
        else:
            needed = 0
            for f in fib(next_level):
                needed += f * 10
            print(f"xp needed for lvl {next_level}: {needed}")
            return needed

    # these absurd classes are because i need
    # to be able to display contextual information
    # in menues about these stats (what they do)
    class STAT:
        name = ""
        exact = 0.0
        value = 0
        max_value = 0
        description = "a state"
        changed = False
        @classmethod
        def inspect(cls):
            return cls.description
        @classmethod
        def increase(cls, value):
            cls.exact += value
            cls.value += int(cls.exact)
            cls.max_value += int(cls.exact)
        @classmethod
        def is_changed(cls):
            changed = cls.changed
            cls.changed = False
            return changed
        @classmethod
        def get_display(cls):
            return f"{cls.name}: {cls.value}/{cls.max_value}"
    class Level(STAT):
        name = "Level"
        value = 0
        max_value = 0
        description = "My current level"
        changed = False
        @classmethod
        def get_display(cls):
            return f"{cls.name}: {cls.value}"
    class Experience(STAT):
        name = "Experience"
        value = 0
        max_value = 10
        description = "My experience"
        changed = False
    class Health(STAT):
        name = "Health"
        value = PLAYER_START_CON
        max_value = PLAYER_START_CON
        description = "My current health"
        changed = False
    class Strength(STAT):
        name = "Strength"
        value = PLAYER_START_STR
        max_value = PLAYER_START_STR
        description = "How many items I can carry"
        changed = False
    class Constitution(STAT):
        name = "Constitution"
        value = PLAYER_START_CON
        max_value = PLAYER_START_CON
        description = "My max hitpoints (at full health)"
        changed = False
    class Intelligence(STAT):
        name = "Intelligence"
        value = PLAYER_START_INT
        max_value = PLAYER_START_INT
        description = "How many spells I can know"
        changed = False
    
    @classmethod
    def level_up(cls):
        # increase the stats current AND max values
        # (in case there are negative/positive effects)
        cls.Strength.increase(PLAYER_STR_RATE)
        cls.Constitution.increase(PLAYER_CON_RATE)
        cls.Health.increase(PLAYER_CON_RATE)
        cls.Intelligence.increase(PLAYER_INT_RATE)
        cls.Level.value += 1
        cls.Experience.max_value = PlayerState.next_level_xp()

    @classmethod
    def get_stats(cls):
        return [cls.Health, cls.Level, cls.Experience, cls.Strength, cls.Constitution, cls.Intelligence]
    
    @classmethod
    def stats_changed(cls):
        return cls.Strength.is_changed() or cls.Constitution.is_changed() or cls.Intelligence.is_changed()


    
