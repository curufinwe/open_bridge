require 'gui/gui'

class BeamDisplay < Gui

  def create_beam(fromid, toid, color)
    from = @state.ids_to_bodies[fromid]
    to = @state.ids_to_bodies[toid]
    if !from || !to
      puts "warning created beam on dead object, no beam will be shown"
      return
    end
    Beam.new(@game, from.pos, to.pos , color)
  end

  def update
    @state.events.each do |evnt|
      if evnt["type"] == "laser_fired"
        toid = evnt["target"].to_s
        fromid = evnt["source"].to_s
        color = 0xf04000
        color = 0x00f060 if fromid == active_ship.id
        create_beam(fromid, toid, color)
      end
    end
  end
end
