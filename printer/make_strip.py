#!/usr/bin/env python3

import argparse
import os
import sys
import PIL, PIL.Image, PIL.ImageDraw


DEFAULT_WIDTH = 320
DEFAULT_GUTTER = 10
DEFAULT_MARGIN = 25


def make_strip(
    images,
    margin=DEFAULT_MARGIN,
    gutter=DEFAULT_GUTTER,
    width=DEFAULT_WIDTH,
):
    images = resize_images(images, width)
    total_width = width + 2*margin
    total_height = sum([
        img.size[1]
        for img in images
    ]) + 2*margin + (len(images)-1) * gutter

    output_img = PIL.Image.new('RGB', (total_width, total_height))
    x = margin
    y = margin
    for img in images:
        output_img.paste(img, (x, y))
        y += img.height + gutter
    return output_img


def resize_images(images, width):
    def _get_height(img):
        return int((width/img.width)*img.height)
    return [
        img.resize((width, _get_height(img)))
        for img in images
    ]


def main():
    parser = argparse.ArgumentParser(
        description='Creates a vertical strip of photos',
    )
    parser.add_argument(
        '--dest',
        nargs=1,
        help='The output image',
    )
    parser.add_argument(
        'src',
        nargs='+',
        help='The input images',
    )
    parser.add_argument(
        '--margin',
        type=int,
        default=DEFAULT_MARGIN,
        help='The page margin (pixels)',
    )
    parser.add_argument(
        '--gutter',
        type=int,
        default=DEFAULT_GUTTER,
        help='The space between images (pixels)',
    )
    parser.add_argument(
        '--width',
        type=int,
        default=DEFAULT_WIDTH,
        help='The target width of the output image (pixels)',
    )
    args = parser.parse_args(sys.argv[1:])
    files = args.src
    dest = args.dest[0]
    margin = args.margin
    gutter = args.gutter
    width = args.width

    images = []
    for src in files:
        img = PIL.Image.open(src)
        images.append(img)

    output = make_strip(
        images,
        margin=margin,
        gutter=gutter,
        width=width,
    )
    output.save(dest)


if __name__ == '__main__':
    main()
