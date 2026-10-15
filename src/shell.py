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
import shlex

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
        self.sessions = dict()
        self.server = None
        self.sid = None
        self.next_sid = 1
        self.sock = None

    def listen(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.address, self.port))
        self.server.listen(10)
        print(f"{GREEN}listening on {self.address}:{self.port}")

        while True:
            try:
                session, host = self.server.accept()
                sid = self.next_sid
                self.next_sid += 1

                print(f"connection from {host}{RESET}")
                session.settimeout(1)
                self.sessions[sid] = Sock(session, host)
            except KeyboardInterrupt:
                print("Shutting Down")
                break
    
    def upgrade(self):
        SHELL = stable(self)
        SHELL.inspect()
        SHELL.upgrade()

    def esc(self):
        esc = Escalate(self)
        esc.scan()

    def exit(self):
        for i in self.sessions.items():
            i[1].send("exit\n")

    def terminal(self): 
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
            print("\n[*] Leaving Interactive Shell\n")

    def command(self, cmd):
        if cmd:
            self.sock.send(cmd + "\n")
            return self.sock.recv()
        
    def list_sessions(self):
        print("ID\t\tAddress")
        for i in self.sessions.items():
            print(f"{i[0]}\t\t{i[1].address}")

    def shell(self):
        txt = f"""{RESET}
╔════════════════════════════════════════════╗
║            RevShellHandler v0.1            ║
║     Authorized pentesting shell manager    ║
╚════════════════════════════════════════════╝

Commands:

  sessions              List sessions
  use <id>              Select session
  upgrade               Attempt PTY upgrade
  escalate              Scan for escalation
  shell                 Interactive shell
  bg                    Return to handler
  help                  Show help
  exit                  Exit
              """
        print(txt)
        while True:
            try:
                prompt = f"RSH"
                if self.sid:
                    prompt += f"({self.sid})"
                cmd = input(f"{prompt}>>").strip()
                if not cmd:
                    continue

                args = shlex.split(cmd)
            
                if args[0] == "sessions":
                    self.list_sessions()
                
                elif args[0] == "use":
                    if len(args) < 2:
                        print("Usage: use <ID>")
                        continue
                    try:
                        choice = int(args[1])
                    except ValueError:
                        print("error choose from")
                        self.list_sessions()
                        continue
                    session = self.sessions.get(choice)
                    if not session:
                        print("[-] session not found")
                        continue
                    self.sid = choice
                    self.sock = session
                elif args[0] == "upgrade":
                    self.upgrade()
                elif args[0] == "escalate":
                    self.esc()
                elif args[0] == "shell":
                    self.terminal()
                elif args[0] == "bg":
                    self.sid = None
                    self.sock = None
                elif args[0] == "help":
                    print(txt)
                elif args[0] in ("exit", "quit"):
                    self.exit()
                    return
            except Exception as e:
                print(e)
                input()
