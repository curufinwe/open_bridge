class Body

  attr_accessor :sprite, :state_path
  attr_reader :id

  def initialize(game,state,id,info)
    @id = id
    @state = state
    @sprite = game.add.sprite(info["x"],info["y"],info["sprite"])
    @sprite.anchor.setTo(0.5,0.5)
    @state_path = ["world","bodies",@id]
    game.physics.arcade.enable(@sprite)
  end

  def state(*names)
    res = @state.get(@state_path+names)
    return res
  end

  def set_state( path, newval )
    @state.set(@state_path+[*path], newval)
  end
end

class Ship < Body
  def initialize(game,state,id,info)
    super
    @state_path = ["world","ships",@id]
  end

  def pos
    return [ state(:x), state(:y) ]
  end

  def rot
    state :direction
  end

  def update
    @sprite[:x] = state :x
    @sprite[:y] = state :y
    @sprite[:rotation] = state :direction
    @sprite[:body][:velocity][:x] = state :dx
    @sprite[:body][:velocity][:y] = state :dy
  end
end
