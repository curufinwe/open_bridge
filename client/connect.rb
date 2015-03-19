
def log(x)
  `console.log(x)`
end

class Connector

  attr_accessor :state

  def initialize(url = "ws://192.168.178.30:9000")
    @changes = []
    @ws = Native(`new WebSocket(url)`)
    @ws.onopen = -> {
      @changes.each do |change|
        send_changes(change)
      end
      @changes = nil
    }
    @ws.onmessage = lambda{|msg| self.onmsg(Native(msg)) }
    @ws.onclose = -> { self.onclose; }
    @ws.onerror = lambda{ self.onerror }
  end

  def send_changes(changes)
    if @changes
      @changes << changes
      return
    end
    log(JSON.dump(changes))
    @ws.send(JSON.dump(changes))
  end

  def onmsg(msg)
    data = msg.data
    json = JSON.parse(data)
    @state.apply(json)
  end

  def onclose()
    puts "connection closed"
  end

  def onerror()
    puts "error occured"
  end

end

