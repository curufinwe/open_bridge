require 'gui'
require 'direction_display'
require 'cone_display'
require 'beam_display'
require 'body_display'

class HelmInterface < Gui
  
  def create()
    @keyboard_throttle_rot = 0;
    @keyboard_throttle_speed = 0;
    setup_keyboard_hooks
    create_helm_ui_elements
    add_display(ConeDisplay)
    add_display(BeamDisplay)
    add_display(DirectionDisplay)
    add_display(BodyDisplay)
  end

  def self.preload(game)
    game.load.image("helm_nav","assets/helm_nav.png")
    game.load.image("helm_target","assets/helm_target.png")
  end

  def update
    next unless active_ship
    update_camera
    update_helm_ui_elements
    update_displays
    calc_and_set_throttle!
  end

  private

  def update_camera
    @game.camera.view.x = active_ship.pos[0]-400
    @game.camera.view.y = active_ship.pos[1]-300
    @game.camera[:bounds]=`null`
  end

  def update_helm_ui_elements
    @helm_nav[:rotation] = active_ship.rot+JSMath::PI
  end


  def calc_and_set_throttle!
    rot,sp = calc_keyboard_throttle
    mp_rot,mp_sp = calc_mouse_pull_throttle
    sp,rot = mp_sp,mp_rot if @game.input.activePointer.isDown
    active_ship.set_state(:throttle_speed, sp)
    active_ship.set_state(:throttle_rot, rot)
  end


  def calc_mouse_pull_throttle
      @helm_target.visible = @game.input.activePointer.isDown
      mx,my = @game.input.activePointer.worldX, @game.input.activePointer.worldY
      sx, sy = active_ship.state(:x), active_ship.state(:y)
      @helm_target.x=mx
      @helm_target.y=my
      dirx, diry = mx-sx, my-sy
      angle = JSMath.atan2(dirx,diry)*JSMath::RadToDeg
      shipa = active_ship.state(:direction)*JSMath::RadToDeg
      adiff = angle-shipa
      adiff = JSMath.clamp_angle180(adiff)
      throttle_rot = (JSMath.clamp(-90, adiff, 90) / 90.0)
      lenSQ = dirx**2 + diry**2
      throttle_speed = 0
      if lenSQ > 1 
        len = JSMath.sqrt(lenSQ)
        throttle_speed =  (JSMath.clamp(50, len, 200)-50) / 150.0
      end
      return throttle_rot, throttle_speed
  end

  def calc_keyboard_throttle
    return @keyboard_throttle_rot, @keyboard_throttle_speed
  end

  def setup_keyboard_hooks
    @input.on("turn_left"){ |mode,_| if mode == :up then @keyboard_throttle_rot = 0 else @keyboard_throttle_rot = -1 end }
    @input.on("turn_right"){|mode,_| if mode == :up then @keyboard_throttle_rot = 0 else @keyboard_throttle_rot = 1 end }
    @input.on("accelerate"){|mode,_| if mode == :up then @keyboard_throttle_speed = 0 else @keyboard_throttle_speed = 1 end }
    @input.on("decelerate"){|mode,_| if mode == :up then @keyboard_throttle_speed = 0 else @keyboard_throttle_speed = -1 end }
  end

  def create_helm_ui_elements
    @helm_nav = @game.add.sprite(0,0,"helm_nav")
    @helm_nav.anchor.setTo(0.5,0.5)
    @helm_nav.fixedToCamera = true;
    @helm_nav.cameraOffset.setTo(400, 300);
    add_sprite(@helm_nav)

    @helm_target = @game.add.sprite(0,0,"helm_target")
    @helm_target.anchor.setTo(0.5,0.5)
    add_sprite(@helm_target)
  end


end

