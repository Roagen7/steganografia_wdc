# input image path, result image path and message from command line arguments, for example:
# python3 lsb_hide.py "your_file_path" "your_result_file_path" "Just a pimpled fatboy"
from PIL import Image
import sys
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def LSB_hide(image_file_path, message):
    image = Image.open(image_file_path)

    binary_message = ''.join(format(ord(i), '08b') for i in message)

    if len(binary_message) > image.width * image.height:
        raise ValueError('Text is too long to be hidden in picture')

    pixels = image.load()
    pixel_index = 0
    for i in range(image.width):
        for j in range(image.height):
            if pixel_index >= len(binary_message):
                break
            r, g, b, alpha = pixels[i, j]
            r = (r & 254) | int(binary_message[pixel_index])
            pixel_index += 1
            if pixel_index >= len(binary_message):
                pixels[i, j] = (r, g, b)
                break
            g = (g & 254) | int(binary_message[pixel_index])
            pixel_index += 1
            if pixel_index >= len(binary_message):
                pixels[i, j] = (r, g, b)
                break
            b = (b & 254) | int(binary_message[pixel_index])
            pixel_index += 1
            pixels[i, j] = (r, g, b, alpha)

    image.save(sys.argv[2])


def main():
    image_path = sys.argv[1]
    message = sys.argv[3].encode('utf-8')
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CTR)
    ct_bytes = cipher.encrypt(message)
    nonce = b64encode(cipher.nonce).decode('utf-8')
    key_file = b64encode(key).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    print("Your nonce: " + nonce + ", your key: " + key_file)
    LSB_hide(image_path, ct)


if __name__ == '__main__':
    main()
