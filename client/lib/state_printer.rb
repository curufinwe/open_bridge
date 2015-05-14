require_relative 'common/connect_mri.rb'
require_relative 'common/state_fast.rb'
require 'pp'

state = State.new(Hash)
con = Connector.new(state)

loop do 
  con.send_state_update
 # system("clear")
  pp state.authoritative
  sleep 1
end
