#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import time
import select
import subprocess

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0
OPEN_TIME_SECONDS = 30  # How long the port stays open after success


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def open_protected_port(protected_port):
    """Open the protected port using firewall rules."""
    logging.info("Opening firewall for port %s", protected_port)
    # Using FORWARD chain is most reliable for Docker-to-Docker or Host-to-Docker traffic
    subprocess.run([
        "iptables", "-I", "FORWARD", "1",
        "-p", "tcp", 
        "--dport", str(protected_port), 
        "-j", "ACCEPT"
    ], check=False)

def close_protected_port(protected_port):
    """Close the protected port using firewall rules."""
    logging.info("Closing firewall for port %s", protected_port)
    subprocess.run([
        "iptables", "-D", "FORWARD",
        "-p", "tcp", 
        "--dport", str(protected_port), 
        "-j", "ACCEPT"
    ], check=False)


def listen_for_knocks(sequence, window_seconds, protected_port):
    """Listen for knock sequence and open the protected port."""
    logger = logging.getLogger("KnockServer")
    logger.info("Listening for knocks: %s", sequence)
    logger.info("Protected port: %s", protected_port)

    # TODO: Create UDP or TCP listeners for each knock port.
    sockets = []
    for port in sequence:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.bind(("0.0.0.0", port))
            s.setblocking(False)
            sockets.append(s)
        except PermissionError:
            logger.error("Permission denied binding to port %s. Try sudo.", port)
            return

    # TODO: Track each source IP and its progress through the sequence.
    # Format:
    # {
    #    "IP": {
    #        "index": current_sequence_index,
    #        "start_time": timestamp
    #    }
    # }
    clients = {}

    port_open_until = None

    # TODO: Enforce timing window per sequence.
    # TODO: On correct sequence, call open_protected_port().
    # TODO: On incorrect sequence, reset progress.

    while True:
        readable, _, _ = select.select(sockets, [], [], 1)

        current_time = time.time()

        # Auto-close port if time expired
        if port_open_until and current_time > port_open_until:
            close_protected_port(protected_port)
            port_open_until = None

        for sock in readable:
            _, addr = sock.recvfrom(1024)
            src_ip = addr[0]
            dst_port = sock.getsockname()[1]

            logger.info("Knock from %s on port %s", src_ip, dst_port)

            if src_ip not in clients:
                clients[src_ip] = {
                    "index": 0,
                    "start_time": current_time,
                }

            client = clients[src_ip]

            # Check timing window
            if current_time - client["start_time"] > window_seconds:
                logger.info("Sequence timeout for %s", src_ip)
                client["index"] = 0
                client["start_time"] = current_time
                # Fall through to check if this knock is the first in a new sequence

            expected_port = sequence[client["index"]]

            if dst_port == expected_port:
                client["index"] += 1
                logger.info(
                    "Correct knock %s/%s from %s",
                    client["index"],
                    len(sequence),
                    src_ip,
                )

                # Full sequence matched
                if client["index"] == len(sequence):
                    logger.info("Sequence complete from %s", src_ip)
                    open_protected_port(protected_port)
                    port_open_until = current_time + OPEN_TIME_SECONDS
                    del clients[src_ip]
            else:
                # If they hit the first port again, treat it as a fresh start
                if dst_port == sequence[0]:
                    client["index"] = 1
                    client["start_time"] = current_time
                else:
                    logger.warning("Incorrect knock from %s, resetting", src_ip)
                    del clients[src_ip]


def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server starter")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    listen_for_knocks(sequence, args.window, args.protected_port)


if __name__ == "__main__":
    main()