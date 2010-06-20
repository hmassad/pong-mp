''' Main Application '''

import pyglet
from sockets import TCPClient
import server_client_interpreter
from config_window import ConfigWindow
from game_window import GameWindow

class Application(object):
    NETOWRK_TIMEOUT = (1 / 60.)

    def __init__(self):
        self.config_window = None
        self.game_window = None

        self.player_name = None

        self.client_socket = None

        self.interpreter = None
        self.interpreter = server_client_interpreter.ServerClientInterpreter()
        self.interpreter.on_wait_for_opponent = self.interpreter_wait_for_opponent
        self.interpreter.on_game_starting = self.interpreter_game_starting
        self.interpreter.on_snapshot = self.interpreter_snapshot
        self.interpreter.on_game_finished = self.interpreter_game_finished
        
        self.__open_config_window()

    def run(self):
        pyglet.app.run()

    def close(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        self.interpreter = None
        self.__close_game_window()
        self.__close_config_window()

    def __open_config_window(self):
        old_config_window = self.config_window
        self.config_window = ConfigWindow()
        self.config_window.on_configured = self.config_window_configured
        self.config_window.on_closed = self.config_window_closed
        if self.player_name:
            self.config_window.player_name_textbox.text = self.player_name
        if old_config_window:
            old_config_window.on_closed = None
            old_config_window.on_configured = None
            old_config_window.close()
        
    def __close_config_window(self):
        if self.config_window:
            self.config_window.close()
            self.config_window = None

    def __open_game_window(self, timer_interval):
        old_game_window = self.game_window
        self.game_window = GameWindow(timer_interval)
        self.game_window.on_updated = self.game_window_updated
        self.game_window.on_closed = self.game_window_closed
        if old_game_window:
            self.__close_game_window()

    def __close_game_window(self):
        if self.game_window:
            self.game_window.close()
            self.game_window = None

    def config_window_configured(self, player_name, server_address):
        self.player_name = player_name
        
        if not self.client_socket:
            self.client_socket = TCPClient(server_address, 8888, self.NETOWRK_TIMEOUT)
            self.client_socket.on_connected = self.client_socket_connected
            self.client_socket.on_disconnected = self.client_socket_disconnected
            self.client_socket.on_sent = self.client_socket_sent
            self.client_socket.on_received = self.client_socket_received
            self.client_socket.on_error = self.client_socket_error
            self.client_socket.open()
    
    def client_socket_connected(self):
        try:
            self.config_window.show_info('Servidor contactado, registrando jugador...')
            # TODO: deshabilitar controles de config_window

            self.client_socket.send(self.interpreter.build_registration(self.player_name))
        except Exception as e:
            #print "client_socket_connected error, type: %s, message: %s" % (e, e.args)
            print 'Exception: type = %s, args = %s, message = %s' % (type(e), e.args, e.message)

    def client_socket_disconnected(self):
        print 'client socket disconnected'
        self.client_socket.close()
        self.client_socket = None
        
        if not self.config_window:
            self.__open_config_window()
        self.config_window.show_warn('El servidor cerro la conexion')

        self.__close_game_window()            

    def client_socket_error(self, message):
        print 'client socket error, message: %s' % (message)

        self.client_socket.close()
        self.client_socket = None
        
        self.__open_config_window()
        if type(message) is tuple:
            self.config_window.show_error('El servidor cerro la conexion (%s)' % (message[0]))
        else:
            self.config_window.show_error(message)

        self.__close_game_window()

    def client_socket_sent(self):
        pass

    def client_socket_received(self, msg):
        try:
            self.interpreter.parse(msg)
        except Exception as e:
            #print "client_socket_received error, args: %s, message: %s" % (e.args, e.message)
            print 'Exception: type = %s, args = %s, message = %s' % (type(e), e.args, e.message)

    def interpreter_wait_for_opponent(self):
        '''
        se dispara cuando hay 1 jugador conectado y hay que esperar al segundo
        '''
        if self.config_window:
            self.config_window.show_info('Esperando oponente...')
        print 'wait for opponent'

    def interpreter_game_starting(self, interval, side, opponent):
        '''
        se dispara cuando hay 2 jugadores conectados
        @param interval: intervalo en que se deben enviar las actualizaciones al servidor
        @param side: lado de la cancha del jugador
        @param opponent: nombre del oponente
        '''
        self.__open_game_window(interval)
        self.__close_config_window()
        if side == 'left':
            self.game_window.player1_name_label.text = self.player_name
            self.game_window.player2_name_label.text = opponent
        elif side == 'right':
            self.game_window.player1_name_label.text = opponent
            self.game_window.player2_name_label.text = self.player_name
        print 'game starting'

    def interpreter_snapshot(self, b_x, b_y, p1_x, p1_y, p1_s, p2_x, p2_y, p2_s):
        '''
        se dispara cuando se modificaron las posiciones de los elementos en el servidor
        @param side: lado de la cancha del jugador
        @param opponent: nombre del oponente
        '''
        if self.game_window:
            try:
                self.game_window.draw_snapshot(b_x, b_y, p1_x, p1_y, p1_s, p2_x, p2_y, p2_s)
            except Exception as e:
                print 'Exception: type = %s, args = %s, message = %s' % (type(e), e.args, e.message)

    def interpreter_game_finished(self, p1_name, p1_score, p2_name, p2_score):
        self.client_socket.close()
        self.client_socket = None
        self.__open_config_window()
        try:
            self.config_window.show_info('Finalizo la partida. %s: %s, %s: %s' % (p1_name, p1_score, p2_name, p2_score))
        except Exception as e:
            print 'Exception: type = %s, args = %s, message = %s' % (type(e), e.args, e.message)

        self.__close_game_window()
        print 'game finished'

    def game_window_updated(self, direction):
        '''
        se dispara de a intervalos regulares, para enviar el cambio de posicion de la paleta del jugador local
        @param direction: direccion hacia donde se mueve la paleta
        '''
        if self.game_window:
            try:
                message = self.interpreter.build_direction_change(direction)
                self.client_socket.send(message)
            except Exception as e:
                print 'Exception: type = %s, args = %s, message = %s' % (type(e), e.args, e.message)

    def game_window_closed(self):
        self.__open_config_window()
        self.client_socket.send(self.interpreter.build_deregistration())

    def config_window_closed(self):
        pass

if __name__ == '__main__':
    application = Application()
    application.run()
    application.close()
