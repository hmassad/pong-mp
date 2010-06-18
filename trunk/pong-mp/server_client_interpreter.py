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
            terminator = self.FIELD_SEPARATOR + self.FIELD_SEPARATOR
            pos = self.buffer.find(terminator)
            if pos == -1:
                return
            message = self.buffer[0:pos]
            self.buffer = self.buffer[pos + len(terminator): len(self.buffer)]
            fields = string.split(message, self.FIELD_SEPARATOR)
            dict = {}
            for i in range(len(fields)):
                field = string.split(fields[i], self.KEY_SEPARATOR)
                if len(field) == 0:
                    continue # separador
                if len(field) < 2:
                    raise Exception('Mensaje mal formado', message)
                dict[field[0]] = field[1]
            if dict['command'] == 'wait for opponent':
                if self.on_wait_for_opponent:
                    self.on_wait_for_opponent()
            elif dict['command'] == 'game starting':
                if self.on_game_starting:
                    self.on_game_starting(float(dict['interval']) / 1000, dict['side'], dict['opponent'])
            elif dict['command'] == 'snapshot':
                if self.on_snapshot:
                    self.on_snapshot(dict['ball x'], dict['ball y'], dict['player1 x'], dict['player1 y'], dict['player1 score'], dict['player2 x'], dict['player2 y'], dict['player2 score'])
            elif dict['command'] == 'game finished':
                if self.on_game_finished:
                    self.on_game_starting(dict['player1 name'], dict['player1 score'], dict['player2 name'], dict['player2 score'])

    def build_registration(self, name):
        message = 'command%sregister%s' % (self.KEY_SEPARATOR, self.FIELD_SEPARATOR)
        message += 'name%s%s%s' % (self.KEY_SEPARATOR, name, self.FIELD_SEPARATOR)
        message += self.FIELD_SEPARATOR
        return message

    def build_direction_change(self, direction):
        message = 'command%supdate%s' % (self.KEY_SEPARATOR, self.FIELD_SEPARATOR)
        if direction == 'UP':
            message += 'direction%s%s%s' % (self.KEY_SEPARATOR, 'up', self.FIELD_SEPARATOR)
        elif direction == 'DOWN':
            message += 'direction%s%s%s' % (self.KEY_SEPARATOR, 'down', self.FIELD_SEPARATOR)
        elif direction == 'NONE':
            message += 'direction%s%s%s' % (self.KEY_SEPARATOR, 'none', self.FIELD_SEPARATOR)
        message += self.FIELD_SEPARATOR
        return message
