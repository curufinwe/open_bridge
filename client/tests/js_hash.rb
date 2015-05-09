require 'opal'
require 'common/js_hash'

$count = 0
$ok = 0
$bad = 0
def log(v)
  `console.log(v)`
end

def assert(desc, &block)
  $count += 1
  if !block.call
    puts "test failed #{desc}"
    `debugger`
    block.call
    $bad += 1
  else
    $ok += 1
  end
end


h = JShash.new
h["foo"] = 3
h["foobar"] = 4

assert( "insert and get" ){ h["foo"] == 3 }
assert( "get other key" ){ h["foobar"] == 4 }
assert( "get nonexisting key" ){ h["blub"] == nil }

res = []
h.each_key{|x| res << x}

assert( "each_key" ) {
  res == ["foo", "foobar"]
}

res = []
h.each_pair{|(x,y)| res << [x,y]}

assert( "each_pair" ) {
  res == [["foo",3], ["foobar",4]]
}

h["bar"] = 5
h["flu"] = 5

h.delete_if do |k,v| 
  k=="bar"
end

assert( "delete_if" ) {
  h["bar"] == nil &&
  h["foo"] == 3 &&
  h["foobar"] == 4
}

assert( "merge" ) {
  other= JShash.new()
  other["flu"] = 10
  other["o"] = 11
  m = h.merge other
  m["o"] == 11 && m["flu"] = 10 && m["foo"] == 3
}

javascript_obj = `{az: 3, ab: {af: 5, az: 4}}`

h = JShash.new
h.from_json_object_js(javascript_obj)
assert("simple getter"){ h["az"] == 3}
log(h)
assert("sub hash"){ h["ab"].is_a? JShash}
assert("sub hash getter"){ h["ab"]["af"] == 5}

puts "#{$ok} of #{$count} tests successfully run, #{$bad} failed"
