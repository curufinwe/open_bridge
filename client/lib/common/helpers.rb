$opal_used = true if RUBY_ENGINE == "opal"
def log(x)
  if $opal_used
  `console.log(x)`
  else
    pp x
  end
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
    if $opal_used
      `setTimeout(block, time)`
    else
      raise "after not available outside of gui"
    end
end
