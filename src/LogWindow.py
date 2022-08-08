import pygame as pg
from settings import *
import os

class LogWindow(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.inspect_message = "Thats my recent thoughts (scroll with arrow keys)"
        self.name = "LogWindow"

        # position should be fixed at the bottom
        self.image = pg.Surface((WIDTH, HEIGHT))
        self.image.fill(BLACK)
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE * 8
        self.rect.y = y * TILESIZE * 2

        # keep track of the log lines
        self.current_place = 0
        self.current_display = []
        self.log = []

        # text stuff
        fonts = pg.font.get_fonts()
        self.font = pg.font.SysFont(fonts[0], TEXT_SIZE)
    
    def init(self):
        for l in INTRO:
            self.log.append(l)
    
    def inspect(self):
        return self.inspect_message
        
    def update_place(self, change):
        # TODO on update if possible... if len(change) > 3 and len()
        self.current_place += change
    
    def info(self, message):
        print(message)
        self.log.append(f"i:{message}")
    
    def update(self):
        # get the last VIS_LOG_LINES lines into draw_lines
        # TODO do something with the current_place to scroll 
        draw_lines = []
        if len(self.log) < 3:
            draw_lines = self.log
        else:
            draw_lines = self.log[-3::]

        # update the current display contents, if necessary        
        if draw_lines != self.current_display:
            self.current_display = draw_lines
    
    def draw(self, screen):
        x = LOG_X
        y = LOG_Y
        screen.blit(self.image, (x, y))
        for line in self.current_display:
            tag = line[:1]
            message = line[2:]
            if tag == "i":
                to_print = f"INFO: {message}"
            elif tag == "e":
                to_print = f"EROR: {message}"
            else:
                to_print = line
            text = self.font.render(to_print, True, (255, 255, 255), (0, 0, 0))
            screen.blit(text, (x, y))
            y += LOG_LINE_DIST 
    

            
        

