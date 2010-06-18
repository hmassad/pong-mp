''' sockets '''
import socket
import threading
import Queue

class TCPServerClient(threading.Thread):
    def __init__ (self, token, socket, addr, timeout):
        threading.Thread.__init__(self)
        self.token = token
        self.socket = socket
        self.timeout = timeout

        # eventos
        self.on_disconnected = None
        self.on_sent = None
        self.on_received = None
        self.on_error = None

        self.queue = Queue.Queue(20)

        self.timer = threading.Timer(self.timeout, self.timer_timer)
        self.timer.start()

    def run(self):
        self.terminated = False
        
        self.socket.settimeout(self.timeout)
        while not self.terminated:
            try:
                data = self.socket.recv(4096)
                if not data:
                    self.queue.put(('disconnected', data))
                    break
                self.queue.put(('received', data))
            except socket.timeout as e:
                pass
            except Exception as e:
                if not self.terminated:
                    self.queue.put(('error', e.args))
                return

    def send(self, data):
        try:
            self.socket.send(data)
            if self.on_sent:
                self.on_sent(self)
        except Exception as exception:
            if self.on_error:
                self.on_error(self, exception.args)

    def timer_timer(self):
        self.timer.cancel()
        del self.timer
        self.timer = None

        while not self.queue.empty():
            task = self.queue.get(True, self.timeout)
            if task[0] == 'error':
                if self.on_error:
                    self.on_error(self, task[1])
                return
            elif task[0] == 'disconnected':
                if self.on_disconnected:
                    self.on_disconnected(self)
                    return
            elif task[0] == 'received':
                if self.on_received:
                    self.on_received(self, task[1])
                self.queue.task_done()

        self.timer = threading.Timer(self.timeout, self.timer_timer)
        self.timer.start()

    def close(self):
        while self.isAlive():
            self.terminated = True
            self.join(self.timeout)
        if self.timer:
            self.timer.cancel()
            del self.timer
        if self.socket:
            self.socket.close()
            del self.socket

class TCPServer(threading.Thread):
    def __init__ (self, port, timeout):
        threading.Thread.__init__(self)
        self.port = port
        self.timeout = timeout
        
        self.socket = None
        self.clients = []
        self.queue = None
        
        # eventos de servidor
        self.on_opened = None
        self.on_closed = None
        self.on_error = None

        # eventos de cliente
        self.on_client_connected = None
        self.on_client_disconnected = None
        self.on_client_sent = None
        self.on_client_received = None
        self.on_client_error = None

    def run(self):
        self.terminated = False
        while not self.terminated:
            try:
                sock, addr = self.socket.accept()
                self.queue.put((sock, addr))
            except:
                if not self.terminated:
                    if self.on_error: 
                        self.on_error(-1)
                break
        
    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))
        self.socket.listen(1)
        self.queue = Queue.Queue(10)
        self.start()

        self.timer = threading.Timer(self.timeout, self.timer_timer)
        self.timer.start()
        
        if self.on_opened:
            self.on_opened()

    def close(self):
        while self.isAlive():
            self.terminated = True
            self.join(self.timeout)
        if self.socket:
            self.socket.close()
            for client in self.clients:
                self.kill_client(client)
        if self.on_closed:
            self.on_closed()

    def send(self, client_token, message):
        for i in range(len(self.clients)):
            if self.clients[i].token == client_token:
                self.clients[i].send(message)
                break

    def client_disconnected(self, client):
        self.kill_client(client)
        if self.on_client_disconnected:
            self.on_client_disconnected(client.token)

    def client_error(self, client, message):
        self.kill_client(client)
        if self.on_client_error:
            self.on_client_error(client.token, message)

    def client_sent(self, client):
        if self.on_client_sent:
            self.on_client_sent(client.token)

    def client_received(self, client, data):
        client.join(self.timeout)
        if self.on_client_received:
            self.on_client_received(client.token, data)

    def generate_token(self):
        if len(self.clients) == 0:
            return 0
        return self.clients[-1].token + 1

    def kill_client(self, client):
        self.clients.remove(client)
        while client.isAlive():
            client.terminated = True
            client.join(self.timeout)

    def timer_timer(self):
        self.timer.cancel()
        del self.timer
        self.timer = None

        while not self.queue.empty():
            task = self.queue.get(True, self.timeout)
            if not task:
                if self.on_error:
                    self.on_error(self)
                break
            else:
                token = self.generate_token()
                client = TCPServerClient(token, task[0], task[1], self.timeout)
                client.on_disconnected = self.client_disconnected
                client.on_error = self.client_error
                client.on_sent = self.client_sent
                client.on_received = self.client_received
                self.clients.append(client)
                client.start()
                if self.on_client_connected:
                    self.on_client_connected(token)
            self.queue.task_done()

        self.timer = threading.Timer(self.timeout, self.timer_timer)
        self.timer.start()
        