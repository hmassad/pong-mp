''' Ventana donde se desarrolla el juego '''

from controls import BaseWindow
import pyglet
import ball
import paddle

class GameWindow(BaseWindow):
    def __init__(self, application):
        BaseWindow.__init__(self, application, width=800, height=600, caption='pong-mp')

        # enviar ready al servidor
        pyglet.clock.schedule_interval(self.update, 1 / 20.)
        self.fps_label = pyglet.text.Label(text='FPS: 0', x=0, y=0, anchor_x='left', anchor_y='bottom', batch=self.batch)
        self.key_label = pyglet.text.Label(text='KEY: Ninguna', x=0, y=20, anchor_x='left', anchor_y='bottom', batch=self.batch)
        self.dt_label = pyglet.text.Label(text='DT: 0', x=0, y=40, anchor_x='left', anchor_y='bottom', batch=self.batch)
        
        self.ball = ball.Ball(self.width / 2, self.height / 2, 8, self.batch)
        self.paddle1 = paddle.Paddle(4, self.height / 2, 8, 64, self.batch)
        self.paddle2 = paddle.Paddle(self.width - 4, self.height / 2, 8, 64, self.batch)

    def update(self, dt):
        # aplicar cambios de posicion de paletas y pelota
        # enviar cambio de posicion de paleta
        self.fps_label.text = 'FPS: %d' % pyglet.clock.get_fps()
        self.dt_label.text = 'DT: %f' % dt
        if self.keymap[pyglet.window.key.UP]:
            self.key_label.text = 'KEY: UP'
        elif self.keymap[pyglet.window.key.DOWN]:
            self.key_label.text = 'KEY: DOWN'
        else:
            self.key_label.text = 'KEY: Ninguna'
