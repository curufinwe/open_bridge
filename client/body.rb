class Body

  attr_accessor :sprite, :state_path

  def initialize(game,state,id,info)
    @id = id
    @state = state
    @sprite = game.add.sprite(info["x"],info["y"],info["sprite"])
    @sprite.anchor.setTo(0.5,0.5)
    @state_path = ["world","ships",@id]
    game.physics.arcade.enable(@sprite)
  end


  def prop(*names)
    res = names.map{|n| @state.get(@state_path+[n])}
    res = res[0] if names.length == 1
    return res
  end

  def set_prop(name,val)
    @state.set(@state_path+[name], val)
  end
end
