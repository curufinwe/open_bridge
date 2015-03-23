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
    @state.ids_to_ships.each_pair do |id,ship|
      ship.sprite.inputEnabled = true
      if !ship.sprite.pixelPerfectClick
        ship.sprite.pixelPerfectClick = true
        ship.sprite.events.onInputDown.add {
          self.clicked_obj(ship)
        }
      end
    end
  end

  def clicked_obj(ship)
    @selected_ship = ship
  end

  def update
    enable_clicks_for_targets!

    next unless ship
    @game.camera.view.x = ship.sprite.x-400
    @game.camera.view.y = ship.sprite.y-300
    @game.camera[:bounds]=`null`

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

  def create(input,state)
    @input = input
    @state = state
    @weapons_target = @game.add.sprite(0,0,"weapons_target")
    @weapons_target.anchor.setTo(0.5,0.5)
    @weapons_selected = @game.add.sprite(0,0,"weapons_selected")
    @weapons_selected.anchor.setTo(0.5,0.5)
  end

end

