from math import *
import sys

from event    import *
from protocol import *
from util     import *
from vector   import *

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

  def do_damage(self, damage):
    self.old_hp = self.hp
    self.hp = clamp(self.hp - damage, 0, self.max_hp)
    effective_damage = self.old_hp - self.hp
    self._ship.handle_event(DamageReceivedEvent(self, effective_damage))

  def _apply_diff(self, diff):
    if 'x' in diff or 'y' in diff:
      self.update_angle()

class ShipModule(Serializable):
  role = ''

  readable_attr = { 'damage': limited_precision_float('damage', 5)
                  }

  def __init__(self):
    self._index = -1 # index in the ship list containing this Node
    self._ship  = None

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

  def _calc_diff(self, client, state):
    diff =  calc_list_diff(client, [n._index for n in self.nodes], state.get('nodes', None))
    return { 'nodes': diff } if diff != DiffOp.IGNORE else DiffOp.IGNORE

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
    self.max_rot_accel                    =  0.00075

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
                    'state'            : lambda client, obj: obj.state.value,
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

  def update(self):
    super().update()
    self.energy = min(self.energy, self.max_energy * (1.0 - self.damage))

  def required_energy(self):
    return self.max_energy * (1.0 - self.damage) - self.energy

  def consume_energy(self, energy):
    self.energy = clamp(self.energy + energy, 0.0, self.max_energy * (1.0 - self.damage))

  def available_energy(self):
    return self.energy

  def produce_energy(self, energy):
    self.energy = clamp(self.energy - energy, 0.0, self.max_energy * (1.0 - self.damage))

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
                    'target'     : lambda client, obj: obj.target.id if obj.target is not None else None,
                    'state'      : lambda client, obj: obj.state.value,
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
    self.power       =  50.0
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
        damage = self.power
        direction = atan2(self._ship.y - self.target.y, self._ship.x - self.target.x)
        self.target.do_damage(damage, direction)
        self.energy = 0.0
        self.state = WeaponState.idle
        self._ship.handle_event(LaserFiredEvent(self._ship, self.target, self._index))

  def required_energy(self):
    return min(self.max_energy - self.energy, self.reload_rate)

  def consume_energy(self, energy):
    self.energy = clamp(self.energy + energy, 0.0, self.max_energy)

  def _apply_diff(self, diff):
    if 'target' in diff:
      ship_id = diff['target']
      try:
        self.target = self._ship._world.ships[ship_id]
      except KeyError:
        raise ProtocolError(reason='Invalid target id: %s' % ship_id)
    return set(['target'])

class ShieldState(Enum):
  disabled = 'disabled'
  enabled  = 'enabled'

class ShipShield(ShipModule, EnergySink):
  role = 'shield'

  readable_attr = { 'base_energy_consumption': limited_precision_float('base_energy_consumption', 5),
                    'recharge_rate'          : limited_precision_float('recharge_rate'          , 5),
                    'recharge_efficiency'    : limited_precision_float('recharge_efficiency'    , 5),
                    'regen_rate'             : limited_precision_float('regen_rate'             , 5),
                    'regen_efficiency'       : limited_precision_float('regen_efficiency'       , 5),
                    'design_capacity'        : limited_precision_float('design_capacity'        , 5),
                    'direction'              : limited_precision_float('direction'              , 5),
                    'arc'                    : limited_precision_float('arc'                    , 5),
                    'strength_limit'         : limited_precision_float('strength_limit'         , 5),
                    'strength'               : limited_precision_float('strength'               , 5),
                    'state'                  : lambda client, obj: obj.state.value,
                  }

  writable_attr = { 'base_energy_consumption': float_setter('base_energy_consumption', 0.0, float('inf')),
                    'recharge_rate'          : float_setter('recharge_rate'          , 0.0, float('inf')),
                    'recharge_efficiency'    : float_setter('recharge_efficiency'    , 0.0, float('inf')),
                    'regen_rate'             : float_setter('regen_rate'             , 0.0, float('inf')),
                    'regen_efficiency'       : float_setter('regen_efficiency'       , 0.0, float('inf')),
                    'design_capacity'        : float_setter('design_capacity'        , 0.0, float('inf')),
                    'arc'                    : float_setter('arc'                    , 0.0,       2 * pi, open_right=True),
                    'strength_limit'         : float_setter('strength_limit'         , 0.0, float('inf')),
                    'strength'               : float_setter('strength'               , 0.0, float('inf')),
                    'state'                  : generic_setter('state', to_enum(ShieldState)) ,
                  }

  def __init__(self):
    super().__init__()

    self.base_energy_consumption =   0.0
    self.recharge_rate           =   2.0
    self.recharge_efficiency     =   1.0
    self.regen_rate              =   0.10 
    self.regen_efficiency        =   0.05
    self.design_capacity         = 250.0
    self.direction               =   0.0
    self.arc                     = deg2rad(180.)

    self.strength_limit          = self.design_capacity
    self.strength                =   0.0
    self.state                   = ShieldState.enabled

  def update(self):
    super().update()

    if self.damage > .25:
      self.disable()

  def required_energy(self):
    if self.state == ShieldState.disabled:
      return 0.0
    regen_energy    = min(self.regen_rate   , (self.design_capacity - self.strength_limit)) / self.regen_efficiency
    max_regen       = regen_energy * self.regen_efficiency
    recharge_energy = min(self.recharge_rate, (self.strength_limit + max_regen - self.strength)) / self.recharge_efficiency
    return self.base_energy_consumption + max(0.0, regen_energy + recharge_energy)

  def consume_energy(self, energy):
    bec = self.base_energy_consumption * (1.0 - self.damage)
    if energy < bec:
      self.disable()
    else:
      energy -= bec

    energy_per_charge   = 1.0 / self.recharge_efficiency
    energy_per_regen    = 1.0 / self.regen_efficiency
    scaling_factor      = 1.0 / (energy_per_charge + energy_per_regen)

    charge_energy       = min(energy, (self.strength_limit - self.strength) / self.recharge_efficiency)
    energy             -= charge_energy
    charge_energy      += energy * energy_per_charge * scaling_factor
    self.strength_limit = min(self.design_capacity, self.strength_limit + energy * scaling_factor)
    self.strength       = min(self.strength_limit , self.strength + charge_energy * self.recharge_efficiency)

  def do_damage(self, damage):
    prev_strength = self.strength
    self.strength_limit = clamp(self.strength_limit - damage, 0.0, self.design_capacity)
    self.strength       = clamp(self.strength       - damage, 0.0, self.strength_limit)
    return prev_strength - self.strength

  def disable(self):
    self.state    = ShieldState.disabled
    self.strength = 0.0
