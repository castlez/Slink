import pygame as pg
from settings import *
import os

class WSCREEN(pg.sprite.Sprite):
    """
    Parent class for non viewport screens
    inventory
    more?
    """
    def __init__(self, game, x, y):
        self.groups = game.screens
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.inspect_message = "A Screen for lookin..."
        self.name = "AScreen"

        # position should be fixed at the bottom
        self.image = pg.Surface((WIDTH, LOG_Y))
        self.image.fill(BLACK)
        self.x = S_X
        self.y = S_Y
        self.cur_x = self.x
        self.cur_y = self.y
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

        # keep track of the visible lines (these will get overridden by children)
        self.current_place = 0
        self.current_display = []

        # text stuff
        fonts = pg.font.get_fonts()
        self.font = pg.font.SysFont(fonts[0], S_TEXT_SIZE)
        self.header_buff = S_TEXT_SIZE * 2  # headers are two lines long
    
    def update(self):
        pass

    def drawt(self, screen):
        pass

class Inventory(WSCREEN):
    """
    Class handling the inventory screen
    """

    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        # keep track of the visible lines
        self.current_place = 0
        # [[inventory], [spells], [states]]
        self.current_display = [[],[],[]]
        self.cur_x = x
        self.cur_y = y + self.header_buff
        self.starting = True

    class Entry(pg.sprite.Sprite):
        def __init__(self, game, obj, font, x, y):
            self.groups = game.screens
            pg.sprite.Sprite.__init__(self, self.groups)
            if type(obj) != str:
                self.obj = obj
                # if its a stat, display its value
                if obj in PlayerState.get_stats():
                    self.text = obj.get_display()
                else:
                    self.text = obj.name
            else:
                self.obj = None
                self.text = obj  # which its text in this case
            self.font = font
            self.image = pg.Surface(self.font.size(self.text))
            self.image.fill(BROWN)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y   
        
        def check(self, mouse_pos):
            if self.rect.collidepoint(mouse_pos):
                return True
            return False
        
        def inspect(self):
            if self.obj:
                return self.obj.inspect()
            else:
                return "A shiny UI element!"
        
        def drawt(self, screen, color):
            text = self.font.render(self.text, True, color, (0, 0, 0))
            screen.blit(text, (self.rect.x, self.rect.y))
            
    
    def check(self, mouse_pos):
        msg = "Its either invisible or that is just the background of my inventory..."
        for category in self.current_display:
            for entry in category:
                if entry.check(mouse_pos):
                    msg = entry.inspect()
        self.game.log.info(msg)
    
    def add_header(self, col, header):
            h1 = Inventory.Entry(self.game, header, self.font, self.cur_x, self.cur_y)
            self.cur_y += S_LINE_DIST
            h2 = Inventory.Entry(self.game, "---------", self.font, self.cur_x, self.cur_y)
            self.cur_y += S_LINE_DIST
            self.current_display[col].append(h1)
            self.current_display[col].append(h2)

    def update(self):
        """
        check the players inventory and update
        current display
        """
        # player inventory
        cur_inven = self.game.player.state.inventory
        # reset with header
        self.current_display[0] = []
        self.add_header(0, "Inventory")
        for item in cur_inven:
            e = Inventory.Entry(self.game, item, self.font, self.cur_x, self.cur_y)
            self.cur_y += S_LINE_DIST
            self.current_display[0].append(e)
        
        # reset
        self.cur_x += WIDTH/3
        self.cur_y = self.y  

        # spells
        cur_spells = self.game.player.spells
        self.current_display[1] = []
        self.add_header(1, "Spells")
        for spell in cur_spells:
            e = Inventory.Entry(self.game, spell, self.font, self.cur_x, self.cur_y)
            self.cur_y += S_LINE_DIST
            self.current_display[1].append(e)
        
        # reset
        self.cur_x += (WIDTH/3)
        self.cur_y = self.y
        
        # stats
        stats = self.game.player.get_stats()
        self.current_display[2] = []
        self.add_header(2, "Stats")
        for stat in stats:
            e = Inventory.Entry(self.game, stat, self.font, self.cur_x, self.cur_y)
            self.cur_y += S_LINE_DIST
            self.current_display[2].append(e)

        # reset cur_x and cur_y
        self.cur_x = self.x
        self.cur_y = self.y
        self.starting = False

    def drawt(self, screen):
        # draw the black backdrop
        screen.blit(self.image, (self.x, self.y))

        # line for each item
        for item in self.current_display[0]:
            if item.obj and item.obj == self.game.player.equipped_item:
                item.drawt(screen, RED)
            else:
                item.drawt(screen, WHITE)

        # line for each spell
        for spell in self.current_display[1]:
            if spell.obj and spell.obj == self.game.player.equipped_spell:
                spell.drawt(screen, RED)
            else:
                spell.drawt(screen, WHITE)

        for stat in self.current_display[2]:
            stat.drawt(screen, WHITE)

        




        

