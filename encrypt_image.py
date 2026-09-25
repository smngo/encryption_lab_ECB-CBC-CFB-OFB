"""
Task 2: 

Encrypt image pixel data with AES (ECB or CBC) and save as a
viewable image, to demonstrate how ECB mode leaks visual patterns

Commands:
    python encrypt_image.py -i Tux.jpg -o Tux_ecb.png -k 0123456789abcdef -m AES_ECB 
	python encrypt_image.py -i Tux.jpg -o Tux_cbc.png -k 0123456789abcdef -m AES_CBC 
	python encrypt_image.py -i whoisCB2.jpg -o whoisCB2_ecb.png -k 0123456789abcdef -m AES_ECB 
	python encrypt_image.py -i whoisCB2.jpg -o whoisCB2_cbc.png -k 0123456789abcdef -m AES_CBC 
	python encrypt_image.py -i pic_original.bmp -o pic_original_ecb.png -k 0123456789abcdef -m AES_ECB 
	python encrypt_image.py -i pic_original.bmp -o pic_original_cbc.png -k 0123456789abcdef -m AES_CBC
    
"""

import argparse
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

AES_BLOCK_SIZE = 16  # bytes (128 bits)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Encrypt an image's pixel data with AES-128 (ECB or CBC)."
    )
    parser.add_argument("-i", "--input", required=True, help="input image filename")
    parser.add_argument("-o", "--output", required=True, help="output image filename")
    parser.add_argument("-k", "--key", required=True, help="128-bit key (16 ASCII characters)")
    parser.add_argument(
        "-m", "--mode",
        required=True,
        choices=["AES_ECB", "AES_CBC"],
        help="encryption mode: AES_ECB or AES_CBC",
    )
    return parser.parse_args()


def get_key_bytes(key_str):
    """Validate and convert the command-line key string into 16 raw key bytes."""
    key_bytes = key_str.encode("utf-8")
    if len(key_bytes) != 16:
        raise ValueError(
            f"Key must be exactly 16 characters (128 bits) long for AES-128; "
            f"got {len(key_bytes)} characters."
        )
    return key_bytes


def build_cipher(mode, key_bytes):
    """Create the AES cipher object for the requested mode."""
    if mode == "AES_ECB":
        return AES.new(key_bytes, AES.MODE_ECB)
    elif mode == "AES_CBC":
        # Fixed all-zero IV keeps this reproducible/simple for the assignment;
        # in a real system a random IV would be generated and stored/prepended.
        iv = b"\x00" * AES_BLOCK_SIZE
        return AES.new(key_bytes, AES.MODE_CBC, iv)
    else:
        raise ValueError(f"Unsupported mode: {mode}")


def encrypt_image(input_path, output_path, key_str, mode):
    # 1. Read the image
    img = Image.open(input_path)
    img = img.convert("RGB")  # normalize to a known, fixed-size-per-pixel mode

    # 2. Convert to a byte object (raw pixel data, no header/metadata)
    pixel_bytes = img.tobytes()
    original_length = len(pixel_bytes)

    # 3. Pad the bytes to a multiple of the AES block size (PKCS7)
    padded_bytes = pad(pixel_bytes, AES_BLOCK_SIZE)

    # 4. Encrypt the bytes
    key_bytes = get_key_bytes(key_str)
    cipher = build_cipher(mode, key_bytes)
    encrypted_bytes = cipher.encrypt(padded_bytes)

    encrypted_bytes_trimmed = encrypted_bytes[:original_length]

    # 5. Convert back to an image object using the ORIGINAL size/mode
    encrypted_img = Image.frombytes(img.mode, img.size, encrypted_bytes_trimmed)

    # 6. Save as an image file
    encrypted_img.save(output_path)
    print(f"Saved encrypted image to '{output_path}' using {mode}.")


def main():
    args = parse_args()
    encrypt_image(args.input, args.output, args.key, args.mode)


if __name__ == "__main__":
    main()