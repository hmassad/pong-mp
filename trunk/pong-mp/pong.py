''' '''

import pyglet
from config_window import ConfigWindow

class Application(object):
    def __init__(self):
        ConfigWindow(self)
        self.http_client = None

application = Application()
pyglet.app.run()
