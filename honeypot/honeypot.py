#!/usr/bin/env python3
"""Starter template for the honeypot assignment."""

import logging
import os
import time
import socket
import threading
import paramiko

from logger import create_logger

LOG_PATH = "/app/logs/honeypot.log"
HOST_KEY = paramiko.RSAKey.generate(2048)
SSH_BANNER = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"


# def setup_logging():
#     os.makedirs("/app/logs", exist_ok=True)
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(levelname)s - %(message)s",
#         handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
#     )

class HoneypotSSHServer(paramiko.ServerInterface):
    def __init__(self, client_addr, logger):
        self.client_addr = client_addr
        self.logger = logger
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        self.logger.info(
            f"AUTH_ATTEMPT src_ip={self.client_addr[0]} "
            f"src_port={self.client_addr[1]} "
            f"username={username} password={password}"
        )
        return paramiko.AUTH_SUCCESSFUL
    
    def check_auth_publickey(self, username, key):
        self.logger.info(
            f"AUTH_ATTEMPT src_ip={self.client_addr[0]} "
            f"src_port={self.client_addr[1]} "
            f"username={username} method=publickey"
        )
        return paramiko.AUTH_FAILED

    def check_auth_interactive(self, username, submethods):
        self.logger.info(
            f"AUTH_ATTEMPT src_ip={self.client_addr[0]} "
            f"src_port={self.client_addr[1]} "
            f"username={username} method=keyboard-interactive"
        )
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password,keyboard-interactive"

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True


def handle_client(client, addr, logger):
    start_time = time.time()
    transport = paramiko.Transport(client)
    transport.local_version = SSH_BANNER
    transport.add_server_key(HOST_KEY)

    server = HoneypotSSHServer(addr, logger)

    try:
        transport.start_server(server=server)
        channel = transport.accept(20)

        if channel is None:
            return

        server.event.wait(10)

        logger.info(f"SESSION_START src_ip={addr[0]} src_port={addr[1]}")

        channel.send("Welcome to Ubuntu 20.04.6 LTS\r\n")
        channel.send("$ ")

        while True:
            data = channel.recv(1024)
            if not data:
                break

            command = data.decode("utf-8", errors="ignore").strip()
            if command == "exit":
                break

            logger.info(
                f"COMMAND src_ip={addr[0]} src_port={addr[1]} command=\"{command}\""
            )

            channel.send(f"bash: {command}: command not found\r\n")
            channel.send("$ ")

    except Exception as e:
        logger.error(f"ERROR src_ip={addr[0]} error={e}")
    finally:
        duration = round(time.time() - start_time, 2)
        logger.info(
            f"DISCONNECT src_ip={addr[0]} src_port={addr[1]} duration={duration}s"
        )
        transport.close()


def run_honeypot():
    logger = create_logger()
    logger.info("Honeypot starter template running.")
    # logger.info("TODO: Implement protocol simulation, logging, and alerting.")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", 22))
    sock.listen(100)

    logger.info("SSH Honeypot listening on port 22")

    while True:
        client, addr = sock.accept()
        logger.info(f"CONNECT src_ip={addr[0]} src_port={addr[1]}")
        threading.Thread(
            target=handle_client,
            args=(client, addr, logger),
            daemon=True,
        ).start()


if __name__ == "__main__":
    # setup_logging()
    run_honeypot()
