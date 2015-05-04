class State

  attr_reader :diff, :authoritative

  def initialize
    @authoritative = {} #the last state confirmed by the server
    @proposed = {} # the changes that have allready been send to the server, but have not yet been confirmed
    @diff = {} #the new changes that have been applied since the last send of a proposed state
  end

  def set(path,val)
    raise "cannot set hashes as values" if val.is_a? Hash
    set_iterative(path,@diff,val)
  end

  def set_authoritative(path,val)
    set_iterative(path,@authoritative,val)
  end


  def get(path, default = nil)
    res = get_and_merge(path, default)
    #puts "#{path.inspect} with default: #{default.inspect}: #{res.inspect}"
    return res
  end

  def inspect
    return [self.class, @authoritative, @proposed, @diff].inspect
  end

  def reset_diff
    @diff = {}
  end

  def reset_proposed
    @proposed = {}
  end

  def promote_diff_to_proposed
    apply_diff_recursive(@proposed,diff)
    @diff = {}
  end

  def apply_patch(diff)
    apply_diff_recursive(@authoritative, diff)
    return nil
  end

  private

  def merge_values(new_ok, new, old_ok, old)
    return old if !new_ok
    return new if !old_ok
    return new if !new.is_a?(Hash) || !old.is_a?(Hash)
    return old.merge(new)
  end

  def get_and_merge(path,default)
    new_ok,new_res = get_iterative(path, @proposed)
    old_ok,old_res = get_iterative(path, @authoritative)
    return merge_values( new_ok,new_res, old_ok,old_res ) if new_ok || old_ok
    return default
  end

  def apply_diff_recursive(root,diff)
    diff.each_pair do |key,val|
      case val
      when Hash then apply_diff_recursive(root[key] ||= {}, val)
      when nil then root.delete key
      else root[key] = delete_nil_values(val)
      end
    end
    return nil
  end

  def delete_nil_values(diff)
    return diff unless diff.is_a? Hash
    diff.delete_if?{|k,v| val==nil}
    diff.each_value{|v| delete_nil_values(v)}
    return diff
  end

  def set_iterative(path,root,val)
    current = root
    path[0...-1].each do |key|
      current[key] ||= {}
      current = current[key]
    end
    current[path.last] = val
  end

  def get_iterative(path,root)
    current = root
    path[0...-1].each do |key|
      raise "getting #{path} in #{root} failed, current should be a hash, but is a #{current.inspect}" unless current.is_a? Hash
      current = current[key]
      return false, nil if !current
    end
    return false, nil if !current.include?(path.last)
    val = current[path.last]
    return true, val if val.is_a? Hash # TODO replace by state_object
    return true, current[path.last]
  end

end
