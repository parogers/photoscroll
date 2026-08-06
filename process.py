#!/usr/bin/env python3

import os
import sys
import PIL, PIL.Image, PIL.ImageDraw


GAP = 10
MARGIN = 25


files = sys.argv[1:]
assert files

images = []
for src in files:
    img = PIL.Image.open(src)
    images.append(img)


total_width = max([
    img.size[0]
    for img in images
]) + 2*MARGIN
total_height = sum([
    img.size[1]
    for img in images
]) + 2*MARGIN + (len(images)-1) * GAP

output_img = PIL.Image.new('RGB', (total_width, total_height))

x = MARGIN
y = MARGIN
for img in images:
    output_img.paste(img, (x, y))
    y += img.size[1] + GAP

output_img.save('out.png')
