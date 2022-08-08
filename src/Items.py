"""
Items
"""
from settings import *

class WITEM:
    def __init__(self, game):
        self.game = game
        self.name = "Uknown Item"
        self.consumable = True
    
    def use(self):
        pass

class HealingPotion(WITEM):
    inspect = lambda _: "A swirling red healing potion, I should use this if I'm hurt."
    def __init__(self, game):
        super().__init__(game)
        self.name = "Healing Potion"
    
    def use(self):
        """
        Heal the player HP_POT % of their health 
        rounded to the nearest integer
        """
        self.game.player.heal_hp(HP_POT)
        self.game.log.info(f"I drank a healing potion healing {int(HP_POT*100)}% of my health")
    
