class BeamDisplay
  attr_accessor :ship

  def initialize(game,state)
    @game,@state = game,state
  end

  def create_beam(fromid, toid, color)
    Beam.new(@game, @state.ids_to_ships[fromid].pos, @state.ids_to_ships[toid].pos, color)
  end

  def update
    @state.events.each do |evnt|
      if evnt["type"] == "laser_fired"
        toid = evnt["target"].to_s
        fromid = evnt["source"].to_s
        color = 0xf04000
        color = 0x00f060 if fromid == @ship.id
        create_beam(fromid, toid, color)
      end
    end
  end
end
