import json
import os
import sys
import urllib

from bs4 import BeautifulSoup
import requests


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
            html = self.session.get(next(query_gen)).text
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


def main():
    google = Google()
    if len(sys.argv) != 3:
        print('Invalid argment')
        print(
            '> python3 ./image_collector_cui.py [target name] [download number]')
        sys.exit()
    else:
        # Save location
        name = sys.argv[1]
        data_dir = 'data/'
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs('data/' + name, exist_ok=True)

        # Search image
        result = google.search(
            name, maximum=int(sys.argv[2]))

        # Download
        download_error = []
        for i in range(len(result)):
            print('-> Downloading image', str(i + 1).zfill(4))
            try:
                urllib.request.urlretrieve(
                    result[i], data_dir + name + '/' + str(i + 1).zfill(4) + '.jpg')
            except BaseException:
                print('--> Could not download image', str(i + 1).zfill(4))
                download_error.append(i + 1)
                continue

        print('Complete download')
        print('├─ Download', len(result) - len(download_error), 'images')
        print('└─ Could not download', len(
            download_error), 'images', download_error)


if __name__ == '__main__':
    main()
