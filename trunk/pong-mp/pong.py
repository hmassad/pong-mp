''' Main Application '''

import pyglet
from config_window import ConfigWindow
import server_client_interpreter
from sockets import TCPClientSocket
from game_window import GameWindow
from awaiting_window import AwaitingWindow

class Application(object):
    def __init__(self):
        self.config_window = None
        self.game_window = None
        self.awaiting_window = None

        self.player_name = None

        self.client_socket = None

        self.config_window = ConfigWindow()
        self.config_window.on_configured = self.config_window_configured
        self.config_window.on_disconnected = self.application_closed

    def config_window_configured(self, player_name, server_address):
        self.player_name = player_name
        
        self.client_socket = TCPClientSocket(server_address, 8888)
        self.client_socket.on_connected = self.client_socket_connected
        self.client_socket.on_disconnected = self.client_socket_disconnected
        self.client_socket.on_sent = self.client_socket_sent
        self.client_socket.on_received = self.client_socket_received
        self.client_socket.on_error = self.client_socket_error
        self.client_socket.open()
    
    def client_socket_connected(self):
        try:
            self.config_window.show_info('Servidor contactado, registrando jugador...')
            # TODO: deshabilitar controles

            self.interpreter = server_client_interpreter.ServerClientInterpreter()
            self.interpreter.on_wait_for_opponent = self.interpreter_wait_for_opponent
            self.interpreter.on_game_starting = self.interpreter_game_starting
            self.interpreter.on_snapshot = self.interpreter_snapshot
            
            self.client_socket.send(self.interpreter.build_registration(self.player_name))
        except:
            import sys
            print "client_socket_connected error: ", sys.exc_info()[0]

    def client_socket_disconnected(self):
        self.client_socket = None
        
        if not self.config_window:
            self.config_window = ConfigWindow()
            self.config_window.on_configured = self.config_window_configured
            self.config_window.on_disconnected = self.application_closed
        self.config_window.show_warn('El servidor cerro la conexion')
            
        if self.awaiting_window:
            self.awaiting_window.close()
            self.awaiting_window = None

        if self.game_window:
            self.game_window.close()
            self.game_window = None

    def client_socket_error(self, message):
        self.client_socket = None
        
        if not self.config_window:
            self.config_window = ConfigWindow()
            self.config_window.on_configured = self.config_window_configured
            self.config_window.on_disconnected = self.application_closed
        self.config_window.show_error(message)
            
        if self.awaiting_window:
            self.awaiting_window.close()
            self.awaiting_window = None

        if self.game_window:
            self.game_window.close()
            self.game_window = None

    def client_socket_sent(self):
        pass

    def client_socket_received(self, msg):
        try:
            self.interpreter.parse(msg)
        except Exception:
            print 'client_socket_received error'

    def interpreter_wait_for_opponent(self):
        '''
        se dispara cuando hay 1 jugador conectado y hay que esperar al segundo
        '''

        '''
        self.awaiting_window = AwaitingWindow()
        self.awaiting_window.on_cancelled = self.awaiting_window_cancelled
        
        if self.config_window:
            self.config_window.close()
            self.config_window = None
        '''
        if self.config_window:
            self.config_window.show_info('esperando oponente')

    def interpreter_game_starting(self, side, opponent):
        print 'side: ', side
        print 'opponent: ', opponent
        '''
        se dispara cuando hay 2 jugadores conectados
        @param side: lado de la cancha del jugador
        @param opponent: nombre del oponente
        '''
        self.game_window = GameWindow()
        self.game_window.on_updated = self.game_window_updated
        
        if self.awaiting_window:
            self.awaiting_window.close()
            self.awaiting_window = None

        if self.config_window:
            self.config_window.close()
            self.config_window = None

    def interpreter_snapshot(self, b_x, b_y, p1_x, p1_y, p2_x, p2_y):
        '''
        se dispara cuando se modificaron las posiciones de los elementos
        @param side: lado de la cancha del jugador
        @param opponent: nombre del oponente
        '''
        if self.game_window:
            self.game_window.draw_snapshot(b_x, b_y, p1_x, p1_y, p2_x, p2_y)

    def game_window_updated(self, direction):
        '''
        se dispara de a intervalos regulares, para enviar el cambio de posicion de la paleta del jugador local
        @param direction: direccion hacia donde se mueve la paleta
        '''
        message = self.interpreter.build_direction_change(direction)
        self.client_socket.send(message)

    def awaiting_window_cancelled(self):
        self.config_window = ConfigWindow()
        self.config_window.on_configured = self.config_window_configured
        self.config_window.on_disconnected = self.application_closed
        
        if self.awaiting_window:
            self.awaiting_window.close()
            self.awaiting_window = None

    def application_closed(self):
        if self.config_window and not self.game_window and not self.awaiting_window:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            self.interpreter = None
            pyglet.app.exit()

if __name__ == '__main__':
    application = Application()
    pyglet.app.run()
