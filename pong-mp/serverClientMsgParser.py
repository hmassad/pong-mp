import string

'''Constants '''
SEPARATOR = ';'
NUMBER_OF_FIELDS = 7

'''  parser ''' 
class ServerClientMsgParser():

    def __init__(self):
        self.on_connected = None
        self.on_snapshot = None

    def parse(self, payload):
        fields = string.split(payload, SEPARATOR) 
        
        '''initializing variables'''
        ballX=0
        ballY=0
        timecode=0
        player1Position=0
        player2Position=0
        player1Score=0
        player2Score=0
        
        try:
            if len(fields) != NUMBER_OF_FIELDS:
                raise IndexError()
            
            ballX=int(fields[0])
            ballY=int(fields[1])
            timecode=int(fields[2])
            player1Position=int(fields[3])
            player2Position=int(fields[4])
            player1Score=int(fields[5])
            player2Score=int(fields[6])
            
        except IndexError:
            print "The received string is out of bounds"
        except ValueError:
            print "The value is not a number"
        except:
            print "Unknown Error"

        if True:
            if self.on_connected:
                self.on_connected()
        elif True: #mensaje de snapshot
            if self.on_snapshot:
                self.on_snapshot(ballX,ballY,timecode,player1Position,player2Position,player1Score,player2Score)

