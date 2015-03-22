class State

  def initial_state
    {
      "world"=>{"ships"=>{}}
    }
  end

  def authoritive
    @authoritive_state
  end

  def state
    @proposed_state
  end

  def initialize(connection)
    @authoritive_state = initial_state
    @proposed_state = @authoritive_state.deep_copy
    @last_proposed_state = @proposed_state.deep_copy
    @connection = connection
    @blocks = []
    `document.gamestate = self`
  end

  def update
    changes, changed = @last_proposed_state.diff(@proposed_state)
    return if not changed
    @last_proposed_state = @proposed_state
    @proposed_state = @proposed_state.deep_copy
    @connection.send_changes(changes)
  end

  def apply(patch)
    changes, changed = @last_proposed_state.diff(@proposed_state)
    @connection.send_changes(changes) if changed
    @proposed_state.apply(patch)
    @authoritive_state = @proposed_state.deep_copy
    @last_proposed_state = @proposed_state
    puts @authoritive_state.inspect if $DEBUG
    @proposed_state = @proposed_state.deep_copy
    @blocks.each(&:call)
  end

  def get_from_state(state,path)
    curr = state
    path.each do |key|
      return nil unless curr.is_a? Hash
      curr = curr[key]
    end
    return curr
  end

  def get(args)
    get_from_state(@authoritive_state,args)
  end

  def set(args, value)
    path = args[0...-1]
    key = args[-1]

    curr = @proposed_state
    path.each do |path_key|
      return nil unless curr.is_a? Hash
      curr[path_key] = {} unless curr.include? path_key
      curr = curr[path_key]
    end
    return curr[key] = value
  end

  def on_server_update(&block)
    @blocks << block
  end
end

class Hash
  def diff(new_hash)
    res = {}
    return [nil, true] unless new_hash

    self.each_key do |key|
      newval, changed = self[key].diff(new_hash[key])
      res[key] = newval if changed
    end

    (new_hash.keys - self.keys).each do |key|
      res[key] = new_hash[key]
    end
    return [res, res.size > 0]
  end

  def apply(patch)
    patch.each_key do |key|
      if self[key]
        self[key] = self[key].apply(patch[key])
      else
        self[key] = patch[key]
      end
      self.delete(key) if self[key] == nil
    end
    return self
  end

  def deep_copy
    return self.each_pair.with_object({}){|(key,val),obj| obj[key] = val.deep_copy}
  end
end

class String 
  def diff(new_string)
    return [new_string,true] if self != new_string
    return [nil,false]
  end

  def apply(patch)
    return patch
  end

  def deep_copy
    return dup
  end
end

class Numeric
  def diff(new_num)
    return  [new_num,true] if self != new_num
    return  [nil,false]
  end

  def apply(patch)
    return patch
  end

  def deep_copy
    return self
  end
end

class Symbol
  def diff(new_sym)
    return [new_sym,true] if self != new_sym
    return [nil,false]
  end

  def apply(patch)
    return patch
  end

  def deep_copy
    return self
  end
end
