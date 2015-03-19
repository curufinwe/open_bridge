#!/usr/bin/env python3

import asyncio

from autobahn.asyncio.websocket import WebSocketServerFactory

from game import Game, GameClient
from config import init_game

if __name__ == '__main__':
  game = Game()
  init_game(game)
  game.run()

  factory = WebSocketServerFactory("ws://0.0.0.0:9000", debug=False)
  factory.protocol = GameClient
  factory.game = game
  loop = asyncio.get_event_loop()
  coro = loop.create_server(factory, '0.0.0.0', 9000)
  server = loop.run_until_complete(coro)
  try:
    loop.run_forever()
  except KeyboardInterrupt:
    pass
  finally:
    server.close()
    loop.close()
