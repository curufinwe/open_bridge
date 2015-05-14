require 'gui/gui'
require 'gui/shield'

class ShieldDisplay < Gui

  def create
    @ships_to_shields = JShash.new
  end

  def update
    update_available_ships
  end

  def activate
    update_available_ships
  end

  def deactivate
    destroy
  end

  private 

  def update_available_ships
    remove_unused_ships!
    add_new_ships!
    @ships_to_shields.each_pair do |ship,_|
      remove_unused_shields!(ship)
      add_new_shields!(ship)
      update_available_shields!(ship)
    end
  end

  def update_shields!(ship)
    @ships_to_shields.each_pair do |ship, ids_to_shields|
      ids_to_shields.values.each do |shield| 
        shield.update
      end
    end
  end

  def add_new_shields!(ship)
    ship.shields.each_key do |sid|
      if !@ships_to_shields[ship].include? sid
        shield = Shield.new(@game,ship,sid)
        @ships_to_shields[ship][sid]=shield
      end
    end
  end

  def add_new_ships!
    @state.ships.each do |ship|
      @ships_to_shields[ship] ||= {}
    end
  end


  def remove_unused_shields!(ship)
    @ships_to_shields[ship].keys.each do |shield_id|
      if !ship.shields.include? shield_id
        @ships_to_shields[ship][shield_id].destroy
        @ships_to_shields[ship].delete shield_id
      end
    end
  end


  def remove_unused_ships!
    state_ships = Set.new(@state.ships)
    @ships_to_shields.keys.each do |ship|
      if !state_ships.include? ship
        @ships_to_shields[ship].each_value{ |shield| shield.destroy }
        @ships_to_shields.delete(ship)
      end
    end
  end

  def update_available_shields!
    @ships_to_shields.each_pair do |ship,sid_to_shield|
      sid_to_shield.each_value do |shield|
        update_shield(ship,shield)
      end
    end
  end

  def update_shield(ship,shield)
    if active_ship == ship
      shield.color = 0x0033ff
      shield.transparency = 0.2
    else
      shield.color = 0xff3300
      shield.transparency = 0.1
    end
    shield.update
    nil
  end

  def destroy
    @ships_to_shields.each_pair do |ship, sid_to_shield|
      sid_to_shield.each_pair do |sid, shield|
        shield.destroy
      end
    end
    @ships_to_shields = {}
  end
end
