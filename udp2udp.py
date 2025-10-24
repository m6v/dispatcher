#!/usr/bin/env python3
import asyncio
import configparser
import functools
from ipaddress import ip_address
import json
import jsonschema
import logging
import os
import sys

import validator

INITIAL_DIR = CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
# Если установлена переменная окружения _MEIPASS, программа запущена
# из временного каталога, созданного при распаковке бандла
if hasattr(sys, "_MEIPASS"):
    # Путь к временному каталогу взять из sys.executable
    INITIAL_DIR = os.path.dirname(sys.executable)

app_name = os.path.basename(__file__)
# Если путь к конфигу не задан, использовать путь исполняемого файла
if len(sys.argv) == 1:
    config_file = os.path.join(INITIAL_DIR, f"{os.path.splitext(app_name)[0]}.conf")
elif len(sys.argv) == 2:
    config_file = os.path.join(INITIAL_DIR, sys.argv[1])
else:
    print(f"Error: Extra parameters are not allowed. Usage: {app_name} [config_file]")
    sys.exit(1)

# Для логирования в файл, добавить параметр filename, иначе лог в консоль
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

config = configparser.ConfigParser(allow_no_value=True)
# Установить чувствительность ключей к регистру
config.optionxform = str

logging.debug(f"Reading config file {config_file}")
try:
    with open(config_file) as file:
        # Используем config.read_file, т.к. config.read
        # не выбрасывает исключения при отсутствии файла
        config.read_file(file)
except FileNotFoundError as err:
    logging.error(err)
    sys.exit(1)

try:
    bind, port = config.get("general", "listen").split(":")
    remote_host, remote_port = config.get("general", "remote").split(":")
    # Если работа без валидации сообщений не допускается, убрать fallback=""
    # validate = validator.xml_validator(config.get("general", "schema", fallback=""))
    validate = validator.validator(config.get("general", "schema", fallback=""))
except (configparser.NoOptionError, ValueError) as err:
    logging.error(err)
    sys.exit(1)


class ProxyDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(self, remote_address):
        self.remote_address = remote_address
        self.remotes = {}
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        logging.info(f"From {addr[0]}:{addr[1]} received request {data}")

        if not validate(data):
            logging.info("Validation error!")
            return

        if addr in self.remotes:
            self.remotes[addr].transport.sendto(data)
            return

        loop = asyncio.get_event_loop()
        self.remotes[addr] = RemoteDatagramProtocol(self, addr, data)
        coro = loop.create_datagram_endpoint(lambda: self.remotes[addr], remote_addr=self.remote_address)
        asyncio.ensure_future(coro)


class RemoteDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(self, proxy, addr, data):
        self.proxy = proxy
        self.addr = addr
        self.data = data
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(self.data)

    def datagram_received(self, data, _):
        logging.info(f"Received response {data}")
        self.proxy.transport.sendto(data, self.addr)

    def connection_lost(self, exc):
        self.proxy.remotes.pop(self.attr)


async def start_datagram_proxy(bind: str, port: int, remote_host: str, remote_port: int):
    loop = asyncio.get_event_loop()
    protocol = ProxyDatagramProtocol((remote_host, remote_port))
    return await loop.create_datagram_endpoint(lambda: protocol, local_addr=(bind, port))


def main():
    # https://stackoverflow.com/questions/73361664/asyncio-get-event-loop-deprecationwarning-there-is-no-current-event-loop
    # https://bobbyhadz.com/blog/deprecationwarning-there-is-no-current-event-loop
    # Начиная с Python 3.11 asyncio.get_event_loop() считается устаревшей и
    # в некоторых ситуациях может приводить к ошибкам, лучше использовать
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # TODO Посмотреть как будет работать в Астре 1.7, а также разобраться с loop.run_until_complete()
    loop = asyncio.get_event_loop()
    logging.info("Starting datagram proxy...")
    # Передать адреса через ip_address, чтобы при неправильном формате вызвать исключение ValueError
    coro = start_datagram_proxy(str(ip_address(bind)), int(port), str(ip_address(remote_host)), int(remote_port))
    transport, _ = loop.run_until_complete(coro)
    logging.info("Datagram proxy is running...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    logging.info("Closing transport...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()
