'''  interpreter ''' 
import string

class ServerClientInterpreter():
    '''Constants '''
    FIELD_SEPARATOR = '\r\n'
    KEY_SEPARATOR = '='

    def __init__(self):
        self.on_wait_for_opponent = None
        self.on_game_starting = None
        self.on_snapshot = None
        self.buffer = ''

    def parse(self, payload):
        self.buffer += payload
        while True:
            pos = self.buffer.find('\r\n\r\n')
            if pos == -1:
                return
            message = self.buffer[0:pos]
            self.buffer = self.buffer[pos + 4: len(self.buffer)]
            fields = string.split(message, self.FIELD_SEPARATOR)
            dict = {}
            for i in range(len(fields)):
                field = string.split(fields[i], self.KEY_SEPARATOR)
                if len(field) == 0:
                    continue # separador
                if len(field) < 2:
                    raise Exception('Mensaje mal formado')
                dict[field[0]] = field[1]
            if dict['command'] == 'wait for opponent':
                if self.on_wait_for_opponent:
                    self.on_wait_for_opponent()
            elif dict['command'] == 'game starting':
                if self.on_game_starting:
                    self.on_game_starting(dict['side'], dict['opponent'])
            elif dict['command'] == 'snapshot':
                if self.on_snapshot:
                    self.on_snapshot(dict['ball x'], dict['ball y'], dict['player1 x'], dict['player1 y'], dict['player2 x'], dict['player2 y'])
            elif dict['command'] == 'game finished':
                self.on_game_finished(dict['player1 score'], dict['player2 score'])

    def build_registration(self, name):
        message = 'command=register\r\n'
        message += 'name=%s\r\n' % name
        message += '\r\n'
        return message

    def build_direction_change(self, direction):
        message = 'command=update\r\n'
        if direction == 'UP':
            message += 'direction=up\r\n'
        elif direction == 'DOWN':
            message += 'direction=down\r\n'
        elif direction == 'NONE':
            message += 'direction=none\r\n'
        message += '\r\n'
        return message
