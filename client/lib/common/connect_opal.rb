require_relative 'connect.rb'

class Connector
  def initialize(host)
    @changes = []
    url = "ws://#{host}:9000"
    @ws = Native(`new WebSocket(url)`)
    @ws.onopen = ->{ onopen }
    @ws.onmessage = lambda{|msg| onmsg(Native(msg)) }
    @ws.onclose = -> { onclose; }
    @ws.onerror = ->{ onerror }
  end
end
