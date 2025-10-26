#!/usr/bin/env python3
import asyncio
import configparser
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
    local_addr = tuple(config.get("local", "addr").split(":"))
    remote_addr = tuple(config.get("remote", "addr").split(":"))
    # Если работа без валидации сообщений не допускается, убрать fallback=""
    local_validate = validator.validator(config.get("local", "schema", fallback=""))
    remote_validate = validator.validator(config.get("remote", "schema", fallback=""))
    # Преобразовать параметр loglevel в числовое значение и установить уровень логирования
    logging.getLogger().setLevel(getattr(logging, config.get("logging", "loglevel", fallback="INFO")))
except (configparser.NoOptionError, ValueError) as err:
    logging.error(err)
    sys.exit(1)


class ProxyDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(self, remote_addr):
        self.remote_addr = remote_addr
        self.remotes = {}
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        logging.info(f"From {addr[0]}:{addr[1]} received request {data}")

        try:
            local_validate(data)
        except validator.MessageValidationError as err:
            logging.info("Request validation error")
            # Вернуть отправителю сообщение об ошибке валидации
            self.transport.sendto(str.encode(f"Request validation error: {err}"), addr)
            return

        if addr in self.remotes:
            self.remotes[addr].transport.sendto(data)
            return
        # Если адресата полученного сообщения нет в self.remotes, то добавить его туда
        # и создать для него новую точку назначения
        loop = asyncio.get_event_loop()
        self.remotes[addr] = RemoteDatagramProtocol(self, addr, data)
        coro = loop.create_datagram_endpoint(lambda: self.remotes[addr], remote_addr=self.remote_addr)
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

    def datagram_received(self, data, addr):
        logging.info(f"From {addr[0]}:{addr[1]} received reply {data}")

        try:
            remote_validate(data):
        except validator.MessageValidationError as err:
            logging.info("Reply validation error")
            return

        self.proxy.transport.sendto(data, self.addr)

    def connection_lost(self, exc):
        self.proxy.remotes.pop(self.attr)


async def start_datagram_proxy(local_addr, remote_addr):
    loop = asyncio.get_event_loop()
    protocol = ProxyDatagramProtocol(remote_addr)
    return await loop.create_datagram_endpoint(lambda: protocol, local_addr=local_addr)


def main():
    loop = asyncio.get_event_loop()
    logging.info("Starting datagram proxy...")
    coro = start_datagram_proxy(local_addr, remote_addr)
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
