from math import *

from util import get_id, ProtocolError

clamp = lambda val, low, high: max(low, min(high, val))

class ShipModule:
  def __init__(self, role):
    self.nodes  = []
    self.damage = 0.0
    self.role   = role

  def addNode(self, node):
    assert isinstance(node, ShipNode)
    self.nodes.append(node)

  def update(self):
    self.damage = 0.0
    for n in self.nodes:
      self.damage += n.damage
    l = len(self.nodes)
    if l > 0:
      self.damage /= len(self.nodes)

class ShipNode:
  def __init__(self, x, y):
    self.x      = x
    self.y      = y
    self.damage = 0.0

class Ship:
  readable_attr = ['x', 'y', 'rotation', 'speed',
                   'throttle_accel', 'throttle_rot',
                   'max_accel', 'max_speed_fwd', 'max_speed_bwd', 'max_drot']
  writable_attr = ['x', 'y', 'rotation', 'speed',
                   'throttle_accel', 'throttle_rot',
                   'max_accel', 'max_speed_fwd', 'max_speed_bwd', 'max_drot']

  def __init__(self):
    self.id = get_id()
    self.x              =  0.0
    self.y              =  0.0
    self.rotation       =  0.0
    self.speed          =  0.0

    self.throttle_accel =  0.0
    self.throttle_rot   =  0.0

    self.max_accel      =  0.2
    self.max_speed_fwd  = 10.0
    self.max_speed_bwd  = 10.0
    self.max_drot       =  0.1

    self.nodes   = []
    self.modules = {}

  def addNode(self, node):
    assert isinstance(node, ShipNode)
    self.nodes.append(node)

  def addModule(self, module):
    assert isinstance(module, ShipModule)
    if module.role not in self.modules:
      self.modules[module.role] = []
    self.modules[module.role].append(module)

  def calc_speed_vector(self):
    dx = cos(self.rotation) * self.speed
    dy = sin(self.rotation) * self.speed
    return (dx, dy)

  def move(self, vector):
    dx, dy = vector
    self.x += dx
    self.y += dy

  def update_rotation(self):
    self.rotation = fmod(self.rotation + self.throttle_rot * self.max_drot, 2*pi)
    if self.rotation < 0.0:
      self.rotation += 2*pi

  def update_speed(self):
    engine_performance = 0.0
    if 'engine' in self.modules and len(self.modules['engine']) > 0:
      engine_performance = 1.0 - self.modules['engine'][0].damage
    max_accel = self.max_accel * engine_performance
    target_speed = self.throttle_accel * (self.max_speed_fwd if self.throttle_accel >= 0.0 else self.max_speed_bwd)
    dspeed = target_speed - self.speed
    if dspeed >= 0.0:
      self.speed += min(dspeed,  max_accel)
    else:
      self.speed += max(dspeed, -max_accel)

  def update_modules(self):
    for modules in self.modules.values():
      for module in modules:
        module.update()

  def update(self):
    self.update_modules()
    self.update_rotation()
    self.update_speed()
    self.move(self.calc_speed_vector())

  def apply_diff(self, diff):
    if type(diff) != dict:
      raise ProtocolError(reason='Ship diffs should be objects')
    for key in diff:
      if key in self.writable_attr:
        try:
          val = float(diff[key])
        except ValueError:
          raise ProtocolError(reason='Invalid type for field %s, expected float got "%s"' % (key, diff[key]))
        else:
          setattr(self, key, val)
      else:
        raise ProtocolError(reason='Unknown key for ship: %s' % key)
    self.rotation = clamp(self.rotation,  0.0, 2*pi)
    self.throttle_accel = clamp(self.throttle_accel, -1.0,  1.0)
    self.throttle_rot   = clamp(self.throttle_rot,   -1.0,  1.0)

  def serialize(self):
    dx, dy = self.calc_speed_vector()
    result = dict((a, getattr(self, a)) for a in self.readable_attr)
    result['dx'] = dx
    result['dy'] = dy
    return result
