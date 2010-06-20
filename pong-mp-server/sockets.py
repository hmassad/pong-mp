''' sockets '''
import socket
import threading
import Queue

class TCPServerClient(threading.Thread):
    def __init__ (self, token, socket, addr, timeout, message_terminator):
        threading.Thread.__init__(self, name='TCPServerClient%d' % (token))
        self.token = token
        self.socket = socket
        self.timeout = timeout
        self.message_terminator = message_terminator

        self.__terminated = False
        self.__buffer = ''
        self.__buffer_lock = threading.Lock()

        # eventos
        self.on_disconnected = None
        self.on_sent = None
        self.on_received = None
        self.on_error = None

        self.__queue = Queue.Queue(20)

        self.__timer = threading.Timer(self.timeout, self.__timer_expired)
        self.__timer.start()

    def run(self):
        self.__terminated = False
        
        self.socket.settimeout(self.timeout)
        while not self.__terminated:
            try:
                data = self.socket.recv(8192)
                if not data:
                    self.__queue.put(('disconnected', data))
                    return
                self.__queue.put(('received', data))
            except socket.timeout as e:
                pass
            except Exception as e:
                if not self.__terminated:
                    self.__queue.put(('error', e.args))
                return

    def send(self, data):
        try:
            self.socket.send(data)
            if self.on_sent:
                self.on_sent(self)
        except Exception as exception:
            if self.on_error:
                self.on_error(self, exception.args)

    def __timer_expired(self):
        self.__timer.cancel()
        del self.__timer
        self.__timer = None

        while not self.__queue.empty():
            task = self.__queue.get(True, self.timeout)
            if task[0] == 'error':
                if self.on_error:
                    self.on_error(self, task[1])
                return
            elif task[0] == 'disconnected':
                if self.on_disconnected:
                    self.on_disconnected(self)
                return
            elif task[0] == 'received':
                # guardar lo reibido en el __buffer
                self.__buffer_lock.acquire()
                try:
                    self.__buffer += task[1]
                    
                    while True:
                        pos = self.__buffer.find(self.message_terminator)
                        if pos == -1:
                            break
                        payload = self.__buffer[0:pos]
                        self.__buffer = self.__buffer[pos + (len(self.message_terminator)): len(self.__buffer)]
    
                        if self.on_received:
                            self.on_received(self, payload)
                finally:
                    self.__buffer_lock.release()

            self.__queue.task_done()

        self.__timer = threading.Timer(self.timeout, self.__timer_expired)
        self.__timer.start()

    def close(self):
        while self.isAlive():
            self.__terminated = True
            self.join(self.timeout)
        if self.__timer:
            self.__timer.cancel()
            self.__timer = None
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
                self.socket = None
            except:
                pass

class TCPServer(threading.Thread):
    def __init__ (self, port, timeout, message_terminator):
        threading.Thread.__init__(self, name='TCPServer')
        self.port = port
        self.timeout = timeout
        self.message_terminator = message_terminator

        self.__last_token = 0
        self.socket = None
        self.clients = []
        self.__queue = None
        
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
        self.__terminated = False
        while not self.__terminated:
            try:
                sock, addr = self.socket.accept()
                self.__queue.put((sock, addr))
            except Exception as e:
                if not self.__terminated:
                    if self.on_error: 
                        self.on_error(e)
                break

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))
        self.socket.listen(1)
        self.__queue = Queue.Queue(10)
        self.start()

        self.__timer = threading.Timer(self.timeout, self.__timer_expired)
        self.__timer.start()
        
        if self.on_opened:
            self.on_opened()

    def close(self):
        while self.isAlive():
            self.__terminated = True
            self.join(self.timeout)
        if self.socket:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            for client in self.clients:
                self.__kill_client(client)
        if self.on_closed:
            self.on_closed()

    def send(self, client_token, message):
        for client in self.clients:
            if client.token == client_token:
                client.send(message)
                return

    def __client_disconnected(self, client):
        self.__kill_client(client)
        if self.on_client_disconnected:
            self.on_client_disconnected(client.token)

    def __client_error(self, client, message):
        self.__kill_client(client)
        if self.on_client_error:
            self.on_client_error(client.token, message)

    def __client_sent(self, client):
        if self.on_client_sent:
            self.on_client_sent(client.token)

    def __client_received(self, client, data):
        client.join(self.timeout)
        if self.on_client_received:
            self.on_client_received(client.token, data)

    def __generate_token(self):
        self.__last_token += 1
        return self.__last_token

    def __kill_client(self, client):
        client.close()
        try:
            self.clients.remove(client)
        except Exception as e:
            # @TODO: ver como obtener el nombre del thread en ejecucion
            print '__kill_client, thread=%s, error=%s' % ('?', e.args)

    def __timer_expired(self):
        self.__timer.cancel()
        del self.__timer
        self.__timer = None

        while not self.__queue.empty():
            task = self.__queue.get(True, self.timeout)
            if not task:
                if self.on_error:
                    self.on_error(('Queue.get == None',))
                break
            else:
                token = self.__generate_token()
                client = TCPServerClient(token, task[0], task[1], self.timeout, self.message_terminator)
                client.on_disconnected = self.__client_disconnected
                client.on_error = self.__client_error
                client.on_sent = self.__client_sent
                client.on_received = self.__client_received
                self.clients.append(client)
                client.start()
                if self.on_client_connected:
                    self.on_client_connected(token)
            self.__queue.task_done()

        self.__timer = threading.Timer(self.timeout, self.__timer_expired)
        self.__timer.start()
        
