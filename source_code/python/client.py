import socket
from threading import Thread
from os import system
system("")

def int_input(s):
    while True:
        r = input(s)
        try: return int(r)
        except ValueError:
            print("\x1b[1A\x1b[K", end = "")
            continue
        
class receiving(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global s, chatting
        while chatting:
            try:
                print("\x1b[3D%-3s\n>> "%s.recv(2048).decode(), end = "")
            except ConnectionResetError:
                chatting = False

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
host = input('IP: ')
port = int_input("Port: ")
port = max(1, min(32767, port))
 
s.connect((host, port))

print("Connected: %s"%host)

chatting = True
recv_thread = receiving()
recv_thread.start()
while chatting:
    data = input(">> ").encode()
    if not data:
        print("\x1b[1A\x1b[K", end = "")
        continue
    if len(data) > 2048:
        print("Error: message too long(%d bytes)"%len(data))
        continue
    s.sendall(data)
s.close()
