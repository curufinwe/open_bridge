class Bar
  attr_accessor :pos, :width, :height, :percentage, :full_color, :empty_color
  def initialize(game, pos, width, height, full_color, empty_color)
    @pos = pos
    @width = width
    @height = height
    @game  = game
    @percentage = 1
    @full_color = full_color
    @empty_color = empty_color
    @graphics = game.add.graphics(0,0)
    @graphics.fixedToCamera = true;
    @graphics.cameraOffset.setTo(0, 0);
  end

  def percentage= (val)
    @percentage = val
  end

  def update
    x,y = *@pos
    h = height * @percentage
    @graphics.clear
    @graphics.beginFill(@full_color)
    @graphics.fillAlpha = 0.5
    @graphics.lineStyle(1, 0xffff00, 0.2)
    @graphics.moveTo(x,y)
    @graphics.lineTo(x+width,y)
    @graphics.lineTo(x+width,y+h)
    @graphics.lineTo(x,y+h)
    @graphics.lineTo(x,y)
    @graphics.endFill()
    y += h
    h = height-h
    @graphics.beginFill(@empty_color)
    @graphics.fillAlpha = 0.5
    @graphics.lineStyle(1, 0xffff00, 0.2)
    @graphics.moveTo(x,y)
    @graphics.lineTo(x+width,y)
    @graphics.lineTo(x+width,y+h)
    @graphics.lineTo(x,y+h)
    @graphics.lineTo(x,y)
    @graphics.endFill()
  end

  def destroy
    @graphics.destroy
    @graphics = nil
  end
end
