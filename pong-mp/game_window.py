''' Ventana donde se desarrolla el juego '''

from controls import BaseWindow
import pyglet

'''  clase que modela la pelota ''' 
class Ball(pyglet.sprite.Sprite):

    def __init__(self, x, y, diameter, batch):
        self.diameter = diameter
        
        ''' # crear la forma de la pelota, cambiar por una imagen '''
        pattern = pyglet.image.SolidColorImagePattern((255, 0, 0, 255))
        image = pyglet.image.create(self.diameter, self.diameter, pattern)

        ''' hacer que el anchor este en el centro de la pelota (calculo de retorno de pelota) '''
        image.anchor_x, image.anchor_y = self.diameter / 2, self.diameter / 2
        
        self.vx = self.vy = 0

        ''' constructor base '''
        pyglet.sprite.Sprite.__init__(self, image, batch=batch)
        
        self.x = x
        self.y = y

''' clase que modela la paleta ''' 
class Paddle(pyglet.sprite.Sprite):

    def __init__(self, x, y, width, height, batch):

        ''' crear la forma de la paleta, cambiar por una imagen '''
        pattern = pyglet.image.SolidColorImagePattern((255, 255, 255, 255))
        image = pyglet.image.create(width, height, pattern)

        ''' hacer que el anchor este en el centro de la paleta (calculo de retorno de pelota) '''
        image.anchor_x = width / 2
        image.anchor_y = height / 2

        ''' constructor base '''
        pyglet.sprite.Sprite.__init__(self, image, x, y, batch=batch)

class GameWindow(BaseWindow):

    def __init__(self):
        BaseWindow.__init__(self, width=800, height=600, caption='pong-mp')

        # enviar ready al servidor
        pyglet.clock.schedule_interval(self.update, 1 / 20.)
        self.fps_label = pyglet.text.Label(text='FPS: 0', x=0, y=0, anchor_x='left', anchor_y='bottom', batch=self.batch)
        self.key_label = pyglet.text.Label(text='KEY: Ninguna', x=0, y=20, anchor_x='left', anchor_y='bottom', batch=self.batch)
        self.dt_label = pyglet.text.Label(text='DT: 0', x=0, y=40, anchor_x='left', anchor_y='bottom', batch=self.batch)
        
        self.ball = Ball(self.width / 2, self.height / 2, 8, self.batch)
        self.paddle1 = Paddle(4, self.height / 2, 8, 64, self.batch)
        self.paddle2 = Paddle(self.width - 4, self.height / 2, 8, 64, self.batch)
        
        # eventos
        self.on_updated = None

    def update(self, dt):
        # aplicar cambios de posicion de paletas y pelota
        # enviar cambio de posicion de paleta
        self.fps_label.text = 'FPS: %d' % pyglet.clock.get_fps()
        self.dt_label.text = 'DT: %f' % dt
        if self.keymap[pyglet.window.key.UP]:
            self.key_label.text = 'KEY: UP'
            if self.on_updated:
                self.on_updated('UP')
        elif self.keymap[pyglet.window.key.DOWN]:
            self.key_label.text = 'KEY: DOWN'
            if self.on_updated:
                self.on_updated('DOWN')
        else:
            self.key_label.text = 'KEY: Ninguna'
            if self.on_updated:
                self.on_updated('NONE')
        
    def draw_snapshot(self, b_x, b_y, p1_x, p1_y, p2_x, p2_y):
        self.ball.x = b_x
        self.ball.y = b_y
        self.paddle1.x = p1_x
        self.paddle1.y = p1_y
        self.paddle2.x = p2_x
        self.paddle2.y = p2_y
