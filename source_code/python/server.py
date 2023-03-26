import socket
from threading import Thread
from time import sleep
from os import system
system("")

def int_input(s):
    while True:
        r = input(s)
        try: return int(r)
        except ValueError:
            print("\x1b[1A\x1b[K", end = "")
            continue

class sending(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global c, chatting
        while chatting:
            data = input(">> ").encode()
            if not data:
                print("\x1b[1A\x1b[K", end = "")
                continue
            if len(data) > 2048:
                print("Error: message too long(%d bytes)"%len(data))
                continue
            c.sendall(data)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
host = socket.gethostbyname(socket.gethostname())
port = int_input("Port: ")
port = max(1, min(32767, port))
s.bind((host, port))
 
s.listen(5)
print("Waiting...\nIP: %s"%host)
c, addr = s.accept()
print("Connected: " + addr[0])

chatting = True
send_thread = sending()
send_thread.start()
while chatting:
    try:
        print("\x1b[3D%-3s\n>> "%c.recv(2048).decode(), end = "")
    except ConnectionResetError:
        chatting = False
c.close()
s.close()
