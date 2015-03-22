class HelmInterface
  attr_accessor :state, :ship

  def initialize(game,input)
    @game = game
  end

  def preload
  end

  def update
    next unless ship
    @game.camera.view.x = ship.sprite.x-400
    @game.camera.view.y = ship.sprite.y-300
  end

  def create(input)
    @input = input
    @input.on("turn_left"){ |mode,_| if mode == :up then @ship.set_state :throttle_rot, 0 else @ship.set_state :throttle_rot, -1 end }
    @input.on("turn_right"){|mode,_| if mode == :up then @ship.set_state :throttle_rot, 0 else @ship.set_state :throttle_rot, 1 end }
    @input.on("accelerate"){|mode,_| if mode == :up then @ship.set_state :throttle_accel, 0 else @ship.set_state :throttle_accel, 1 end }
    @input.on("decelerate"){|mode,_| if mode == :up then @ship.set_state :throttle_accel, 0 else @ship.set_state :throttle_accel, -1 end }
  end

end
