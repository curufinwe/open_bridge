$DEBUG = false
require 'opal'
require 'native'
require 'set'
require "helpers.rb"
require "jsmath.rb"
require "text.rb"
require "cone.rb"
require "bar.rb"
require "weapons_status_display.rb"
require "input.rb"
require "connect.rb"
require "state.rb"
require "annotated_state.rb"
require "beam.rb"
require "body.rb"
require "weapons.rb"
require "helm.rb"

def get_url_params
  params = `window.location.search`.gsub(/^\?/,"").split("&").each.with_object({}) do |param,h|
    key,val =*param.split("=")
    h[key] = val
  end
  return params
end

game = nil
gui = nil
state = nil
connect = nil
input = nil

preload = lambda{
  game.load.image("bg","assets/iris.png")
  game.load.image("planet","assets/planet.png")
  game.load.image("ship","assets/cruiser.png")
  gui.preload
}

create = lambda{
      game.world.setBounds(-500,-500,1000,1000)
      game.add.sprite(-500, -500, 'bg');
      input = Input.new(game)
      input.key("ship1","ONE")
      input.key("ship2","TWO")
      input.key("ship3","THREE")
      input.key("turn_left","LEFT")
      input.key("turn_right","RIGHT")
      input.key("accelerate","UP")
      input.key("decelerate","DOWN")
      `game.native.physics.startSystem(Phaser.Physics.ARCADE)`
      connect = Connector.new(get_url_params["host"] || "127.0.0.1")
      state = AnotatedState.new(game,connect)
      connect.state = state
      gui.create(input, state)
}

render = lambda{
  game.debug.cameraInfo(game.camera, 32, 32);
}

update = lambda do
  gui.ship ||= state.ids_to_ships["1"] if state.ids_to_ships["1"]
  input.on("ship1"){ gui.ship = state.ids_to_ships["1"] }
  input.on("ship2"){ gui.ship = state.ids_to_ships["2"] }
  input.on("ship3"){ gui.ship = state.ids_to_ships["3"] }

  state.update_objects!
  gui.update
  state.update
end

game = Native(`new Phaser.Game(800, 600, Phaser.AUTO, '', { preload: preload, create: create, update: update, render: render})`)

case get_url_params["station"].downcase
  when "helm" then gui = HelmInterface.new(game)
  when "weapons" then gui = WeaponsInterface.new(game)
  else gui = HelmInterface.new(game)
end
