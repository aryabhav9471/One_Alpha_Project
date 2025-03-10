import random
import string

def otp_encrypt(plaintext, key):
    if len(plaintext) != len(key):
        raise ValueError("The key must be the same length as the plaintext")

    ciphertext = []

    for p_char, k_char in zip(plaintext.upper(), key.upper()):
        p_index = ord(p_char) - ord('A')
        k_index = ord(k_char) - ord('A')

        c_index = (p_index + k_index) % 26
        c_char = chr(c_index + ord('A'))

        ciphertext.append(c_char)

    return ''.join(ciphertext)

def generate_key(length):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

plaintext = input("Enter the plaintext: ").replace(" ", "").upper()
key = input("Enter the key (same length as plaintext): ").upper()
if len(key) != len(plaintext):
    print("Key must be the same length as the plaintext. Please try again.")
else:
    ciphertext = otp_encrypt(plaintext, key)
    print(f"Ciphertext: {ciphertext}")
