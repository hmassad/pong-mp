''' '''

import pyglet
from config_window import ConfigWindow
import serverClientMsgParser

class Application(object):
    def __init__(self):
        ConfigWindow(self)
        self.client_socket = None
        self.client_socket.on_received = self.client_socket_received
        self.parser = serverClientMsgParser.ServerClientMsgParser()
        self.parser.on_connected = self.parser_connected
        
    def client_socket_received(self, msg):
        self.parser.parse(msg)
        
    def parser_connected(self):
        pass
    
application = Application()
pyglet.app.run()
