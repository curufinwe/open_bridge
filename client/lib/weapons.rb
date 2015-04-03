require 'gui'
require 'cone_display'
require 'beam_display'
require 'weapons_status_display'

class WeaponsInterface < Gui

  def self.preload(game)
    game.load.image("weapons_target","assets/weapons_target.png")
    game.load.image("weapons_selected","assets/weapons_selected.png")
  end

  def create()
    create_weapons_ui_elements
    add_display(ConeDisplay)
    add_display(WeaponsStatusDisplay)
    add_display(BeamDisplay)
  end

  def update
    next unless active? && active_ship
    enable_clicks_for_targets!
    update_camera
    update_weapons_ui_elements
    update_displays
  end

  def activate
    super
  end

  def deactivate
    super
  end

  private

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
    @game.camera.view.x = active_ship.sprite.x-400
    @game.camera.view.y = active_ship.sprite.y-300
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


  def set_target(selected_ship)
    @selected_ship = selected_ship
    active_ship.set_state(["modules","weapon","0","target"],selected_ship.id)
    active_ship.set_state(["modules","weapon","0","state"],"firing")
  end

  def create_weapons_ui_elements
    @weapons_target = @game.add.sprite(0,0,"weapons_target")
    @weapons_target.anchor.setTo(0.5,0.5)
    add_sprite(@weapons_target)
    @weapons_selected = @game.add.sprite(0,0,"weapons_selected")
    @weapons_selected.anchor.setTo(0.5,0.5)
    add_sprite(@weapons_selected)
  end

end

