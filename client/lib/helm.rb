
class DegInfo
  attr_accessor :x, :y, :text
  def initialize(x,y, text)
    @x,@y,@text = x,y, text
  end
end

class HelmInterface
  attr_accessor :state, :ship

  def initialize(game)
    @game = game
    @keyboard_throttle_rot = 0;
    @keyboard_throttle_speed = 0;
  end

  def preload
    @game.load.image("helm_nav","assets/helm_nav.png")
    @game.load.image("helm_target","assets/helm_target.png")
  end

  def update
    next unless ship

    @game.camera.view.x = ship.pos[0]-400
    @game.camera.view.y = ship.pos[1]-300
    @helm_nav[:rotation] = ship.rot+JSMath::PI
    @game.camera[:bounds]=`null`

    @cones.update
    @beams.ship = ship
    @beams.update
    
    rot,sp = calc_keyboard_throttle
    mp_rot,mp_sp = calc_mouse_pull_throttle

    sp,rot = mp_sp,mp_rot if @game.input.activePointer.isDown
    @ship.set_state(:throttle_speed, sp)
    @ship.set_state(:throttle_rot, rot)
  end

  def calc_mouse_pull_throttle
      @helm_target.visible = @game.input.activePointer.isDown
      mx,my = @game.input.activePointer.worldX, @game.input.activePointer.worldY
      sx, sy = ship.sprite.x, ship.sprite.y
      @helm_target.x=mx
      @helm_target.y=my
      dirx, diry = mx-sx, my-sy
      angle = JSMath.atan2(dirx,diry)*JSMath::RadToDeg
      shipa = @ship.sprite[:rotation]*JSMath::RadToDeg
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

  def create(input, state)
    @input = input
    @state = state
    @input.on("turn_left"){ |mode,_| if mode == :up then @keyboard_throttle_rot = 0 else @keyboard_throttle_rot = -1 end }
    @input.on("turn_right"){|mode,_| if mode == :up then @keyboard_throttle_rot = 0 else @keyboard_throttle_rot = 1 end }
    @input.on("accelerate"){|mode,_| if mode == :up then @keyboard_throttle_speed = 0 else @keyboard_throttle_speed = 1 end }
    @input.on("decelerate"){|mode,_| if mode == :up then @keyboard_throttle_speed = 0 else @keyboard_throttle_speed = -1 end }

    @helm_nav = @game.add.sprite(0,0,"helm_nav")
    @helm_nav.anchor.setTo(0.5,0.5)
    @helm_nav.fixedToCamera = true;
    @helm_nav.cameraOffset.setTo(400, 300);

    @helm_target = @game.add.sprite(0,0,"helm_target")
    @helm_target.anchor.setTo(0.5,0.5)

    @cones = ConeDisplay.new(@game, @state)
    @beams = BeamDisplay.new(@game,@state)

    steps = 12
    @deg_indicators = []
    (0...steps).each do |ind|
      deg = ind*(360/steps)
      desc = JSMath.clamp_angle360(deg+90).to_s
      x,y = *JSMath.dir(deg*JSMath::DegToRad,220)
      text = @game.add.text(x,y+2.5, desc, Text::DefaultText);
      text.fixedToCamera = true;
      text.cameraOffset.setTo(400+x, 300+y);
      text.anchor.setTo(0.5,0.5)
      deg = DegInfo.new(x-5, y+5, text)
      @deg_indicators << deg
    end
  end

end

