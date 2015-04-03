from protocol import get_attr, Serializable

class Event(Serializable):
  event_type = ''
  readable_attr = { 'type': get_attr('event_type') }

class LaserFiredEvent(Event):
  event_type = 'laser_fired'

  readable_attr = { 'source': lambda obj: obj.source.id,
                    'target': lambda obj: obj.target.id,
                    'idx'   : get_attr('idx')
                  }

  def __init__(self, source, target, idx):
    self.source = source
    self.target = target
    self.idx    = idx

class DamageReceivedEvent(Event):
  event_type = 'damage_received'

  readable_attr = { 'ship': lambda obj: obj.node._ship.id,
                    'node': lambda obj: obj.node._index,
                    'dmg' : get_attr('dmg')                }

  def __init__(self, node, dmg):
    self.node = node
    self.dmg  = dmg

class ShipDestroyedEvent(Event):
  event_type = 'ship_destroyed'

  readable_attr = { 'ship': lambda obj: obj.ship.id }

  def __init__(self, ship):
    self.ship = ship

