#!/usr/bin/env python3
import asyncio
import configparser
from ipaddress import ip_address
import json
import jsonschema
import logging
import os
import sys


INITIAL_DIR = CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
# Если установлена переменная окружения _MEIPASS, программа запущена
# из временного каталога, созданного при распаковке бандла
if hasattr(sys, "_MEIPASS"):
    # Путь к временному каталогу взять из sys.executable
    INITIAL_DIR = os.path.dirname(sys.executable)

# Для логирования в файл, добавить параметр filename, иначе лог в консоль
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

config = configparser.ConfigParser(allow_no_value=True)
# Установить чувствительность ключей к регистру
config.optionxform = str

# Если путь не задан, использовать путь исполняемого файла
config_file = os.path.join(INITIAL_DIR, "udp2udp.conf")
logging.debug(f"Reading config file {config_file}")
# Используем config.read_file, т.к. config.read не выбрасывает исключения при отсутствии файла
try:
    with open(config_file) as f:
        config.read_file(f)
except FileNotFoundError as err:
    logging.error(err)
    sys.exit(1)

try:
    bind, port = config.get("general", "listen").split(":")
    remote_host, remote_port = config.get("general", "remote").split(":")
    schema = config.get("general", "schema", fallback="")
except (configparser.NoOptionError, ValueError) as err:
    logging.error(err)
    sys.exit(1)

try:
    # Если задан файл со схемой данных, прочитать ее в schema
    if config.get("general", "schema", fallback=""):
        with open(config.get("general", "schema", fallback="")) as f:
            schema = json.load(f)
        logging.debug(schema)
    else:
        schema = ""
        logging.warning("Schema not defined")
except (FileNotFoundError) as err:
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
        logging.info(f"Proxy datagram received: {data}")
        try:
            # Если задана схема данных, выполнить валидацию data
            if schema:
                jsonschema.validate(instance=json.loads(data.decode()), schema=schema)
                logging.debug("Data is validated")

            if addr in self.remotes:
                self.remotes[addr].transport.sendto(data)
                return
            loop = asyncio.get_event_loop()
            self.remotes[addr] = RemoteDatagramProtocol(self, addr, data)
            coro = loop.create_datagram_endpoint(
                lambda: self.remotes[addr], remote_addr=self.remote_address)
            asyncio.ensure_future(coro)

        except json.decoder.JSONDecodeError as err:
            logging.info(f"Data format error: {err}")
        except jsonschema.exceptions.ValidationError as err:
            logging.info(f"Data validation error: {err.message}")


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
        logging.info(f"Remote datagram received: {data}")
        self.proxy.transport.sendto(data, self.addr)

    def connection_lost(self, exc):
        self.proxy.remotes.pop(self.attr)


async def start_datagram_proxy(bind: str, port: int, remote_host: str, remote_port: int):
    loop = asyncio.get_event_loop()
    protocol = ProxyDatagramProtocol((remote_host, remote_port))
    return await loop.create_datagram_endpoint(
        lambda: protocol, local_addr=(bind, port))


def main():
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
