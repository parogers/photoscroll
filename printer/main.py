#!/usr/bin/env python3

import tempfile
import io
import PIL, PIL.Image
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

from make_strip import make_strip


def make_ws_url(server_url):
    parsed = urlparse(server_url)
    ws_scheme = ''
    if parsed.scheme == 'http':
        ws_scheme = 'ws'
    elif parsed.scheme == 'https':
        ws_scheme = 'wss'
    else:
        raise Exception(f'unknown scheme: {server_url}')

    url = f'{ws_scheme}://{parsed.netloc}'
    if parsed.path != '/':
        url += parsed.path
    if not url.endswith('/'):
        url += '/'
    url += 'ws'
    return url


def parse_image(data):
    return PIL.Image.open(io.BytesIO(base64.b64decode(data)))


async def serve(server_url):
    websocket_url = make_ws_url(server_url)
    print('Connecting to server:', websocket_url)
    with connect(websocket_url) as websocket:
        print('Connected')
        while True:
            payload_data = websocket.recv()
            if not payload_data:
                # Must be a ping
                continue

            payload = json.loads(payload_data)
            images = []
            print(payload['job'])
            for img_data in payload['images']:
                print('=>', len(img_data), 'bytes')
                images.append(parse_image(img_data))
            print('=> (done)')
            print()

            print('Printing...')
            strip_img = make_strip(images)
            with tempfile.NamedTemporaryFile(suffix='.png') as file:
                strip_img.save(file.name)
                subprocess.run([
                    './print_scroll.sh',
                    file.name,
                ])
            print('Done')


async def main():
    parser = argparse.ArgumentParser(description='Prints photoscrolls')
    parser.add_argument(
        '--url',
        type=str,
        nargs=1,
        required=False,
        default=['http://localhost:8000'],
        help='URL base for the API server',
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
