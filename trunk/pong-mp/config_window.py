''' '''

import pyglet
from controls import BaseWindow, TextBox, Button
from game_window import GameWindow

class ConfigWindow(BaseWindow):
    def __init__(self, application):
        BaseWindow.__init__(self, application, width=400, height=140, caption='Configuracion')

        self.labels = [
            pyglet.text.Label('Jugador', x=10, y=100, anchor_y='bottom', color=(255, 255, 255, 255), batch=self.batch),
            pyglet.text.Label('Servidor', x=10, y=60, anchor_y='bottom', color=(255, 255, 255, 255), batch=self.batch)
        ]
        
        self.jugadorTextBox = TextBox(self, 200, 100, self.width - 210, 20, 'Jugador', (255, 255, 255, 255), (0, 0, 0, 255))
        self.controls.append(self.jugadorTextBox)
        
        self.servidorTextBox = TextBox(self, 200, 60, self.width - 210, 20, 'Servidor', (255, 255, 255, 255), (0, 0, 0, 255))
        self.controls.append(self.servidorTextBox)
        
        self.serveButton = Button(self, (self.width - 30) / 2 + 20, 20, (self.width - 30) / 2, 20, 'Crear Servidor', (204, 204, 204, 255), (0, 0, 0, 255))
        self.controls.append(self.serveButton)
        self.serveButton.click = self.serveButton_click

        self.joinButton = Button(self, 10, 20, (self.width - 30) / 2, 20, 'Conectar a Servidor', (204, 204, 204, 255), (0, 0, 0, 255))
        self.controls.append(self.joinButton)
        self.joinButton.click = self.joinButton_click

        self.application.http_client = None

    def serveButton_click(self):
        # crear un servidor
        # abrir ventana de juego
        GameWindow(self.application)
        self.close()
    
    def joinButton_click(self):
        # conectar a un servidor
        self.server_connected()
    
    def server_connected(self):
        # abrir pantalla de juego
        GameWindow(self.application)
        self.close()
