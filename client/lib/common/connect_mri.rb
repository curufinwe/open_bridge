require_relative './connect.rb'
require 'websocket-client-simple'

class Connector
  def initialize(host)
    @ws = WebSocket::Client::Simple.connect 'ws://localhost:9000'
    ws.on(:message){ |msg| onmsg(msg) }
    ws.on(:open){ onopen }
    ws.on(:close){ onclose }
    ws.on(:error){ onerror }
  end
end
