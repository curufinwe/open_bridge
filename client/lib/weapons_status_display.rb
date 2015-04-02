class WeaponsStatusDisplay
  attr_accessor :ship
  def initialize(game)
    @last_ship = nil
    @game = game
    @weapon_bars = {}
  end

  def update
    update_ship if @last_ship != @ship
    update_bars
  end

  def update_bars
    @weapon_bars.each_pair do |id,bar|
      status = ship.state("modules","weapon",id)
      bar.percentage = status["energy"]/status["max_energy"]
      bar.update
    end
  end

  def update_ship
    @last_ship = ship
    @weapon_bars.each_value(&:destroy)
    @weapon_bars = {} 
    bar_pos =[40,40]
    ship.state("modules","weapon").each_pair do |weap_id, weapon|
      bar_pos[0]+30
      bar = @weapon_bars[weap_id] = Bar.new(@game, bar_pos, 10, 50, 0x00ff00, 0xff0000)
    end
  end
end
