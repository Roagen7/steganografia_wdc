"""
change image to wav file
sources:
    https://github.com/solusipse/spectrology/blob/master/spectrology.py
    https://solusipse.net/blog/post/basic-methods-of-audio-steganography-spectrograms/
    https://www.clear.rice.edu/elec301/Projects01/smokey_steg/freq.html

how does it work?

we iterate through every pixel of an image file and create a sine wave with corresponding amplitude
we then add the sine wave
"""

import wave, math, array, argparse, sys, timeit

from PIL import Image, ImageOps
from math import sin, pi

SAMPLERATE = 44100
MIN_FREQ = 20
MAX_FREQ = 20000
PIXEL_SIZE = 30
FRAME_SIZE = SAMPLERATE // PIXEL_SIZE


def generate_frequency(freq, amplitude):
    return int(sin(freq * 2 * pi) * amplitude)


def conversion(args):
    img = Image.open(args.input).convert('L')
    height = img.size[1]
    width = img.size[0]

    interval = (MAX_FREQ - MIN_FREQ) / height

    output = wave.open(args.output, 'w')
    output.setparams((1, 2, SAMPLERATE, 0, 'NONE', 'not compressed'))
    data = array.array('h')

    for x in range(width):
        sample = 0
        for y in range(height):
            amplitude = img.getpixel((x, y))
            freq_height = float(y * interval + MIN_FREQ)
            sample += generate_frequency(freq_height, amplitude)
        for i in range(PIXEL_SIZE):
            data.insert(x * PIXEL_SIZE + i, sample)

    output.writeframes(data.tobytes())
    output.close()

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Name of the image to be convected.")
parser.add_argument("-o", "--output", help="Name of the output wav file. Default value: out.wav).")
args = parser.parse_args()

if not args.input or not args.output:
    raise RuntimeError("provide input and output")

conversion(args)
