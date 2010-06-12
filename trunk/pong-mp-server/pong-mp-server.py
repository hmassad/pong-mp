''' servidor '''

from sockets import TCPServer
import pyglet
import player

class PongMpServer():
    def __init__(self):
        self.players = []

        self.socket_server = TCPServer(8888)
        self.socket_server.on_opened = self.socket_server_opened
        self.socket_server.on_closed = self.socket_server_closed
        self.socket_server.on_sent = self.socket_server_sent
        self.socket_server.on_received = self.socket_server_received
        self.socket_server.on_error = self.socket_server_error
        self.socket_server.on_client_connected = self.socket_server_client_connected
        self.socket_server.on_client_disconnected = self.socket_server_client_disconnected

        self.socket_server.open()
        
        pyglet.clock.schedule_interval(self.main_loop, 1)

    def dispose(self):
        self.socket_server.close()

    def socket_server_opened(self):
        print 'socket server opened'

    def socket_server_closed(self):
        print 'socket server closed'

    def socket_server_sent(self):
        print 'socket server sent'

    def socket_server_received(self):
        print 'socket server received'

    def socket_server_error(self):
        print 'socket server error'
    
    def socket_server_client_connected(self, token):
        print 'socket server client connected, token = ', token
    
    def socket_server_client_disconnected(self, token):
        print 'socket server client disconnected, token = ', token
    
    def main_loop(self, dt):
        for player in self.players:
            socket_server.send(player.token, 'holaa')

if __name__ == '__main__':
    application = PongMpServer()
    pyglet.app.run()
