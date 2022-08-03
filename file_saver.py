from telegram import File
import secrets


class FileException(Exception):
    pass


def file_saver(file):
    try:
        new_file = File.download(file, custom_path=f'static/img/{secrets.token_urlsafe(16)}.jpg')
    except FileException:
        new_file = File.download(file, custom_path=f'static/img/{secrets.token_urlsafe(16)}.png')
    return new_file
