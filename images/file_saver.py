from telegram import File


def file_saver(file):
    new_file = File.download(file)
    return new_file