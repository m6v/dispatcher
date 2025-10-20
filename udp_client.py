#!/usr/bin/env python3
import json
import socket
import time

addr = ("127.0.0.1", 14550)
bufferSize = 1024

# Передаваемое сообщение
msg = {"name": "Sergey Maksimov", "age": 52}
data = str.encode(json.dumps(msg))
# data = str.encode("Unknown text!")

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.sendto(data, addr)

data = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from Server {}".format(data[0])
print(msg)


