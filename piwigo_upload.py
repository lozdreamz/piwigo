#!/usr/bin/env python3

from configparser import ConfigParser
from pathlib import Path
from .piwigo import Piwigo

config = ConfigParser()
config.read('config')
if 'default' in config:
    host = config.get('default', 'host')
    username = config.get('default', 'username')
    password = config.get('default', 'password')
else:
    exit('Config file not found')

p = Piwigo(host, username, password)
if p.is_ok:
    album_name = Path.cwd().stem
    print(f'Create album "{album_name}"...', end='')
    album_id = p.create_album(album_name)
    if album_id != 0:
        print(' OK')
        # pathlib in Linux is case sensitive ¯\_(ツ)_/¯
        files = list(Path.cwd().glob('*.jpg')) + list(Path.cwd().glob('*.JPG'))
        print(f'Uploading {len(files)} photos...')
        for f in files:
            p.upload(f, album_id)
            if p.is_ok:
                print('.')
            else:
                print('-')

input('Press ENTER to continue...')
