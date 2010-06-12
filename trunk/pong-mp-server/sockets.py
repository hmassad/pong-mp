''' sockets '''
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

class TCPServerClient(Thread):
    def __init__ (self, token, socket, address):
        Thread.__init__(self)
        self.token = token
        self.socket = socket
        self.address = address

        # eventos
        self.on_sent = None
        self.on_receive = None
        self.on_error = None
        
    def run(self):
        self.terminated = False
        self.socket.settimeout(5)
        while not self.terminated:
            try:
                data = self.socket.recv(65535)
                if self.on_receive:
                    self.on_receive(self, data)
            except:
                if self.on_error and not self.terminated:
                    self.on_error(self)
                break

    def send(self, data):
        self.socket.send(data)
        if self.on_sent:
            self.on_sent(self)
        

class TCPServer(Thread):
    def __init__ (self, port):
        Thread.__init__(self)
        self.port = port
        
        self.clients = []
        
        #eventos
        self.on_opened = None
        self.on_closed = None
        self.on_sent = None
        self.on_received = None
        self.on_error = None
        self.on_client_connected = None
        self.on_client_disconnected = None

    def run(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(('', self.port))
        self.socket.listen(1)

        if self.on_opened:
            self.on_opened()

        self.terminated = False
        while not self.terminated:
            try:
                sock, addr = self.socket.accept()
                token = self.generate_token()
                client = TCPServerClient(token, sock, addr)
                self.clients.append(client)
                client.start()
                if self.on_client_connected:
                    self.on_client_connected(token)
            except:
                if self.on_error and not self.terminated:
                    self.on_error()
                break
        
    def open(self):
        self.run()

    def close(self):
        self.socket.close()
        for i in range(len(self.clients)):
            # matar thread
            while self.clients[i] and self.clients[i].isAlive():
                self.clients[i].terminated = True
                self.clients[i].join(1)
            
        if self.on_closed:
            self.on_closed()

    def send(self, client_token, message):
        for i in range(len(self.clients)):
            if client_token == self.clients[i].token:
                self.clients[i].send(message)
            if self.on_error:
                self.on_error(client_token)

    def socket_client_sent(self, client):
        if self.on_sent:
            self.on_sent(client.token)

    def socket_client_error(self, client):
        if self.on_error:
            self.on_error(client.token)

    def socket_client_receive(self, client, data):
        if self.on_received:
            self.on_received(client.token, data)

    def generate_token(self):
        if len(self.clients) == 0:
            return 0
        return self.clients[-1].token + 1