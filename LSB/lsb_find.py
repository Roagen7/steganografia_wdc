# input image name, block size and probability of text threshold from command line arguments, for example:
# python3 lsb_find.py "gamer_modified.png" 100 0.06
from PIL import Image
import os
import sys
from base64 import b64decode
from Crypto.Cipher import AES
import json

image_name = sys.argv[1]
path = os.path.dirname(os.path.abspath(__file__))
path_result = os.path.join(path, "Result_Images")
BLOCK_SIZE = int(sys.argv[2])
THRESHOLD = float(sys.argv[3])
with open(os.path.join(path_result, image_name.split('.')[0] + "_key.json"), "r") as file:
    elements = json.loads(file.read())
nonce = b64decode(elements['nonce'])
key = b64decode(elements['key'])
cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)


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
    modified_image_file_path = os.path.join(path_result, image_name)
    texts = LSB_find(modified_image_file_path)
    if texts:
        for text in texts:
            possible_encrypted = '\n'.join(text.split('\n')[1:])
            for i in range(1, len(possible_encrypted)):
                try:
                    to_decrypt = possible_encrypted[:i]
                    ct = b64decode(to_decrypt)
                    message = cipher.decrypt(ct)
                    if message:
                        print(text.split('\n')[0] + " " + message.decode('utf-8'))
                except:
                    continue
    else:
        print('No hidden text found')


if __name__ == '__main__':
    main()
