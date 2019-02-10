"""
image_collector.py

You can get any number of arbitrary images from Google Image Search.
The main use is to automatically collect data sets for machine learning.

Python 3.6.6
"""

import json
import os
import urllib

from bs4 import BeautifulSoup
import requests
import tkinter as tk
from tkinter import filedialog


class ImageCollector(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        master.minsize(width=600, height=450)

        # Default is currently directory
        self.dl_dir = os.getcwd().replace('\\', '/')

        self.pack()
        self.create_entry()
        self.create_slider()
        self.create_button()
        self.create_execute()

        self.GOOGLE_SEARCH_URL = 'https://www.google.co.jp/search'
        self.session = requests.session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'})

        self.label_selected = tk.Label()

    def create_entry(self):
        # Entry of what user download
        self.frame = tk.Frame(root, pady=20)
        self.frame.pack()
        self.label = tk.Label(
            self.frame,
            text='Input what you download.',
            font=(
                'consolas',
                12),
            height=2)
        self.label.pack()
        self.entry = tk.Entry(self.frame, font=(
            'consolas', 12), justify='center', width=15)
        self.entry.pack()

    def create_slider(self):
        # Slider of how many images user download
        self.label = tk.Label(
            self.frame,
            text='Input how many images you download.',
            font=(
                'consolas',
                12),
            height=2)
        self.label.pack()
        self.slider = tk.Scale(self.frame, orient='h',
                               from_=0, to=1000, length=200)
        self.slider.set(500)  # Default
        self.slider.pack()

    def create_filedialog(self):
        # If button pushed
        self.dl_dir = filedialog.askdirectory()
        self.label_selected.destroy()
        self.label_selected = tk.Label(
            self.frame, text=self.dl_dir, font=('consolas', 10), height=2)
        self.label_selected.pack()

    def create_button(self):
        # Button to get target directory
        self.label = tk.Label(
            self.frame,
            text='Select download directory.',
            font=(
                'consolas',
                12),
            height=2)
        self.label.pack()
        self.button = tk.Button(
            self.frame, text='reference', command=self.create_filedialog)
        self.button.pack()

    def create_execute(self):
        # Button to execute
        self.frame_exe = tk.Frame(root, pady=40)
        self.frame_exe.pack()
        self.button = tk.Button(
            self.frame_exe,
            text='execute',
            bg='#00ffff',
            command=self.download)
        self.button.pack()

    def download(self):
        # Download using dl_name, dl_count and dl_dir

        self.dl_name = self.entry.get()
        self.dl_count = self.slider.get()

        # Save location
        self.data_dir = self.dl_dir + '/data/'
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.data_dir + self.dl_name, exist_ok=True)

        # Search image and download
        self.result = self.search(
            self.dl_name, maximum=int(self.dl_count))

        download_error = []
        for i in range(len(self.result)):
            self.download_condition(i)
            try:
                urllib.request.urlretrieve(
                    self.result[i], self.data_dir + self.dl_name + '/' + str(i + 1).zfill(4) + '.jpg')
            except BaseException:
                download_error.append(i + 1)
                continue

    def download_condition(self, i):
        pass

    def search(self, keyword, maximum):
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
                # No images
                break
            elif len(imageURLs) > maximum - total:
                result += imageURLs[:maximum - total]
                break
            else:
                result += imageURLs
                total += len(imageURLs)

        return result


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Image Collector')
    root.geometry('800x600')
    app = ImageCollector(master=root)
    app.mainloop()
