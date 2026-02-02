#!/usr/bin/env python3
"""
Port Scanner - Starter Template for Students
Assignment 2: Network Security

This is a STARTER TEMPLATE to help you get started.
You should expand and improve upon this basic implementation.

TODO for students:
1. Implement multi-threading for faster scans [v]
2. Add banner grabbing to detect services
3. Add support for CIDR notation (e.g., 192.168.1.0/24)
4. Add different scan types (SYN scan, UDP scan, etc.)
5. Add output formatting (JSON, CSV, etc.)
6. Implement timeout and error handling
7. Add progress indicators [v]
8. Add service fingerprinting
"""

import socket
import sys
import threading
import ipaddress
import time


def scan_port(target, port, timeout=1.0):
    """
    Scan a single port on the target host

    Args:
        target (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        bool: True if port is open, False otherwise
    """
    try:
        # TODO: Create a socket
        # TODO: Set timeout
        # TODO: Try to connect to target:port
        # TODO: Close the socket
        # TODO: Return True if connection successful
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.settimeout(timeout)

        start_time = time.time()
        result = sk.connect_ex((target, port))
        total_time = time.time() - start_time

        banner = None
        if result == 0:
            try:
                sk.sendall(b"\r\n")
                banner = sk.recv(512).decode(errors="ignore").strip()
            except:
                banner = None

        sk.close()

        if result == 0:
            return True, total_time, banner
        return False, total_time, None

    except (socket.timeout, ConnectionRefusedError, OSError):
        return False, timeout, None


def scan_range(target, start_port, end_port):
    """
    Scan a range of ports on the target host

    Args:
        target (str): IP address or hostname to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of open ports
    """
    open_ports = []
    closed_ports = []
    try:
        socket.gethostbyname(target)
    except socket.gaierror:
        print("Invalid hostname or IP address")
        sys.exit(1)

    print(f"[*] Scanning {target} from port {start_port} to {end_port}")
    print(f"[*] This may take a while...")

    # TODO: Implement the scanning logic
    # Hint: Loop through port range and call scan_port()
    # Hint: Consider using threading for better performance
    lock = threading.Lock()
    scanned = 0
    total_ports = end_port - start_port + 1

    def th(port):
        nonlocal scanned
        is_open, total_time, banner = scan_port(target, port)
        service = banner if banner else None

        with lock:
            if is_open:
                open_ports.append((port, total_time, banner))
            else:
                closed_ports.append((port, total_time, service))
            scanned += 1
            percent = int((scanned / total_ports) * 100)
            sys.stdout.write(f"\rProgress: {percent}% ({scanned}/{total_ports})")
            sys.stdout.flush()

    threads = []

    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=th, args=(port,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    
    return closed_ports, open_ports

def main():
    """Main function"""
    # TODO: Parse command-line arguments
    # TODO: Validate inputs
    # TODO: Call scan_range()
    # TODO: Display results

    # Example usage (you should improve this):
    if len(sys.argv) < 2:
        print("Usage: python3 port_scanner_template.py <target> [start_port end_port]")
        print("Example: python3 port_scanner_template.py 172.20.0.10 1 1024")
        sys.exit(1)

    target = sys.argv[1]
    start_port = 1
    end_port = 1024  # Scan first 1024 ports by default

    if len(sys.argv) >= 4:
        try:
            start_port = int(sys.argv[2])
            end_port = int(sys.argv[3])
        except ValueError:
            print("Invalid port range")
            sys.exit(1)

    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("Invalid port range")
        sys.exit(1)

    print(f"[*] Starting port scan on {target}")

    closed_ports, open_ports = scan_range(target, start_port, end_port)

    print(f"\n[+] Scan complete!")
    print(f"\n[+] Found {len(open_ports)} open ports:")
    for port, total_time, banner in sorted(open_ports):
        print(f"Port {port}: open, ({round(total_time*1000,2)} ms), {banner}")

    print(f"\n[+] Found {len(closed_ports)} closed ports")
    for port, total_time, banner in sorted(closed_ports):
        print(f"Port {port}: closed, ({round(total_time*1000,2)} ms), {banner}")

if __name__ == "__main__":
    main()
