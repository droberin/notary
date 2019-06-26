import logging
from flask import Flask, request
from os import environ
from os.path import isfile, join, curdir
from notary import Notary
from notary.notifier.notifier import NotificationManager
from yaml import safe_load

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
notification_manager = NotificationManager()


@app.route('/notary/<token>/<encryption_key>')
def decrypt_data(token, encryption_key):
    expected_token = environ.get('token')
    if not expected_token == token:
        return "Incorrect password, fuck off"
    try:
        cryptographer = Notary(encryption_key)
    except ValueError:
        notification_manager.backend_module.notify(
            message=f'Valid token requested but malformed decryption key from {request.remote_addr}'
        )
        return 'That key is fucked up'
    if getattr(app, '_encrypted_from_env'):
        data = environ.get('encrypted_data')
    else:
        with open('encrypted_data.bytes', 'rb') as data_file_handler:
            data = data_file_handler.read()
            data_file_handler.close()
    decrypted_data = cryptographer.decrypt(data)
    if not decrypt_data:
        message = f'Valid token requested but incorrect decryption key from {request.remote_addr}'
        response = notification_manager.backend_module.notify(message=message)
        logging.warning(message)
        return message
    message = f':WARNING: Your key has been obtained from {request.remote_addr}'
    response = notification_manager.backend_module.notify(message=message)
    if response:
        return decrypted_data
    else:
        logging.warning('Key will not be sent as notification backend did not respond properly.')
        return


if __name__ == '__main__':
    if not environ.get('token'):
        raise ValueError('No token found in env var "token".')
    if not isfile('encrypted_data.bytes'):
        if environ.get('encrypted_data'):
            setattr(app, '_encrypted_from_env', True)
        else:
            raise ValueError('No file nor env var.')
    with open(join(curdir, 'etc', 'notary.yaml'), 'rb') as configuration_data_file_handler:
        configuration_data = safe_load(configuration_data_file_handler)
        if 'notifications' in configuration_data:
            if 'type' in configuration_data['notifications']:
                notification_backend = configuration_data['notifications']['type']
            elif not environ.get('NOTIFICATION_BACKEND'):
                notification_backend = environ.get('NOTIFICATION_BACKEND')
            else:
                raise ValueError(f'No notification backend defined.')
    if not notification_manager.select_backend(notification_backend):
        raise ValueError(f'Notification backend "{notification_backend}" is not valid')

    notification_manager.backend_module.configure(configuration=configuration_data['notifications'])
    if not notification_manager.backend_module.validate_configuration():
        exit(1)
    app.run(host='0.0.0.0')
