from cryptography.fernet import Fernet


class Notary:
    cryptographer = None

    def __init__(self, key):
        if type(key) != bytes:
            key = self.to_bytes(key)
        self.cryptographer = Fernet(key)

    def decrypt(self, data_to_decrypt):
        if type(data_to_decrypt) != bytes:
            data_to_decrypt = self.to_bytes(data_to_decrypt)
        return self.cryptographer.decrypt(data_to_decrypt)

    @staticmethod
    def to_bytes(input_data):
        return bytes(input_data, encoding='utf-8')
