require 'json'

class Connector
    attr_accessor :state

    def send_changes(changes)
      if @changes
        @changes << changes
        return
      end
      @ws.send(JSON.dump(changes))
    end

    def onopen
      @changes.each do |change|
        send_changes(change)
      end
      @changes = nil
    end

    def onmsg(msg)
      data = msg.data
      json = JSON.parse(data)
      @state.apply(json)
    end

    def onclose()
      puts "connection closed"
    end

    def onerror(e="")
      puts "error occured: #{e}"
    end

end

