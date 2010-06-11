''' sockets '''
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep

class SocketListener(Thread):
    def __init__(self, socket):
        Thread.__init__(self)
        self.socket = socket
        self.on_receive = None
        self.on_error = None

    def run(self):
        self.terminated = False
        data = ''
        # Para http. Si llega un "enter enter", se termino el mensaje
        while not self.terminated:
            try:
                data += self.socket.recv(65535)
                if (len(data) > 2) and (data[-4:len(data)] == '\r\n\r\n'):
                    if self.on_receive:
                        self.on_receive(data)
                    data = ''
            except:
                if self.on_error and not self.terminated:
                    self.on_error()
                break

    
class TCPClientSocket:

    def __init__(self, serverip, serverport):
        self.serverip = serverip;
        self.serverport = serverport;
        
        self.socket_listener = None
        
        # events
        self.on_connected = None
        self.on_disconnected = None
        self.on_error = None
        self.on_sent = None
        self.on_received = None

    def connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(2)
        self.socket.connect((self.serverip, self.serverport))

        self.socket_listener = SocketListener(self.socket)
        self.socket_listener.on_receive = self.socket_listener_receive
        self.socket_listener.on_error = self.socket_listener_error
        self.socket_listener.start()
        
        if self.on_connected:
            self.on_connected()
    
    def disconnect(self):
        # matar thread
        self.socket.close()
        while self.socket_listener and self.socket_listener.isAlive():
            self.socket_listener.terminated = True
            self.socket_listener.join(1)
            
        if self.on_disconnected:
            self.on_disconnected()

    def send(self, mensaje):
        self.socket.send(mensaje)
        if self.on_sent:
            self.on_sent()

    def socket_listener_error(self):
        if self.on_error:
            self.on_error()

    def socket_listener_receive(self, data):
        if self.on_received:
            self.on_received(data)

''' pruebas '''
if __name__ == '__main__':
    def cs_connected():
        print 'socket connected'
    def cs_disconnected():
        print 'socket disconnected'
    def cs_error():
        print 'socket error'
    def cs_sent():
        print 'request sent'
    def cs_received(msj):
        print '--- response begin ---\n', msj, '\n--- response end ---'
        
    cs = TCPClientSocket('www.example.com', 80)
    cs.on_connected = cs_connected
    cs.on_disconnected = cs_disconnected
    cs.on_error = cs_error
    cs.on_sent = cs_sent
    cs.on_received = cs_received
    
    cs.connect()
    #httpclient.enviar('GET /search?q=hernan HTTP/1.1\nHost: www.google.com\nUser-Agent: Mozilla/4.0\nContent-Length: 8\nContent-Type: application/x-www-form-urlencoded\n\nq=hernan\n\n')
    #cs.send('GET /search?q=hernan HTTP/1.1\nHost: www.google.com\nUser-Agent: Mozilla/4.0\nContent-Length: 0\n\n')
    cs.send('GET / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: Mozilla/4.0\r\n\r\n')
    cs.send('GET / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: Mozilla/4.0\r\n\r\n')
    cs.send('GET / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: Mozilla/4.0\r\n\r\n')
    sleep(1)
    cs.disconnect()
