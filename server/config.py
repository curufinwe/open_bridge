import itertools as it

from ship import *

def build_ship(smc, rmc):
  ship = Ship()

  nodes = list(it.starmap(ShipNode, [(-20.0, 0.0), (0.0, 0.0), (20.0, 0.0)]))
  for node in nodes:
    ship.addNode(node)

  bridge = ShipBridge()
  bridge.addNode(nodes[1])

  engine = ShipEngine()
  engine.addNode(nodes[0])

  laser = ShipLaser()
  laser.addNode(nodes[0])

  reactor = ShipReactor()
  reactor.addNode(nodes[1])
  reactor.state = ReactorState.warmup

  ship.addModule(bridge)
  ship.addModule(engine)
  ship.addModule(laser)
  ship.addModule(reactor)

  if smc:
    smc = ShipSMC()
    smc.addNode(nodes[2])
    ship.addModule(smc)

  if rmc:
    rmc = ShipRMC()
    rmc.addNode(nodes[2])
    ship.addModule(rmc)

  return ship

def init_game(game):
  game.world.addShip(build_ship(True, True))
  game.world.addShip(build_ship(False, True))
  game.world.addShip(build_ship(False, False))
  game.world.ships[1].x += 60
  game.world.ships[2].x -= 60
