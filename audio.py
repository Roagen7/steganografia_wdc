"""
change image to wav file

sources:
    https://github.com/solusipse/spectrology/blob/master/spectrology.py
    https://solusipse.net/blog/post/basic-methods-of-audio-steganography-spectrograms/
    https://www.clear.rice.edu/elec301/Projects01/smokey_steg/freq.html

how does it work?
    1. we iterate through every pixel of an image file
    2. create a sine wave with corresponding amplitude
    3. then add the sine wave to sample
"""

import wave, math, array, argparse, sys, timeit

from PIL import Image, ImageOps
from math import sin, pi

SAMPLERATE = 44100
MIN_FREQ = 20
MAX_FREQ = 20000
PIXEL_SIZE = 50
FRAME_SIZE = SAMPLERATE // PIXEL_SIZE


def generate_frequency(freq, amplitude):
    out = []
    for frame in range(FRAME_SIZE):
        out += [int(sin(freq * 2 * pi * frame/SAMPLERATE) * amplitude)]
    return out


def conversion(args):
    img = ImageOps.mirror(Image.open(args.input).convert('L').rotate(180))
    height = img.size[1]
    width = img.size[0]

    interval = (MAX_FREQ - MIN_FREQ) / height

    output = wave.open(args.output, 'w')
    output.setparams((1, 2, SAMPLERATE, 0, 'NONE', 'not compressed'))
    data = array.array('h') # signed short

    for x in range(width):
        sample = [0 for _ in range(FRAME_SIZE)]
        for y in range(height):
            amplitude = img.getpixel((x, y))
            freq_height = float(y * interval + MIN_FREQ)
            fr = generate_frequency(freq_height, amplitude)
            sample = [sample[i] + fr[i] for i in range(FRAME_SIZE)]

        for i in range(FRAME_SIZE):
            sample_norm = sample[i] if sample[i] < 32767 else 32767
            sample_norm = sample_norm if sample_norm > -32768 else -32768
            data.insert(x * FRAME_SIZE + i, sample_norm)

    output.writeframes(data.tobytes())
    output.close()

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Name of the image to be convected.")
parser.add_argument("-o", "--output", help="Name of the output wav file. Default value: out.wav).")
args = parser.parse_args()

if not args.input or not args.output:
    raise RuntimeError("provide input and output")

conversion(args)
