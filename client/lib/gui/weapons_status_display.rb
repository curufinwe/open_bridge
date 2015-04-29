require 'gui/gui'
require 'gui/bar'

class WeaponsStatusDisplay < Gui

  def create
    @last_ship = nil
    @weapon_bars = {}
  end

  def update
    update_ship if @last_ship != active_ship
    update_bars
  end

  def activate
    update_ship if active_ship
  end

  def deactivate
    @weapon_bars.each_value(&:destroy)
    @weapon_bars = {}
    @last_ship = nil
  end

  private

  def update_bars
    @weapon_bars.each_pair do |id,bar|
      status = active_ship.state("modules","weapon",id)
      bar.percentage = status["energy"]/status["max_energy"]
      bar.update
    end
  end

  def update_ship
    @last_ship = active_ship
    @weapon_bars.each_value(&:destroy)
    @weapon_bars = {} 
    bar_pos =[40,40]
    active_ship.state("modules","weapon").each_pair do |weap_id, weapon|
      bar_pos[0]+30
      bar = @weapon_bars[weap_id] = Bar.new(@game, bar_pos, 10, 50, 0x00ff00, 0xff0000)
    end
  end

end
