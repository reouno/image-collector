#!/usr/bin/env python3

'''
Take statistics
- histogram of the no. of samples for each class


Which data can be dealt with?
- dataset for classification
- each category (class) has one directory including all samples belonging to the category
- assuming the following directory structure
[dataset top dir to be passed as the argument]
  |
  |--[class 1 dir]
  |    |
  |    |--[img file]
  |    |--[img file]
  |    |--...
  |--[class 2 dir]
  |--...
'''

from collections import OrderedDict
import glob
import matplotlib.pyplot as plt
import os
import shutil
from typing import Text

def main(
        dataset_dir: Text,
        dest_dir: Text='dataset_stats'
        ):
    '''statistics
    :param dataset_dir: dataset directory
    '''

    # histogram file name
    hist_file = 'hist.png'
    # summary file name
    summary_file = 'summary.txt'

    # validate args
    if not os.path.isdir(dataset_dir):
        raise RuntimeError('invalid dataset dirctory path, "{}", is not dir or does not exist'.format(dataset_dir))
    if os.path.exists(dest_dir):
        while True:
            choice = input('Delete existing {}?[y/N]: '.format(dest_dir))
            if choice.upper() in ['Y','YES']:
                shutil.rmtree(dest_dir)
                break
            elif choice.upper() in ['N','NO']:
                print('delete the directory or specify another directory')
                exit()
    try:
        os.makedirs(dest_dir)
    except OSError as e:
        print('Cannot create directory. \nError message:',e)
        exit()

    # basic stats
    class_dirs = [d for d in glob.glob(os.path.join(dataset_dir, '*')) if os.path.isdir(d)]
    class_dirnames = [os.path.split(d)[1] for d in class_dirs] # for labels of histogram
    class_samples = OrderedDict()
    for dirpath in class_dirs:
        class_samples[dirpath] = [f for f in glob.glob(os.path.join(dirpath, '*')) if is_img_file(f)]
    num_class_samples = list(map(len, class_samples.values()))

    # histogram of the number of samples for each class
    num_class_samples_names = sorted(zip(class_dirnames, num_class_samples), key=lambda x: x[1], reverse=True)
    classes, nums = zip(*num_class_samples_names)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.bar(list(classes), list(nums))
    fig.savefig(os.path.join(dest_dir, hist_file))

    # dataset summary
    contents = ''
    num_total = sum(num_class_samples)
    contents += 'the number of samples: {:,}'.format(num_total)
    contents += '\n\n\n'
    for i, (class_name, n) in enumerate(zip(class_dirnames, num_class_samples)):
        contents += '{:03d}  {:<40s}: {}\n'.format(i, class_name, n)
    with open(os.path.join(dest_dir, summary_file), 'w') as f:
        f.write(contents)

def is_img_file(fpath: Text):
    exts = ['.BMP','.GIF','.JPG','.JPEG','.PNG','.TIF','.TIFF']
    if os.path.splitext(fpath)[1].upper() in exts:
        return True
    else:
        return False


if __name__ == '__main__':
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument('data', help='dataset directory')
    psr.add_argument('-o', '--out', help='output directory', required=False, default='dataset_stats')
    a = psr.parse_args()
    main(a.data, dest_dir=a.out)
