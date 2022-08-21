import pygame as pg
from spells import *
from settings import *
import traceback
import math

# Super class
class WSPRITE(pg.sprite.Sprite):
    """
    Parent class for all sprites but the player
    (you are special ;) )

    oh and the log window (because it doesnt move)

    also spells have their own parent
    """
    def __init__(self, game, x, y, gx, gy, group, color=GREEN):
        self.groups = game.all_sprites, group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.gx = gx
        self.gy = gy
        self.start_pos = (gx, gy)
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

        # for other sprites to check
        self.visible = True
        self.blocking = False
        self.is_enemy = False
    
    def inspect(self):
        return self.inspect_message
    
    def interact(self, player):
        return self.interact_message
    
    def kill(self):
        super().kill()
    
    def drawt(self, screen):
        if self.visible:
            screen.blit(self.image, (self.rect.x, self.rect.y))
    
    def update(self):
        if self.visible:
            try:
                x, y = self.get_local_pos() 
                if x == -1 and y == -1:
                    return
                self.x = x - self.game.player.dx
                self.y = y - self.game.player.dy
            except Exception as e:
                print(e)
                traceback.print_exc(e)
            self.rect.x = self.x * TILESIZE
            self.rect.y = self.y * TILESIZE

    def get_local_pos(self):
        return self.game.current_floor.get_local_pos(self.gx, self.gy)
    
    def set_sign(self, sign):
        self.game.current_floor.layout[self.start_pos[0]][self.start_pos[1]] = sign
    
    def get_next_space(self):
        """
        returns the next global space the apple should go to
        """
        # Find direction vector (dx, dy) between enemy and player.
        dx, dy = self.game.player.x - self.x, self.game.player.y - self.y

        # flip it to make the apples run away
        dx *= -1
        dy *= -1

        # math shit
        dist = math.hypot(dx, dy)
        if dist == 0:
            # dont need to move if already munching on player
            return 0, 0
        dx, dy = dx / dist, dy / dist  # Normalize.
        # Move along this normalized vector towards the player at current speed.

        # normalize and adjust for player movement
        cx = round(dx)
        cy = round(dy)

        # # check if already diagonal to player and just
        # # need to move to hit range (adjacent NON diagonal)
        # if self.adjacent_to_player(self.x, self.y):
        #     if abs(cx) == 1 and abs(cy) == 1:
        #         # we are diagonal
        #         t = cx + cy
        #         if t == 0:
        #             cx = 0
        #         else:
        #             cy = 0
        gx = self.gx + cx
        gy = self.gy + cy
        return gx, gy
    
    def check_player_los(self):
        x = self.gx
        y = self.gy

        if self.visible and ONSCREEN.enemies:
            while x in range(0, GRIDWIDTH) and y in range(0, GRIDHEIGHT):
                if self.adjacent_to_player(x, y):
                    return True
                cur = self.game.current_floor.layout[x][y]
                if cur == WALL:  # wall
                    break
                x, y = self.get_next_space()
            return False
    
    def adjacent_to_player(self, newx, newy):
        px = self.game.player.x
        py = self.game.player.y
        dx = abs(px - newx)
        dy = abs(py - newy)
        adjacent = dx <= 1 and dy <= 1
        return adjacent

# Walls
class Wall(WSPRITE):
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.walls, color=LIGHTGREY)
        self.inspect_message = "I think its.. well, it might be.. yeah that is! Its a wall!"
        self.blocking = True
        self.name = "Wall"
    
    def inspect(self):
        return "I think its.. well, it might be.. yeah that is! Its a wall!"
    
    def take_damage(self, amount):
        self.game.log.info(f"You would have done {amount} damage to the wall, if that was possible.")

# Interactables
class BurningPile(WSPRITE):
    """
    These give you fire
    """
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=RED)
        self.inspect_message = "A magic fire, i better watch out. Hmm.. "\
                               "its interesting (right click to study)"
        self.name = "BurningPile"
        self.set_sign(FIRE + SPAWNED)
    
    def interact(self, player):
        if player.has_element("fire"):
            return "I already know how to wield fire magic"
        else:
            player.add_spell(Fire)
            return "I studied the pile and learned the secrets of fire magic!"

class Chest(WSPRITE):
    """
    These have items in them!
    """
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=BROWN)
        self.inspect_message = "Its a chest. Might have some loot in it..."
        self.name = "Chest"
        self.set_sign(CHEST + SPAWNED)
        self.contents = self.game.current_floor.get_loot()
    
    def interact(self, player):
        if self.adjacent_to_player(self.x, self.y):
            # if the players inven is not full, grab the item
            # and remove the chest
            got = self.game.player.get_item(self.contents)
            if got:
                self.game.current_floor.remove_inter(self)
                return f"Got a {self.contents.name}!"
            else:
                return "I can't carry any more :("

        else:
            return "The chest is to far away for me to open..."


# Enemies
class Apple(WSPRITE):
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.enemies, color=RED)
        self.start_pos = (gx, gy)
        self.name = "Apple"
        self.sign = APPLE + SPAWNED
        self.unspawned_sign = APPLE
        self.set_sign(self.sign)
        self.health = 6
        self.inspect_message = f"An animated skeleton. A good fireball should do the trick."
        self.blocking = True
        self.is_enemy = True
        self.alive = True

        # movement
        self.skip = False  # skip a tick after hitting the player

    def die(self):
        self.game.current_floor.eaten_enemies.append(self)
        self.alive = False

    def update(self):
        """
        If you see the snake... RUN
        """
        if self.visible:
            try:
                x, y = self.get_local_pos()
                if x == -1 and y == -1:
                    return
                self.x = x - self.game.player.dx
                self.y = y - self.game.player.dy
            except Exception as e:
                print(e)
                traceback.print_exc(e)
            self.rect.x = self.x * TILESIZE
            self.rect.y = self.y * TILESIZE

    def drawt(self, screen):
        if self.visible and self.alive:
            screen.blit(self.image, (self.rect.x, self.rect.y))
