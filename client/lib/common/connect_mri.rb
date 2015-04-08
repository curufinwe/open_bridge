require_relative './connect.rb'
require 'websocket-client-simple'

class Connector
  def initialize(host="localhost")
    @changes = []
    @ws = WebSocket::Client::Simple.connect("ws://#{host}:9000")
    this = self
    @ws.on(:message){ |msg| this.onmsg(msg) }
    @ws.on(:open){this.onopen }
    @ws.on(:close){ this.onclose }
    @ws.on(:error){ |e| this.onerror(e) }
  end
end
