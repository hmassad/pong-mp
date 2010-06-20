'''  interpreter ''' 
import string

class ClientServerInterpreter():
    '''Constants '''
    FIELD_SEPARATOR = '\r\n'
    KEY_SEPARATOR = '='
    TERMINATOR = FIELD_SEPARATOR + FIELD_SEPARATOR

    def __init__(self):
        # eventos
        self.on_client_register = None
        self.on_client_update = None
        self.on_client_unregister = None

    def parse(self, token, payload):
        fields = string.split(payload, self.FIELD_SEPARATOR)
        dict = {}
        for i in range(len(fields)):
            field = string.split(fields[i], self.KEY_SEPARATOR)
            if len(field) == 0:
                continue # separador
            if len(field) < 2:
                raise Exception('Mensaje mal formado: "%s"' % payload)
            dict[field[0]] = field[1]

        if dict['command'] == 'register':
            if self.on_client_register:
                self.on_client_register(token, dict['name'])
        
        if dict['command'] == 'unregister':
            if self.on_client_unregister:
                self.on_client_unregister(token)
        
        if dict['command'] == 'update':
            if self.on_client_update:
                self.on_client_update(token, dict['direction'])
        
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
        message = 'command%sgame finished%s' % (self.KEY_SEPARATOR, self.FIELD_SEPARATOR)
        message += 'player1 name%s%s%s' % (self.KEY_SEPARATOR, p1_name, self.FIELD_SEPARATOR)
        message += 'player1 score%s%d%s' % (self.KEY_SEPARATOR, p1_score, self.FIELD_SEPARATOR)
        message += 'player2 name%s%s%s' % (self.KEY_SEPARATOR, p2_name, self.FIELD_SEPARATOR)
        message += 'player2 score%s%d%s' % (self.KEY_SEPARATOR, p2_score, self.FIELD_SEPARATOR)
        message += self.FIELD_SEPARATOR
        return message
