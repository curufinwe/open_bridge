require 'display'

class DegInfo
  attr_accessor :x, :y, :text
  def initialize(x,y, text)
    @x,@y,@text = x,y, text
  end
end

class DirectionDisplay < Display
  def initialize(game,state)
    super
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
