from math import *

from util import get_id, ProtocolError, limited_precision_float

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
  readable_attr = { 'x'             : limited_precision_float(5),
                    'y'             : limited_precision_float(5),
                    'rotation'      : limited_precision_float(5),
                    'speed'         : limited_precision_float(5),
                    'throttle_accel': limited_precision_float(5),
                    'throttle_rot'  : limited_precision_float(5),
                    'max_accel'     : limited_precision_float(5),
                    'max_speed_fwd' : limited_precision_float(5),
                    'max_speed_bwd' : limited_precision_float(5),
                    'max_drot'      : limited_precision_float(5)  }

  writable_attr = { 'x'             : float,
                    'y'             : float,
                    'rotation'      : float,
                    'speed'         : float,
                    'throttle_accel': float,
                    'throttle_rot'  : float,
                    'max_accel'     : float,
                    'max_speed_fwd' : float,
                    'max_speed_bwd' : float,
                    'max_drot'      : float  }

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
        ctor = self.writable_attr[key]
        try:
          val = ctor(diff[key])
        except ValueError:
          raise ProtocolError(reason='Invalid type for field %s, expected %s got "%s"' % (key, str(ctor), diff[key]))
        else:
          setattr(self, key, val)
      else:
        raise ProtocolError(reason='Unknown key for ship: %s' % key)
    self.rotation = clamp(self.rotation,  0.0, 2*pi)
    self.throttle_accel = clamp(self.throttle_accel, -1.0,  1.0)
    self.throttle_rot   = clamp(self.throttle_rot,   -1.0,  1.0)

  def serialize(self):
    dx, dy = self.calc_speed_vector()
    result = dict((a, ctor(getattr(self, a))) for a, ctor in self.readable_attr.items())
    result['dx'] = round(dx, 5)
    result['dy'] = round(dy, 5)
    return result
