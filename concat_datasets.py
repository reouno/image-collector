import glob
import os
import re
import shutil
from typing import Dict, Set, Text

def main(
        mode: Text,
        main_set_dir: Text,
        second_set_dir: Text,
        dest_path: Text
        ):
    '''concatenate two datasets into one new dataset
    Four modes are supported:
      merge: merge two datasets (merge class and merge image, if there are two files with the same name, the file of second is deleted.)
      add_image: merge (merge class and add image. if there are two files with the same name, the file of second is renamed.)
      replace: replace with larger class directory (if there are two classes with the same name, select one that has larger number of files)
      add_class: sum of two datasets. if two datasets has same class label, second set class name is renamed to distinguish

    :param mode: merge, add_image, replace, add_class
    :param main_set_dir: main dataset directory path
    :param second_set_dir: second dataset directory path
    :param dest_path: directory path to new dataset
    '''

    # constants
    ADD_CLASS = 'add_class'
    ADD_IMAGE = 'add_image'
    MERGE = 'merge'
    REPLACE = 'replace'
    MODES = [ADD_CLASS, ADD_IMAGE, MERGE, REPLACE]

    # validate args
    if not mode in MODES:
        raise RuntimeError('invalid `mode`, {} are supported.'.format(MODES))

    if not os.path.isdir(main_set_dir):
        raise RuntimeError('main set directory does not exist or is not direcotry, "{}"'.format(main_set_dir))
    if not os.path.isdir(second_set_dir):
        raise RuntimeError('second set directory does not exist or is not direcotry, "{}"'.format(second_set_dir))
    if os.path.exists(dest_path):
        while True:
            choice = input('Delete existing "{}"?[y/N]: '.format(dest_path))
            if choice.upper() in ['Y','YES']:
                shutil.rmtree(dest_path)
                break
            elif choice.upper() in ['N','NO']:
                print('Delete/move "{}", or specify another path'.format(dest_path))
                exit()
    os.makedirs(dest_path)
    os.makedirs(os.path.join(dest_path, 'images'))
    os.makedirs(os.path.join(dest_path, 'urls'))

    # tasks overview
    #   1. do different task in the condition of `mode`
    #   2. get dir list and file list for each dir of main set
    #   3. get the same info of second set
    #   4. concatenate

    concator = DatasetConcatenator(main_set_dir, second_set_dir, dest_path)

    if mode == ADD_CLASS:
        concator.add_class()
    elif mode == MERGE:
        concator.merge()
    elif mode == ADD_IMAGE:
        concator.add_image()
    else: # mode == REPLACE
        concator.replace()

    return

def read_dataset_path(dir_path: Text):
    '''read dataset paths
    :param dir_path: dataset path, assuming the following structure

    dir_path
      |
      |--class1 dir
      |    |--img1 file
      |    |--img2 file
      |--class2 dir
      |    |--img1 file
      |    |--img2 file
    jpg
    '''
    def glob_img(d):
        '''get all image file path
        '''
        return set([p for p in glob.glob(os.path.join(d, '*')) if re.fullmatch(r'.*\.(BMP|GIF|JPG|JPEG|PNG|TIF|TIFF)', p.upper())])

    class_dirs = [d for d in glob.glob(os.path.join(dir_path, '*')) if os.path.isdir(d)]
    dataset = {class_dir:glob_img(class_dir) for class_dir in class_dirs}
    return dataset

def list_dirnames(dir_paths: Text):
    '''get all dir names (equal to class labels)
    '''
    return set([os.path.split(d)[1] for d in dir_paths])

class Dataset:
    def __init__(self, dir_path):
        self.__root_dir = dir_path
        self.__images_paths: Dict[Text, Set[Text]] = read_dataset_path(self.images_dir())
        self.__images_infos: Dict[Text, List[Text, int]] = {os.path.split(d)[1]:[d, len(vs)] for d, vs in self.__images_paths.items()}
        self.__urls_paths: Dict[Text, Text] = {os.path.splitext(os.path.split(d)[1])[0]:d for d in glob.glob(os.path.join(self.urls_dir(), '*'))}

    def images_dir(self):
        return os.path.join(self.__root_dir, 'images')

    def urls_dir(self):
        return os.path.join(self.__root_dir, 'urls')

    def class_labels(self):
        return  self.__images_infos.keys()

    def images_paths(self):
        return self.__images_paths

    def urls_paths(self):
        return self.__urls_paths

    def num_samples(self, label):
        try:
            return self.__images_infos[label][1]
        except KeyError as e:
            return 0

    def class_path(self, label):
        try:
            return self.__images_infos[label][0]
        except KeyError as e:
            return None

    def urls_file(self, label):
        try:
            return self.__urls_paths[label]
        except KeyError as e:
            return None

class DatasetConcatenator:
    def __init__(self, main_set_dir: Text, second_set_dir: Text, dest_path: Text):
        self.main_set_dir = main_set_dir
        self.second_set_dir = second_set_dir
        self.dest_path = dest_path
        self.dest_images_path = os.path.join(self.dest_path, 'images')
        self.dest_urls_path = os.path.join(self.dest_path, 'urls')

        self.main_set = Dataset(self.main_set_dir)
        self.second_set = Dataset(self.second_set_dir)

    def add_class(self):
        raise RuntimeError('need update')
        # copy main set to dest
        shutil.copytree(self.main_set_dir, self.dest_path)
        print('copy main set {}\n  to {}\n  done'.format(self.main_set_dir, self.dest_path))

        ## copy second set to dest with renaming dir name if exists in main
        #for class_dir in self.second_set.paths().keys():
        #    dir_name = os.path.split(class_dir)[1]
        #    while dir_name in self.main_set.class_labels():
        #        dir_name += '_2'
        #    save_dir = os.path.join(self.dest_path, dir_name)
        #    shutil.copytree(class_dir, save_dir)
        #    print('copy {}\n  in second set to\n  {}\n  done'.format(class_dir, save_dir))

    def merge(self):
        # to be implemented
        pass

    def add_image(self):
        # to be implemented
        pass

    def replace(self):
        '''concatenate two dataset with "replace" mode
        sub tasks
          1. get union classes
          2. compare the no. of samples in main and in second
          3. adopt set that has larger number of samples
        '''
        union_classes = set(self.main_set.class_labels()).union(self.second_set.class_labels())
        for class_name in union_classes:
            print('copy {} class...'.format(class_name))
            class_dir, urls_file = self.select_larger(class_name)
            print('class_dir:{}, urls_file:{}'.format(class_dir, urls_file))
            dest_dir = os.path.join(self.dest_images_path, class_name)
            dest_url_file = os.path.join(self.dest_urls_path, os.path.split(urls_file)[1])
            shutil.copytree(class_dir, dest_dir)
            shutil.copy(urls_file, dest_url_file)
            print('copy {}\n  to\n  {}\n  done'.format(class_dir, dest_dir))
            print('copy {}\n  to\n  {}\n  done'.format(urls_file, dest_url_file))

    def select_larger(self, class_name):
        num_main_samples = self.main_set.num_samples(class_name)
        num_second_samples = self.second_set.num_samples(class_name)
        print('main: {}, second: {}'.format(num_main_samples, num_second_samples))
        if num_main_samples >= num_second_samples:
            return self.main_set.class_path(class_name), self.main_set.urls_file(class_name)
        else:
            return self.second_set.class_path(class_name), self.second_set.urls_file(class_name)



if __name__ == '__main__':
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument('--mode', help='mode of concatenation. merge, add_image, select, and add_class are supported.', required=True)
    psr.add_argument('--main_set', help='main dataset directory path', required=True)
    psr.add_argument('--second_set', help='second dataset directory path', required=True)
    psr.add_argument('--dest', help='directory path to new dataset', required=True)
    a = psr.parse_args()
    main(a.mode, a.main_set, a.second_set, a.dest)
