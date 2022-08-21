"""
SLNK Main Code
template from KidsCanCode
https://www.youtube.com/watch?v=3UxnelT9aCo
massively changed for my nefarious purposes

SLNK is a snake-like dungeon roguelike
"""
import pygame as pg
from pygame.locals import *
import sys
import math
from settings import *
from sprites import *
from Floor import *
from LogWindow import *
from player import *
from Screens import *
from dg.dungeonGenerationAlgorithms import RoomAddition


class Game:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT), flags=DOUBLEBUF)
        self.screen.set_alpha(None)
        pg.event.set_allowed([QUIT, KEYDOWN, KEYUP])

        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(SPRINT_DELAY, SPRINT_SPEED)
        self.current_floor = None
        self.view = None
        self.load_data()
        self.show_grid = True
        self.log = None
        self.tick = False
        self.show_inventory = False
        self.godmode = GODMODE
        self.playing = False

        self.cur_time = time.time()
        self.last_time = self.cur_time

        pg.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    def load_data(self):
        pass

    def new(self):
        """
        This is wack dude
        fuck you

        at the beginning of the game load everything
        """
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.playerg = pg.sprite.Group()
        self.screens = pg.sprite.Group()
        self.player = Player(self, int(GRIDWIDTH/2), int(GRIDHEIGHT/2))
        self.inventory = Inventory(self, 0, 0)

        # first floor (TODO start screen)
        self.current_floor = Floor(self, 1)
        self.current_floor.populate_floor()

        # put the player in a random place
        gx, gy = self.current_floor.get_valid_pos()
        self.player.gx = gx
        self.player.gy = gy

        # start the engines
        self.tick = True
        self.playing = True

        # TODO remove
        self.save_map()

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
        return self.playing
    
    def save_map(self):
        map_string = ""
        fl = self.current_floor.layout
        px = self.player.gx
        py = self.player.gy
        for y in range(0, MAP_HEIGHT):
            for x in range(0, MAP_WIDTH):
                if x == px and y == py:
                    map_string += "@"
                elif fl[x][y] == 9:
                    map_string += "^"
                elif fl[x][y] == 0:
                    map_string += "."
                else:
                    map_string += str(fl[x][y])
            map_string += '\n'
        if not os.path.exists("../scraps"):
            os.makedirs("../scraps")
        with open("../scraps/last_map.txt", 'w') as f:
            f.write(map_string)
        print("level map saved in scraps/last_map.txt!")

    def quit(self, save_map=False):
        if save_map:
            self.save_map()
        pg.quit()
        sys.exit()

    def update(self):
        # only update on tick
        # (currently just player movement)
        self.cur_time = time.time()
        if self.cur_time - self.last_time > TICK:
            self.last_time = self.cur_time
            self.tick = True

        if self.tick:  # NOTE: might be able to toggle turn based here...
            # use the global position of the player to decide what to draw
            cur_g_x = self.player.gx
            cur_g_y = self.player.gy

            self.playerg.update()
            for w in ONSCREEN.walls:
                w.update()
            for e in ONSCREEN.enemies:
                e.update()
            self.current_floor.update_viewport(self.player.gx, self.player.gy)
            self.player.check_eat()
            self.tick = False

        if not self.player.alive:
            self.playing = False

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, DARKGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, DARKGREY, (0, y), (WIDTH, y))

    def draw(self):
        if self.show_inventory:
            self.inventory.drawt(self.screen)
        else:
            self.screen.fill(BGCOLOR)
            for wall in self.walls:
                wall.drawt(self.screen)
            for enemy in self.enemies:
                enemy.drawt(self.screen)
            if self.show_grid:
                self.draw_grid()
            self.player.drawt(self.screen)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if self.show_inventory:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_i:
                        self.show_inventory = False
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    mouse_pos = pg.mouse.get_pos()
                    self.inventory.check(mouse_pos)
            else:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.quit()
                    if event.key == pg.K_a:
                        self.player.move(dx=-1, dy=0)
                    if event.key == pg.K_d:
                        self.player.move(dx=1, dy=0)
                    if event.key == pg.K_w:
                        self.player.move(dx=0, dy=-1)
                    if event.key == pg.K_s:
                        self.player.move(dx=0, dy=1)
                    if event.key == pg.K_RETURN:
                        self.tick = True

    def get_sprite_at(self, x, y):
        for sprite in self.all_sprites:
            try:
                if sprite.x == x and sprite.y == y:
                    return sprite
            except:
                pass
        return None
    
    def object_in_view(self, gx, gy):
        """
        gx and gy are global quards
        """
        # use the global position of the player to decide what to draw
        cur_g_x = self.player.gx
        cur_g_y = self.player.gy

        # need to massage the indexes so that (xmin, ymin) is (0, 0) on the view
        xmin = cur_g_x - 6
        xmax = cur_g_x + 10
        ymin = cur_g_y - 6 
        ymax = cur_g_y + 10 

        # if we are out of sight, despawn
        if gx < xmin or gx > xmax or gy < ymin or gy > ymax:
            return False
        return True

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

# create the game object
while True:
    print(" ________  new game ________")
    g = Game()
    g.show_start_screen()
    alive = True
    while alive:
        g.new()
        alive = g.run()
