import itertools as it

from ship import *
import templates as t

def init_game(game):
  game.debug = True
  ship_id = game.world.addShip(t.ship_templates['debug_ship_1']())
  ship_id = game.world.addShip(t.ship_templates['debug_ship_2']())
  game.world.ships[ship_id].x += 60
  ship_id = game.world.addShip(t.ship_templates['debug_ship_3']())
  game.world.ships[ship_id].x -= 60
  #for i in range(50):
  #  ship_id = game.world.addShip(t.ship_templates['debug_ship_1']())
  #  game.world.ships[ship_id].x += 120
