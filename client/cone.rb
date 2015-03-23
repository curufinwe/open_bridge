class Cone
  attr_accessor :length, :pos, :color, :transparency, :dir, :firing_arc

  def initialize(game)
    @game = game
    @graphics = game.add.graphics(0,0)
    @length = 200
    @firing_arc = 50
    @color = 0xFF3300
    @transparency = 0.2
  end
  
  def update
    #@graphics.alpha = 0.2
    @graphics.clear
    @graphics.beginFill(@color)
    @graphics.fillAlpha = @transparency
    @graphics.lineStyle(1, 0x000000, 0.2)
    x,y = *pos
    @graphics.moveTo(x,y)
    segments = 6
    (0...segments).each do |i|
      dx,dy = *Math.dir(i*(@firing_arc/(segments-1))*Math::DegToRad+@dir - (@firing_arc/2)*Math::DegToRad, @length)
      @graphics.lineTo(x+dx, y+dy)
    end
    @graphics.lineTo(x,y)
    @graphics.endFill()
  end

end
