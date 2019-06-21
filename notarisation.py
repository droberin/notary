import logging
from flask import Flask
from os import environ
from os.path import isfile
from notary import Notary

app = Flask(__name__)


@app.route('/notary/<token>/<encryption_key>')
def decrypt_data(token, encryption_key):
    expected_token = environ.get('token')
    if not expected_token == token:
        return "Incorrect password, fuck off"
    try:
        cryptographer = Notary(encryption_key)
    except ValueError:
        return 'That key is fucked up'
    if getattr(app, '_encrypted_from_env'):
        data = environ.get('encrypted_data')
    else:
        with open('encrypted_data.bytes', 'rb') as data_file_handler:
            data = data_file_handler.read()
            data_file_handler.close()
    decrypted_data = cryptographer.decrypt(data)
    if not decrypt_data:
        logging.debug('Valid token but possible incorrect decryption key was provided... ')
    return decrypted_data


if __name__ == '__main__':
    if not environ.get('token'):
        raise ValueError('No token found in env var "token".')
    if not isfile('encrypted_data.bytes'):
        if environ.get('encrypted_data'):
            setattr(app, '_encrypted_from_env', True)
        else:
            raise ValueError('No file nor env var.')
    app.run(host='0.0.0.0')
