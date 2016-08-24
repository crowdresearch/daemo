import base64
from Crypto import Random
from Crypto.Cipher import AES
from django.conf import settings
from hashids import Hashids


def to_hash(pk):
    id_hash = Hashids(salt=settings.SECRET_KEY, min_length=12)
    return id_hash.encode(pk)


def to_pk(hash_string):
    id_hash = Hashids(salt=settings.SECRET_KEY, min_length=12)
    pk = id_hash.decode(hash_string)
    if len(pk):
        return pk[0]
    else:
        return None


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
