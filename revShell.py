#!/bin/python3

import argparse
from src.shell import Shell
import threading
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="RevShell Handler"
    )
    parser.add_argument(
        "-l",
        "--listen",
        default="0.0.0.0",
        help="Listen address"
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=4444,
        help="Listen port"
    )

    args = parser.parse_args()

    handler = Shell(args.listen, args.port)
    threading.Thread(
        target=handler.listen,
        daemon=True
    ).start()
    time.sleep(0.3)

    handler.shell()

