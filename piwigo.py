#!/usr/bin/env python3

from configparser import ConfigParser
from math import ceil
from pathlib import Path
from requests import Session
from requests.compat import urljoin


class Piwigo(object):

    def __init__(self, url, username, password):
        self.url = urljoin(url, 'ws.php?format=json')
        self.session = Session()
        # login to piwigo
        self._request('session.login', username=username, password=password)
        if self.is_ok:
            self._request('session.getStatus')
            if self.is_ok:
                self.token = self.msg.get('pwg_token', '')

    def _request(self, method, **kwargs):
        self.is_ok = False
        files = kwargs.pop('files', None)
        kwargs.update({'method': f'pwg.{method}'})
        resp = self.session.post(self.url, kwargs, files=files)
        if resp.status_code != 200:
            self.error = f'HTTP error ({resp.text})'
        else:
            # print(resp.text)
            resp = resp.json()
            if resp['stat'] == 'fail':
                self.error = resp.get('message')
            else:
                self.is_ok = True
                self.msg = resp.get('result')

    def create_album(self, name):
        self._request('categories.add', name=name)
        return self.msg.get('id') if self.is_ok else 0

    def upload(self, filename, album_id, chunk_size=500_000):

        def chunks(filename, chunk_size):
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        p = Path(filename)
        name = p.stem
        chunks_num = ceil(p.stat().st_size / chunk_size)
        for i, c in enumerate(chunks(filename, chunk_size)):
            self._request('images.upload',
                          pwg_token=self.token,
                          category=album_id,
                          name=name,
                          chunk=i,
                          chunks=chunks_num,
                          files={'file': c})


if __name__ == '__main__':
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
