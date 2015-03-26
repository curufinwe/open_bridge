def log(x)
  `console.log(x)`
end

class Numeric
  def seconds
    return self * 1000.0
  end

  def milliseconds
    return self
  end

  def minutes
    return 60 * 1000.0 * self
  end
end

def after(time, &block) 
  `setTimeout(block, time)`
end
