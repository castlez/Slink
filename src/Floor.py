"""
Floor stuff
"""
from settings import *
from sprites import *
from Items import *
import os
import json
import random
import traceback

from dg.dungeonGenerationAlgorithms import RoomAddition

class Floor:
    """
    Handles the floor and all its rooms
    for self.layout:
        0 is empty floor
        1 is wall
        2 is enemy
        ...
    """

    def __init__(self, game, floor_number):
        self.fire = []
        self.ice = []
        self.secret = []
        self.enemies = []
        self.eaten_enemies = []
        self.inters = []
        self.floor_number = floor_number
        self.walls = []
        self.all = []
        # current view port, [[xmin, xmax], [ymin, ymax]]
        self.current_global_view = [[0, 0], [0, 0]]
        self.game = game

        # layout
        generator = RoomAddition()
        self.layout = generator.generateLevel(MAP_WIDTH, MAP_HEIGHT)
        # self.update_viewport(self.game.player.gx, self.game.player.gy)
        print("Level Loaded!")
    
    def set_loot_table(self):
        """
        Sets the loot table based on floor
        """
        if self.floor_number == 1:
            self.loot_table = [HealingPotion]

    def get_loot(self):
        """
        Gets a random item from the loot table
        """
        item_index = random.randint(0, len(self.loot_table)-1)
        item = self.loot_table[item_index](self.game)
        return item
    
    def get_valid_pos(self):
        while True:
            gx = random.randint(2, MAP_WIDTH-1)
            gy = random.randint(2, MAP_HEIGHT-1)
            if self.layout[gx][gy] == 0:
                return gx, gy

    def get_local_pos(self, gx, gy):
        xmin = self.current_global_view[0][0]
        xmax = self.current_global_view[0][1]
        ymin = self.current_global_view[1][0]
        ymax = self.current_global_view[1][1]

        if gx < xmin or gx > xmax or gy < ymin or gy > ymax:
            return -1, -1
        
        lx = gx - xmin
        ly = gy - ymin
        return lx, ly
    
    def purge_unseen(self):
        gxmin = self.current_global_view[0][0]
        gxmax = self.current_global_view[0][1]
        gymin = self.current_global_view[1][0]
        gymax = self.current_global_view[1][1]

        removed_walls = []
        for wall in ONSCREEN.walls:
            if gxmin > wall.gx > gxmax or gymin > wall.gy > gymax:
                removed_walls.append(wall)
        for wall in removed_walls:
                wall.x = OFFSCREEN_DIST
                wall.visible = False
                ONSCREEN.walls.remove(wall)
                OFFSCREEN.walls.append(wall)

        removed_enemies = []
        for enemy in ONSCREEN.enemies:
            if gxmin > enemy.gx > gxmax or gymin > enemy.gy > gymax:
                removed_enemies.append(enemy)
        for enemy in removed_enemies + self.eaten_enemies:
            # move the enemy from onscreen to offscreen
            enemy.x = OFFSCREEN_DIST
            enemy.visible = False
            ONSCREEN.enemies.remove(enemy)
            OFFSCREEN.enemies.append(enemy)
        self.eaten_enemies = []
    
    def update_seen(self):
        """
        if something is still in the lists
        set its visible to true
        """
        gxmin = self.current_global_view[0][0]
        gxmax = self.current_global_view[0][1]
        gymin = self.current_global_view[1][0]
        gymax = self.current_global_view[1][1]

        walls_to_view = []
        for wall in OFFSCREEN.walls:
            if gxmin <= wall.gx <= gxmax and gymin <= wall.gy <= gymax:
                walls_to_view.append(wall)
        for wall in walls_to_view:
            # wall is now visible, move it into view
            wall.x, wall.y = self.get_local_pos(wall.gx, wall.gy)
            wall.visible = True
            OFFSCREEN.walls.remove(wall)
            ONSCREEN.walls.append(wall)

        enemies_to_view = []
        for enemy in OFFSCREEN.enemies:
            if gxmin < enemy.gx < gxmax and gymin < enemy.gy < gymax:
                enemies_to_view.append(enemy)
        for enemy in enemies_to_view:
            # enemy is now visible, move it into view
            enemy.x, enemy.y = self.get_local_pos(enemy.gx, enemy.gy)
            enemy.visible = True
            OFFSCREEN.enemies.remove(enemy)
            ONSCREEN.enemies.append(enemy)

    def update_viewport(self, gx, gy):
        """
        Runs the update functions needed to update the viewport
        based on the players global position

        gx is global x position in the layout grid
        gy is global y position in the layout grid
        """
        offset = int(GRIDHEIGHT/2) + 1     # this is dumb and only works cuz the game is a square
        # need to massage the indexes so that (xmin, ymin) is (0, 0) on the view
        xmin = gx - offset
        xmax = gx + offset
        ymin = gy - offset
        ymax = gy + offset

        # update the current view and purge anything
        # no longer visible
        self.current_global_view = [[xmin, xmax], [ymin, ymax]]
        self.purge_unseen()
        self.update_seen()

    def populate_floor(self):
        """
        Populates the map with stuff
        start by creating everything offscreen, then in the update
        things will get pulled in. This prevents ram offerflows from creating
        and destroying objects.
        """

        # walls
        for gx in range(len(self.layout)):
            for gy in range(len(self.layout[gx])):
                if self.layout[gx][gy] == 1:
                    OFFSCREEN.walls.append(Wall(self.game, OFFSCREEN_DIST, 0, gx, gy))

        # skeletons
        num_skele = random.randint(AMIN, AMAX)
        for _ in range(num_skele):
            gx, gy = self.get_valid_pos()
            self.layout[gx][gy] = APPLE
            OFFSCREEN.enemies.append(Apple(self.game, OFFSCREEN_DIST, 0, gx, gy))

