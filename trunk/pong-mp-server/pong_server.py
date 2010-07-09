''' pong-mp-server '''

import sys
import sockets
import client_server_interpreter
import pyglet
import game_engine

class PongMpServer():
    NETWORK_TIMEOUT = (1 / 15.)

    def __init__(self):
        self.games = []

        self.__server = sockets.TCPServer(8888, self.NETWORK_TIMEOUT, client_server_interpreter.ClientServerInterpreter.TERMINATOR)
        self.__server.on_opened = self.__server_opened
        self.__server.on_closed = self.__server_closed
        self.__server.on_error = self.__server_error
        self.__server.on_client_connected = self.__server_client_connected
        self.__server.on_client_disconnected = self.__server_client_disconnected
        self.__server.on_client_sent = self.__server_client_sent
        self.__server.on_client_received = self.__server_client_received
        self.__server.on_client_error = self.__server_client_error

        self.__interpreter = client_server_interpreter.ClientServerInterpreter()
        self.__interpreter.on_client_register = self.__interpreter_client_register
        self.__interpreter.on_client_unregister = self.__interpreter_client_unregister
        self.__interpreter.on_client_update = self.__interpreter_client_update
        
    def run(self):
        self.__server.open()
        pyglet.clock.schedule_interval(self.__update, self.NETWORK_TIMEOUT)
        pyglet.app.run()

    def close(self):
        self.__server.close()

    def __interpreter_client_register(self, token, name):
        if (len(self.games) == 0) or (len(self.games[-1].players) == 2):
            # crear juego
            game = game_engine.Game()
            game.on_game_starting = self.__game_game_starting
            game.on_wait_for_opponent = self.__game_wait_for_opponent
            game.on_game_finished = self.__game_game_finished

            # agregar jugador
            game.add_player(token, name)
            self.games.append(game)
        else:
            # agregar juegador al primer juego que este con 1 jugador solo
            self.games[-1].add_player(token, name)

    def __interpreter_client_unregister(self, token):
        for game in self.games:
            for player in game.players:
                if player.token == token:
                    game.finish()
                    return

    def __game_game_starting(self, game):
        print 'Juego iniciado.'
        self.__server.send(game.players[0].token, self.__interpreter.build_game_starting(game_engine.Game.UPDATE_INTERVAL * 1000, side='left', opponent=game.players[1].name))
        self.__server.send(game.players[1].token, self.__interpreter.build_game_starting(game_engine.Game.UPDATE_INTERVAL * 1000, side='right', opponent=game.players[0].name))
        
    def __game_wait_for_opponent(self, game):
        print 'Esperando oponente...'
        self.__server.send(game.players[0].token, self.__interpreter.build_wait_for_opponent())
        
    def __interpreter_client_update(self, token, direction):
        for game in self.games:
            for player in game.players:
                if player.token == token:
                    game.update_player(player, direction)
                    return

    def __game_game_finished(self, game):
        print 'Juego finalizado.'
        self.games.remove(game)
        message = self.__interpreter.build_game_finished(game.players[0].name, game.players[0].score, game.players[1].name, game.players[1].score)
        for player in game.players:
            self.__server.send(player.token, message)

    def __server_opened(self):
        print 'TCPServer, escuchando en el puerto %d...' % (self.__server.port)

    def __server_closed(self):
        print 'TCPServer cerrado.'

    def __server_error(self, message):
        print 'TCPServer error, message = %s' % (message)

    def __server_client_connected(self, token):
        print 'Se conecto un cliente, token = %d' % (token)
    
    def __server_client_disconnected(self, token):
        print 'Se desconecto un cliente, token = %d' % (token)
        for game in self.games:
            for player in game.players:
                if player.token == token:
                    game.finish()
                    return

    def __server_client_error(self, token, message):
        print 'Error en cliente, token = %s, message = %s' % (token, message)
        for game in self.games:
            for player in game.players:
                if player.token == token:
                    game.finish()
                    return

    def __server_client_sent(self, token):
        #print 'server client sent, token = %s' % token
        pass

    def __server_client_received(self, token, payload):
        #print 'server client received, token = %s, message = %s' % (token, payload)
        self.__interpreter.parse(token, payload)

    def __update(self, dt):
        for game in self.games:
            if len(game.players) != 2:
                continue

            # actualizar el estado del juego
            game.update(dt)

            # informar a los clientes
            message = self.__interpreter.build_snapshot(
                game.ball.x,
                game.ball.y,
                game.players[0].paddle.x,
                game.players[0].paddle.y,
                game.players[0].score,
                game.players[1].paddle.x,
                game.players[1].paddle.y,
                game.players[1].score
            )
            for player in game.players:
                self.__server.send(player.token, message)

if __name__ == '__main__':
    application = PongMpServer()
    application.run()
    application.close()
    sys.exit(0)
