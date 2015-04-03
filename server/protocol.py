import functools as ft
import operator as op

# -------------------- Getters --------------------

def get_attr(attr):
  return lambda obj: getattr(obj, attr)

def limited_precision_float(attr, precision):
  return lambda obj: round(getattr(obj, attr), precision)

# -------------------- Setters --------------------

def get_attr3(name):
  return lambda obj, diff, key: (getattr(obj, name), diff, key)

def set_attr(attr):
  def _set_attr(obj, val, key):
    setattr(obj, attr, val)
    return obj, val, key
  return _set_attr

def to_int(min_val, max_val):
  def _to_int(obj, val, key):
    try:
      val = int(val)
    except ValueError:
      raise ProtocolError('Key "%s" is expected to be an int, but got "%s"' % (key, str(val)))
    if not min_val <= val <= max_val:
      raise ProtocolError('"%s" is not in the allowed range [%d, %d]' % (key, min_val, max_val))
    return (obj, val, key)
  return _to_int

def to_float(min_val, max_val, open_left=False, open_right=False):
  left_bracket  = '('   if open_left  else '['
  right_bracket = ')'   if open_right else ']'
  left_op       = op.lt if open_left  else op.le
  right_op      = op.lt if open_right else op.le
  error_range   = '"%%s" = %%f is not in the allowed range %s%f, %f%s' % (left_bracket, min_val, max_val, right_bracket)

  def _to_float(obj, val, key):
    try:
      val = float(val)
    except ValueError:
      raise ProtocolError('"%s" is expected to be a float, but got "%s"' % val)
    if not (left_op(min_val, val) and right_op(val, max_val)):
      raise ProtocolError(error_range % (key, val))
    return (obj, val, key)

  return _to_float

def to_enum(enum):
  def _to_enum(obj, val, key):
    try:
      val = enum(val)
    except ValueError:
      raise ProtocolError(reason='"%s" is not a valid enum for "%s"' % (val, key))
    return obj, val, key
  return _to_enum

def apply_to_list(name=None, func=None):
  def _apply_to_list(obj, val, key):
    if type(val) != dict:
      raise ProtocolError(reason='"%s" should be an object' % key)
    l = obj if name is None else getattr(obj, name)
    for k, v in val.items():
      try:
        idx = int(k)
      except ValueError:
        raise ProtocolError(reason='"%s" in object "%s" is expected to be an int (list index)' % (k, key))
      if not (0 <= idx < len(l)):
        raise ProtocolError(reason='%d is not a valid list index for "%s", should be in range [0, %d)' % (idx, len(l)))
      sub_key = '%s[%d]' % (key, idx)
      if func is None:
        apply_diff(l[idx], v, sub_key)
      else:
        l[idx] = func(l[idx], v, sub_key)
    return l, val, key
  return _apply_to_list

# -------------------- Higher Order Setters --------------------

def generic_setter(name, setter):
  return [ setter,
           set_attr(name) ]

def float_setter(name, *args, **kwargs):
  return generic_setter(name, to_float(*args, **kwargs))

def int_setter(name, *args, **kwargs):
  return generic_setter(name, to_int(*args, **kwargs))

# -------------------- Exceptions --------------------

class ProtocolError(BaseException):
  def __init__(self, code=3000, reason='protocol error'):
    self.code = code
    self.reason = reason

# -------------------- Serialization --------------------

def walk_classes(obj):
  visited = set()
  def walk(cls):
    if cls not in visited:
      visited.add(cls)
      yield cls
      for base in cls.__bases__:
        yield from walk(base)
  yield from walk(obj.__class__)

def serialize(obj):
  result = {}
  for cls in walk_classes(obj):
    if hasattr(cls, 'readable_attr'):
      for k, v in cls.readable_attr.items():
        result[k] = v(obj)
    if hasattr(cls, '_serialize'):
      result.update(cls.serialize(obj))
  return result

def apply_diff(obj, diff, key=''):
  consumed = set()
  for cls in walk_classes(obj):
    if hasattr(cls, 'writable_attr'):
      for k, v in cls.writable_attr.items():
        if k in diff:
          consumed.add(k)
          val = diff[k]
          if type(v) not in [list, tuple]:
            v = [v]
          k = '%s.%s' % (key, k)
          for func in v:
            obj, val, k = func(obj, val, k)
    if hasattr(cls, '_apply_diff'):
      consumed = consumed.union(cls._apply_diff(obj, diff))
  unconsumed_keys = set(diff.keys()).difference(consumed)
  if len(unconsumed_keys) > 0:
    raise ProtocolError(reason='Unconsumed keys: %s' % str(unconsumed_keys))
  return consumed

class Serializable():
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
    return serialize(self)

  def apply_diff(self, diff):
    return apply_diff(self, diff)

# -------------------- Diff --------------------

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
