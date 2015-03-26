from enum import Enum
from math import *
import random

from event import LaserFiredEvent, DamageReceivedEvent
from protocol import *
from util import get_id
from vector import *

clamp = lambda val, low, high: max(low, min(high, val))

class ShipNode(Serializable):
  readable_attr = { 'x'     : limited_precision_float('x'     , 5),
                    'y'     : limited_precision_float('y'     , 5),
                    'hp'    : limited_precision_float('hp'    , 5),
                    'max_hp': limited_precision_float('max_hp', 5)  }
  
  writable_attr = { 'x'     : float,
                    'y'     : float,
                    'hp'    : float,
                    'max_hp': float  }

  def __init__(self, x, y):
    self._index = -1 # index in the ship list containing this Node
    self._ship   = None

    self.x      = x
    self.y      = y
    self.hp     = 100.0
    self.max_hp = 100.0

  def do_dmg(self, dmg):
    self.old_hp = self.hp
    self.hp = clamp(self.hp - dmg, 0, self.max_hp)
    effective_dmg = self.old_hp - self.hp
    self._ship.handle_event(DamageReceivedEvent(self, effective_dmg))

  def apply_diff(self, diff):
    super().apply_diff(diff)

class ShipModule(Serializable):
  role = ''

  readable_attr = { 'nodes': lambda obj: dict((n._index, 1) for n in obj.nodes),
                    'damage': limited_precision_float('damage', 5)
                  }

  def __init__(self):
    self._index = -1 # index in the ship list containing this Node
    self._ship   = None

    self.nodes  = []
    self.damage = 0.0

  def addNode(self, node):
    assert isinstance(node, ShipNode)
    self.nodes.append(node)

  def update(self):
    self.performance = 0.0
    hp = 0.0
    max_hp = 0.0
    for n in self.nodes:
      hp     += n.hp
      max_hp += n.max_hp
    if max_hp > 0.0:
      self.damage = 1.0 - hp / max_hp

  def apply_diff(self, diff):
    pass

class ShipEngine(ShipModule):
  role = 'engine'

class ShipBridge(ShipModule):
  role = 'bridge'

class ShipSMC(ShipModule): # Speed Management Computer
  role = 'smc'

class ShipRMC(ShipModule): # Rotation Management Computer
  role = 'rmc'

class ShipLaser(ShipModule):
  class WeaponState(Enum):
    idle   = 'idle'
    firing = 'firing'

  role = 'weapon'

  readable_attr = { 'power'      : limited_precision_float('power'      , 5),
                    'min_range'  : limited_precision_float('min_range'  , 5),
                    'max_range'  : limited_precision_float('max_range'  , 5),
                    'energy'     : limited_precision_float('energy'     , 5),
                    'max_energy' : limited_precision_float('max_energy' , 5),
                    'reload_rate': limited_precision_float('reload_rate', 5),
                    'target'     : lambda obj: obj.target.id if obj.target is not None else None,
                    'state'      : lambda obj: obj.state.name,
                  }

  writable_attr = { 'power'      : float,
                    'min_range'  : float,
                    'max_range'  : float,
                    'energy'     : float,
                    'max_energy' : float,
                    'reload_rate': float,
                    'state'      : WeaponState,
                  }

  def __init__(self):
    ShipModule.__init__(self)
    Serializable.__init__(self)
    self.power       =  20.0
    self.min_range   =  10.0
    self.max_range   = 100.0
    self.energy      =   0.0
    self.max_energy  = 100.0
    self.reload_rate =   5.0
    self.target      =  None
    self.state       = ShipLaser.WeaponState.idle

  def update(self):
    self.energy = clamp(self.energy + self.reload_rate, 0, self.max_energy)
    if self.energy == self.max_energy and self.state == ShipLaser.WeaponState.firing and self.target is not None:
      r = hypot(self.target.x - self._ship.x, self.target.y - self._ship.y)
      dmg = self.power if self.min_range <= r <= self.max_range else 0.0
      self.target.do_dmg(dmg)
      self.energy = 0.0
      self.state = ShipLaser.WeaponState.idle
      self._ship.handle_event(LaserFiredEvent(self._ship, self.target, self._index))

  def apply_diff(self, diff):
    Serializable.apply_diff(self, diff)
    ShipModule.apply_diff(self, diff)
    if 'target' in diff:
      ship_id = to_int(diff['target'], error='target is not an int')
      self.target = self._ship._world.getShipById(ship_id)

class Ship(Serializable):
  readable_attr = { 'x'             : limited_precision_float('x'             , 5),
                    'y'             : limited_precision_float('y'             , 5),
                    'direction'     : limited_precision_float('direction'     , 5),
                    'speed'         : limited_precision_float('speed'         , 5),
                    'trajectory'    : limited_precision_float('trajectory'    , 5),
                    'rotation'      : limited_precision_float('rotation'      , 5),
                    'throttle_speed': limited_precision_float('throttle_speed', 5),
                    'throttle_rot'  : limited_precision_float('throttle_rot'  , 5),
                    'max_speed'     : limited_precision_float('max_speed'     , 5),
                    'max_accel'     : limited_precision_float('max_accel'     , 5),
                    'max_rot'       : limited_precision_float('max_rot'       , 5),
                    'max_rot_accel' : limited_precision_float('max_rot_accel' , 5),
                    'modules'       : lambda obj: obj.serialize_modules()         ,
                    'nodes'         : lambda obj: obj.serialize_nodes()           ,
                    'dx'            : lambda obj: round(obj.calc_speed_x(), 5)    ,
                    'dy'            : lambda obj: round(obj.calc_speed_y(), 5)      }

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
    self._world   = None

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
    node._ship  = self
    self.nodes.append(node)

  def addModule(self, module):
    assert isinstance(module, ShipModule)
    if module.role not in self.modules:
      self.modules[module.role] = []
    module._index = len(self.modules[module.role])
    module._ship  = self
    self.modules[module.role].append(module)
    module.ship = self

  def calc_speed_x(self):
    return cos(self.trajectory) * self.speed

  def calc_speed_y(self):
    return sin(self.trajectory) * self.speed

  def calc_speed_vector(self):
    return (self.calc_speed_x(), self.calc_speed_y())

  def do_dmg(self, dmg):
    n = random.randrange(len(self.nodes))
    self.nodes[n].do_dmg(dmg)

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

  def handle_event(self, evt):
    self._world.handle_event(evt)

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
      if key == 'modules':
        if type(diff[key]) != dict:
          raise ProtocolError(reason='Modules diffs should be objects')
        for role in diff[key]:
          if role in self.modules:
            for mod_key, mod_diff in diff[key][role].items():
              mod_idx = to_int(mod_key, error='Module ids should be integers, not "%s"' % mod_key)
              if mod_idx >= len(self.modules[role]) or mod_idx < 0:
                raise ProtocolError(reason='Module index %d is not valid. Should be in [%d, %d)' %(mod_idx, 0, len(self.modules[role])))
              self.modules[role][mod_idx].apply_diff(mod_diff)
          else:
            raise ProtocolError(reason='Unknown module "%s"' % role)
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
