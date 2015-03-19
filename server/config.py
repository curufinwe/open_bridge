import itertools as it

from ship import Ship, ShipNode, ShipModule

def build_ship():
  ship = Ship()

  nodes = list(it.starmap(ShipNode, [(-20.0, 0.0), (0.0, 0.0), (20.0, 0.0)]))
  for node in nodes:
    ship.addNode(node)

  bridge = ShipModule('bridge')
  bridge.addNode(nodes[1])

  engine = ShipModule('engine')
  engine.addNode(nodes[0])

  ship.addModule(bridge)
  ship.addModule(engine)

  return ship

def init_game(game):
  game.world.ships.append(build_ship())
  game.world.ships.append(build_ship())
