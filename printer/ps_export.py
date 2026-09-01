#!/usr/bin/env python3

import io
from PIL import PSDraw
import PIL.Image


def save_as_ps(img: PIL.Image, dest: str, dpi: int):
    with open(dest, 'wb') as file:
        img_width = img.width/(dpi/72)
        img_height = img.height/(dpi/72)

        buf = io.BytesIO()
        draw = PSDraw.PSDraw(buf)
        draw.begin_document()
        draw.image((0, 0, img_width, img_height), img, dpi=dpi)
        draw.end_document()

        # Inject the page bounding box because PIL doesn't seem to support that
        bytes_data = buf.getvalue()
        index = bytes_data.index(b'\n')
        bytes_data = (
            bytes_data[0:index+1] +
            bytes(f'%%BoundingBox: -0 -0 {img_width} {img_height}', encoding='utf-8') +
            bytes_data[index:]
        )
        file.write(bytes_data)
