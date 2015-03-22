class Input
  def initialize(game)
    @game = game
    @config = {}
    on_key = lambda{ |evnt| self.trigger_event( Native(evnt) ) }
    @game.input.keyboard.addCallbacks(nil, on_key, on_key, on_key)
    @events_toggled = {}
  end

  def get(key)
    keycode = @config[key]
    return @game[:input][:keyboard].isDown(keycode)
  end

  def on(name,&block)
    keycode = @config[name]
    @events_toggled[keycode] ||= Set.new
    @events_toggled[keycode] << block
  end

  def trigger_event(evt)
    type = evt[:type] == "keydown" ? :down : :up
    @events_toggled.each_pair do |key,blocks| 
      next unless key == evt[:keyCode]
      blocks.each{|block| block.call(type,evt)}
    end
  end

  def key(name,keycode)
    raise "thats not a valid name #{name} for an input" unless name
    @config[name] = Native(`Phaser.Keyboard[keycode]`)
  end

end
