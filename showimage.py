#!/usr/bin/env python3

import argparse
import operator
import subprocess
import sys

from PIL import Image

RESET = '\x1b[0m'

FLOYD_STEINBERG_ERROR_DISTRIBUTION = [
    {'dc':  1, 'dr': 0, 'weight': 7 / 16},
    {'dc': -1, 'dr': 1, 'weight': 3 / 16},
    {'dc':  0, 'dr': 1, 'weight': 5 / 16},
    {'dc':  1, 'dr': 1, 'weight': 1 / 16}
]

parser = argparse.ArgumentParser(description='Displays an image in your terminal')
parser.add_argument('image', help='the image to show')
parser.add_argument('--cols', type=int, dest='cols', help='number of columns to output')
parser.add_argument('--rows', type=int, dest='rows', help='number of rows to output')
parser.add_argument('--dither', dest='dither', action='store_true', help='dither the image')
parser.add_argument('--no-dither', dest='dither', action='store_false', help='do not dither the image')
parser.set_defaults(dither=False)

def get_bg_prefix(rgb_6):
  r, g, b = rgb_6
  rgb = 16 + r * 36 + g * 6 + b
  return '\x1b[48;5;%dm' % rgb

def get_default_output_size(image_size, console_size):
  image_rows, image_cols = image_size
  console_rows, console_cols = console_size
  if console_rows / image_rows < console_cols / image_cols:
    # Constrained by console rows.
    return console_rows, round(image_cols * console_rows / image_rows)
  else:
    # Constrained by console cols.
    return round(image_rows * console_cols / image_cols), console_cols

def show_image(image, dither):
  cols, rows = image.size
  rgb_data = chunks(list(image.getdata()), cols)
  for r in range(rows):
    for c in range(cols):
      rgb_256 = rgb_data[r][c]
      rgb_6 = [round(x * 5 / 255) for x in rgb_256]
      print(get_bg_prefix(rgb_6) + ' ', end='')
      result_rgb_256 = [x * 255 / 5 for x in rgb_6]
      error = list(map(operator.sub, rgb_256, result_rgb_256))
      if dither:
        for error_component in FLOYD_STEINBERG_ERROR_DISTRIBUTION:
          new_r = r + error_component['dr']
          new_c = c + error_component['dc']
          adjustment = [x * error_component['weight'] for x in error]
          if new_r in range(rows) and new_c in range(cols):
            rgb_data[new_r][new_c] = map(operator.add, rgb_data[new_r][new_c], adjustment)
            rgb_data[new_r][new_c] = [clamp(x, 0, 255) for x in rgb_data[new_r][new_c]]
    print(RESET)

def chunks(l, n):
  return [l[i:i + n] for i in range(0, len(l), n)]

def clamp(x, min_value, max_value):
  if x < min_value:
    return min_value
  if x > max_value:
    return max_value
  return x

if __name__ == '__main__':
  args = parser.parse_args()
  image = Image.open(args.image)
  original_width, original_height = image.size

  rows, cols = args.rows, args.cols
  if not rows and not cols:
    console_size = map(int, subprocess.check_output(['stty', 'size']).split())
    rows, cols = get_default_output_size((original_height, original_width), console_size)
  rows = rows or round(original_height * cols / original_width)
  cols = cols or round(original_width * rows / original_height)

  image = image.resize((cols, rows))
  image = image.convert('RGB')
  show_image(image, args.dither)
