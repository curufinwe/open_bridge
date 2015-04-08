$DEBUG = false
require 'opal'
require 'native'
require 'set'
require "common/helpers.rb"
require "gui/jsmath.rb"
require "gui/text.rb"
require "gui/cone.rb"
require "gui/bar.rb"
require "gui/weapons_status_display.rb"
require "gui/input.rb"
require "common/connect_opal.rb"
require "common/state.rb"
require "gui/annotated_state.rb"
require "gui/beam.rb"
require "gui/body.rb"
require "gui/weapons.rb"
require "gui/helm.rb"
require 'configs'

def get_url_params
  params = `window.location.search`.gsub(/^\?/,"").split("&").each.with_object({}) do |param,h|
    key,val =*param.split("=")
    h[key] = val
  end
  return params
end

def select_interface(guis,i)
  gui = guis[i%guis.length]
  guis.select(&:active?).each(&:deactivate)
  gui.activate
  return gui
end

game = nil
guis = []
current_gui = nil
state = nil
connect = nil
input = nil

preload = lambda{
  game.load.image("bg","assets/iris.png")
  game.load.image("planet","assets/planet.png")
  game.load.image("ship","assets/cruiser.png")
  guis.each{|klass| klass.preload(game) }
}

create = lambda{
      game.world.setBounds(-500,-500,1000,1000)
      game.add.sprite(-500, -500, 'bg');
      input = Input.new(game)
      $configs.keymappings.each_pair{ |name, key| input.key(name,key) }
      `game.native.physics.startSystem(Phaser.Physics.ARCADE)`
      connect = Connector.new(get_url_params["host"] || "127.0.0.1")
      state = AnotatedState.new(game,connect)
      connect.state = state
      guis = guis.map{|klass| klass.new(game,state,input) }
      current_gui = select_interface(guis,0)
      position_index = 0
      input.on("next_position") do |type| 
        next if type == :up 
        position_index += 1
        current_gui = select_interface(guis, position_index)
      end
}

render = lambda{
  game.debug.cameraInfo(game.camera, 32, 32) if $DEBUG
}

update = lambda do
  state.update_objects!
  state.active_ship = state.ids_to_bodies["1"]
  current_gui.update
  state.update
end

game = Native(`new Phaser.Game(800, 600, Phaser.AUTO, '', { preload: preload, create: create, update: update, render: render})`)

#guis= [WeaponsInterface]
#guis= [HelmInterface]
guis= [HelmInterface,WeaponsInterface]
