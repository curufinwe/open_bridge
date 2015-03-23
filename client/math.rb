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

  def self.sin(x)
    return `Math.sin(x)`
  end

  def self.cos(x)
    return `Math.cos(x)`
  end

  # in radians
  def self.dir(angle, len = 1)
    x = cos(angle)*len
    y = sin(angle)*len
    return x,y
  end

  def self.clamp_angle180(angle)
      angle = angle % 360
      angle += 360 if angle < 0
      angle -= 360 if angle > 180
      return angle
  end

  def self.clamp_angle360(angle)
      angle = angle % 360
      angle += 360 if angle < 0
      return angle
  end
end
