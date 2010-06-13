'''Constants '''
UP_ACTION = "UP"
NONE_ACTION = "NONE"
DOWN_ACTION = "DOWN"

'''  parser ''' 
class ClientServerMsgParser():

    def __init__(self):
        self.on_connected = None
        self.on_snapshot = None

    def parse(self, payload):
        '''initializing variables'''
        userAction= payload
        
        try:
            if userAction != UP_ACTION or userAction != DOWN_ACTION or userAction != NONE_ACTION:
                raise ValueError()
            
        except ValueError:
            print "The value is not valid"
        except:
            print "Unknown Error"
            
        ''' hacer algo con userAction '''
        
         