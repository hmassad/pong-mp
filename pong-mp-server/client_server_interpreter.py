'''  interpreter ''' 
import string

class ClientServerInterpreter():
    '''Constants '''
    FIELD_SEPARATOR = '\r\n'
    KEY_SEPARATOR = '='

    def __init__(self):
        self.buffer = ''

        # eventos
        self.on_client_register = None
        self.on_client_update = None

    def parse(self, client_token, payload):
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
            if dict['command'] == 'register':
                if self.on_client_register:
                    self.on_client_register(client_token, dict['name'])
            
            if dict['command'] == 'update':
                if self.on_client_update:
                    self.on_client_update(client_token, dict['direction'])
        
    def build_wait_for_opponent(self):
        message = 'command=wait for opponent\r\n'
        message += '\r\n'
        return message

    def build_game_starting(self, side, opponent):
        message = 'command=game starting\r\n'
        message += 'side=%s\r\n' % side
        message += 'opponent=%s\r\n' % opponent 
        message += '\r\n'
        return message

    def build_snapshot(self, b_x, b_y, p1_x, p1_y, p2_x, p2_y):
        message = 'command=snapshot'
        message += 'ball x=%d\r\n' % b_x
        message += 'ball y=%d\r\n' % b_y
        message += 'player1 x=%d\r\n' % p1_x
        message += 'player1 y=%d\r\n' % p1_y
        message += 'player2 x=%d\r\n' % p2_x
        message += 'player2 y=%d\r\n' % p2_y
        message += '\r\n'
        return message

    def build_game_finished(self, p1_score, p2_score):
        message = 'command=game finished'
        message += 'player1 score=%d\r\n' % p1_score
        message += 'player2 score=%d\r\n' % p2_score
        message += '\r\n'
        return message
