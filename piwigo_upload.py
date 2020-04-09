#!/usr/bin/env python3

from configparser import ConfigParser
from pathlib import Path
from tqdm import tqdm
from piwigo import Piwigo

config = ConfigParser()
config.read(Path(__file__).resolve().parent.joinpath('config'))
if 'default' in config:
    host = config.get('default', 'host')
    username = config.get('default', 'username')
    password = config.get('default', 'password')
else:
    exit('Config file not found')

print('Login to Piwigo...', end='')
p = Piwigo(host, username, password)
if p.is_ok:
    print(' OK')
    work_dir = Path.cwd()
    album_name = work_dir.stem
    print(f'Create album "{album_name}"...', end='')
    album_id = p.create_album(album_name)
    if album_id:
        print(' OK')
        # pathlib in Linux is case sensitive ¯\_(ツ)_/¯
        ext = ['jpg', 'JPG', 'jpeg', 'JPEG']
        files = []
        for e in ext:
            files.extend(list(work_dir.glob(f'*.{e}')))
        n_files = len(files)
        if n_files:
            print(f'Uploading {n_files} photos...')
            errors = []
            with tqdm(total=n_files, ascii=' #') as pbar:
                for f in sorted(files):
                    pbar.write(str(f))
                    p.upload(f, album_id)
                    if not p.is_ok:
                        errors.append(f)
                    pbar.update(1)
            n_err = len(errors)
            print(f'\nCompleted with {n_err} error{"" if n_err==1 else "s"}.')
            if n_err:
                print('Failed to upload files:')
                for e in errors:
                    print(str(e))
input('Press ENTER to continue...')
