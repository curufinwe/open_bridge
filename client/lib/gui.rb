require 'set'

class Gui
  def initialize(game, state, input)
    @game,@state,@input = game,state,input
    @displays = []
    @sprites = {}
    @active = true
    create()
  end

  def create
  end

  def self.preload
  end

  def add_display(klass)
    res = klass.new(@game,@state,@input)
    @displays << res
    return res
  end

  def add_sprite(sp)
    @sprites[sp.__id__] = sp
  end

  def update_displays
    @displays.each do |d|
      d.update
    end
  end

  def active_ship
    @state.active_ship
  end

  def update
  end

  def active?
    @active
  end

  def activate
    show_sprites
    @active = true
    @displays.each(&:activate)
  end

  def deactivate
    hide_sprites
    @active = false
    @displays.each(&:deactivate)
  end

  private

  def hide_sprites
    @was_visible = {}
    @sprites.each_value do |sp|
      @was_visible[sp.__id__] = sp.visible
      sp.visible = false
    end
  end

  def show_sprites
    @sprites.each_value do |sp|
      sp.visible = @was_visible[sp.__id__]
    end
    @was_visible = {}
  end

end
