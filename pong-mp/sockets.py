''' socket del cliente '''
import socket
import threading
import Queue
import pyglet
import utils

class TCPClientListener(threading.Thread):
    '''
    Thread que escucha al socket.
    '''

    def __init__(self, socket, queue):
        '''
        Inicializacion
        @param socket: socket a escuchar
        @param queue: cola en la que se encolara lo recibido por el socket
        '''
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue
        
    def run(self):
        self.terminated = False
        while not self.terminated:
            try:
                data = self.socket.recv(65535)
                if not data:
                    self.queue.put(('disconnected', None))
                self.queue.put(('received', data))
            except socket.timeout:
                pass
            except Exception as e:
                if not self.terminated:
                    self.queue.put(('error', e.args))
                break

class TCPClient:
    '''
    Socket TCP cliente.
    Se utiliza pyglet.clock para el timer, porque se dibujara a partir de lo recibido por el socket.
    '''

    def __init__(self, server_ip, server_port, timeout):
        '''
        Inicializacion
        @param server_ip: direccion ip de pong-mp-server
        @param server_port: puerto de pong-mp-server
        @param timeout: timeout para las operaciones sobre sockets
        '''
        self.server_ip = server_ip
        self.server_port = server_port
        self.timeout = timeout

        self.__opened = False
        self.socket = None
        self.queue = None
        self.listener = None
        
        # eventos
        self.on_connected = None
        self.on_disconnected = None
        self.on_error = None
        self.on_sent = None
        self.on_received = None
        
    def open(self):
        if not self.__opened:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(self.timeout)
                self.socket.connect((self.server_ip, self.server_port))
            except:
                if self.on_error:
                    self.on_error('No se puede conectar al servidor')
                return
        
            self.queue = Queue.Queue(10)
            pyglet.clock.schedule_interval(self.__timer_expired, self.timeout)

            self.listener = TCPClientListener(self.socket, self.queue)
            self.listener.start()

            self.__opened = True
            if self.on_connected:
                self.on_connected()

    def close(self):
        '''
        Cierra el cliente.
        Cierra el thread que escucha al socket, el socket
        '''
        if self.__opened:
            try:
                pyglet.clock.unschedule(self.__timer_expired)
            except:
                pass
    
            if self.listener:
                try:
                    while self.listener and self.listener.isAlive():
                        self.listener.terminated = True
                        self.listener.join(self.timeout)
                except:
                    pass
                finally:
                    self.listener = None
            
            if self.socket:
                try:
                    self.socket.close()
                except Exception as e:
                    utils.print_exception(e)
                finally:
                    self.socket = None
                    
            if self.queue:
                self.queue = None
    
            self.__opened = False

    def send(self, message):
        '''
        Envia un mensaje al servidor
        @param message: mensaje a enviar por el socket
        '''
        if self.__opened:
            try:
                self.socket.send(message)
                if self.on_sent:
                    self.on_sent()
            except Exception as e:
                self.close()
                if self.on_error:
                    self.on_error(e.args)
                return
        else:
            if self.on_error:
                self.on_error(('socket closed',))

    def __timer_expired(self, dt):
        '''
        Funcion que se ejecuta periodicamente para levantar los mensajes del socket
        @param dt: tiempo transcurrido desde la ultima revision
        '''
        if not self.__opened:
            pyglet.clock.unschedule(self.__timer_expired)
            return

        while self.queue and not self.queue.empty():
            try:
                task = self.queue.get(True, self.timeout)
                if task[0] == 'received':
                    if self.on_received:
                        self.on_received(task[1])
                elif task[0] == 'disconnected':
                    self.close()
                    if self.on_disconnected:
                        self.on_disconnected()
                    return
                elif task[0] == 'error':
                    self.close()
                    if self.on_error:
                        self.on_error(task[1])
                    return
                self.queue.task_done()
            except:
                pass
