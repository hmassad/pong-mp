
import pyglet
import configuration

class Paddle(pyglet.sprite.Sprite):

    def __init__(self, x, y, batch):
#        crear la forma de la paleta, cambiar por una imagen
        pattern = pyglet.image.SolidColorImagePattern((255, 255, 255, 255))
        image = pyglet.image.create(configuration.PADDLE_WIDTH, configuration.PADDLE_HEIGHT, pattern)

#        hacer que el anchor este en el centro de la paleta (calculo de retorno de pelota)
        image.anchor_x = configuration.PADDLE_WIDTH / 2
        image.anchor_y = configuration.PADDLE_HEIGHT /2

#        constructor base
        pyglet.sprite.Sprite.__init__(self, image, x, y, batch = batch)
        