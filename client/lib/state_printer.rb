require_relative 'common/connect_mri.rb'
require_relative 'common/state.rb'
require 'pp'

con = Connector.new
state = State.new(con)
con.state = state
loop do 
  state.update
  system("clear")
  pp state.authoritive
  sleep 1
end
