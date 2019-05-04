# IMAGE-COLLECTOR

## Overview
This program collects images from Google Image Search.

## Description
You can get any number of arbitrary images from Google Image Search.  
The main use is to automatically collect data sets for machine learning.

## Requirement
This code is written in `Python 3.6.6`.  
You can get the necessary libraries like below.  
```
pip3 install -r requirements.txt
```

## Usage
```
# target name is one of query, directory path, or file path
python3 image_collector_cui.py [target name] [download number] [save dir]
```

## Run sample
```
# use directory
./run_sample.sh dir

# use file
./run_sample.sh file

# use query
./run_sample.sh query
```

## Test
```
./test.sh
```

## Licence
[MIT License](https://github.com/reouno/image-collector/blob/master/LICENSE)

## Notice
I do not assume any responsibility for copyright issues concerning image collection.
