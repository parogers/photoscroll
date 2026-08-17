#!/usr/bin/env python3

import subprocess
import base64
from urllib.parse import urlparse
import argparse
import sys
import socket
import json
import time
import asyncio
from websockets.sync.client import connect
from websockets.exceptions import (
    ConnectionClosedError,
    InvalidMessage,
    InvalidStatus,
)
from serial import SerialException


def make_ws_url(server_url):
    parsed = urlparse(server_url)
    ws_scheme = ''
    if parsed.scheme == 'http':
        ws_scheme = 'ws'
    elif parsed.scheme == 'https':
        ws_scheme = 'wss'
    else:
        raise Exception(f'unknown scheme: {server_url}')

    url = f'{ws_scheme}://{parsed.netloc}/{parsed.path}'
    if not url.endswith('/'):
        url += '/'
    url += 'ws/'
    return url


async def serve(server_url):
    with connect(make_ws_url(server_url)) as websocket:
        print('Connected')
        while True:
            job_marker = websocket.recv()
            if not job_marker:
                # Must be a ping
                continue
            print(job_marker)
            # List of base64 encoded images
            images = []
            while True:
                img_data = websocket.recv().strip()
                if not img_data:
                    break;
                print('=>', img_data)

                with open('photo.png', 'wb') as file:
                    file.write(base64.b64decode(img_data))

                subprocess.run([
                    './print_scroll.sh',
                    'photo.png',
                ])

            print('=> (done)')
            print()


async def main():
    parser = argparse.ArgumentParser(description='Prints photoscrolls')
    parser.add_argument(
        '--url',
        type=str,
        nargs=1,
        required=False,
        default=['http://localhost:8000'],
    )
    args = parser.parse_args(sys.argv[1:])
    url = args.url[0]
    while True:
        try:
            await serve(url)
        except (ConnectionClosedError, InvalidMessage, ConnectionError):
            print('Connection closed... re-connecting')
        except (ConnectionRefusedError, TimeoutError, InvalidStatus, socket.gaierror):
            print('Could not reach server... retrying')
        time.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
