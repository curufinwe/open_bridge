require_relative './connect.rb'
require 'websocket-client-simple'

class Connector
  attr_accessor :ws
  def initialize(state,host="localhost")
    @state = state
    @changes = []
    @ws = WebSocket::Client::Simple.connect("ws://#{host}:9000")
    this = self
    @ws.on(:open){ puts "open"; this.onopen }
    @ws.on(:close){ puts "close"; this.onclose }
    @ws.on(:error){ |e| puts "error"; this.onerror(e) }
    @ws.on(:message){ |msg| puts "fnord"; this.onmsg(msg) }
  end
end
