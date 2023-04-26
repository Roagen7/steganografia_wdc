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
from scipy.io import wavfile


SAMPLERATE = 44100
MIN_FREQ = 10000
MAX_FREQ = 20000
PIXEL_SIZE = 100
FRAME_SIZE = SAMPLERATE // PIXEL_SIZE
DAMP = 50
START_SOUND_SECOND = 1


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

    carrier = wavfile.read(args.carrier)[1]

    if len(carrier[0]) != 1:  # stereo to mono
        carrier = [sum(k)/len(k) for k in carrier]

    start_sound_frame = int(START_SOUND_SECOND * SAMPLERATE)
    data = array.array('h') # signed short

    for i in range(min(start_sound_frame, len(carrier))): data.insert(i, int(carrier[i]))

    for x in range(width):
        sample = [0 for _ in range(FRAME_SIZE)]
        for y in range(height):
            amplitude = img.getpixel((x, y))/DAMP
            freq_height = float(y * interval + MIN_FREQ)
            fr = generate_frequency(freq_height, amplitude)
            sample = [sample[i] + fr[i] for i in range(FRAME_SIZE)]

        for i in range(FRAME_SIZE):

            ix = x * FRAME_SIZE + i + start_sound_frame
            original_sample = int(carrier[ix])
            sample_norm = sample[i] + original_sample
            sample_norm = sample_norm if sample_norm < 32767 else 32767
            sample_norm = sample_norm if sample_norm > -32768 else -32768
            data.insert(ix, sample_norm)

    for i in range(width * FRAME_SIZE + start_sound_frame, len(carrier)): data.insert(i, int(carrier[i]))

    output.writeframes(data.tobytes())
    output.close()

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Name of the image to be convected.")
parser.add_argument("-o", "--output", help="Name of the output wav file. ).")
parser.add_argument("-c", "--carrier", help="Name of the input wav file to be used as stegocarrier.")
parser.add_argument("-p", "--pixel", help="'pixel size', pixels per sample")
parser.add_argument("-s", help="second, from which to embed image")
parser.add_argument("-d", "--damp", help="specify damp")
args = parser.parse_args()

if not args.input or not args.output or not args.carrier:
    raise RuntimeError("provide input, output and carrier")

if args.damp:
    DAMP = int(args.damp)

if args.s:
    START_SOUND_SECOND = int(args.s)

if args.pixel:
    PIXEL_SIZE = int(args.pixel)
    FRAME_SIZE = SAMPLERATE // PIXEL_SIZE

conversion(args)
