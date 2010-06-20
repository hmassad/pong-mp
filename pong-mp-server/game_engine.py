''' motor de pong '''
import math, random

class Ball():
    SPEED = 200
    RADIUS = 8
    DIAMETER = RADIUS * 2

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0

class Player():
    def __init__(self, token, name):
        self.token = token
        self.name = name
        self.paddle = Paddle()
        self.score = 0

class Paddle():
    SPEED = 200
    WIDTH = 8
    HEIGHT = 64

    def __init__(self):
        self.x = 0
        self.y = 0
        self.direction = 0

class GameState():
    WAITING_FOR_PLAYERS = 0
    RUNNING = 1
    FINISHED = 2

class Game():
    UPDATE_INTERVAL = 1 / 50.
    COURT_WIDTH = 800
    COURT_HEIGHT = 600

    def __init__(self):
        self.ball = Ball()
        self.players = []

        self.on_game_starting = None
        self.on_wait_for_opponent = None
        self.on_game_finished = None
        
        self.state = GameState.WAITING_FOR_PLAYERS

    def add_player(self, token, name):
        if len(self.players) == 2:
            raise Exception('No se puede agregar al jugador. El juego esta completo.')
        else:
            player = Player(token, name)
            self.players.append(player)
            if len(self.players) == 2:
                self.start()
            elif self.on_wait_for_opponent:
                self.on_wait_for_opponent(self)

    def start(self):
        self.state = GameState.RUNNING
        self.__new_round()
        if self.on_game_starting:
            self.on_game_starting(self)
        
    def finish(self):
        if self.state == GameState.RUNNING:
            if self.on_game_finished:
                self.on_game_finished(self)
        self.state = GameState.FINISHED
        for player in self.players:
            self.players.remove(player)

    def __new_round(self):
        self.ball.x = Game.COURT_WIDTH / 2
        self.ball.y = Game.COURT_HEIGHT / 2

        # configurar una velocidad inicial de la pelota
        angle = random.random() * math.pi / 2 + random.choice([-math.pi / 4, 3 * math.pi / 4])
        # convertir el angulo en direccion
        self.ball.vx = math.cos(angle) * Ball.SPEED
        self.ball.vy = math.sin(angle) * Ball.SPEED

        self.players[0].paddle.x = Paddle.WIDTH / 2
        self.players[0].paddle.y = Game.COURT_HEIGHT / 2

        self.players[1].paddle.x = Game.COURT_WIDTH - Paddle.WIDTH / 2
        self.players[1].paddle.y = Game.COURT_HEIGHT / 2

    def __handle_ball(self, dt):
        self.ball.x += self.ball.vx * dt
        self.ball.y += self.ball.vy * dt

        # hacer rebotar arriba
        if self.ball.y > Game.COURT_HEIGHT - Ball.RADIUS:
            self.ball.y = Game.COURT_HEIGHT - Ball.RADIUS
            self.ball.vy = -self.ball.vy
        # y abajo
        elif self.ball.y < Ball.RADIUS:
            self.ball.y = Ball.RADIUS
            self.ball.vy = -self.ball.vy

        # hacer rebotar la pelota contra jugador 2
        if self.ball.x > Game.COURT_WIDTH - Paddle.WIDTH and self.ball.y <= self.players[1].paddle.y + Paddle.HEIGHT / 2 and self.ball.y >= self.players[1].paddle.y - Paddle.HEIGHT / 2:
            self.ball.x = Game.COURT_WIDTH - Paddle.WIDTH
            self.ball.vx = -self.ball.vx
            # la velocidad de la pelota depende de la distancia entre centros cuando chocan la pelota y la paleta
            self.ball.vy += (self.ball.y - self.players[1].paddle.y) * Ball.RADIUS
        # hacer rebotar la pelota contra jugador 1
        elif self.ball.x < Paddle.WIDTH and self.ball.y <= self.players[0].paddle.y + Paddle.HEIGHT / 2 and self.ball.y >= self.players[0].paddle.y - Paddle.HEIGHT / 2:
            self.ball.x = Paddle.WIDTH
            self.ball.vx = -self.ball.vx
            self.ball.vy += (self.ball.y - self.players[0].paddle.y) * Ball.RADIUS

        # verificar que la pelota no se haya ido por los costados. Si fue punto, resetear
        if self.ball.x < 0 or self.ball.x > Game.COURT_WIDTH:
            # si se va por la izquierda, punto para jugador 2
            if self.ball.x < 0:
                self.players[1].score += 1
            # si se va por la derecha, punto para jugador 1
            else:
                self.players[0].score += 1

            # resetaer todo
            self.__new_round()

    def __handle_paddle(self, paddle, dt):
        paddle.y += paddle.direction * Paddle.SPEED * dt
        if paddle.y > Game.COURT_HEIGHT - Paddle.HEIGHT / 2:
            paddle.y = Game.COURT_HEIGHT - Paddle.HEIGHT / 2
        elif paddle.y < Paddle.HEIGHT / 2:
            paddle.y = Paddle.HEIGHT / 2

    def update(self, dt):
        for player in self.players:
            self.__handle_paddle(player.paddle, dt)
        self.__handle_ball(dt)

    def update_player(self, player, direction):
        '''
        Actualiza la direccion de la paleta
        @param player: jugador
        @param direction: up, down, none
        '''
        if direction == 'up':
            player.paddle.direction = 1
        elif direction == 'down':
            player.paddle.direction = -1
        else:
            player.paddle.direction = 0
