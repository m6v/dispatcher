#!/usr/bin/env python3
import json
import logging
import socket
import sys

# Для логирования в файл, добавить параметр filename, иначе лог в консоль
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

addr = ("127.0.0.1", 14550)
bufferSize = 1024

try:
    # Если стандартный ввод пустой, попытаться открыть файл,
    # заданный в первом аргументе, иначе читать из стандарного ввода
    if sys.stdin.isatty():
        f = open(sys.argv[1])
    else:
        f = sys.stdin
    msg = json.load(f)
except FileNotFoundError:
    logging.error("Файл с сообщением не найден")
    sys.exit(1)
except IndexError:
    logging.error("Сообщение не задано")
    sys.exit(1)

data = str.encode(json.dumps(msg))
logging.info(f"Send {data}")
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.sendto(data, addr)

data = UDPClientSocket.recvfrom(bufferSize)
logging.info(f"Recieve {data[0]}")
