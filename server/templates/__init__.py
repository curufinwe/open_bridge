import itertools as it

from ship import *

# -------------------- Ships --------------------

def minimal_ship(smc=True, rmc=True):
  ship = Ship()

  nodes = list(it.starmap(ShipNode, [(  0.0,  0.0), ( 10.0,  0.0), (-10.0,  0.0),
                                     (  0.0, 10.0), (  0.0,-10.0)]))
  for node in nodes:
    ship.addNode(node)

  bridge = ShipBridge()
  bridge.addNode(nodes[0])
  ship.addModule(bridge)

  if smc:
    smc = ShipSMC()
    smc.addNode(nodes[0])
    ship.addModule(smc)

  if rmc:
    rmc = ShipRMC()
    rmc.addNode(nodes[0])
    ship.addModule(rmc)

  laser = ShipLaser()
  laser.addNode(nodes[1])
  ship.addModule(laser)

  engine = ShipEngine()
  engine.addNode(nodes[2])
  ship.addModule(engine)

  reactor = ShipReactor()
  reactor.addNode(nodes[3])
  reactor.state = ReactorState.warmup
  ship.addModule(reactor)

  energybank = ShipEnergyBank()
  energybank.addNode(nodes[4])
  ship.addModule(energybank)

  shield = ShipShield()
  shield.addNode(nodes[4])
  ship.addModule(shield)

  return ship

ship_templates = { 'debug_ship_1': minimal_ship,
                   'debug_ship_2': lambda: minimal_ship(smc=False),
                   'debug_ship_3': lambda: minimal_ship(smc=False, rmc=False),
                 }

# -------------------- Engine --------------------

# -------------------- Reactor --------------------

# -------------------- EnergyBank --------------------

# -------------------- Weapons --------------------

