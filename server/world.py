from math import *

from protocol import ProtocolError, DiffOp, calc_dict_diff
from ship import Ship, ShipState
from util import clamp
from vector import *

def enforce_boundary(dist, obj):
  obj_dist = hypot(obj.x, obj.y)
  if obj_dist > dist:
    scale = dist / obj_dist
    obj.x *= scale
    obj.y *= scale

def find_obj_by_id(lst, id):
 for idx, candidate in enumerate(lst):
   if candidate.id == id:
     return idx
 return None

class World:
  def __init__(self, game):
    self.game = game
    self.sector_size = 900.0
    self.ships       = {}
    self.bodies      = {}

  def addShip(self, ship):
    ship._world = self
    self.ships[ship.id] = ship
    return ship.id

  def handle_event(self, evt):
    self.game.handle_event(evt)

  def detect_collision(self):
    ship_ids = list(self.ships.keys())
    for idx_a in range(len(ship_ids)):
      ship_a = self.ships[ship_ids[idx_a]]
      for idx_b in range(idx_a + 1, len(ship_ids)):
        ship_b = self.ships[ship_ids[idx_b]]
        diff = (ship_a.x - ship_b.x, ship_a.y - ship_b.y)
        dist = hypot(*diff)
        min_dist = ship_a.radius + ship_b.radius
        if dist < min_dist:
          force = 20 * (1.0 - (dist / min_dist))
          dist = clamp(dist, 1.0, float('inf'))
          ship_a.add_impulse(mul_vec(diff,  force / dist))
          ship_b.add_impulse(mul_vec(diff, -force / dist))

  def update(self):
    for s in self.ships.values():
      s.update()
      enforce_boundary(self.sector_size, s)
    for b in self.bodies:
      b.update()
      enforce_boundary(self.sector_size, b)
    self.detect_collision()

    ships_to_del = []
    for s_id, s in self.ships.items():
      s.update_state()
      if s.state == ShipState.destroyed:
        ships_to_del.append(s_id)
    ships_to_del.reverse()
    for s_id in ships_to_del:
      del self.ships[s_id]

  def apply_diff(self, diff):
    for key in diff:
      if key == 'ships':
        if type(diff['ships']) != dict:
          raise ProtocolError(reason='Ship diffs should be an object')

        for key, val in diff['ships'].items():
          if key not in self.ships:
            raise ProtocolError(reason='Invalid id for a ship: %s' % key)
          elif val is None:
            del self.ships[key]
          else:
            self.ships[key].apply_diff(val)
      else:
        raise ProtocolError(reason='Unknown key "%s" in world' % key)

  def calc_diff(self, client, state):
    result = {}

    if state is None:
      state = {}

    if 'sector_size' not in state or state['sector_size'] != self.sector_size:
      result['sector_size'] = self.sector_size

    s_diff = calc_dict_diff(client, self.ships, state['ships'] if 'ships' in state else {})
    if s_diff == DiffOp.IGNORE:
      pass
    elif s_diff == DiffOp.DELETE:
      result['ships'] = None
    else:
      result['ships'] = s_diff

    return result if len(result) > 0 else DiffOp.IGNORE

