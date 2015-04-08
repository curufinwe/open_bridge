from enum import Enum
import functools as fun
from math import *
import random
import sys

from event import *
from protocol import *
from util import *
from vector import *

class ShipNode(Serializable):
  readable_attr = { 'x'     : limited_precision_float('x'     , 5),
                    'y'     : limited_precision_float('y'     , 5),
                    'hp'    : limited_precision_float('hp'    , 5),
                    'max_hp': limited_precision_float('max_hp', 5)  }
  
  writable_attr = { 'x'     : float_setter('x'     , float('-inf'), float('inf')),
                    'y'     : float_setter('y'     , float('-inf'), float('inf')),
                    'hp'    : float_setter('hp'    , 0.0          , float('inf')),
                    'max_hp': float_setter('max_hp', 0.0          , float('inf')),
                  }

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
    hp = 0.0
    max_hp = 0.0
    for n in self.nodes:
      hp     += n.hp
      max_hp += n.max_hp
    if max_hp > 0.0:
      self.damage = 1.0 - hp / max_hp

class EnergySource:
  energy_source_priority = 100

  def available_energy(self):
    return 0.0

  def produce_energy(self, energy):
    pass

class EnergySink:
  energy_sink_priority = 100

  def required_energy(self):
    return 0.0

  def consume_energy(self, energy):
    pass

class ShipEngine(ShipModule, EnergySink):
  role = 'engine'

  readable_attr = { 'max_energy_consumption_accel'     : limited_precision_float('max_energy_consumption_accel'    , 2),
                    'max_energy_consumption_rot_accel' : limited_precision_float('max_energy_consumption_rot_accel', 2),
                    'max_accel'                        : limited_precision_float('max_accel'                       , 5),
                    'max_rot_accel'                    : limited_precision_float('max_rot_accel'                   , 5),
                  }

  writable_attr = { 'max_energy_consumption_accel'     : float_setter('max_energy_consumption_accel'     , 0.0, float('inf')                 ),
                    'max_energy_consumption_rot_accel' : float_setter('max_energy_consumption_rot_accel' , 0.0, float('inf')                 ),
                    'max_accel'                        : float_setter('max_accel'                        , 0.0, float('inf')                 ),
                    'max_rot_accel'                    : float_setter('max_rot_accel'                    , 0.0, 2*pi        , open_right=True),
                  }

  def __init__(self):
    super().__init__()
    self.max_energy_consumption_accel     = 50.0
    self.max_energy_consumption_rot_accel =  5.0
    self.max_accel                        =  0.2
    self.max_rot_accel                    =  0.01

    self.accel                            =  0.0
    self.rot_accel                        =  0.0
    self.energy_consumption               =  0.0

  def update(self):
    super().update()

  def required_energy(self):
    # adjust max (rot_)accel for damage
    max_accel               = self.max_accel     * (1.0 - self.damage)
    max_rot_accel           = self.max_rot_accel * (1.0 - self.damage)
    # compute (rot_)accel the engine can deliver
    self.accel              = min(    self._ship.desired_accel     , max_accel)
    self.rot_accel          = min(abs(self._ship.desired_rot_accel), max_rot_accel)
    # the level the engine is performing at
    perf_accel              = self.accel     / (max_accel     if max_accel     > 0.0 else 1.0)
    perf_rot_accel          = self.rot_accel / (max_rot_accel if max_rot_accel > 0.0 else 1.0)
    # adjust sign of rot_accel
    self.rot_accel          = copysign(self.rot_accel, self._ship.desired_rot_accel)
    # the required energy consumption
    energy_accel            = self.max_energy_consumption_accel     * perf_accel
    energy_rot_accel        = self.max_energy_consumption_rot_accel * perf_rot_accel
    self.energy_consumption = energy_accel + energy_rot_accel
    return self.energy_consumption

  def consume_energy(self, energy):
    scale = energy / (self.energy_consumption if self.energy_consumption > 0.0 else 1.0)
    self.accel     *= scale
    self.rot_accel *= scale

class ShipBridge(ShipModule):
  role = 'bridge'

class ShipSMC(ShipModule): # Speed Management Computer
  role = 'smc'

class ShipRMC(ShipModule): # Rotation Management Computer
  role = 'rmc'

class ReactorState(Enum):
  off      = 'off'
  warmup   = 'warmup'
  shutdown = 'shutdown'
  on       = 'on'

class ShipReactor(ShipModule, EnergySource):
  role = 'reactor'

  readable_attr = { 'max_energy_output': limited_precision_float('max_energy_output', 2),
                    'warmup_time'      : get_attr('warmup_time'),
                    'shutdown_time'    : get_attr('shutdown_time'),
                    'state'            : lambda obj: obj.state.value,
                    'warmup'           : limited_precision_float('warmup', 2),
                  }

  writable_attr = { 'max_energy_output':   float_setter('max_energy_output', 0.0, float('inf')),
                    'warmup_time'      :     int_setter('warmup_time'      , 0  , sys.maxsize ),
                    'shutdown_time'    :     int_setter('shutdown_time'    , 0  , sys.maxsize ),
                    'state'            : generic_setter('state',         to_enum(ReactorState)),
                    'warmup'           :   float_setter('warmup'           , 0.0, float('inf')),
                  }

  def __init__(self):
    super().__init__()

    self.max_energy_output =  50.0
    self.warmup_time       = 200
    self.shutdown_time     =  20

    self.state           = ReactorState.off
    self.warmup          =   0.0

  def update(self):
    super().update()
    if self.state == ReactorState.warmup:
      self.warmup   = clamp(self.warmup + 1.0 / self.warmup_time,   0.0, 1.0)
      if self.warmup == 1.0:
        self.state = ReactorState.on
    if self.state == ReactorState.shutdown:
      self.shutdown = clamp(self.warmup - 1.0 / self.shutdown_time, 0.0, 1.0)
      if self.warmup == 0.0:
        self.state = ReactorState.off

  def available_energy(self):
    return self.max_energy_output * self.warmup * (1.0 - self.damage)

class ShipEnergyBank(ShipModule, EnergySink, EnergySource):
  role = 'energy_bank'
  energy_sink_priority = 10
  energy_source_priority = 50

  readable_attr = { 'max_energy': limited_precision_float('max_energy', 2),
                    'energy'    : limited_precision_float('energy'    , 2),
                  }

  writable_attr = { 'max_energy': float_setter('max_energy', 0.0, float('inf')),
                    'energy'    : float_setter('energy'    , 0.0, float('inf')),
                  }

  def __init__(self):
    super().__init__()

    self.energy     =    0.0
    self.max_energy = 1000.0

  def required_energy(self):
    return self.max_energy - self.energy

  def consume_energy(self, energy):
    self.energy = clamp(self.energy + energy, 0.0, self.max_energy)

  def available_energy(self):
    return self.energy

  def produce_energy(self, energy):
    self.energy = clamp(self.energy - energy, 0.0, self.max_energy)

class WeaponState(Enum):
  idle   = 'idle'
  firing = 'firing'

class ShipLaser(ShipModule, EnergySink):
  role = 'weapon'

  readable_attr = { 'power'      : limited_precision_float('power'      , 5),
                    'min_range'  : limited_precision_float('min_range'  , 5),
                    'max_range'  : limited_precision_float('max_range'  , 5),
                    'direction'  : limited_precision_float('direction'  , 5),
                    'firing_arc' : limited_precision_float('firing_arc' , 5),
                    'energy'     : limited_precision_float('energy'     , 5),
                    'max_energy' : limited_precision_float('max_energy' , 5),
                    'reload_rate': limited_precision_float('reload_rate', 5),
                    'target'     : lambda obj: obj.target.id if obj.target is not None else None,
                    'state'      : lambda obj: obj.state.value,
                  }

  writable_attr = { 'power'      : float_setter('power'      , 0.0, float('inf')),
                    'min_range'  : float_setter('min_range'  , 0.0, float('inf')),
                    'max_range'  : float_setter('max_range'  , 0.0, float('inf')),
                    'direction'  : float_setter('direction'  , 0.0, 2*pi        ),
                    'firing_arc' : float_setter('firing_arc' , 0.0, 2*pi        ),
                    'energy'     : float_setter('energy'     , 0.0, float('inf')),
                    'max_energy' : float_setter('max_energy' , 0.0, float('inf')),
                    'reload_rate': float_setter('reload_rate', 0.0, float('inf')),
                    'state'      : generic_setter('state', to_enum(WeaponState)) ,
                  }

  def __init__(self):
    super().__init__()
    self.power       =  20.0
    self.min_range   =  10.0
    self.max_range   = 200.0
    self.direction   =   0.0
    self.firing_arc  = deg2rad(50.)
    self.energy      =   0.0
    self.max_energy  = 100.0
    self.reload_rate =   5.0
    self.target      =  None
    self.state       = WeaponState.idle

  def can_fire_at(self, target):
    diff_x = target.x - self._ship.x
    diff_y = target.y - self._ship.y
    r = hypot(diff_x, diff_y)
    if self.min_range <= r <= self.max_range:
      target_dir = atan2(diff_y, diff_x)
      if target_dir < 0.0:
        target_dir += 2*pi
      weapon_dir = fmod(self._ship.direction + self.direction, 2*pi)
      diff_dir = target_dir - weapon_dir
      if diff_dir > pi:
        diff_dir -= 2*pi
      if abs(diff_dir) <= self.firing_arc * 0.5:
        return True
    return False

  def update(self):
    super().update()
    if self.energy == self.max_energy and self.state == WeaponState.firing and self.target is not None:
      if self.can_fire_at(self.target):
        dmg = self.power
        self.target.do_dmg(dmg)
        self.energy = 0.0
        self.state = WeaponState.idle
        self._ship.handle_event(LaserFiredEvent(self._ship, self.target, self._index))

  def required_energy(self):
    return min(self.max_energy - self.energy, self.reload_rate)

  def consume_energy(self, energy):
    self.energy = clamp(self.energy + energy, 0.0, self.max_energy)

  def _apply_diff(self, diff):
    if 'target' in diff:
      try:
        ship_id = int(diff['target'])
      except ValueError:
        raise ProtocolError('target is not an int')
      self.target = self._ship._world.getShipById(ship_id)
    return set(['target'])

class ShipState(Enum):
  operational = 'operational'
  destroyed   = 'destroyed'

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
                    'max_rot'       : limited_precision_float('max_rot'       , 5),
                    'radius'        : limited_precision_float('radius'        , 5),
                    'modules'       : lambda obj: obj.serialize_modules()         ,
                    'nodes'         : lambda obj: obj.serialize_nodes()           ,
                    'dx'            : lambda obj: round(obj.calc_speed_x(), 5)    ,
                    'dy'            : lambda obj: round(obj.calc_speed_y(), 5)      }

  writable_attr = { 'x'             : float_setter('x'             , float('-inf'), float('inf')                  ),
                    'y'             : float_setter('y'             , float('-inf'), float('inf')                  ),
                    'direction'     : float_setter('direction'     , 0.0          , 2*pi         , open_right=True),
                    'speed'         : float_setter('speed'         , 0.0          , float('inf')                  ),
                    'trajectory'    : float_setter('trajectory'    , 0.0          , 2*pi         , open_right=True),
                    'rotation'      : float_setter('rotation'      , 0.0          , 2*pi         , open_right=True),
                    'throttle_speed': float_setter('throttle_speed', -1.0         , 1.0                           ),
                    'throttle_rot'  : float_setter('throttle_rot'  , -1.0         , 1.0                           ),
                    'max_speed'     : float_setter('max_speed'     , 0.0          , float('inf')                  ),
                    'max_rot'       : float_setter('max_rot'       , 0.0          , 2*pi         , open_right=True),
                    'radius'        : float_setter('radius'        , 0.0          , float('inf')                  ),
                    'nodes'         : [ apply_to_list(name='nodes', func=None) ]
                  }

  module_update_order = ('bridge', 'rmc', 'smc', 'reactor', 'energy_bank', 'weapon', 'engine')

  def __init__(self):
    self._world   = None

    self.id = get_id()
    self.x                 =  0.0
    self.y                 =  0.0
    self.direction         =  0.0

    self.speed             =  0.0
    self.trajectory        =  0.0
    self.rotation          =  0.0

    self.throttle_speed    =  0.0
    self.throttle_rot      =  0.0
    self.desired_accel     =  0.0
    self.desired_rot_accel =  0.0

    self.max_speed         = 10.0
    self.max_rot           =  0.1
    self.radius            = 30.0

    self.state             = ShipState.operational

    self.nodes   = []
    self.modules = dict((s, []) for s in self.module_update_order)
    self.energy_sources = {}
    self.energy_sinks   = {}

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
    if isinstance(module, EnergySource):
      priority = module.energy_source_priority
      if priority not in self.energy_sources:
        self.energy_sources[priority] = []
      self.energy_sources[priority].append(module)
    if isinstance(module, EnergySink):
      priority = module.energy_sink_priority
      if priority not in self.energy_sinks:
        self.energy_sinks[priority] = []
      self.energy_sinks[priority].append(module)

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
    if role in self.modules and len(self.modules[role]) > 0:
      s = 0.0
      for m in self.modules[role]:
        s += m.damage
      return s / len(self.modules[role])
    return 1.0

  def add_impulse(self, vec):
    cur_vec = to_vec(self.trajectory, self.speed)
    new_vec = add_vec(cur_vec, vec)
    self.trajectory = atan2(new_vec[1], new_vec[0])
    self.speed = hypot(*new_vec)

  def move(self, vector):
    self.x += vector[0]
    self.y += vector[1]

  def rotate(self, rotation):
    self.direction += self.rotation
    self.direction = fmod(self.direction, 2*pi)
    if self.direction < 0.0:
      self.direction += 2*pi

  def handle_event(self, evt):
    self._world.handle_event(evt)

  def update_desired_rot_accel(self):
    if self.avg_dmg('rmc') < 1.0:
      self.desired_rot_accel = self.max_rot * self.throttle_rot - self.rotation
    else:
      self.desired_rot_accel = self.throttle_rot * sum(m.max_rot_accel for m in self.modules['engine'])

  def update_desired_accel_dir(self):
    if self.avg_dmg('smc') < 1.0:
      cur_vec                = to_vec(self.trajectory, self.speed)
      target_speed           = self.max_speed * self.throttle_speed
      target_vec             = to_vec(self.direction, target_speed)
      diff_vec               = sub_vec(target_vec, cur_vec)
      self.desired_accel_dir = atan2(diff_vec[1], diff_vec[0])
      self.desired_accel     = hypot(*diff_vec)
    else:
      max_accel              = sum(m.max_accel for m in self.modules['engine'])
      self.desired_accel     = max_accel * self.throttle_speed
      self.desired_accel_dir = self.direction

  def update_modules(self):
    for role in self.module_update_order:
      for module in self.modules[role]:
        module.update()

  def update_energy(self):
    source_priorities = sorted(list(self.energy_sources.keys()), reverse=True)
    available = [[m.available_energy() for m in self.energy_sources[p]] for p in source_priorities]
    available_prio = [sum(ms) for ms in available]
    total_available = sum(available_prio)

    sink_priorities   = sorted(list(self.energy_sinks.keys()), reverse=True)
    required = [[m.required_energy() for m in self.energy_sinks[p]] for p in sink_priorities]
    required_prio = [sum(ms) for ms in required]
    total_required = sum(required_prio)

    for p_idx in range(len(available)):
      consume_prio   = min(total_required, available_prio[p_idx])
      total_required = max(total_required - consume_prio, 0.0)
      ratio = 0.0 if available_prio[p_idx] == 0.0 else consume_prio / available_prio[p_idx]
      for m_idx, m in enumerate(self.energy_sources[source_priorities[p_idx]]):
        m.produce_energy(ratio * available[p_idx][m_idx])

    for p_idx in range(len(required)):
      consume_prio    = min(total_available, required_prio[p_idx])
      total_available = max(total_available - consume_prio, 0.0)
      ratio = 0.0 if required_prio[p_idx] == 0.0 else consume_prio / required_prio[p_idx]
      for m_idx, m in enumerate(self.energy_sinks[sink_priorities[p_idx]]):
        m.consume_energy(ratio * required[p_idx][m_idx])

  def update_state(self):
    hp, max_hp = fun.reduce(add_vec, map(lambda n: (n.hp, n.max_hp), self.nodes))
    if hp / max_hp < .20:
      self.state = ShipState.destroyed
      self.handle_event(ShipDestroyedEvent(self))

  def update_rotation(self):
    rot_accel = sum(m.rot_accel for m in self.modules['engine'])
    self.rotation = clamp(self.rotation + rot_accel, -self.max_rot, self.max_rot)

  def update_speed(self):
    accel    = sum(m.accel for m in self.modules['engine'])
    cur_vec  = self.calc_speed_vector()
    diff_vec = to_vec(self.desired_accel_dir, accel)
    new_vec  = add_vec(cur_vec, diff_vec)

    self.trajectory = atan2(new_vec[1], new_vec[0])
    self.speed      = clamp(hypot(*new_vec), 0.0, self.max_speed)

  def update(self):
    """ Update loop for a single ship:
          - Update desired (rot_)accel and accel_dir
          - Update module state
          - Update energy levels (modules consume/produce energy here)
          - Update rotation/speed
          - rotate/move the ship
    """
    self.update_desired_rot_accel()
    self.update_desired_accel_dir()
    self.update_modules()
    self.update_energy()
    self.update_rotation()
    self.update_speed()
    self.rotate(self.rotation)
    self.move(self.calc_speed_vector())

  def _apply_diff(self, diff):
    for key in diff:
      if key == 'modules':
        if type(diff[key]) != dict:
          raise ProtocolError(reason='Modules diffs should be objects')
        for role in diff[key]:
          if role in self.modules:
            for mod_key, mod_diff in diff[key][role].items():
              try:
                mod_idx = int(mod_key)
              except ValueError:
                raise ProtocolError(reason='Module ids should be integers, not "%s"' % mod_key)
              if mod_idx >= len(self.modules[role]) or mod_idx < 0:
                raise ProtocolError(reason='Module index %d is not valid. Should be in [%d, %d)' %(mod_idx, 0, len(self.modules[role])))
              self.modules[role][mod_idx].apply_diff(mod_diff)
          else:
            raise ProtocolError(reason='Unknown module "%s"' % role)
    return set(['modules'])

  def serialize_modules(self):
    res = {}
    for k, modules in self.modules.items():
      res[k] = dict((i, m.serialize()) for i, m in enumerate(modules))
    return res

  def serialize_nodes(self):
    return dict((idx, node.serialize()) for idx, node in enumerate(self.nodes))
