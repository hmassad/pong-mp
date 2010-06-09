
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
