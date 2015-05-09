class JShash

  def from_json_object_js(obj)
    @hash = obj
    %x{ 
    for(var index in self.hash) { 
      if (self.hash.hasOwnProperty(index)) {
       var attr = self.hash[index];
       if(typeof attr === "object" && attr !== null){
        self.hash[index] = $scope.get('JShash').$new().$from_json_object_js(attr);
       }
      }
    }
    }
    return self
  end

  def initialize
    @hash = nil
    `self.hash = {}`
  end

  def [](key)
    val = `self.hash[key]`
    return nil if `val === undefined`
    return val
  end

  def []=(key,val)
    `self.hash[key]=val`
  end

  def each_key(&block)
    %x{
    for(var index in self.hash) { 
      if (self.hash.hasOwnProperty(index)) {
       block.$call(index)
      }
    }
    }
    return nil
  end

  def each_value(&block)
    %x{
    for(var index in self.hash) { 
      if (self.hash.hasOwnProperty(index)) {
       block.$call(self.hash[index])
      }
    }
    }
    return nil
  end

  def each_pair(&block)
    %x{ for(var index in self.hash) { 
      if (self.hash.hasOwnProperty(index)) {
       var attr = self.hash[index];
       block.$call(index,attr)
      }
    }
    }
    return nil
  end

  def values
    res = []
    each_value{|v| res << v}
    return res
  end

  def keys
    res = []
    each_key{|v| res << v}
    return res
  end

  def delete_if(&block)
    %x{
    for(var index in self.hash) { 
      if (self.hash.hasOwnProperty(index)) {
       var attr = self.hash[index];
       self.$delete_key_if_block(index, attr, block)
      }
    }
    }
  end

  def delete(key)
    `delete self.hash[key]`
    return nil
  end

  def include?(key)
    return `self.hash.hasOwnProperty(key)`
  end

  def merge(other)
    h = JShash.new
    each_pair{|k,v| h[k] = v}
    other.each_pair{|k,v| h[k] = v}
    return h
  end

  def to_h
    res =  Hash.new
    each_pair do |k,v| 
        v = v.to_h if v.is_a? JShash
        res[k] = v
    end
    return res
  end

  def inspect
    to_h.inspect
  end

  def empty?
    each_key{return true}
    return false
  end

  private
  def delete_key_if_block(key,val, block)
    delete(key) if block.call(key,val)
  end
end
