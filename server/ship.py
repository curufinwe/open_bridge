from enum import Enum
import functools as fun
from math import *
import random
import sys

from event    import ShipDestroyedEvent
from modules  import *
from protocol import *
from util     import *

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
                    'dx'            : lambda client, obj: round(obj.calc_speed_x(), 5)    ,
                    'dy'            : lambda client, obj: round(obj.calc_speed_y(), 5)      }

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

  module_update_order = ('bridge', 'rmc', 'smc', 'reactor', 'energy_bank', 'weapon', 'engine', 'shield')

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
    self.desired_accel_dir =  0.0
    self.desired_rot_accel =  0.0

    self.max_speed         = 10.0
    self.max_rot           =  0.02
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

  def do_shield_damage(self, damage, direction):
    for shield in self.modules['shield']:
      if shield.state == ShieldState.enabled and angle_diff(direction, shield.direction) < shield.arc * 0.5:
        damage = shield.do_damage(damage)
    return max(0.0, damage)

  def do_node_damage(self, damage, direction):
    source_dist = max(hypot(n.x, n.y) for n in self.nodes) + 10.0
    source = (cos(direction) * source_dist, sin(direction) * source_dist)
    sorted_nodes = sorted(self.nodes, key=lambda n: hypot(*sub_vec((n.x, n.y), source)))
    for n in sorted_nodes:
      if n.hp > 0 and random.uniform(0., 1.) < .9:
        n.do_damage(damage)
        break
    else:
      for n in sorted_nodes:
        if n.hp > 0:
          n.do_damage(damage)

  def do_damage(self, damage, direction):
    print('DMG: ', damage)
    remaining_damage = self.do_shield_damage(damage, direction)
    if remaining_damage > 0.0:
      self.do_node_damage(remaining_damage, direction)

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

  def _calc_diff(self, client, state):
    result = {}
    if state is None:
      state = {}

    if 'modules' not in state or type(state['modules']) != dict:
      state['modules'] = {}

    for k in self.modules:
      if k not in state['modules']:
        state['modules'][k] = None
      diff = calc_list_diff(client, self.modules[k], state['modules'][k])
      if diff != DiffOp.IGNORE:
        if 'modules' not in result:
          result['modules'] = {}
        result['modules'][k] = diff

    diff = calc_list_diff(client, self.nodes, state.get('nodes', None))
    if diff != DiffOp.IGNORE:
      result['nodes'] = diff

    return result if len(result) > 0 else DiffOp.IGNORE
