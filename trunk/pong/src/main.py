
import pyglet
import configuration

class Main(object):

    def __init__(self):
        # crear la ventana
        window = pyglet.window.Window(configuration.WINDOW_WIDTH, configuration.WINDOW_HEIGHT, resizable = False, visible = False, caption = configuration.WINDOW_CAPTION)
        window.set_location(window.screen.width / 2 - window.width / 2, window.screen.height / 2 - window.height / 2)

        # crear un 'batch' para dibujar todo junto
        batch = pyglet.graphics.Batch()
