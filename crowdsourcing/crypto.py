import base64
from Crypto import Random
from Crypto.Cipher import AES


class AESUtil(object):
    def __init__(self, key):
        self.key = base64.b64decode(key)

    @staticmethod
    def _pad(data):
        length = AES.block_size - (len(data) % AES.block_size)
        data += chr(length) * length
        return data

    def encrypt(self, data):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(self._pad(data)))

    def decrypt(self, data):
        decoded_data = base64.b64decode(data)
        iv = decoded_data[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(decoded_data[AES.block_size:])
        return decrypted[:-ord(decrypted[len(decrypted) - 1:])]
