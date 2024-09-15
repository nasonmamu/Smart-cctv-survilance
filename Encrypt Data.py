from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

key = b'Sixteen byte key'
cipher = AES.new(key, AES.MODE_CBC, iv=b'Sixteen byte IV ')

def encrypt(data):
    padded_data = pad(data.encode(), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_data).decode()

def decrypt(encrypted_data):
    encrypted_data = base64.b64decode(encrypted_data)
    cipher = AES.new(key, AES.MODE_CBC, iv=b'Sixteen byte IV ')
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data.decode()
