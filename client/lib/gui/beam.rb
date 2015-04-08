class Beam
  def initialize(game, from_pos, to_pos, color)
    @from = from_pos
    @to = to_pos
    @color = color
    @game = game
    @graphics = game.add.graphics(0,0)
    draw!
    after 0.2.seconds do 
      @graphics.destroy
    end
  end

  def draw!
    @graphics.clear
    @graphics.lineStyle(1, @color , 2)
    x,y = *@from
    @graphics.moveTo(x,y)
    x,y = *@to
    @graphics.lineTo(x,y)
  end
end
