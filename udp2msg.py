#!/usr/bin/env python3
import logging
import socket
from lxml import etree

# Для логирования в файл, добавить параметр filename, иначе лог в консоль
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

def main(addr="127.0.0.1", port=12200, bufsize=1024):
    reply = str.encode("UDP server recieved message")

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((addr, port))

    logging.info("UDP server up and listening...")

    while(True):
        data, address = UDPServerSocket.recvfrom(bufsize)

        msg = "Message from {}: {}".format(address, data)
        logging.info(msg)

        root = etree.fromstring(data.decode())
        for item in root.xpath('//person'):
            identifier = item.find('id').text
            name = item.find('name').text
            age = item.find('age').text
            logging.info(f'Get msg id={identifier}, name={name}, age={age}')
            reply =str.encode(f"<reply1>{identifier}</reply1>")
            UDPServerSocket.sendto(reply, address)

if __name__ == '__main__':
    main()
