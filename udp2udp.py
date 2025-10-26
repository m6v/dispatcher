#!/usr/bin/env python3
import asyncio
import configparser
from ipaddress import ip_address
import logging
import os
import sys

import validator


app_dir, app_name = os.path.split(__file__)
config_file = os.path.join(app_dir, f"{os.path.splitext(app_name)[0]}.conf")
if len(sys.argv) > 1:
    config_file = os.path.join(app_dir, sys.argv[1])

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

config = configparser.ConfigParser(allow_no_value=True)
logging.debug(f"Reading config file {config_file}...")
try:
    with open(config_file) as file:
        config.read_file(file)
except FileNotFoundError as err:
    logging.error(err)
    sys.exit(1)

try:
    bind, port = config.get("listen", "addr").split(":")
    remote_host, remote_port = config.get("remote", "addr").split(":")
    # Если работа без валидации сообщений не допускается, убрать fallback=""
    listen_validate = validator.validator(config.get("listen", "schema", fallback=""))
    remote_validate = validator.validator(config.get("remote", "schema", fallback=""))
    logging.getLogger().setLevel(getattr(logging, config.get("logging", "loglevel", fallback="INFO")))
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

        if not listen_validate(data):
            logging.info("Validation error, msg droped")
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
        # Если нужна валидация входящих сообщений, добавляем ее здесь!
        if not remote_validate(data):
            logging.info("Response validation error, msg droped")
            return

        self.proxy.transport.sendto(data, self.addr)

    def connection_lost(self, exc):
        self.proxy.remotes.pop(self.attr)


async def start_datagram_proxy(bind: str, port: int, remote_host: str, remote_port: int):
    loop = asyncio.get_event_loop()
    protocol = ProxyDatagramProtocol((remote_host, remote_port))
    return await loop.create_datagram_endpoint(lambda: protocol, local_addr=(bind, port))


def main():
    loop = asyncio.get_event_loop()
    logging.info("Starting datagram proxy...")
    try:
        # Передать адреса через ip_address, чтобы при неправильном формате вызвать исключение ValueError
        coro = start_datagram_proxy(str(ip_address(bind)), int(port), str(ip_address(remote_host)), int(remote_port))
    except ValueError as err:
        logging.error(err)
        sys.exit(1)
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
