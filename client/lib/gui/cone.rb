class Cone
  attr_accessor :length, :pos, :color, :transparency, :dir, :firing_arc

  def initialize(game, ship=nil, weapon_id=nil)
    @game = game
    @graphics = game.add.graphics(0,0)
    @color = 0xFF3300
    @transparency = 0.2
    @ship = ship
    @weapon_id = weapon_id
  end

  def set_ship(ship, weapon_id)
    @ship = ship
    @weapon_id = weapon_id
  end

  def update_params
    new_length = @length || @ship.state("modules","weapon",@weapon_id,"max_range")
    new_firing_arc = @firing_arc || @ship.state("modules","weapon",@weapon_id,"firing_arc")*JSMath::RadToDeg
    if new_length != @length || new_firing_arc != @firing_arc
      @needs_redraw = true 
      @length = new_length
      @firing_arc = new_firing_arc
    end
    @dir = @ship.rot
    @pos =  @ship.pos
  end

  def create_cone_graphics
    return unless @needs_redraw
    @needs_redraw = false
    @graphics.clear
    @graphics.beginFill(@color)
    @graphics.fillAlpha = @transparency
    @graphics.lineStyle(1, 0x000000, 0.2)
    x,y = [0,0]
    @graphics.moveTo(x,y)
    segments = 6
    (0...segments).each do |i|
      dx,dy = *JSMath.dir(i*(@firing_arc/(segments-1))*JSMath::DegToRad - (@firing_arc/2)*JSMath::DegToRad, @length)
      @graphics.lineTo(x+dx, y+dy)
    end
    @graphics.lineTo(x,y)
    @graphics.endFill()
  end
  
  def update
    return unless @ship
    update_params
    create_cone_graphics
    `self.graphics.native.x= self.pos[0]`
    `self.graphics.native.y= self.pos[1]`
    `self.graphics.native.rotation = self.dir`
  end

  def destroy
    @graphics.destroy
  end

end
