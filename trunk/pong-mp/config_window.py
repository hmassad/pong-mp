''' '''

import pyglet
from controls import BaseWindow, TextBox, Button

class ConfigWindow(BaseWindow):
    def __init__(self):
        BaseWindow.__init__(self, width=400, height=140, caption='Configuracion')

        # eventos
        self.on_configured = None
        
        # controles
        self.player_name_label = pyglet.text.Label('Jugador', x=10, y=100, anchor_y='bottom', color=(255, 255, 255, 255), batch=self.batch)

        self.server_address_label = pyglet.text.Label('Servidor', x=10, y=60, anchor_y='bottom', color=(255, 255, 255, 255), batch=self.batch)
        
        self.message_label = pyglet.text.Label('', x=10, y=140, anchor_y='bottom', color=(255, 255, 255, 255), batch=self.batch)
        
        self.player_name_textbox = TextBox(self, 200, 100, self.width - 210, 20, 'Jugador1', (255, 255, 255, 255), (0, 0, 0, 255))
        self.controls.append(self.player_name_textbox)
        
        self.server_address_textbox = TextBox(self, 200, 60, self.width - 210, 20, 'localhost', (255, 255, 255, 255), (0, 0, 0, 255))
        self.controls.append(self.server_address_textbox)
        
        self.join_button = Button(self, (self.width - 30) / 2 + 20, 20, (self.width - 30) / 2, 20, 'Conectar a Servidor', (204, 204, 204, 255), (0, 0, 0, 255))
        self.controls.append(self.join_button)
        self.join_button.click = self.join_button_click

    def show_info(self, message):
        self.height = 180
        self.message_label.color = (0, 0, 255, 255) # azul
        self.message_label.text = message

    def show_warn(self, message):
        self.height = 180
        self.message_label.color = (255, 242, 0, 255) # amarillo
        self.message_label.text = message

    def show_error(self, message):
        self.height = 180
        self.message_label.color = (255, 0, 0, 255) # rojo
        self.message_label.text = message

    def join_button_click(self):
        if self.on_configured:
            self.on_configured(self.player_name_textbox.text, self.server_address_textbox.text)
