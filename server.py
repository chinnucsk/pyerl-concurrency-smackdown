#!/usr/bin/env python2

import socket
import threading
import time

HOST = ''
PORT = 7000
BACKLOG = 5
RECV_BUF = 1024
WORK_DELAY = 100

handler_count = None

class Counter(object):

    def __init__(self):
        self.lock = threading.Lock()
        self.count = 0

    def incr(self):
        with self.lock:
            self.count = self.count + 1
            return self.count

    def decr(self):
        with self.lock:
            self.count = self.count - 1
            return self.count

class Handler(threading.Thread):

    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        self.client.recv(RECV_BUF)
        time.sleep(WORK_DELAY / 1000.0)
        self.client.send("HTTP/1.1 200 OK\r\n"
                         "Content-Length: 5\r\n"
                         "Content-Type: text/plain\r\n"
                         "\r\n"
                         "hello")
        self.client.close()
        handler_counter.decr()

def serve_forever():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(BACKLOG)
    print "Python server is listening on port %i" % PORT
    while True:
        client, peer = s.accept()
        active_handlers = handler_counter.incr()
        print "%i %05.i %s" % (time.time() * 1000, active_handlers,
                            format_peer(peer))
        Handler(client).start()

def format_peer((Address, Port)):
    return "%s:%i" % (Address, Port)

if __name__ == '__main__':
    global handler_counter
    handler_counter = Counter()
    serve_forever()