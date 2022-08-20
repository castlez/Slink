# strings
from dataclasses import dataclass

INTRO = ["i:Welcome to Wizrad! Find all the elements and break " \
         "the Omni Gem for ultimate POWER",
         "i:(wasd to move, left click to inspect)"]

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (168, 104, 50)

# Sizes
TILESIZE = 8
WIDTH = TILESIZE * 64
HEIGHT = TILESIZE * 64
TEXTBOX_HEIGHT = 10
GRIDWIDTH = int(WIDTH / TILESIZE)
GRIDHEIGHT = int(HEIGHT / TILESIZE)

# where the player is drawn on the screen
PLAYER_X = WIDTH / 2
PLAYER_Y = HEIGHT / 2

# full map size (for generation)
MAP_WIDTH = 100
MAP_HEIGHT = 100

# size of the tunnels
TUNNEL_WIDTH = 3

# Meta Data
FPS = 30
TITLE = "SLNK"
BGCOLOR = BLACK

# Log
VIS_LOG_LINES = 3
TEXT_SIZE = 12
LOG_LINE_DIST = TEXT_SIZE + 5
LOG_X = 0
LOG_Y = int(float(HEIGHT) * 0.90)

# Screens (inven, spellmaking, etc)
S_TEXT_SIZE = 15
S_LINE_DIST = S_TEXT_SIZE + 5
S_X = 0
S_Y = 0

###### Player ######

# META
GODMODE = False
TICK = 0.05  # time in between game ticks

@dataclass
class SPRITEPOOL:
    walls: list
    enemies: list


OFFSCREEN = SPRITEPOOL(walls=[], enemies=[])
ONSCREEN = SPRITEPOOL(walls=[], enemies=[])
OFFSCREEN_DIST = WIDTH + 10 * TILESIZE

# Movement
SPRINT_DELAY = 1
SPRINT_SPEED = 100

###### Interactables ######

CHEST = "ch"
CHMIN = 20
CHMAX = 30

###### Items ######

HP_POT = 0.4  # heal the player 40%

###### Elements/Spells ######

FIRING_SPEED = 15

# how far a spell must travel (in tiles) before
# it tries to hit things
SPELL_BUFFER = 0

SPELL_SIZE = int(TILESIZE / 2)

# Fire
FIRE = "f"
FMIN = 20
FMAX = 30
FDAMAGE_RANGE = [0, 5]

###### Enemies ######

# modifiers for map tracking
# no mods means the enemy is unspawned
SPAWNED = "sp"
DEAD = "x"

# Apples
APPLE = "a"
AMIN = 5
AMAX = 10

# Wall
WALL = 1