
import pyglet
import configuration

class Ball(pyglet.sprite.Sprite):

    def __init__(self, x, y, batch):
#        crear la forma de la pelota, cambiar por una imagen
        pattern = pyglet.image.SolidColorImagePattern((255, 0, 0, 255))
        image = pyglet.image.create(configuration.BALL_DIAMETER, configuration.BALL_DIAMETER, pattern)

#        hacer que el anchor este en el centro de la pelota (calculo de retorno de pelota)
        image.anchor_x, image.anchor_y = configuration.BALL_DIAMETER / 2, configuration.BALL_DIAMETER / 2

#        constructor base
        pyglet.sprite.Sprite.__init__(self, image, batch = batch)

        self.reset()

        