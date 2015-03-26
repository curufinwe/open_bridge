import math

id = 0
def get_id():
  global id
  id += 1
  return id

DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi

def deg2rad(a):
  return a * DEG2RAD

def rad2deg(r):
  return r * RAD2DEG
