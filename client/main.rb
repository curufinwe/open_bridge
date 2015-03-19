# ERB

game = nil

h = nil

preload = lambda{
  game.load.image("bg","assets/iris.png")
  game.load.image("planet","assets/planet.png")
  game.load.image("ship","assets/cruiser.png")
  h.preload
}

on_press= lambda{|event|
  `console.log(event)`
}

create = lambda{
      h.create
      $game = game
      game.world.setBounds(-500,-500,1000,1000)
      game.add.sprite(-500, -500, 'bg');
      on_down = nil
      on_up = nil
      $cursors = game[:input][:keyboard].createCursorKeys()
      game.input.keyboard.addCallbacks(nil, on_down, on_press, on_up);
      `game.native.physics.startSystem(Phaser.Physics.ARCADE)`
      game = $game
      c = Connector.new
      s = State.new(c)
      $s = s
      c.state = s
}

render = lambda{
  $game.debug.cameraInfo($game.camera, 32, 32);
}

ships = {}
shipinfo = { "sprite" => "ship", "x" => 30, "y" => 30, "dx" => 0, "dy" => 0 }

pressed_ro =false;
pressed_ac =false;
cam_setup = false

update = lambda{

  h.update
  $s.get(%w{world ships}).each_key do |id|
    ships[id] ||= Body.new(game,id,shipinfo)
    ship = ships[id]
    ship.sprite[:x] = $s.get(%w{world ships 1 x})
    ship.sprite[:y] = $s.get(%w{world ships 1 y})
    ship.sprite[:rotation] = $s.get(%w{world ships 1 rotation})
    ship.sprite[:body][:velocity][:x] = $s.get(%w{world ships 1 dx})
    ship.sprite[:body][:velocity][:y] = $s.get(%w{world ships 1 dy})
  end
  
  if ships["1"] 
    ship = ships["1"]
    #game.camera.bounds = nil
    game.camera.view.x = ship.sprite.x-400
    game.camera.view.y = ship.sprite.y-300
    nil
  end
  if $cursors[:right][:isDown]
    pressed_ro = true
    $s.set(%w{world ships 1 throttle_rot},1)
  elsif $cursors[:left][:isDown]
    pressed_ro = true
    $s.set(%w{world ships 1 throttle_rot},-1)
  elsif pressed_ro
    pressed_ro = false
    $s.set(%w{world ships 1 throttle_rot},0)
  end

  if $cursors[:up][:isDown]
    pressed_ac = true
    $s.set(%w{world ships 1 throttle_accel},1)
  elsif $cursors[:down][:isDown]
    pressed_ac = true
    $s.set(%w{world ships 1 throttle_accel},-1)
  elsif pressed_ac
    pressed_ac = false
    $s.set(%w{world ships 1 throttle_accel},0)
  end
  $s.update
  nil
}

game = Native(`new Phaser.Game(800, 600, Phaser.AUTO, '', { preload: preload, create: create, update: update, render: render})`)

h = HelmInterface.new(game)
