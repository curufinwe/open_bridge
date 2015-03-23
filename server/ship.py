from math import *

from util import get_id, to_int, ProtocolError, limited_precision_float
from vector import *

clamp = lambda val, low, high: max(low, min(high, val))

class Serializable():
  readable_attr = {}
  writable_attr = {}

  def apply_diff(self, diff):
    keys_to_del = []
    if type(diff) != dict:
      raise ProtocolError(reason='%s diffs should be objects' % self.__class__.__name__)
    for key in diff:
      if key in self.writable_attr:
        keys_to_del.append(key)
        ctor = self.writable_attr[key]
        try:
          val = ctor(diff[key])
        except ValueError:
          raise ProtocolError(reason='Invalid type for field %s, expected %s got "%s"' % (key, str(ctor), diff[key]))
        else:
          setattr(self, key, val)
    for key in keys_to_del:
      del diff[key]

  def serialize(self):
    return dict((a, ctor(getattr(self, a))) for a, ctor in self.readable_attr.items())

class ShipModule:
  def __init__(self):
    self.nodes  = []
    self.damage = 0.0

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

  def serialize(self):
    return { 'nodes' : dict((n._index, 1) for n in self.nodes), 
             'damage': round(self.damage, 5)                    }

class ShipEngine(ShipModule):
  role = 'engine'

class ShipBridge(ShipModule):
  role = 'bridge'

class ShipSMC(ShipModule): # Speed Management Computer
  role = 'smc'

class ShipRMC(ShipModule): # Rotation Management Computer
  role = 'rmc'

class ShipLaser(ShipModule, Serializable):
  role = 'weapon'

  readable_attr = { 'power'      : limited_precision_float(5),
                    'min_range'  : limited_precision_float(5),
                    'max_range'  : limited_precision_float(5),
                    'energy'     : int,
                    'max_energy' : int,
                    'reload_time': int,
                  }

  writable_attr = { 'power'      : float,
                    'min_range'  : float,
                    'max_range'  : float,
                    'energy'     : int,
                    'max_energy' : int,
                    'reload_rate': int,
                  }

  def __init__(self):
    ShipModule.__init__(self)
    Serializable.__init__(self)
    self.power       = 20.0
    self.min_range   = 10.0
    self.max_range   = 100.0
    self.energy      = 0
    self.max_energy  = 100
    self.reload_rate = 5

  def update(self):
    self.energy = clamp(self.energy + self.reload_rate, 0, self.max_energy)

  def apply_diff(self, diff):
    Serializable.apply_diff(diff)
    ShipModule.apply_diff(diff)

  def serialize(self):
    result = ShipModule.serialize(self)
    tmp = Serializable.serialize(self)
    result.update(tmp)
    return result

class ShipNode(Serializable):
  readable_attr = { 'x'     : limited_precision_float(5),
                    'y'     : limited_precision_float(5),
                    'damage': limited_precision_float(5)  }
  
  writable_attr = { 'x'     : float,
                    'y'     : float,
                    'damage': float }

  def __init__(self, x, y):
    self._index = -1 # index in the ship list containing this Node
    self.x      = x
    self.y      = y
    self.damage = 0.0

  def apply_diff(self, diff):
    super().apply_diff(diff)

  def serialize(self):
    return super().serialize()

class Ship(Serializable):
  readable_attr = { 'x'             : limited_precision_float(5),
                    'y'             : limited_precision_float(5),
                    'direction'     : limited_precision_float(5),
                    'speed'         : limited_precision_float(5),
                    'trajectory'    : limited_precision_float(5),
                    'rotation'      : limited_precision_float(5),
                    'throttle_speed': limited_precision_float(5),
                    'throttle_rot'  : limited_precision_float(5),
                    'max_speed'     : limited_precision_float(5),
                    'max_accel'     : limited_precision_float(5),
                    'max_rot'       : limited_precision_float(5),
                    'max_rot_accel' : limited_precision_float(5)  }

  writable_attr = { 'x'             : float,
                    'y'             : float,
                    'direction'     : float,
                    'speed'         : float,
                    'trajectory'    : float,
                    'rotation'      : float,
                    'throttle_speed': float,
                    'throttle_rot'  : float,
                    'max_speed'     : float,
                    'max_accel'     : float,
                    'max_rot'       : float,
                    'max_rot_accel' : float  }

  def __init__(self):
    self.id = get_id()
    self.x              =  0.0
    self.y              =  0.0
    self.direction      =  0.0

    self.speed          =  0.0
    self.trajectory     =  0.0
    self.rotation       =  0.0

    self.throttle_speed =  0.0
    self.throttle_rot   =  0.0

    self.max_speed      = 10.0
    self.max_accel      =  0.2
    self.max_rot        =  0.1
    self.max_rot_accel  =  0.01

    self.nodes   = []
    self.modules = {}

  def addNode(self, node):
    assert isinstance(node, ShipNode)
    node._index = len(self.nodes)
    self.nodes.append(node)

  def addModule(self, module):
    assert isinstance(module, ShipModule)
    if module.role not in self.modules:
      self.modules[module.role] = []
    self.modules[module.role].append(module)

  def calc_speed_vector(self):
    dx = cos(self.trajectory) * self.speed
    dy = sin(self.trajectory) * self.speed
    return (dx, dy)

  def avg_dmg(self, role):
    if role in self.modules:
      s = 0.0
      for m in self.modules[role]:
        s += m.damage
      return s / len(self.modules[role])
    return 1.0

  def move(self, vector):
    self.x += vector[0]
    self.y += vector[1]

  def update_direction(self):
    if self.avg_dmg('rmc') < 1.0:
      target_rotation = self.max_rot * self.throttle_rot
      diff = clamp(target_rotation - self.rotation, -self.max_rot_accel, self.max_rot_accel)
      self.rotation += diff
    else:
      self.rotation += self.max_rot_accel * self.throttle_rot
    self.rotation = clamp(self.rotation, -self.max_rot, self.max_rot)
    self.direction += self.rotation
    self.direction = fmod(self.direction, 2*pi)
    if self.direction < 0.0:
      self.direction += 2*pi

  def update_speed(self):
    engine_performance = 1.0 - self.avg_dmg('engine')
    max_accel = self.max_accel * engine_performance

    cur_vec  = to_vec(self.trajectory, self.speed)
    if self.avg_dmg('smc') < 1.0:
      target_speed = self.max_speed * self.throttle_speed
      target_vec = to_vec(self.direction, target_speed)
      diff_vec = sub_vec(target_vec, cur_vec)
      l = hypot(*diff_vec)
      if l > 0.0:
        scale = clamp(l, 0, max_accel) / l
      else:
        scale = 0.0
      diff_vec = mul_vec(diff_vec, scale)
    else:
      diff_vec = to_vec(self.direction,  max_accel * self.throttle_speed)

    new_vec = add_vec(cur_vec, diff_vec)
    self.trajectory = atan2(new_vec[1], new_vec[0])
    self.speed = hypot(*new_vec)

  def update_modules(self):
    for modules in self.modules.values():
      for module in modules:
        module.update()

  def update(self):
    self.update_modules()
    self.update_direction()
    self.update_speed()
    self.move(self.calc_speed_vector())

  def apply_diff(self, diff):
    super().apply_diff(diff)
    for key in diff:
      if key == 'nodes':
        if type(diff[key]) != dict:
          raise ProtocolError(reason='Node diffs should be objects')
        for node_key, node_diff in diff[key].items():
          node_idx = to_int(node_key, error='Node ids should be integers, not "%s"')
          if node_idx >= len(self.nodes) or node_idx < 0:
            raise ProtocolError(reason='Node index %d is not valid. Should be in [%d, %d)' %(node_idx, 0, len(self.nodes)))
          self.nodes[node_idx].apply_diff(node_diff)
      else:
        raise ProtocolError(reason='Unknown key for ship: %s' % key)

    self.direction      = clamp(self.direction     ,  0.0, 2*pi)
    self.throttle_speed = clamp(self.throttle_speed, -1.0,  1.0)
    self.throttle_rot   = clamp(self.throttle_rot  , -1.0,  1.0)

  def serialize_modules(self):
    res = {}
    for k, modules in self.modules.items():
      res[k] = dict((i, m.serialize()) for i, m in enumerate(modules))
    return res

  def serialize_nodes(self):
    return dict((idx, node.serialize()) for idx, node in enumerate(self.nodes))

  def serialize(self):
    result = super().serialize()
    dx, dy = self.calc_speed_vector()
    result['modules'] = self.serialize_modules()
    result['nodes']   = self.serialize_nodes()
    result['dx']      = round(dx, 5)
    result['dy']      = round(dy, 5)
    return result
