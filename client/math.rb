module Math
  PI = `Math.PI`
  RadToDeg = `180/Math.PI`
  DegToRad = `Math.PI/180`

  def self.atan2(x,y)
    return `Math.atan2(y,x)`
  end

  def self.clamp(lower, x, upper)
    return [[lower,x].max,upper].min
  end

  def self.sqrt(v)
    return `Math.sqrt(v)`
  end
end
