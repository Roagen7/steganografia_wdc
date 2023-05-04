from PIL import Image
import os

image_name = "gamer.jpg"
message = 'Fat Cartman'
path = os.path.dirname(os.path.abspath(__file__))
path_test = os.path.join(path, "Test_Images")
path_result = os.path.join(path, "Result_Images")
BLOCK_SIZE = 100
THRESHOLD = 0.06


def LSB_hide(image_file_path, message):
    image = Image.open(image_file_path)

    binary_message = ''.join(format(ord(i), '08b') for i in message)

    if image.format != 'JPEG':
        raise ValueError('Wrong picture format')

    if len(binary_message) > image.width * image.height:
        raise ValueError('Text is too long to be hidden in picture')

    pixels = image.load()
    pixel_index = 0
    for i in range(image.width):
        for j in range(image.height):
            if pixel_index >= len(binary_message):
                break
            r, g, b = pixels[i, j]
            r = (r & 254) | int(binary_message[pixel_index])
            pixel_index += 1
            if pixel_index >= len(binary_message):
                break
            g = (g & 254) | int(binary_message[pixel_index])
            pixel_index += 1
            if pixel_index >= len(binary_message):
                break
            b = (b & 254) | int(binary_message[pixel_index])
            pixel_index += 1
            pixels[i, j] = (r, g, b)

    image.save(os.path.join(path_result, image_name.split('.')[0] + "_modified.png"))


def check_block(row, col, pixels, height):
    LSB_counter = 0
    general_counter = 0
    binary_text = ''
    for i in range(BLOCK_SIZE):
        if col + i >= height:
            r, g, b = pixels[row, height - 1]
        else:
            r, g, b = pixels[row, col + i]
        binary_text += str((r & 1))
        binary_text += str((g & 1))
        binary_text += str((b & 1))
        LSB_counter += (r & 1) + (g & 1) + (b & 1)
        general_counter += 3
        if col + i >= height:
            break
    if 0.5 - THRESHOLD <= LSB_counter / general_counter <= 0.5 + THRESHOLD:
        return ''.join(chr(int(binary_text[i:i + 8], 2)) for i in range(0, len(binary_text), 8))
    else:
        return None


def LSB_find(image_file_path):
    image = Image.open(image_file_path)

    if image.format != 'PNG':
        raise ValueError('Wrong picture format')

    pixels = image.load()
    number_of_blocks = 0
    possible_texts = []
    for i in range(image.width):
        for j in range(0, image.height, BLOCK_SIZE):
            binary_text = check_block(i, j, pixels, image.height)
            if binary_text is not None:
                possible_texts.append('Possible text at block ' + str(number_of_blocks) + ':\n' + binary_text)
            number_of_blocks += 1
    return possible_texts


def main():
    image_file_path = os.path.join(path_test, image_name)
    modified_image_file_path = os.path.join(path_result, image_name.split('.')[0] + "_modified.png")
    LSB_hide(image_file_path, message)
    texts = LSB_find(modified_image_file_path)
    if texts:
        for text in texts:
            print(text)
    else:
        print('No hidden text found')


if __name__ == '__main__':
    main()
