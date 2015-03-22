from math import sin, cos

def add_vec(a, b):
  return (a[0] + b[0], a[1] + b[1])

def sub_vec(a, b):
  return (a[0] - b[0], a[1] - b[1])

def mul_vec(v, s):
  return (v[0] * s, v[1] * s)

def div_vec(v, s):
  return (v[0] / s, v[1] / s)

def to_vec(dir, mag):
  x = cos(dir)
  y = sin(dir)
  return (mag * x, mag * y)
