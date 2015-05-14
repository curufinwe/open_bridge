class State

  attr_reader :diff, :authoritative

  def initialize(hash_class = Hash)
    @hash_class = hash_class
    @authoritative = hash_class.new #the last state confirmed by the server
    @proposed = hash_class.new # the changes that have allready been send to the server, but have not yet been confirmed
    @diff = hash_class.new #the new changes that have been applied since the last send of a proposed state
  end

  def set(path,val)
    raise "cannot set hashes as values" if val.is_a? @hash_class
    set_iterative(path,@diff,val)
  end

  def set_authoritative(path,val)
    puts "auth"
    set_iterative(path,@authoritative,val)
  end


  def get(path, default = nil)
    default = @hash_class.new if default == :or_empty
    res = get_and_merge(path, default)
    return res
  end

  def inspect
    return [self.class, @authoritative, @proposed, @diff].inspect
  end

  def reset_diff
    @diff = @hash_class.new
  end

  def reset_proposed
    @proposed = @hash_class.new
  end

  def promote_diff_to_proposed
    apply_diff_recursive(@proposed,diff)
    @diff = @hash_class.new
  end

  def apply_patch(diff)
    apply_diff_recursive(@authoritative, diff)
    return nil
  end

  private

  def merge_values(new_ok, new, old_ok, old)
    return old if !new_ok
    return new if !old_ok
    return new if !new.is_a?(@hash_class) || !old.is_a?(@hash_class)
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
      when @hash_class then apply_diff_recursive(root[key] ||= @hash_class.new, val)
      when nil then root.delete key
      else root[key] = delete_nil_values(val)
      end
    end
    return nil
  end

  def delete_nil_values(diff)
    return diff unless diff.is_a? @hash_class
    diff.delete_if?{|k,v| val==nil}
    diff.each_value{|v| delete_nil_values(v)}
    return diff
  end

  def set_iterative(path,root,val)
    current = root
    path[0...-1].each do |key|
      current[key] ||= @hash_class.new
      current = current[key]
    end
    current[path.last] = val
  end

  def get_iterative(path,root)
    current = root
    if RUBY_ENGINE != "ruby"
    %x{
      for(var i =0; i< path.length-1; i++){
        current = current['$[]'](path[i]);
        if ((($a = current['$!']()) !== nil && (!$a.$$is_boolean || $a == true))) {
          return false
        }
      }
    }
    else
      path[0...-1].each do |key|
        puts "getting #{path} in #{root} failed, current should be a hash, but is a #{current.inspect}" unless current.is_a? @hash_class
        current = current[key]
        return false, nil if !current
      end
    end
    return false, nil if !current.include?(path.last)
    val = current[path.last]
    return true, val if val.is_a? @hash_class # TODO replace by state_object
    return true, current[path.last]
  end

end
