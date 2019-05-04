import csv
from datetime import datetime
import glob
import json
import os
import re
import sys
import time
import urllib

from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError, ReadTimeout
from typing import List

def queries_from_other_sources(func):
    '''decorator to edit sys.args and run func several times

    If the query is file path:
    The file should be simple text format and one query in one line.

    If the query is directory path:
    Assuming the dirctory names like "n02098105-soft-coated_wheaten_terrier".
    For example, the above directory names are parsed to "soft-coated wheaten terrier"
    with the following rules:
    - if the first character is "n", the following 8 characters are numbers,
      and the following character is "-", then remove all these 10 characters
      and apply the following rules to the remaining characters.
    - replace all the "_" with " " (space).

    Otherwise:
    just use the query to search with google
    '''
    def wrapper(*args, **kwargs):
        if len(args[0]) != 4:
            raise RuntimeError('Invalid argment\n> python3 ./image_collector_cui.py [target name] [download number] [save dir]')
        if os.path.isfile(args[0][1]):
            with open(args[0][1], 'r') as f:
                queries = [q[:-1] for q in f.readlines()] # remove '\n' at the end of each string
            dirnames = [q.replace(' ', '_') for q in queries]
            args[0].append('')
            for query, dirname in zip(queries, dirnames):
                args[0][1] = query
                args[0][4] = dirname
                func(args[0], **kwargs)
        elif os.path.isdir(os.path.split(args[0][1])[0]):
            dirnames = [os.path.split(p)[1] for p in glob.glob(args[0][1])]
            queries = [re.sub(r'^n\d{8}-', '', s.replace('_', ' ')) for s in dirnames]
            args[0].append('')
            for query, dirname in zip(queries, dirnames):
                args[0][1] = query
                args[0][4] = dirname
                func(args[0], **kwargs)
        else:
            func(args[0], **kwargs)
        return None
    return wrapper


class Google(object):

    def __init__(self):
        self.GOOGLE_SEARCH_URL = 'https://www.google.co.jp/search'
        self.session = requests.session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'})

    def search(self, keyword, maximum):
        print('Begining searching', keyword)
        query = self.query_gen(keyword)
        return self.image_search(query, maximum)

    def query_gen(self, keyword):
        # Search query generator
        page = 0
        while True:
            params = urllib.parse.urlencode({
                'q': keyword,
                'tbm': 'isch',
                'ijn': str(page)})

            yield self.GOOGLE_SEARCH_URL + '?' + params
            page += 1

    def image_search(self, query_gen, maximum):
        # Search image
        result = []
        total = 0
        while True:
            # Search
            query = next(query_gen)
            try:
                html = self.session.get(query, timeout=20).text
            except (ConnectionError, ReadTimeout) as e:
                print(e)
                print('retry in 10 sec...')
                time.sleep(10) # may need some time to escape connection refusion next time
                try:
                    html = self.session.get(query, timeout=20).text
                except Exception as e:
                    print(e)
                    continue
            soup = BeautifulSoup(html, 'lxml')
            elements = soup.select('.rg_meta.notranslate')
            jsons = [json.loads(e.get_text()) for e in elements]
            imageURLs = [js['ou'] for js in jsons]

            # Add search result
            if not len(imageURLs):
                print('-> No more images')
                break
            elif len(imageURLs) > maximum - total:
                result += imageURLs[:maximum - total]
                break
            else:
                result += imageURLs
                total += len(imageURLs)

        print('-> Found', str(len(result)), 'images')
        return result


@queries_from_other_sources
def main(args: List):
    '''download images by google search
    :param args: should be sys.argv
    '''
    google = Google()
    req_headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
    if len(args) < 4:
        print('Invalid argment')
        print(
            '> python3 ./image_collector_cui.py [target name] [download number] [save dir]')
        sys.exit()
    else:
        # Save location
        name = args[1]
        data_dir = args[3]
        if len(args) > 4:
            dest_dir_path = os.path.join(data_dir, 'images', args[4])
            urls_dest_dir_path = os.path.join(data_dir, 'urls')
            urls_file = os.path.join(urls_dest_dir_path, args[4] + '.csv')
        else:
            dest_dir_path = os.path.join(data_dir, 'images', name.replace(' ', '_'))
            urls_dest_dir_path = os.path.join(data_dir, 'urls')
            urls_file = os.path.join(urls_dest_dir_path, name.replace(' ', '_') + '.csv')
        os.makedirs(dest_dir_path, exist_ok=True)
        os.makedirs(urls_dest_dir_path, exist_ok=True)

        # Search image
        result = google.search(
            name, maximum=int(args[2]))
        result_logs = []

        # Download
        download_error = []
        for i in range(len(result)):
            print('-> Downloading image', str(i + 1).zfill(4))
            try:
                request = urllib.request.Request(url=result[i], headers=req_headers)
                data = urllib.request.urlopen(request, timeout=15).read()
                with open(os.path.join(dest_dir_path, str(i + 1).zfill(4) + '.jpg'), "wb") as f:
                    f.write(data)
                downloaded = 1
            except requests.exceptions.ConnectionError as e:
                print('--> Could not download image', str(i + 1).zfill(4))
                print(e)
                download_error.append(i + 1)
                downloaded = 0
                time.sleep(10) # may need some time to escape connection refusion next time
            except Exception as e:
                print('--> Could not download image', str(i + 1).zfill(4))
                print(e)
                download_error.append(i + 1)
                downloaded = 0

            result_logs.append((i+1, result[i], downloaded))

        # save logs
        with open(urls_file, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(['No.', 'url', 'is_downloaded'])
            writer.writerows(result_logs)

        print('Complete download')
        print('├─ Download', len(result) - len(download_error), 'images')
        print('└─ Could not download', len(
            download_error), 'images', download_error)


if __name__ == '__main__':
    main(sys.argv)
