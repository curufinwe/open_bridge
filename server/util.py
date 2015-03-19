id = 0
def get_id():
  global id
  id += 1
  return id

class ProtocolError(BaseException):
  def __init__(self, code=3000, reason='protocol error'):
    self.code = code
    self.reason = reason

def limited_precision_float(precision):
  return lambda x: round(x, precision)
