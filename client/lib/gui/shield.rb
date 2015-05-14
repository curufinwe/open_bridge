class Shield
  attr_accessor :pos, :color, :transparency, :dir, :firing_arc

  def initialize(game, ship=nil, shield_id=nil)
    @game = game
    @graphics = game.add.graphics(0,0)
    @color = 0xFF3300
    @transparency = 0.2
    @ship = ship
    @shield_id = shield_id
  end

  def set_ship(ship, shield_id)
    @ship = ship
    @shield_id = shield_id
  end

  def update_params
    arc = @arc || @ship.state( ["modules","shield",@shield_id,"arc"] )*JSMath::RadToDeg
    arcdir = @arcdir || @ship.state( ["modules","shield",@shield_id,"direction"] )*JSMath::RadToDeg
    health =  @ship.state( ["modules","shield",@shield_id,"strength"] ) / @ship.state( ["modules","shield",@shield_id,"design_capacity"] )
    if arc != @arc || arcdir != @arcdir || health != @health
      @needs_redraw = true 
      @arc = arc
      @arcdir = arcdir
      @health  = health
    end
    @dir = @ship.rot
    @pos =  @ship.pos
  end

  def create_shield_graphics
    return unless @needs_redraw
    puts "graphics"
    @needs_redraw = false
    @graphics.clear
    #@graphics.beginFill(@color)
    #@graphics.fillAlpha = @transparency
    @graphics.lineStyle(5, 0x0000ff, @health)
    segments = 15
    first = true
    shield_radius = 30
    (0...segments).each do |i|
      dx,dy = *JSMath.dir( @arcdir*JSMath::DegToRad + i*(@arc/(segments-1))*JSMath::DegToRad - (@arc/2)*JSMath::DegToRad, shield_radius )
      if first
        first = false
        @graphics.moveTo(dx, dy)
      else
        @graphics.lineTo(dx, dy)
      end
    end
    #@graphics.endFill()
  end
  
  def update
    return unless @ship
    update_params
    create_shield_graphics
    `self.graphics.native.x= self.pos[0]`
    `self.graphics.native.y= self.pos[1]`
    `self.graphics.native.rotation = self.dir`
  end

  def destroy
    @graphics.destroy
  end

end
