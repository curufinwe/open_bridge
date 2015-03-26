require 'websocket-client-simple'
require 'json'
require 'pp'

ws = WebSocket::Client::Simple.connect 'ws://localhost:9000'

ws.on :message do |msg|
  state = JSON.parse(msg.data)
  pp state
  exit
end

ws.on :open do
end

ws.on :close do |e|
  p e
  exit 1
end

ws.on :error do |e|
  p e
end

sleep 1
