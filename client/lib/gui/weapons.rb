require 'gui/gui'
require 'gui/cone_display'
require 'gui/beam_display'
require 'gui/weapons_status_display'

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
    @body_display = add_display(BodyDisplay)
  end

  def update
    next unless active? && active_ship
    update_displays
    update_camera
    update_weapons_ui_elements
    enable_clicks_for_targets!
  end

  def activate
    super
  end

  def deactivate
    super
  end

  private

  def enable_clicks_for_targets!
    @state.ids_to_bodies.each_pair do |id,body|
      next unless body.attackable?
      sprite = @body_display.bodies_to_sprites[body]
      sprite.inputEnabled = true
      if !sprite.pixelPerfectClick
        sprite.pixelPerfectClick = true
        sprite.events.onInputDown.add {
          self.clicked_obj(body)
        }
      end
    end
  end

  def clicked_obj(selected_body)
    return unless active?
    set_target(selected_body)
  end


  def update_camera
    @game.camera.view.x = active_ship.x-400
    @game.camera.view.y = active_ship.y-300
    @game.camera[:bounds]=`null`
  end

  def update_weapons_ui_elements
    mx,my = @game.input.activePointer.worldX, @game.input.activePointer.worldY
    @weapons_target.x=mx
    @weapons_target.y=my
    if @selected_body && @selected_body.alive?
      @weapons_selected.visible = true
      sx,sy = @selected_body.x, @selected_body.y
      @weapons_selected.x = sx
      @weapons_selected.y = sy
    else
      @weapons_selected.visible = false
    end
  end


  def set_target(selected_body)
    @selected_body = selected_body
    active_ship.set_state(["modules","weapon","0","target"],selected_body.id)
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

