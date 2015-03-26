import functools as ft

class ProtocolError(BaseException):
  def __init__(self, code=3000, reason='protocol error'):
    self.code = code
    self.reason = reason

def compose(*functions):
  return ft.reduce(lambda f, g: lambda x: f(g(x)), functions)

def compose2(*functions):
  return ft.reduce(lambda f, g: lambda x, y: f(*g(x, y)), functions)

def to_int(val, error='Expected int, got "%s"'):
  try:
    return int(val)
  except ValueError:
    raise ProtocolError(error % val)

def convert_to(ctor, error='Expected int, got "%s"'):
  def convert(obj, val):
    try:
      return (obj, ctor(val))
    except ValueError:
      raise ProtocolError(error % val)
  return convert

def ensure_dict(val, error='Expected object, got "%s"'):
  if type(val) != dict:
    raise ProtocolError(error % val)

def get_attr(attr):
  return lambda obj: getattr(obj, attr)

def set_attr(attr):
  return lambda obj, val: setattr(obj, attr, val)

def limited_precision_float(attr, precision):
  return lambda obj: round(getattr(obj, attr), precision)

def walk_classes(obj):
  visited = set()
  def walk(cls):
    if cls not in visited:
      visited.add(cls)
      yield cls
      for base in cls.__bases__:
        yield from walk(base)
  yield from walk(obj.__class__)

def serialize_attr(obj):
  result = {}
  for cls in walk_classes(obj):
    if hasattr(cls, 'readable_attr'):
      for k, v in cls.readable_attr.items():
        result[k] = v(obj)
    if hasattr(cls, '_serialize'):
      result.update(cls.serialize(obj))
  return result

def apply_diff(obj, diff):
  consumed = set()
  for cls in walk_classes(obj):
    if hasattr(cls, 'writable_attr'):
      for k, v in cls.writable_attr.items():
        if k in diff:
          v(obj, diff[k])
    if hasattr(cls, '_apply_diff'):
      consumed = consumed.union(cls.apply_diff(obj, diff))
  unconsumed_keys = set(diff.keys()).difference(consumed)
  if len(unconsumed_keys) > 0:
    raise ProtocolError(error='Unconsumed keys: %s' % str(unconsumed_keys))
  return consumed


class Serializable():
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
        except KeyError:
          raise ProtocolError(reason='Invalid key for field %s ("%s")' % (key, diff[key]))
        else:
          setattr(self, key, val)
    for key in keys_to_del:
      del diff[key]

  def serialize(self):
    return serialize_attr(self)

def calc_diff(prev, now):
  if type(prev) != type(now):
    return now

  if type(now) == dict:
    res = {}
    for k in now:
      if k not in prev:
        res[k] = now[k]
      else:
        diff = calc_diff(prev[k], now[k])
        if type(diff) != dict or len(diff) > 0:
          res[k] = diff
    for k in prev:
      if k not in now:
        res[k] = None
    return res
  else:
    return now if prev != now else {}
