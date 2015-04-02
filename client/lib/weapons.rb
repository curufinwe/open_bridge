require 'cone_display'
require 'beam_display'

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


  def update_camera
    @game.camera.view.x = ship.sprite.x-400
    @game.camera.view.y = ship.sprite.y-300
    @game.camera[:bounds]=`null`
  end

  def update_weapons_ui_elements
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

  def update
    enable_clicks_for_targets!
    next unless ship
    update_camera
    update_weapons_ui_elements

    @cones.update
    @beams.ship = ship
    @beams.update
    @weapons_status.ship = ship
    @weapons_status.update
  end

  def set_target(selected_ship)
    @selected_ship = selected_ship
    ship.set_state(["modules","weapon","0","target"],selected_ship.id)
    ship.set_state(["modules","weapon","0","state"],"firing")
  end

  def create_weapons_ui_elements
    @weapons_target = @game.add.sprite(0,0,"weapons_target")
    @weapons_target.anchor.setTo(0.5,0.5)
    @weapons_selected = @game.add.sprite(0,0,"weapons_selected")
    @weapons_selected.anchor.setTo(0.5,0.5)
  end

  def create(input,state)
    @input = input
    @state = state
    create_weapons_ui_elements
    @cones = ConeDisplay.new(@game, @state)
    @weapons_status = WeaponsStatusDisplay.new(@game,@state)
    @beams = BeamDisplay.new(@game,@state)
  end

end

