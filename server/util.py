id = 0
def get_id():
  global id
  id += 1
  print('New id: %d' % id)
  return id

class ProtocolError(BaseException):
  def __init__(self, code=3000, reason='protocol error'):
    self.code = code
    self.reason = reason
