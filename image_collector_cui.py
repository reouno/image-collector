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
from urllib.request import HTTPError, URLError

def with_timestamp(func):
    '''add prefix of timestamp to input text
    '''
    def wrapper(*args, **kwargs):
        prefix = '[{}]:'.format(datetime.now())
        #arg = ' '.join(str(args))
        #arg = '[{}]: {}'.format(datetime.now(), arg)
        args = [prefix] + list(args)
        return func(*args, **kwargs)
    return wrapper

@with_timestamp
def my_print(*args, **kwargs):
    print(*args, **kwargs)

def print_erro_with_trace(e):
    '''print error contents with trace back
    :param e: exception object
    '''
    # NOTE: seems not to show trace back
    tb = sys.exc_info()[2]
    my_print(e.with_traceback(tb))

def queries_from_other_sources(func):
    '''decorator to edit sys.args and run func several times

    If the query is file path:
    Assuming the file contains query texts.
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
    just use the arg as query to search with google
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

            # retry download if the no. of images is less than this number.
            min_num_enough_images = 400

            dirpaths = [p for p in glob.glob(args[0][1]) if os.path.isdir(p)]
            #my_print('dirpaths:',dirpaths)
            dirnames = [os.path.split(p)[1] for p in dirpaths]
            #my_print('dirnames:',dirnames)
            queries = [re.sub(r'^n\d{8}-', '', s.replace('_', ' ')) for s in dirnames]
            args[0].append('')
            for query, dirname, dirpath in zip(queries, dirnames, dirpaths):
                num_images = len([f for f in glob.glob(os.path.join(dirpath, '*')) if os.path.isfile(f)])
                my_print('The no. of images downloaded with "{}" of "{}": {}'.format(query, dirname, num_images))
                if num_images >= min_num_enough_images:
                    my_print('skip download')
                    continue
                args[0][1] = query
                args[0][4] = dirname
                my_print(args[0])
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
        my_print('Begining searching', keyword)
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

    def request_with_retry(self, query, timeout=20, max_try=2):
        '''try to send search request and get html
        :param query: request query
        :param timeout: request timeout
        :param max_try: max times of trying to request. 1 means no retry.
        '''
        html = None
        # retry if the exception is ConnectionError or ReadTimeout
        for i in range(max_try):
            try:
                html = self.session.get(query, timeout=timeout).text
                break
            except (ConnectionError, ReadTimeout) as e:
                print('ConnectionError, ReadTimeout')
                print_erro_with_trace(e)
            except Exception as e:
                print('Exception')
                print_erro_with_trace(e)
                break

            my_print('retry in 30 sec...')
            time.sleep(30) # may need some time to escape connection refusion next time

        return html

    def image_search(self, query_gen, maximum):
        # Search image
        result = []
        total = 0
        while True:
            # Search
            query = next(query_gen)
            html = self.request_with_retry(query, timeout=20, max_try=2)
            if html is None:
                continue

            # parse to find image url
            soup = BeautifulSoup(html, 'lxml')
            elements = soup.select('.rg_meta.notranslate')
            jsons = [json.loads(e.get_text()) for e in elements]
            imageURLs = [js['ou'] for js in jsons]

            # Add search result
            if not len(imageURLs):
                my_print('-> No more images')
                break
            elif len(imageURLs) > maximum - total:
                result += imageURLs[:maximum - total]
                break
            else:
                result += imageURLs
                total += len(imageURLs)

        my_print('-> Found', str(len(result)), 'images')
        return result

def download_img_with_retry(query, timeout=15, max_try=2):
    '''try to download image from web URL
    :param query: request query
    :param timeout: request timeout
    :param max_try: max times of trying to request. 1 means no retry.
    '''
    data = None
    # retry if the exception is ConnectionError or URLError
    for i in range(max_try):
        try:
            data = urllib.request.urlopen(query, timeout=15).read()
            break
        except HTTPError as e:
            print('HTTPError')
            # must be caught before URLError because HTTPError is
            # sub class of URLError.
            print_erro_with_trace(e)
            break
        except (ConnectionError, URLError) as e:
            print('ConnectionError, URLError')
            print_erro_with_trace(e)
        except Exception as e:
            print('Exception')
            print_erro_with_trace(e)
            break

        my_print('retry in 30 sec...')
        time.sleep(30) # may need some time to escape connection refusion next time

    return data

@queries_from_other_sources
def main(args: List):
    '''download images by google search
    :param args: should be sys.argv

    TODO: should use argparse to parse command line arguments.
    '''
    google = Google()
    req_headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
    if len(args) < 4:
        my_print('Invalid argment')
        my_print(
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
            my_print('-> Downloading image', str(i + 1).zfill(4))

            query = urllib.request.Request(url=result[i], headers=req_headers)
            image_data = download_img_with_retry(query, timeout=15, max_try=2)
            if image_data is None:
                my_print('--> Could not download image with error', str(i + 1).zfill(4))
                download_error.append(i + 1)
                downloaded = 0
            else:
                with open(os.path.join(dest_dir_path, str(i + 1).zfill(4) + '.jpg'), "wb") as f:
                    f.write(image_data)
                downloaded = 1

            result_logs.append((i+1, result[i], downloaded))

        # save logs
        with open(urls_file, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(['No.', 'url', 'is_downloaded'])
            writer.writerows(result_logs)

        my_print('Complete download')
        my_print('├─ Download', len(result) - len(download_error), 'images')
        my_print('└─ Could not download', len(
            download_error), 'images', download_error)


if __name__ == '__main__':
    main(sys.argv)
