
import pyglet

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
