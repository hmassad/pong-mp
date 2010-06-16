''' servidor '''

import sockets
import client_server_interpreter
import pyglet

class Player():
    def __init__(self, token):
        self.token = token
        self.name = None
        self.paddle_position_x = 0
        self.paddle_position_y = 0
        
class PongMpServer():
    GLOBAL_WAITING_TIME = (1 / 20.)

    def __init__(self):
        self.players = []

        self.socket_server = sockets.TCPServer(8888, self.GLOBAL_WAITING_TIME)

        self.socket_server.on_opened = self.socket_server_opened
        self.socket_server.on_closed = self.socket_server_closed
        self.socket_server.on_error = self.socket_server_error

        self.socket_server.on_client_connected = self.socket_server_client_connected
        self.socket_server.on_client_disconnected = self.socket_server_client_disconnected
        self.socket_server.on_client_sent = self.socket_server_client_sent
        self.socket_server.on_client_received = self.socket_server_client_received
        self.socket_server.on_client_error = self.socket_server_client_error

        self.interpreter = client_server_interpreter.ClientServerInterpreter()
        self.interpreter.on_client_register = self.interpreter_client_register
        self.interpreter.on_client_update = self.interpreter_client_update
        
        self.socket_server.open()
        
        pyglet.clock.schedule_once(self.update, self.GLOBAL_WAITING_TIME)
    
    def interpreter_client_register(self, token, name):
        player = None
        for player in self.players:
            if player.token == token:
                player.name = name
                break
        
        if len(self.players) < 2:
            self.socket_server.send(token, self.interpreter.build_wait_for_opponent())
        elif len(self.players) == 2:
            self.socket_server.send(self.players[0].token, self.interpreter.build_game_starting('left', self.players[1].name))
            self.socket_server.send(self.players[1].token, self.interpreter.build_game_starting('right', self.players[0].name))

    def interpreter_client_update(self, token, direction):
        print 'interpreter_client_update, direction = ', direction

    def dispose(self):
        self.socket_server.close()

    def socket_server_opened(self):
        print 'socket server opened'

    def socket_server_closed(self):
        print 'socket server closed'

    def socket_server_error(self):
        print 'socket server error'

    def socket_server_sent(self, token):
        print 'socket server sent'

    def socket_server_client_connected(self, token):
        print 'socket_server_client_connected, token = ', token
        player = Player(token)
        self.players.append(player)
    
    def socket_server_client_disconnected(self, token):
        for i in range(len(self.players)):
            if self.players[i].token == token:
                del self.players[i]
        print 'socket_server_client_disconnected, token = ', token
    
    def socket_server_client_sent(self, token):
        print 'socket server sent, token = %s' % token

    def socket_server_client_received(self, token, data):
        print 'socket server received, token = ', token, ', data = ' , data
        self.interpreter.parse(token, data)

    def socket_server_client_error(self, token, message):
        print 'socket_server_client_error, token = ', token, 'message = %s', message
        for player in self.players:
            del player
    
    def update(self, dt):
        # actualizar las posiciones
        #for player in self.players:
        #    self.socket_server.send(player.token, self.interpreter.build_wait_for_opponent())

        pyglet.clock.schedule_once(self.update, dt)

if __name__ == '__main__':
    application = PongMpServer()
    pyglet.app.run()
