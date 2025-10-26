#!/usr/bin/env python3
import logging
import socket
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

addr = ("127.0.0.1", 14550)
bufferSize = 1024
timeout = 5

try:
    # Если стандартный ввод пустой, попытаться открыть файл,
    # заданный в первом аргументе, иначе читать из стандарного ввода
    if sys.stdin.isatty():
        file = open(sys.argv[1])
    else:
        file = sys.stdin
    msg = file.read().rstrip()
except FileNotFoundError:
    logging.error(f"File {sys.argv[1]} not found")
    sys.exit(1)
except IndexError:
    logging.error("The message is not set")
    sys.exit(1)

data = str.encode(msg)
logging.info(f"Send: {data}")

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.settimeout(timeout)
s.connect(addr)
s.send(data)

try:
    response = s.recv(bufferSize)
    logging.info(f"Recieve: {response}")
except socket.timeout:
    logging.error("Didn't receive data! [Timeout]")
finally:
    s.close()
