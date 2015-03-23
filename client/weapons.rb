class WeaponsInterface
  attr_accessor :state, :ship

  def initialize(game)
    @game = game
  end

  def preload
    @game.load.image("weapons_target","assets/weapons_target.png")
    @game.load.image("weapons_selected","assets/weapons_selected.png")
  end

  def enable_clicks_for_targets!
    @state.ids_to_ships.each_pair do |id,other_ship|
      other_ship.sprite.inputEnabled = true
      if !other_ship.sprite.pixelPerfectClick
        other_ship.sprite.pixelPerfectClick = true
        other_ship.sprite.events.onInputDown.add {
          self.clicked_obj(other_ship)
        }
      end
    end
  end

  def clicked_obj(selected_ship)
    set_target(selected_ship)
  end

  def update
    enable_clicks_for_targets!

    next unless ship
    @game.camera.view.x = ship.sprite.x-400
    @game.camera.view.y = ship.sprite.y-300
    @game.camera[:bounds]=`null`
    @weapons_cone.pos =[ship.sprite.x, ship.sprite.y]
    @weapons_cone.dir = @ship.state :direction
    @weapons_cone.update

    mx,my = @game.input.activePointer.worldX, @game.input.activePointer.worldY
    @weapons_target.x=mx
    @weapons_target.y=my
    if @selected_ship
      @weapons_selected.visible = true
      sx,sy = @selected_ship.sprite.x, @selected_ship.sprite.y
      @weapons_selected.x = sx
      @weapons_selected.y = sy
    else
      @weapons_selected.visible = false
    end
  end

  def set_target(selected_ship)
    @selected_ship = selected_ship
    ship.set_state(["modules","weapon","0","target"],selected_ship.id)
  end

  def create(input,state)
    @input = input
    @state = state
    @weapons_target = @game.add.sprite(0,0,"weapons_target")
    @weapons_target.anchor.setTo(0.5,0.5)
    @weapons_selected = @game.add.sprite(0,0,"weapons_selected")
    @weapons_selected.anchor.setTo(0.5,0.5)
    @weapons_cone = Cone.new(@game)
  end

end

