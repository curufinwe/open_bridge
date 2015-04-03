class AnotatedState < State
  attr_accessor :ids_to_ships, :active_ship
  def initialize(*args)
    super(*args)
    @ids_to_ships = {}
  end

  def update
    super
  end

  def ships
    get(%w{world ships}).each_key.map{|id| @ids_to_ships[id]}
  end

  def active_ship
    @active_ship
  end

  def update_objects!()
    shipinfo = { "sprite" => "ship", "x" => 30, "y" => 30, "dx" => 0, "dy" => 0 }
    get(%w{world ships}).each_key do |id|
      @ids_to_ships[id] ||= Ship.new(@game, self, id, shipinfo)
      @ids_to_ships[id].update
    end
  end

end
