class Body

  attr_accessor :state_path
  attr_reader :id

  def initialize(state,id)
    @id = id
    @state = state
    @state_path = ["world","bodies",@id]
    @alive = true
  end

  def create_sprite(game,spritename)
    sprite = game.add.sprite(self.x,self.y, spritename)
    sprite.anchor.setTo(0.5,0.5)
    game.physics.arcade.enable(sprite)
    return sprite
  end

  def state(names)
    res = @state.get(@state_path+names)
    return res
  end

  def set_state( path, newval )
    @state.set(@state_path+[*path], newval)
  end

  def attackable?
    return false
  end

  def destroy
    @id = nil
    @state = nil
    @state_path = nil
    @alive = false
  end

  def x; state ["x"]; end
  def y; state ["y"]; end

  def alive?
    return @alive
  end
end

class Ship < Body
  def initialize(state,id)
    super
    @state_path = ["world","ships",@id]
  end

  def pos
    return [ self.x, self.y ]
  end

  def rot
    state ["direction"]
  end

  def weapons
    state ["modules", "weapon"]
  end

  def shields
    state ["modules", "shield"]
  end

  def update_sprite(sprite)
    sprite[:x] = self.x
    sprite[:y] = self.y
    sprite[:rotation] = state ["direction"]
    sprite[:body][:velocity][:x] = state ["dx"]
    sprite[:body][:velocity][:y] = state ["dy"]
  end

  def attackable?
    return true
  end
end
