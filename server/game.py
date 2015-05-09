import asyncio
import json
import math
import time

from autobahn.asyncio.websocket import WebSocketServerProtocol

from protocol import ProtocolError, calc_dict_diff, clean_diff, apply_trusted_diff
from world import World

def timestamp():
  epoch = time.time()
  return '%s.%.3d' % (time.strftime('%H:%M:%S', time.localtime(epoch)),
                      int(math.fmod(epoch, 1) * 1000)                       )

class GameClient(WebSocketServerProtocol):
  next_prefix = 0

  def __init__(self):
    self.game_state = { 'world': None, 'events': None, 'prefix': None }
    self.prefix = 'c%d.' % GameClient.next_prefix
    GameClient.next_prefix += 1

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
    self.debug = False
    self.ticks_per_second = 20.0
    self.ticks = 0
    self.time  = 0.0
    self.update_time = 0.0

  def run(self):
    loop = asyncio.get_event_loop()
    loop.call_soon(self.update)

  def handle_event(self, evt):
    self.events.append(evt)

  def update(self):
    start = time.clock()

    self.world.update()

    end_update = time.clock()  

    for client in self.clients:
      diff = { 'world' : self.world.calc_diff(client, client.game_state['world']),
               'events': calc_dict_diff(client, dict(enumerate(self.events)), client.game_state['events']),
             }
      if client.game_state['prefix'] is None:
        diff['prefix'] = client.prefix
      apply_trusted_diff(client.game_state, diff)
      clean_diff(diff)
      msg = json.dumps(diff)
      if self.debug and len(diff) > 0:
        print('[%s] To  : %s' % (timestamp(), msg))
      client.sendMessage(msg.encode('utf-8'))
    if len(self.events) > 0:
      self.events = []

    end = time.clock()

    if self.debug:
      self.time        += (end - start)
      self.update_time += (end_update - start)
      self.ticks       += 1
      if self.ticks % 40 == 0:
        print("Update: %.2f ms" % (1000 * self.update_time / self.ticks))
        print("Total : %.2f ms" % (1000 * self.time / self.ticks))
        self.time        = 0
        self.update_time = 0
        self.ticks       = 0
    loop = asyncio.get_event_loop()
    loop.call_later(max(0.0, 1.0/self.ticks_per_second - (end - start)), self.update)

  def apply_diff(self, diff):
    for key in diff:
      if key == 'world':
        self.world.apply_diff(diff['world'])
      else:
        raise ProtocolError(reason='Unknown key "%s" in root' % key)
    
