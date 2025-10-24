#!/usr/bin/env python3
import asyncio
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
        file = open(sys.argv[1])
    else:
        file = sys.stdin
    msg = file.read().rstrip()
except FileNotFoundError:
    logging.error("Файл с сообщением не найден")
    sys.exit(1)
except IndexError:
    logging.error("Сообщение не задано")
    sys.exit(1)

data = str.encode(msg)
logging.info(f"Send {data}")

# Реализация отправки udp датаграмм с помощью asyncio
async def send_datagram():
    # в local_addr можно задавать конкретный порт, 0 - выбирается случайно из незанятых
    transport, protocol = await asyncio.get_event_loop().create_datagram_endpoint(
        asyncio.DatagramProtocol,
        local_addr=('127.0.0.1', 0)
    )
    transport.sendto(data, ('127.0.0.1', 14550))


# asyncio.run(send_datagram())


async def main():
    send_task = asyncio.create_task(send_datagram())
    result = await asyncio.wait_for(send_task, timeout=5)

asyncio.run(main())



'''
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.sendto(data, addr)

data = UDPClientSocket.recvfrom(bufferSize)
logging.info(f"Recieve {data[0]}")
'''
