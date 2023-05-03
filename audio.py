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


DEFAULT_SAMPLERATE = 44100
DEFAULT_BOTTOM_FREQ = 10000
DEFAULT_TOP_FREQ = 20000
DEFAULT_PIXEL_SIZE = 100
DEFAULT_DAMP = 50
DEFAULT_START_SOUND_SECOND = 0
MIN_INT16 = -32768
MAX_INT16 = 32767


def generate_frequency(freq, amplitude, frame_size, samplerate):
    out = []
    for frame in range(frame_size):
        out += [int(sin(freq * 2 * pi * frame / samplerate) * amplitude)]
    return out


def conversion(args):
    img = ImageOps.mirror(Image.open(args.input).convert('L').rotate(180))
    data = array.array('h')
    output = wave.open(args.output, 'w')
    output.setparams((1, 2, args.samplerate, 0, 'NONE', 'not compressed'))

    height = img.size[1]
    width = img.size[0]
    interval = (args.tfreq - args.bfreq) / height
    frame_size = args.samplerate // args.pixel

    if args.carrier:
        carrier = wavfile.read(args.carrier)[1]
        if len(carrier[0]) != 1:  # stereo to mono
            carrier = [sum(k)/len(k) for k in carrier]

        start_sound_frame = int(args.startt * args.samplerate)
        for i in range(min(start_sound_frame, len(carrier))):
            data.insert(i, int(carrier[i]))
    else:
        start_sound_frame = 0

    for x in range(width):
        sample = [0 for _ in range(frame_size)]
        for y in range(height):
            amplitude = img.getpixel((x, y))/args.damp
            freq_height = float(y * interval + args.bfreq)
            fr = generate_frequency(freq_height, amplitude, frame_size, args.samplerate)
            sample = [sample[i] + fr[i] for i in range(frame_size)]

        for i in range(frame_size):
            ix = x * frame_size + i + start_sound_frame
            if args.carrier and ix < len(carrier):
                original_sample = int(carrier[ix])
            else:
                original_sample = 0

            sample_norm = sample[i] + original_sample
            sample_norm = sample_norm if sample_norm < MAX_INT16 else MAX_INT16
            sample_norm = sample_norm if sample_norm > MIN_INT16 else MIN_INT16
            data.insert(ix, sample_norm)

    if args.carrier:
        for i in range(width * frame_size + start_sound_frame, len(carrier)):
            data.insert(i, int(carrier[i]))

    output.writeframes(data.tobytes())
    output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Name of the image to be convected.")
    parser.add_argument("-o", "--output", help="Name of the output wav file. ).")
    parser.add_argument("-c", "--carrier", help="Name of the input wav file to be used as stegocarrier.")
    parser.add_argument("-p", "--pixel", help="'pixel size', samples per pixel")
    parser.add_argument("-s", "--startt", help="second, from which to embed image into carrier")
    parser.add_argument("-d", "--damp", help="specify damp i.e. the mute coefficient on signal")
    parser.add_argument("-b", "--bfreq", help="specify bottom frequency i.e. bottom edge of an image")
    parser.add_argument("-t", "--tfreq", help="specify top frequency i.e. top edge of an image")
    parser.add_argument("-r", "--samplerate", help="specify samplerate of an audio file")

    args = parser.parse_args()

    if not args.input or not args.output:
        raise AttributeError("provide input and output")

    if args.damp:
        args.damp = int(args.damp)
    else:
        args.damp = DEFAULT_DAMP

    if args.startt:
        args.startt = int(args.startt)
    else:
        args.startt = DEFAULT_START_SOUND_SECOND

    if args.startt and not args.carrier:
        import warnings
        warnings.warn(UserWarning("-s/--startt flag has no effect as carrier is not specified"))

    if args.pixel:
        args.pixel = int(args.pixel)
    else:
        args.pixel = DEFAULT_PIXEL_SIZE

    if args.bfreq:
        args.bfreq = int(args.bfreq)
    else:
        args.bfreq = DEFAULT_BOTTOM_FREQ

    if args.tfreq:
        args.tfreq = int(args.tfreq)
    else:
        args.tfreq = DEFAULT_TOP_FREQ

    if args.samplerate:
        args.samplerate = int(args.samplerate)
    else:
        args.samplerate = DEFAULT_SAMPLERATE

    if args.tfreq < args.bfreq:
        raise AttributeError("top frequency should > bottom frequency")

    conversion(args)
