''' '''

from controls import BaseWindow, Label, Button

class AwaitingWindow(BaseWindow):
    def __init__(self):
        BaseWindow.__init__(self, width=800, height=600, caption='pong-mp: esperando oponente')
        
        # eventos
        self.on_cancelled = None

        # controles
        self.message_label = Label(self, self.width / 2, 60, self.width, 20, 'esperando oponente', (0, 0, 0, 0), (255, 255, 255, 255))
        self.controls.append(self.message_label)

        self.cancel_button = Button(self, (self.width - 30) / 2 + 20, 20, (self.width - 30) / 2, 20, 'Cancelar', (204, 204, 204, 255), (0, 0, 0, 255))
        self.controls.append(self.cancel_button)
        self.cancel_button.click = self.cancel_button_click

    def cancel_button_click(self):
        if self.on_cancelled:
            self.on_cancelled()