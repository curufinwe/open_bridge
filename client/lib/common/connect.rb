require 'json'

class Connector
    attr_accessor :state

    def send_changes(changes)
      return @changes << changes if @changes
      @ws.send(JSON.dump(changes))
    end

    def onopen
      @changes.each do |change|
        send_changes(change)
      end
      @changes = nil
    end

    def send_state_update
      diff = @state.diff.to_h
      return if !diff.empty?
      send_changes(diff)
      @state.promote_diff_to_proposed
    end

    def parse(msg)
      json = JSON.parse(data)
    end

    def onmsg(msg)
      data = msg.data
      json = parse(data)
      diff = @state.diff.to_h
      @state.reset_diff 
      @state.reset_proposed
      @state.apply_patch(json)
      send_changes(diff) if !diff.empty?
    end

    def onclose()
      puts "connection closed"
    end

    def onerror(e="")
      puts "error occured: #{e}"
    end

end

