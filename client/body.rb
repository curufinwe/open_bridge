class Body

  attr_accessor :sprite

  def initialize(game,id,info)
    @id = id
    @sprite = game.add.sprite(info["x"],info["y"],info["sprite"])
    @sprite.anchor.setTo(0.5,0.5)
    game.physics.arcade.enable(@sprite)
    #@sprite.body.velocity.x = info["dx"] || 0
    #@sprite.body.velocity.y = info["dy"] || 0
  end
end
