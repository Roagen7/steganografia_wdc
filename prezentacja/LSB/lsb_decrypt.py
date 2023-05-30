# input image path, block size and coords of possible text from command line arguments, for example:
# python3 lsb_find.py "your_file_path" 100 width height nonce key
from PIL import Image
import sys
from base64 import b64decode
from Crypto.Cipher import AES


def LSB_decrypt(BLOCK_SIZE, row, col, height, pixels, nonce, key):
    binary_text = ''
    for i in range(BLOCK_SIZE):
        if col + i >= height:
            r, g, b, _ = pixels[row, height - 1]
        else:
            r, g, b, _ = pixels[row, col + i]
        binary_text += str((r & 1))
        binary_text += str((g & 1))
        binary_text += str((b & 1))
        if col + i >= height:
            break
    text = ''.join(chr(int(binary_text[i:i + 8], 2)) for i in range(0, len(binary_text), 8))
    for i in range(1, len(text)):
        try:
            to_decrypt = text[:i]
            ct = b64decode(to_decrypt)
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
            message = cipher.decrypt(ct)
            if message:
                print("Attempt of decrypting message: " + message.decode('utf-8'))
        except:
            continue


def main():
    image = Image.open(sys.argv[1])
    BLOCK_SIZE = int(sys.argv[2])
    row = int(sys.argv[3])
    col = int(sys.argv[4])
    height = image.height
    pixels = image.load()
    nonce = b64decode(sys.argv[5])
    key = b64decode(sys.argv[6])
    LSB_decrypt(BLOCK_SIZE, row, col, height, pixels, nonce, key)


if __name__ == '__main__':
    main()
