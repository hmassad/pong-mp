import random
import math
import pyglet

if __name__ == '__main__':

    # Jugar contra la computadora?
    player1_computer = False
    player2_computer = True
    
    def window_width(): return 800
    WINDOW_WIDTH = window_width()
    
    def window_height(): return 600
    WINDOW_HEIGHT = window_height()
    
    def window_caption(): return "pong"
    WINDOW_CAPTION = window_caption()
    
    def court_width(): return 800
    COURT_WIDTH = court_width()
    
    def court_height(): return 500
    COURT_HEIGHT = court_height()
    
    def paddle_speed(): return 500
    PADDLE_SPEED = paddle_speed()
    PADDLE_SPEED_CPU = 3 * PADDLE_SPEED / 4
    
    def paddle_width(): return 8
    PADDLE_WIDTH = paddle_width()
    
    def paddle_height(): return 64
    PADDLE_HEIGHT = paddle_height()
    
    def ball_diameter(): return 8
    BALL_DIAMETER = ball_diameter()
    
    def ball_speed(): return 800
    BALL_SPEED = ball_speed()
    
    # crear la ventana
    window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, resizable=False, visible=False, caption=WINDOW_CAPTION)
    window.set_location(window.screen.width / 2 - window.width / 2, window.screen.height / 2 - window.height / 2)
    
    # crear un 'batch' para dibujar todo junto
    batch = pyglet.graphics.Batch()
    
    # paleta
    class Paddle(pyglet.sprite.Sprite):
        def __init__(self, x, y):
            # crear la forma de la paleta, cambiar por una imagen
            pattern = pyglet.image.SolidColorImagePattern((255, 255, 255, 255))
            image = pyglet.image.create(PADDLE_WIDTH, PADDLE_HEIGHT, pattern)
    
            # hacer que el anchor este en el centro de la paleta (calculo de retorno de pelota)  
            image.anchor_x = PADDLE_WIDTH / 2
            image.anchor_y = PADDLE_HEIGHT / 2
    
            # constructor base
            pyglet.sprite.Sprite.__init__(self, image, x, y, batch=batch)
    
        def reset(self):
            self.y = COURT_HEIGHT / 2
    
    # pelota
    class Ball(pyglet.sprite.Sprite):
        def __init__(self):
    
            # crear la forma de la pelota, cambiar por una imagen
            pattern = pyglet.image.SolidColorImagePattern((255, 0, 0, 255))
            image = pyglet.image.create(BALL_DIAMETER, BALL_DIAMETER, pattern)
    
            # hacer que el anchor este en el centro de la pelota (calculo de retorno de pelota)  
            image.anchor_x, image.anchor_y = BALL_DIAMETER / 2, BALL_DIAMETER / 2
    
            # constructor base
            pyglet.sprite.Sprite.__init__(self, image, batch=batch)
    
            self.reset()
    
        def reset(self):
            # poner la pelota en el centro de la cancha
            self.x = COURT_WIDTH / 2
            self.y = COURT_HEIGHT / 2
    
            # configurar un angulo inicial de la pelota de +-45 grados para cuando se saque
            angle = random.random() * math.pi / 2 + random.choice([-math.pi / 4, 3 * math.pi / 4])
            # convertir el angulo en direccion
            self.vx = math.cos(angle) * BALL_SPEED
            self.vy = math.sin(angle) * BALL_SPEED
    
    # handler del teclado
    keymap = pyglet.window.key.KeyStateHandler()
    window.push_handlers(keymap)
    
    # setup a stack for our game states
    states = []
    
    # this game state does nothing until the space bar is pressed
    # at which point it returns control to the previous state
    class PausedState:
        def update(self, dt):
            if keymap[pyglet.window.key.SPACE]:
                states.pop()
    
    # this class plays the actual game
    class GameState:
        def __init__(self):
            # nombre de los jugadores
            pyglet.text.Label('Jugador 1', font_name='Verdana', font_size=24, x=200, y=575, anchor_x='center', anchor_y='center', batch=batch)
            pyglet.text.Label('Jugador 2', font_name='Verdana', font_size=24, x=600, y=575, anchor_x='center', anchor_y='center', batch=batch)
    
            # puntaje
            self.player1_label = pyglet.text.Label('0', font_name='Verdana', font_size=24, x=200, y=525, anchor_x='center', anchor_y='center', batch=batch)
            self.player2_label = pyglet.text.Label('0', font_name='Verdana', font_size=24, x=600, y=525, anchor_x='center', anchor_y='center', batch=batch)
    
            # bordes: magia de OpenGL
            batch.add(8, pyglet.gl.GL_LINES, None, ('v2i', (WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH, 0, WINDOW_WIDTH, 0, 0, 0, 0, 0, 0, WINDOW_HEIGHT, 0, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - 1)))
            # borde para puntaje
            batch.add(2, pyglet.gl.GL_LINES, None, ('v2i', (0, COURT_HEIGHT, COURT_WIDTH, COURT_HEIGHT)))
    
            self.player1_score = 0
            self.player2_score = 0
    
            # crear paletas
            self.player1 = Paddle(PADDLE_WIDTH / 2, COURT_HEIGHT / 2)
            self.player2 = Paddle(COURT_WIDTH - PADDLE_WIDTH / 2, COURT_HEIGHT / 2)
    
            # crear pelota
            self.ball = Ball()
    
        def reset(self):
            self.player1.reset()
            self.player2.reset()
    
            self.ball.reset()
    
        # mover paleta del jugador 1
        def handle_player1(self, dt):
            if player1_computer:
                diff = self.ball.y - self.player1.y
                self.player1.y += (diff if diff < PADDLE_SPEED_CPU * dt else PADDLE_SPEED_CPU * dt)
            elif player2_computer:
                if keymap[pyglet.window.key.UP]:
                    self.player1.y += PADDLE_SPEED * dt
                elif keymap[pyglet.window.key.DOWN]:
                    self.player1.y -= PADDLE_SPEED * dt
            else:    
                if keymap[pyglet.window.key.W]:
                    self.player1.y += PADDLE_SPEED * dt
                elif keymap[pyglet.window.key.S]:
                    self.player1.y -= PADDLE_SPEED * dt
    
        # mover paleta del jugador 2 o que se mueva la paleta de la computadora
        # la velocidad de la computadora es un toque menor, porque si no, no hay manera de ganarle
        def handle_player2(self, dt):
            if player2_computer:
                diff = self.ball.y - self.player2.y
                self.player2.y += (diff if diff < PADDLE_SPEED_CPU * dt else PADDLE_SPEED_CPU * dt)
            elif player1_computer:
                if keymap[pyglet.window.key.UP]:
                    self.player2.y += PADDLE_SPEED * dt
                elif keymap[pyglet.window.key.DOWN]:
                    self.player2.y -= PADDLE_SPEED * dt
            else:
                if keymap[pyglet.window.key.UP]:
                    self.player2.y += PADDLE_SPEED * dt
                elif keymap[pyglet.window.key.DOWN]:
                    self.player2.y -= PADDLE_SPEED * dt
    
        def update(self, dt):
            # mover la pelota
            self.ball.x += self.ball.vx * dt
            self.ball.y += self.ball.vy * dt
    
            # mover las paletas
            self.handle_player1(dt)
            self.handle_player2(dt)
    
            # hacer que las paletas no se vayan de la pantalla
            for p in [self.player1, self.player2]:
                if p.y > COURT_HEIGHT - PADDLE_HEIGHT / 2:
                    p.y = COURT_HEIGHT - PADDLE_HEIGHT / 2
                elif p.y < PADDLE_HEIGHT / 2:
                    p.y = PADDLE_HEIGHT / 2
    
            # hacer rebotar la pelota arriba
            if self.ball.y > COURT_HEIGHT - BALL_DIAMETER / 2:
                self.ball.y = COURT_HEIGHT - BALL_DIAMETER / 2
                self.ball.vy = -self.ball.vy
            # y abajo
            elif self.ball.y < BALL_DIAMETER / 2:
                self.ball.y = BALL_DIAMETER / 2
                self.ball.vy = -self.ball.vy
    
            # hacer rebotar la pelota contra jugador 2
            if self.ball.x > COURT_WIDTH - PADDLE_WIDTH and self.ball.y <= self.player2.y + PADDLE_HEIGHT / 2 and self.ball.y >= self.player2.y - PADDLE_HEIGHT / 2:
                self.ball.x = COURT_WIDTH - PADDLE_WIDTH
                self.ball.vx = -self.ball.vx
                # la velocidad de la pelota depende de la distancia entre centros cuando chocan la pelota y la paleta
                self.ball.vy += (self.ball.y - self.player2.y) * BALL_DIAMETER / 2
            # hacer rebotar la pelota contra jugador 1
            elif self.ball.x < PADDLE_WIDTH and self.ball.y <= self.player1.y + 32 and self.ball.y >= self.player1.y - PADDLE_HEIGHT / 2:
                self.ball.x = PADDLE_WIDTH
                self.ball.vx = -self.ball.vx
                self.ball.vy += (self.ball.y - self.player1.y) * BALL_DIAMETER / 2
    
            # verificar que la pelota no se haya ido por los costados. Si fue punto, resetear esperar a que saquen
            if self.ball.x < 0 or self.ball.x > COURT_WIDTH:
                # si se va por la izquierda, punto para jugador 2
                if self.ball.x < 0:
                    global player2_score
                    self.player2_score += 1
                    self.player2_label.text = '%d' % self.player2_score
                # si se va por la derecha, punto para jugador 1
                else:
                    global player1_score
                    self.player1_score += 1
                    self.player1_label.text = '%d' % self.player1_score
    
                # resetaer todo
                self.reset()
                # poner en pausa
                states.append(PausedState())
    
    @window.event
    def on_draw():
        window.clear()
    
        batch.draw()
    
    # update callback
    def update(dt):
        # update the topmost state, if we have any
        if len(states):
            states[-1].update(dt)
        # otherwise quit
        else:
            pyglet.app.exit()
    
    # setup the inital states
    states.append(GameState())
    # game starts paused
    states.append(PausedState())
    
    # timer de 20 ms que es el que hace de base de tiempo
    pyglet.clock.schedule_interval(update, 1 / 60.)
    
    # borrar la ventana
    window.clear()
    window.flip()
    
    window.set_visible(True)
    
    pyglet.app.run()
