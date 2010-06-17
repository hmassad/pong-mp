'''  interpreter ''' 
import string
import threading

class ClientServerInterpreter():
    '''Constants '''
    FIELD_SEPARATOR = '\r\n'
    KEY_SEPARATOR = '='

    def __init__(self):
        self.buffer = ''
        self.lock = threading.Lock()

        # variables auxiliares
        self.pos = -1
        self.message = None

        # eventos
        self.on_client_register = None
        self.on_client_update = None

    def parse(self, client_token, payload):
        # guardar el mensaje en el buffer protegido
        with self.lock:
            self.buffer += payload

        while True:
            terminator = self.FIELD_SEPARATOR + self.FIELD_SEPARATOR

            # leer del buffer protegido
            with self.lock:
                self.pos = self.buffer.find(terminator)
                if self.pos == -1:
                    return
                self.message = self.buffer[0:self.pos]
                self.buffer = self.buffer[self.pos + (len(terminator)): len(self.buffer)]

            # seguir procesando normalmente
            fields = string.split(self.message, self.FIELD_SEPARATOR)
            dict = {}
            for i in range(len(fields)):
                field = string.split(fields[i], self.KEY_SEPARATOR)
                if len(field) == 0:
                    continue # separador
                if len(field) < 2:
                    raise Exception('Mensaje mal formado', self.message)
                dict[field[0]] = field[1]
            try:
                if dict['command'] == 'register':
                    if self.on_client_register:
                        self.on_client_register(client_token, dict['name'])
                
                if dict['command'] == 'update':
                    if self.on_client_update:
                        self.on_client_update(client_token, dict['direction'])
            except Exception as e:
                print e.args
                print dict
        
    def build_wait_for_opponent(self):
        message = 'command%swait for opponent%s' % (self.KEY_SEPARATOR, self.FIELD_SEPARATOR)
        message += self.FIELD_SEPARATOR
        return message

    def build_game_starting(self, interval, side, opponent):
        message = 'command%sgame starting%s' % (self.KEY_SEPARATOR, self.FIELD_SEPARATOR)
        message += 'interval%s%d%s' % (self.KEY_SEPARATOR, interval, self.FIELD_SEPARATOR)
        message += 'side%s%s%s' % (self.KEY_SEPARATOR, side, self.FIELD_SEPARATOR)
        message += 'opponent%s%s%s' % (self.KEY_SEPARATOR, opponent, self.FIELD_SEPARATOR)
        message += self.FIELD_SEPARATOR
        return message

    def build_snapshot(self, b_x, b_y, p1_x, p1_y, p1_s, p2_x, p2_y, p2_s):
        message = 'command%ssnapshot%s' % (self.KEY_SEPARATOR, self.FIELD_SEPARATOR)
        message += 'ball x%s%d%s' % (self.KEY_SEPARATOR, b_x, self.FIELD_SEPARATOR)
        message += 'ball y%s%d%s' % (self.KEY_SEPARATOR, b_y, self.FIELD_SEPARATOR)
        message += 'player1 x%s%d%s' % (self.KEY_SEPARATOR, p1_x, self.FIELD_SEPARATOR)
        message += 'player1 y%s%d%s' % (self.KEY_SEPARATOR, p1_y, self.FIELD_SEPARATOR)
        message += 'player1 score%s%d%s' % (self.KEY_SEPARATOR, p1_s, self.FIELD_SEPARATOR)
        message += 'player2 x%s%d%s' % (self.KEY_SEPARATOR, p2_x, self.FIELD_SEPARATOR)
        message += 'player2 y%s%d%s' % (self.KEY_SEPARATOR, p2_y, self.FIELD_SEPARATOR)
        message += 'player2 score%s%d%s' % (self.KEY_SEPARATOR, p2_s, self.FIELD_SEPARATOR)
        message += self.FIELD_SEPARATOR
        return message

    def build_game_finished(self, p1_name, p1_score, p2_name, p2_score):
        message = 'command=game finished'
        message += 'player1 name%s%d%s' % (self.KEY_SEPARATOR, p1_score, self.FIELD_SEPARATOR)
        message += 'player1 score%s%d%s' % (self.KEY_SEPARATOR, p1_score, self.FIELD_SEPARATOR)
        message += 'player2 name%s%d%s' % (self.KEY_SEPARATOR, p2_score, self.FIELD_SEPARATOR)
        message += 'player2 score%s%d%s' % (self.KEY_SEPARATOR, p1_score, self.FIELD_SEPARATOR)
        message += self.FIELD_SEPARATOR
        return message
