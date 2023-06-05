# input image path, block size and probability of text threshold from command line arguments, for example:
# python3 lsb_find.py "your_file_path" 100 0.05
import matplotlib.pyplot
import matplotlib
from PIL import Image
import sys

values = []


def check_block(row, col, pixels, height, BLOCK_SIZE, THRESHOLD):
    LSB_counter = 0
    general_counter = 0
    for i in range(BLOCK_SIZE):
        if col + i >= height:
            r, g, b, _ = pixels[row, height - 1]
        else:
            r, g, b, _ = pixels[row, col + i]
        LSB_counter += (r & 1) + (g & 1) + (b & 1)
        general_counter += 3
        if col + i >= height:
            break
    values.append(LSB_counter / general_counter)
    if 0.5 - THRESHOLD <= LSB_counter / general_counter <= 0.5 + THRESHOLD:
        return True
    else:
        return False


def LSB_find(image_file_path, BLOCK_SIZE, THRESHOLD):
    image = Image.open(image_file_path)

    pixels = image.load()
    number_of_blocks = 0
    for i in range(image.width):
        for j in range(0, image.height, BLOCK_SIZE):
            if check_block(i, j, pixels, image.height, BLOCK_SIZE, THRESHOLD):
                print('Possible message at block ' + str(number_of_blocks) + ', coords: ' + str(i) + " " + str(j))
            number_of_blocks += 1

    matplotlib.pyplot.plot(values, 'bo')
    matplotlib.pyplot.show()


def main():
    image_path = sys.argv[1]
    BLOCK_SIZE = int(sys.argv[2])
    THRESHOLD = float(sys.argv[3])
    LSB_find(image_path, BLOCK_SIZE, THRESHOLD)


if __name__ == '__main__':
    main()
