class Cone
  attr_accessor :length, :pos, :color, :transparency, :dir, :spread_angle

  def initialize(game)
    @game = game
    @graphics = game.add.graphics(0,0)
    @length = 200
    @spread_angle = 50
  end
  
  def update
    #@graphics.alpha = 0.2
    @graphics.clear
    @graphics.beginFill(0xFF3300)
    @graphics.fillAlpha = 0.2
    @graphics.lineStyle(1, 0xffd900, 1)
    x,y = *pos
    @graphics.moveTo(x,y)
    segments = 6
    (0...segments).each do |i|
      dx,dy = *Math.dir(i*(@spread_angle/(segments-1))*Math::DegToRad+@dir - (@spread_angle/2)*Math::DegToRad, @length)
      @graphics.lineTo(x+dx, y+dy)
    end
    @graphics.lineTo(x,y)
    @graphics.endFill()
  end

end
