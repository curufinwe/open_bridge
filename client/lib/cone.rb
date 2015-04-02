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
    @length = @ship.state("modules","weapon",@weapon_id,"max_range")
    @firing_arc = @ship.state("modules","weapon",@weapon_id,"firing_arc")*JSMath::RadToDeg
    @dir = @ship.rot
    @pos = @ship.pos
  end
  
  def update
    return unless @ship
    update_params
    @graphics.clear
    @graphics.beginFill(@color)
    @graphics.fillAlpha = @transparency
    @graphics.lineStyle(1, 0x000000, 0.2)
    x,y = *pos
    @graphics.moveTo(x,y)
    segments = 6
    (0...segments).each do |i|
      dx,dy = *JSMath.dir(i*(@firing_arc/(segments-1))*JSMath::DegToRad+@dir - (@firing_arc/2)*JSMath::DegToRad, @length)
      @graphics.lineTo(x+dx, y+dy)
    end
    @graphics.lineTo(x,y)
    @graphics.endFill()
  end

  def destroy
    @graphics.destroy
  end

end
