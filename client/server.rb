require 'opal'
require 'opal-jquery'
require 'em-websocket'
require 'em-http-server'
require 'set'
require 'thread'
require 'erb'

require 'sass'

class Commands

  def needs_erb(path,content)
    return true if path =~/.erb\Z/
    return true if content =~ /\A[#\/*]+ ERB/
    return false
  end

  def inc(path)
    content =File.read(path) 
    content = render(content) if needs_erb(path,content)
    content = "\n"+content if path =~/.rb(.erb)?\Z/
    return "\n"+content
  end

  def inc_rb(path)
    return "<script type='text/ruby'>\n#{inc(path)}</script>"
  end

  def inc_sass(path)
    content =File.read(path) 
    return Sass::Engine.new(content, :syntax => :sass).render
  end

  def render(content)
    return ERB.new(content).result(binding)
  end

end

$erb_binding = Commands.new

class HTTPHandler < EM::HttpServer::Server

    def compile_app
      Opal.append_path("app")
      Opal.append_path("lib")
      puts "not slacking of, code is compiling"
      mainjs = Opal::Builder.build('main')
      return mainjs
    end

    def compile_css(path)
      content = File.read(path.gsub(/.css\Z/,".sass")) 
      css = Sass::Engine.new(content, :syntax => :sass).render
      return css
    end
  
    def process_http_request
          path = File.expand_path("."+@http_request_uri)
          puts "serving #{path}"
          extension = File.extname(path)
          raise "WTF" unless path.index(Dir.pwd) == 0
          response = EM::DelegatedHttpResponse.new(self)
          response.status = 200
#          response.content_type 'text/html'
          if File.exist?(path)
          response.content = File.read(path)
          elsif path.end_with? "/app/main.js"
            response.content = compile_app
          elsif path.end_with? ".css"
            response.content = compile_css(path)
          #elsif File.exist?(path+".erb")
          #  file = File.read(path+".erb")
          #  resp = $erb_binding.render(file)
          #  response.content = resp
          else
            puts "404 File not found#{path}"
            raise "file not found"
          end
          puts "sendin resp"
          response.send_response
    end

    def http_request_errback e
      puts e.inspect
    end
end

#$websockets = Set.new
#$wsm = Mutex.new
#
#Thread.abort_on_exception = true
#
#Thread.new do
#  loop do
#    puts `inotifywait -e modify -e attrib -e close_write -e create -e delete -e move -e move_self -r * .`
#    puts "File system Changes"
#    $wsm.synchronize do 
#      $websockets.each { |ws| ws.send("update") }
#    end
#  end
#end
#
EM.run do
#
#  EM::WebSocket.run(:host => "0.0.0.0", :port => 8080) do |ws|
#    ws.onopen { $wsm.synchronize{$websockets.add ws} }
#    ws.onclose { $wsm.synchronize{$websockets.delete ws} }
#  end
#
  EM::start_server("0.0.0.0", 8000, HTTPHandler)
#
end
#
