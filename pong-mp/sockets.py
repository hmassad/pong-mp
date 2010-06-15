''' sockets '''
import socket
import threading
import Queue
import pyglet

GLOBAL_WAITING_INTERVAL = (1/20.)

class TCPSocketListener(threading.Thread):
    def __init__(self, socket, queue):
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue
        
    def run(self):
        self.terminated = False
        while not self.terminated:
            try:
                data = self.socket.recv(65535)
                if not data:
                    self.queue.put(None)
                self.queue.put(data)
            except socket.timeout:
                pass
            except socket.error:
                if not self.terminated:
                    self.queue.put(None)
                break

class TCPClientSocket:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip;
        self.server_port = server_port;

        self.socket = None
        self.socket_listener = None
        
        # events
        self.on_connected = None
        self.on_disconnected = None
        self.on_error = None
        self.on_sent = None
        self.on_received = None
        
        self.queue = None
        self.timer = None
        
    def open(self):
        if not self.socket:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(GLOBAL_WAITING_INTERVAL)
                self.socket.connect((self.server_ip, self.server_port))
            except:
                if self.on_error:
                    self.on_error('No se puede conectar al servidor')
                return
        
            self.queue = Queue.Queue(10)
            
            pyglet.clock.schedule_once(self.on_timer, GLOBAL_WAITING_INTERVAL)

            self.socket_listener = TCPSocketListener(self.socket, self.queue)
            self.socket_listener.start()
            
            if self.on_connected:
                self.on_connected()

    def __kill_listener_thread(self):
        while self.socket_listener and self.socket_listener.isAlive():
            self.socket_listener.terminated = True
            self.socket_listener.join(GLOBAL_WAITING_INTERVAL)
        self.socket_listener = None
        
    def close(self):
        pyglet.clock.unschedule(self.on_timer)

        if self.socket:
            self.kill_listener_thread()
            self.socket.close()
            self.socket = None
                
            if self.queue:
                self.queue = None

    def send(self, mensaje):
        if self.socket:
            self.socket.send(mensaje)
            if self.on_sent:
                self.on_sent()
        else:
            if self.on_error:
                self.on_error()

    def __on_timer(self, dt):
        pyglet.clock.unschedule(self.on_timer)
        if not self.queue:
            return
        while not self.queue.empty():
            data = self.queue.get(False)
            if not data:
                self.kill_listener_thread()
                
                self.socket.close()
                self.socket = None
                
                if self.on_disconnected:
                    self.on_disconnected()
                break
            if self.on_received:
                self.on_received(data) 
        pyglet.clock.schedule_once(self.on_timer, dt)
