import asyncio
import json
import math
import time

from autobahn.asyncio.websocket import WebSocketServerProtocol

from protocol import ProtocolError, calc_diff
from world import World

def timestamp():
  epoch = time.time()
  return '%s.%.3d' % (time.strftime('%H:%M:%S', time.localtime(epoch)),
                      int(math.fmod(epoch, 1) * 1000)                       )

class GameClient(WebSocketServerProtocol):
  def __init__(self):
    self.last_state = {}

  def onConnect(self, request):
    print('Client connecting: %s' % str(request.peer))

  def onOpen(self):
    game = self.factory.game
    game.clients.append(self)

  def onMessage(self, payload, is_binary):
    game = self.factory.game
    if not is_binary:
      try:
        msg = payload.decode('utf-8')
        diff = json.loads(msg)
        if game.debug:
          print('[%s] From: %s' % (timestamp(), payload.decode('utf-8')))
      except ValueError:
        self.sendClose(3000, 'read the json spec. please')
      else:
        try:
          game.apply_diff(diff)
        except ProtocolError as e:
          self.sendClose(e.code, e.reason)
    else:
      self.sendClose(3000, 'no binary data please')

  def onClose(self, wasClean, code, reason):
    game = self.factory.game
    idx = game.clients.index(self)
    del game.clients[idx]
    print('WebSocket connection closed: %s' % str(reason))

class Game:
  def __init__(self):
    self.world = World(self)
    self.clients = []
    self.events = []
    self.debug = True
    self.ticks_per_second = 20.0

  def run(self):
    loop = asyncio.get_event_loop()
    loop.call_soon(self.update)

  def handle_event(self, evt):
    self.events.append(evt)

  def update(self):
    start = time.clock()

    self.world.update()
    for client in self.clients:
      new_state = { 'world': self.world.serialize(),
                    'events': dict((idx, evt.serialize()) for idx, evt in enumerate(self.events))
                  }
      diff = calc_diff(client.last_state, new_state)
      msg = json.dumps(diff)
      if self.debug and len(diff) > 0:
        print('[%s] To   : %s' % (timestamp(), msg))
      client.sendMessage(msg.encode('utf-8'))
      client.last_state = new_state
    if len(self.events) > 0:
      self.events = []

    end = time.clock()

    loop = asyncio.get_event_loop()
    loop.call_later(max(0.0, 1.0/self.ticks_per_second - (end - start)), self.update)

  def apply_diff(self, diff):
    if 'world' in diff:
      self.world.apply_diff(diff['world'])
