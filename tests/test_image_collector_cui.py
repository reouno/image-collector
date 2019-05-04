import glob
import os
import shutil
from unittest import TestCase

from image_collector_cui import main

class TestMain(TestCase):

    def testArgDir(self):
        query_dir = 'sample/chicken_breeds/*'
        num_queries = len([d for d in glob.glob(query_dir) if os.path.isdir(d)])
        search_len = 2
        out_dir = '.test_tmp_dir_out'
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        args = [None, query_dir, search_len, out_dir]
        main(args)

        # test output dir existence
        self.assertTrue(os.path.isdir(out_dir))

        # test existence of two sub dirs
        img_dir_root = os.path.join(out_dir, 'images')
        url_dir = os.path.join(out_dir, 'urls')
        self.assertTrue(os.path.isdir(img_dir_root))
        self.assertTrue(os.path.isdir(url_dir))

        # test existence of search query dirs
        # cannot test if download was successful
        img_dirs = [d for d in glob.glob(os.path.join(img_dir_root, '*')) if os.path.isdir(d)]
        self.assertEqual(num_queries, len(img_dirs))

        # test existence of url csvs
        csvs = [f for f in glob.glob(os.path.join(url_dir, '*.csv')) if os.path.isfile(f)]
        self.assertEqual(num_queries, len(csvs))

        # delete tmp
        shutil.rmtree(out_dir)

    def testArgFile(self):
        query_file = 'sample/search_queries.txt'
        with open(query_file, 'r') as f:
            num_queries = len([l for l in f.readlines() if len(l.strip()) > 0])
        search_len = 2
        out_dir = '.test_tmp_file_out'
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        args = [None, query_file, search_len, out_dir]
        main(args)

        # test output dir existence
        self.assertTrue(os.path.isdir(out_dir))

        # test existence of two sub dirs
        img_dir_root = os.path.join(out_dir, 'images')
        url_dir = os.path.join(out_dir, 'urls')
        self.assertTrue(os.path.isdir(img_dir_root))
        self.assertTrue(os.path.isdir(url_dir))

        # test existence of search query dirs
        # cannot test if download was successful
        img_dirs = [d for d in glob.glob(os.path.join(img_dir_root, '*')) if os.path.isdir(d)]
        self.assertEqual(num_queries, len(img_dirs))

        # test existence of url csvs
        csvs = [f for f in glob.glob(os.path.join(url_dir, '*.csv')) if os.path.isfile(f)]
        self.assertEqual(num_queries, len(csvs))

        # delete tmp
        shutil.rmtree(out_dir)

    def testArgQuery(self):
        query = 'johnny depp'
        search_len = 2
        out_dir = '.test_tmp_query_out'
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        args = [None, query, search_len, out_dir]
        main(args)

        # test output dir existence
        self.assertTrue(os.path.isdir(out_dir))

        # test existence of two sub dirs
        img_dir_root = os.path.join(out_dir, 'images')
        url_dir = os.path.join(out_dir, 'urls')
        self.assertTrue(os.path.isdir(img_dir_root))
        self.assertTrue(os.path.isdir(url_dir))

        # test existence of search query dirs
        # cannot test if download was successful
        img_dirs = [d for d in glob.glob(os.path.join(img_dir_root, '*')) if os.path.isdir(d)]
        self.assertEqual(1, len(img_dirs))

        # test existence of url csvs
        csvs = [f for f in glob.glob(os.path.join(url_dir, '*.csv')) if os.path.isfile(f)]
        self.assertEqual(1, len(csvs))

        # delete tmp
        shutil.rmtree(out_dir)
