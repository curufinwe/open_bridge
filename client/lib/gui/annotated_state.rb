require 'common/js_hash'
class AnotatedState < State
  attr_accessor :ids_to_bodies, :active_ship

  def initialize(*args)
    super(JShash)
    @ids_to_bodies = @hash_class.new
  end

  def events
    get(["events"])
  end

  def update
    super
  end

  def ships
    ships = get(%w{world ships}, :or_empty)
    res = []
    ships.each_key{|id| res << @ids_to_bodies[id]}
    return res
  end

  def bodies
    Set.new(@ids_to_bodies.values)
  end

  def active_ship
    @active_ship
  end

  def update_objects!()
    update_ships!()
    delete_dead_bodies!
  end

  def update_ships!()
    get(%w{world ships},:or_empty).each_key do |id|
      @ids_to_bodies[id] ||= Ship.new(self, id)
    end
  end

  def delete_dead_bodies!
    @ids_to_bodies.delete_if do |id,body|
      still_alive = get(%w{world ships}, :or_empty).include?(id) || get(%w{world bodies}, :or_empty).include?(id)
      body.destroy unless still_alive #I'm making a note here
      !still_alive
    end
  end

end
