from enum import Enum
import functools as ft
import operator as op

# -------------------- Getters --------------------

def get_attr(attr):
  return lambda client, obj: getattr(obj, attr)

def limited_precision_float(attr, precision):
  return lambda client, obj: round(getattr(obj, attr), precision)

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
      if k.startswith('insert_'):
        pass
      else:
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

def calc_diff(client, state, obj):
  try:
    all_attr      = obj.__class__._all_readable_attr_
    all_calc_diff = obj.__class__._all_calc_diff_
  except AttributeError:
    all_attr      = dict()
    all_calc_diff = []
    for cls in walk_classes(obj):
      if hasattr(cls, 'readable_attr'):
        all_attr.update(cls.readable_attr)
      if hasattr(cls, '_calc_diff'):
        all_calc_diff.append(cls._calc_diff)
    obj.__class__._all_readable_attr_ = all_attr
    obj.__class__._all_calc_diff_     = all_calc_diff


  result = {}

  if type(state) != dict:
    state = {}

  for attr, func in all_attr.items():
    val = func(client, obj)
    if state.get(attr, None) != val:
      result[attr] = val

  for cd in all_calc_diff:
    diff = cd(obj, client, state)
    if type(diff) == dict and type(result) == dict:
      result.update(diff)
    elif diff != DiffOp.IGNORE:
      result = diff
    
  return result if type(result) != dict or len(result) > 0 else DiffOp.IGNORE

def apply_diff(obj, diff, key=''):
  consumed = set()

  try:
    base_classes = obj.__class__._all_base_classes_
  except AttributeError:
    base_classes = obj.__class__._all_base_classes_ = list(walk_classes(obj))
    
  for cls in base_classes:
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
    return apply_diff(self, diff)

  def calc_diff(self, client, state):
    return calc_diff(client, state, self)

# -------------------- Diff --------------------

class DiffOp(Enum):
  IGNORE = 1
  DELETE = 2

def calc_dict_diff(client, objs, state):
  result = {}
  set_empty_state = False
  if type(state) == dict:
    for k in state:
      if k not in objs:
        result[k] = DiffOp.DELETE
  else:
    set_empty_state = True
    state = {}

  for k, obj in objs.items():
    diff = obj.calc_diff(client, state.get(k, None))
    if diff != DiffOp.IGNORE:
      result[k] = diff

  if len(result) > 0 or set_empty_state:
    return result
  else:
    return DiffOp.IGNORE

def calc_list_diff(client, obj, state):
  result = {}
  l = len(obj)
  set_empty_state = False
  if type(state) == dict:
    for k in state:
      if type(k) != int or k < 0 or k >= l:
        result[k] = DiffOp.DELETE
  else:
    set_empty_state = True
    state = {}

  for k in range(l):
    o = obj[k]
    v = state.get(k, None)
    if hasattr(o, 'calc_diff'):
      diff = o.calc_diff(client, v)
      if diff != DiffOp.IGNORE:
        result[k] = diff
    else:
      if o != v:
        result[k] = o

  if len(result) > 0 or set_empty_state:
    return result
  else:
    return DiffOp.IGNORE

def clean_diff(diff):
  if type(diff) == dict:
    keys_to_del = []
    for k, v in diff.items():
      if v == DiffOp.IGNORE:
        keys_to_del.append(k)
      elif v == DiffOp.DELETE:
        diff[k] = None
      elif type(v) == dict:
        clean_diff(diff[k])

    for k in keys_to_del:
      del diff[k]

def apply_trusted_diff(obj, diff):
  if type(diff) == dict:
    for k, v in diff.items():
      if type(v) == dict:
        if k not in obj or obj[k] is None:
          obj[k] = v
        else:
          apply_trusted_diff(obj[k], v)
      elif v == DiffOp.IGNORE:
        pass
      elif v == DiffOp.DELETE:
        del obj[k]
      else:
        obj[k] = v

