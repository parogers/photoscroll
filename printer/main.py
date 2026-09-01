#!/usr/bin/env python3

import tempfile
import io
import PIL, PIL.Image
from PIL import PSDraw
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

from ps_export import save_as_ps
from make_strip import make_strip


# See https://files.support.epson.com/pdf/pos/bulk/tm-t88v_hwum_en_02.pdf
PRINTER_DPI = 180
PAPER_WIDTH_MM_DEFAULT = 58
MM_PER_IN = 25.4


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


def print_image(img, dpi):
    with tempfile.NamedTemporaryFile(suffix='.ps') as file:
        save_as_ps(img, file.name, dpi=dpi)
        subprocess.run([
            'lp',
            '-d', 'Epson-TM-T88V',
            '-o', 'TmtPaperSource=DocNoFeedNoCut',
            '-o', 'TmtPaperReduction=Both',
            file.name,
        ])


async def serve(
    server_url,
    paper_width_mm=PAPER_WIDTH_MM_DEFAULT,
):
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
            paper_width_pixels = int(PRINTER_DPI*paper_width_mm/MM_PER_IN)
            strip_img = make_strip(images, width=paper_width_pixels)
            print_image(strip_img, dpi=PRINTER_DPI)
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
    parser.add_argument(
        '--paper-width-mm',
        type=float,
        nargs=1,
        required=False,
        default=[PAPER_WIDTH_MM_DEFAULT],
        help='Paper width in mm',
    )
    args = parser.parse_args(sys.argv[1:])
    url = args.url[0]
    paper_width_mm = args.paper_width_mm[0]
    while True:
        try:
            await serve(
                url,
                paper_width_mm=paper_width_mm,
            )
        except (ConnectionClosedError, InvalidMessage, ConnectionError):
            print('Connection closed... re-connecting')
        except (ConnectionRefusedError, TimeoutError, InvalidStatus, socket.gaierror):
            print('Could not reach server... retrying')
        time.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
