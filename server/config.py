import itertools as it

from ship import *

def build_ship(has_fmc):
  ship = Ship()

  nodes = list(it.starmap(ShipNode, [(-20.0, 0.0), (0.0, 0.0), (20.0, 0.0)]))
  for node in nodes:
    ship.addNode(node)

  bridge = ShipBridge()
  bridge.addNode(nodes[1])

  engine = ShipEngine()
  engine.addNode(nodes[0])

  ship.addModule(bridge)
  ship.addModule(engine)

  if has_fmc:
    fmc = ShipFMC()
    fmc.addNode(nodes[2])
    ship.addModule(fmc)

  return ship

def init_game(game):
  game.world.ships.append(build_ship(True))
  game.world.ships.append(build_ship(False))
