from math import *

from protocol import to_int, ProtocolError
from ship import Ship

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
    self.ships       = []
    self.bodies      = []

  def addShip(self, ship):
    ship._world = self
    self.ships.append(ship)

  def getShipById(self, id):
    for s in self.ships:
      if s.id == id:
        return s
    return None

  def handle_event(self, evt):
    self.game.handle_event(evt)

  def update(self):
    for s in self.ships:
      s.update()
      enforce_boundary(self.sector_size, s)
    for b in self.bodies:
      b.update()
      enforce_boundary(self.sector_size, b)

  def apply_diff(self, diff):
    if 'ships' in diff:
      if type(diff['ships']) != dict:
        raise ProtocolError(reason='Ship diffs should be an object')

      for key, val in diff['ships'].items():
        try:
          key = int(key)
        except:
          raise ProtocolError('ship id is not an int but "%s"' % key)
        idx = find_obj_by_id(self.ships, key)
        if idx is None:
          raise ProtocolError(reason='Invalid id for a ship: %d' % key)
        elif val is None:
          del self.ships[idx]
        else:
          self.ships[idx].apply_diff(val)

  def serialize(self):
    return { 'sector_size': self.sector_size,
             'ships'      : dict((s.id, s.serialize()) for s in self.ships),
             'bodies'     : dict((b.id, b.serialize()) for b in self.bodies) }
