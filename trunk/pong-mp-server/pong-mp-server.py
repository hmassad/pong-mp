''' servidor '''

import sockets
import client_server_interpreter
import pyglet
import game

class Client():
    def __init__(self, token):
        self.token = token
        self.name = None
        self.paddle_index = None

class PongMpServer():
    GLOBAL_WAITING_TIME = (1/60.)

    def __init__(self):
        self.game = None
        self.clients = []

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
        
        pyglet.clock.schedule_interval(self.update, self.GLOBAL_WAITING_TIME)

    def interpreter_client_register(self, token, name):
        client = None
        for client in self.clients:
            if client.token == token:
                client.name = name
                break
        
        if len(self.clients) < 2:
            self.socket_server.send(token, self.interpreter.build_wait_for_opponent())
        elif len(self.clients) == 2:
            self.clients[0].paddle_index = 0
            self.clients[1].paddle_index = 1
            self.game = game.Game(self.clients[0].name, self.clients[1].name)
            self.socket_server.send(self.clients[0].token, self.interpreter.build_game_starting(side='left', opponent=self.clients[1].name))
            self.socket_server.send(self.clients[1].token, self.interpreter.build_game_starting(side='right', opponent=self.clients[0].name))

    def interpreter_client_update(self, token, direction):
        client = None
        for i in range(len(self.clients)):
            if self.clients[i].token == token:
                client = self.clients[i]
                break
        if client:
            self.game.update_paddle_direction(client.paddle_index, direction)

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
        client = Client(token)
        self.clients.append(client)
    
    def socket_server_client_disconnected(self, token):
        for i in range(len(self.clients)):
            if self.clients[i].token == token:
                self.clients.remove(self.clients[i])
                break
        print 'socket_server_client_disconnected, token = ', token
    
    def socket_server_client_sent(self, token):
        #print 'socket server sent, token = %s' % token
        pass

    def socket_server_client_received(self, token, data):
        #print 'socket server received, token = ', token, ', data = ' , data
        self.interpreter.parse(token, data)

    def socket_server_client_error(self, token, message):
        print 'socket_server_client_error, token = ', token, 'message = %s', message
        for client in self.clients:
            del client
    
    def update(self, dt):
        if not self.game:
            return
        # actualizar las posiciones e informar a los clientes
        self.game.update(dt)
        for client in self.clients:
            message = self.interpreter.build_snapshot(self.game.ball.x, self.game.ball.y, self.game.paddle1.x, self.game.paddle1.y, self.game.paddle2.x, self.game.paddle2.y)
            self.socket_server.send(client.token, message)

if __name__ == '__main__':
    application = PongMpServer()
    pyglet.app.run()
