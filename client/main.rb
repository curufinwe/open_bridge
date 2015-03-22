# ERB

def get_url_params
  return `window.location.search`.split("&").each.with_object({}) do |param,h|
    key,val =*param.split("=")
    h[key] = val
  end
end

game = nil
gui = nil
state = nil
connect = nil
input = nil
ships = {}

shipinfo = { "sprite" => "ship", "x" => 30, "y" => 30, "dx" => 0, "dy" => 0 }

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
      input.key("turn_left","LEFT")
      input.key("turn_right","RIGHT")
      input.key("accelerate","UP")
      input.key("decelerate","DOWN")
      `game.native.physics.startSystem(Phaser.Physics.ARCADE)`
      connect = Connector.new(get_url_params["host"] || "127.0.0.1")
      state = State.new(connect)
      connect.state = state
      gui.create(input)
}

render = lambda{
  game.debug.cameraInfo(game.camera, 32, 32);
}

update = lambda do

  gui.ship ||= ships["1"] if ships["1"]
  input.on("ship1"){ gui.ship = ships["1"] }
  input.on("ship2"){ gui.ship = ships["2"] }

  state.get(%w{world ships}).each_key do |id|
    ships[id] ||= Ship.new(game, state, id, shipinfo)
    ships[id].update
  end

  gui.update
  state.update
end

game = Native(`new Phaser.Game(800, 600, Phaser.AUTO, '', { preload: preload, create: create, update: update, render: render})`)
gui = HelmInterface.new(game)
