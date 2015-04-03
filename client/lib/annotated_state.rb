class AnotatedState < State
  attr_accessor :ids_to_bodies, :active_ship
  def initialize(*args)
    super(*args)
    @ids_to_bodies = {}
  end

  def update
    super
  end

  def ships
    get(%w{world ships}).each_key.map{|id| @ids_to_bodies[id]}
  end

  def bodies
    Set.new(@ids_to_bodies.values)
  end

  def active_ship
    @active_ship
  end

  def update_objects!()
    update_ships!()
  end

  def update_ships!()
    get(%w{world ships}).each_key do |id|
      @ids_to_bodies[id] ||= Ship.new(self, id)
    end
  end

  def delete_dead_bodies
    dead_body_ids = @ids_to_bodies.delete_if do |id,body|
       still_alive = get(%w{world ships}).include?(id) || get(%w{world bodies}).include?(id)
       body.destroy unless still_alive
       !still_alive
      end
  end

end
