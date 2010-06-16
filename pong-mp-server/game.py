''' motor de pong '''
import math, random

class Ball():
    RADIUS = 8
    DIAMETER = RADIUS * 2
    SPEED = 10

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0

class Paddle():
    SPEED = 10
    WIDTH = 8
    HEIGHT = 64

    def __init__(self, name):
        self.x = 0
        self.y = 0
        self.direction = 0
        self.name = name
        self.score = 0

class Game():
    COURT_WIDTH = 800
    COURT_HEIGHT = 600

    def __init__(self, player1_name, player2_name):
        self.ball = Ball()
        self.paddles = []
        self.paddles.append(Paddle(player1_name))
        self.paddles.append(Paddle(player2_name))
        self.__new_round()

    def __new_round(self):
        self.ball.x = Game.COURT_WIDTH / 2
        self.ball.y = Game.COURT_HEIGHT / 2

        # configurar una velocidad inicial de la pelota
        angle = random.random() * math.pi / 2 + random.choice([-math.pi / 4, 3 * math.pi / 4])
        # convertir el angulo en direccion
        self.ball.vx = math.cos(angle) * Ball.SPEED
        self.ball.vy = math.sin(angle) * Ball.SPEED

        self.paddles[0].x = Paddle.WIDTH / 2
        self.paddles[0].y = Game.COURT_HEIGHT / 2

        self.paddles[1].x = Game.COURT_WIDTH - Paddle.WIDTH / 2
        self.paddles[1].y = Game.COURT_HEIGHT / 2

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
        if self.ball.x > Game.COURT_WIDTH - Paddle.WIDTH and self.ball.y <= self.paddles[1].y + Paddle.HEIGHT / 2 and self.ball.y >= self.paddles[1].y - Paddle.HEIGHT / 2:
            self.ball.x = Game.COURT_WIDTH - Paddle.WIDTH
            self.ball.vx = -self.ball.vx
            # la velocidad de la pelota depende de la distancia entre centros cuando chocan la pelota y la paleta
            #self.ball.vy += (self.ball.y - self.paddles[1].y) * Ball.RADIUS
        # hacer rebotar la pelota contra jugador 1
        elif self.ball.x < Paddle.WIDTH and self.ball.y <= self.paddles[0].y + Paddle.HEIGHT / 2 and self.ball.y >= self.paddles[0].y - Paddle.HEIGHT / 2:
            self.ball.x = Paddle.WIDTH
            self.ball.vx = -self.ball.vx
            #self.ball.vy += (self.ball.y - self.paddles[0].y) * Ball.RADIUS

        # verificar que la pelota no se haya ido por los costados. Si fue punto, resetear
        if self.ball.x < 0 or self.ball.x > Game.COURT_WIDTH:
            # si se va por la izquierda, punto para jugador 2
            if self.ball.x < 0:
                self.paddles[0].score += 1
            # si se va por la derecha, punto para jugador 1
            else:
                self.paddles[1].score += 1

            # resetaer todo
            self.__new_round()

    def __handle_paddle(self, paddle, dt):
        paddle.y += paddle.direction * Paddle.SPEED
        if paddle.y > Game.COURT_HEIGHT - Paddle.HEIGHT / 2:
            paddle.y = Game.COURT_HEIGHT - Paddle.HEIGHT / 2
        elif paddle.y < Paddle.HEIGHT / 2:
            paddle.y = Paddle.HEIGHT / 2

    def update(self, dt):
        self.__handle_paddle(self.paddles[0], dt)
        self.__handle_paddle(self.paddles[1], dt)
        self.__handle_ball(dt)

    def update_paddle_direction(self, paddle_index, direction):
        '''
        Actualiza la direccion de la paleta
        @param paddle_index: 0 o 1, numero de jugador
        @param direction: up, down, none
        '''
        if direction == 'up':
            self.paddles[paddle_index].direction = 1
        elif direction == 'down':
            self.paddles[paddle_index].direction = -1
        else:
            self.paddles[paddle_index].direction = 0
