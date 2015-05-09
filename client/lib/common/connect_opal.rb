require_relative 'connect.rb'

class Connector

  def parse(data)
    #return JSON.parse(data)
    return JShash.new.from_json_object_js(`JSON.parse(data)`)
  end

  def initialize(state,host)
    @state = state
    @changes = []
    url = "ws://#{host}:9000"
    @ws = Native(`new WebSocket(url)`)
    @ws.onopen = ->{ onopen }
    @ws.onmessage = lambda{|msg| onmsg(Native(msg)) }
    @ws.onclose = -> { onclose; }
    @ws.onerror = ->{ onerror }
  end
end
