import math

next_id = 0
def get_id():
  global next_id
  result = next_id
  next_id += 1
  return 's%d' % result

DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi

def deg2rad(a):
  return a * DEG2RAD

def rad2deg(r):
  return r * RAD2DEG

def angle_diff(a, b):
  diff = abs(math.fmod(a - b, 2*math.pi))
  if diff > math.pi:
    diff -= math.pi
  return diff

clamp = lambda val, low, high: max(low, min(high, val))

