class ConeDisplay
  def initialize(game,state)
    @game = game
    @state = state
    @ships_to_weapons = {}
  end

  def update
    update_available_ships
  end

  def update_available_ships
    remove_unused_ships!
    add_new_ships!
    @ships_to_weapons.each_pair do |ship,_|
      remove_unused_weapons!(ship)
      add_new_weapons!(ship)
      update_available_weapons!(ship)
    end
  end

  def update_weapons!(ship)
    @ships_to_weapons.each_pair do |ship, ids_to_cones|
      ids_to_cones.values.each do |cone| 
        cone.update
      end
    end
  end

  def add_new_weapons!(ship)
    ship.weapons.each_key do |wid|
      if !@ships_to_weapons[ship].include? wid
        cone = Cone.new(@game,ship,wid)
        @ships_to_weapons[ship][wid]=cone
      end
    end
  end

  def add_new_ships!
    @state.ships.each do |ship|
      @ships_to_weapons[ship] ||= {}
    end
  end


  def remove_unused_weapons!(ship)
    @ships_to_weapons[ship].keys.each do |weapon_id|
      if !ship.weapons.include? weapon_id
        @ships_to_weapons[ship][weapon_id].destroy
        @ships_to_weapons[ship].delete weapon_id
      end
    end
  end


  def remove_unused_ships!
    state_ships = Set.new(@state.ships)
    @ships_to_weapons.keys.each do |ship|
      if !state_ships.include? ship
        @ships_to_weapons[ship].each_value{ |cone| cone.destroy }
        @ships_to_weapons.delete(ship)
      end
    end
  end

  def update_available_weapons!
    @ships_to_weapons.each_value do |id_to_cone|
      id_to_cone.each_value do |cone|
        cone.update
      end
    end
  end
end
