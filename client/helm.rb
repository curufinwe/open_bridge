class HelmInterface
  attr_accessor :state, :ship

  def initialize(game)
    @game = game
  end

  def preload
    @game.load.image("helm_nav","assets/helm_nav.png")
  end

  def update
    next unless ship
    @game.camera.view.x = ship.sprite.x-400
    @game.camera.view.y = ship.sprite.y-300
    @helm_nav.x = ship.sprite.x
    @helm_nav.y = ship.sprite.y
    @helm_nav[:rotation] = ship.sprite[:rotation]+`Math.PI`
  end

  def create(input)
    @input = input
    @input.on("turn_left"){ |mode,_| if mode == :up then @ship.set_state :throttle_rot, 0 else @ship.set_state :throttle_rot, -1 end }
    @input.on("turn_right"){|mode,_| if mode == :up then @ship.set_state :throttle_rot, 0 else @ship.set_state :throttle_rot, 1 end }
    @input.on("accelerate"){|mode,_| if mode == :up then @ship.set_state :throttle_accel, 0 else @ship.set_state :throttle_accel, 1 end }
    @input.on("decelerate"){|mode,_| if mode == :up then @ship.set_state :throttle_accel, 0 else @ship.set_state :throttle_accel, -1 end }
    @helm_nav = @game.add.sprite(0,0,"helm_nav")
    @helm_nav.anchor.setTo(0.5,0.5)
  end

end
