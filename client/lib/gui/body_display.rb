require 'gui/gui'
require 'set'

class BodyDisplay < Gui
  attr_reader :bodies_to_sprites

  def create
    @bodies_to_sprites = {}
  end

  def update
    remove_dead_sprites
    add_missing_sprites
    @bodies_to_sprites.each_pair do |body, sprite|
      body.update_sprite(sprite)
    end
  end

  def activate
    super
  end

  def deactivate
    super
  end

  private

  def add_missing_sprites
    (@state.bodies - @bodies_to_sprites.keys).each do |body|
      sprite = body.create_sprite(@game,"ship")
      @bodies_to_sprites[body] = sprite
      add_sprite sprite
    end
  end

  def remove_dead_sprites
    (Set.new(@bodies_to_sprites.keys)-@state.bodies).each do |body|
      @bodies_to_sprites[body].destroy
      @bodies_to_sprites.delete(body)
    end
  end

end
