require_relative './state.rb'
require 'pp'
require 'pry'

old = {
  foo: 3,
  bar: 4,
  baz: 5,
}

new = {
  foo: 3,
  bar: {0 => 1},
  fnord: 6
}


res,_ = old.diff(new)
(binding.pry; puts "") unless (res == {bar: {0=>1}, fnord: 6, baz: nil})


new = {
  foo: {x: {0=>1}}
}

res,_ = old.diff(new)
(binding.pry; puts "") unless (res == {foo: {x: {0=>1}}, bar: nil, baz: nil})


diff,_ = old.diff(new)
dup = old.deep_copy
dup.apply(diff)
(binding.pry; puts "") unless (dup == new)

old =  {"world"=>{"sector_size"=>10000, "bodies"=>{}, "ships"=>{"1"=>{"dx"=>0.01, "x"=>437.8799999999979, "dy"=>0.01, "y"=>2.9299999999999815}}}}

patch = {"world"=>{"ships"=>{"1"=>{"x"=>437.8899999999979, "y"=>2.9399999999999813}}}}

new = old.apply(patch)
expected = {"world"=>{"sector_size"=>10000, "bodies"=>{}, "ships"=>{"1"=>{"dx"=>0.01, "x"=>437.8899999999979, "dy"=>0.01, "y"=>2.9399999999999813}}}}
(binding.pry; puts "") unless (expected == new)

puts "tests done" #do not remove or else binding.pry wont run
