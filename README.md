# showimage

This is a simple command to display an image in a terminal.

Usage:

    showimage.py [-h] [--cols COLS] [--rows ROWS] [--dither] [--no-dither] image

Displays an image in your terminal

positional arguments:

- image: the image to show

optional arguments:

- `-h`, `--help`: show help message and exit
- `--cols COLS`: number of columns to output
- `--rows ROWS`: number of rows to output
- `--dither`: dither the image
- `--no-dither`: do not dither the image

# Example

    ./showimage.py octocat.png

Original image:

![octocat](octocat_original.png)

Output:

![octocat](octocat_terminal.png)
