import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

SECRET_KEY = "PassGuardPro2024SecretEncryptKey"


def get_key():
    return hashlib.sha256(SECRET_KEY.encode()).digest()


def encrypt_password(plain_text):
    key = get_key()
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))
    return base64.b64encode(iv + encrypted).decode('utf-8')


def decrypt_password(encrypted_text):
    try:
        key = get_key()
        raw = base64.b64decode(encrypted_text)
        iv = raw[:16]
        encrypted = raw[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return decrypted.decode('utf-8')
    except Exception:
        return '*** Decryption Error ***'