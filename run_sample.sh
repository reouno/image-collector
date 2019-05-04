#!/bin/sh
set -eu

ARG_DIR='dir'
ARG_FILE='file'
ARG_QUERY='query'

if test $1 = $ARG_DIR; then
    python3 image_collector_cui.py "sample/chicken_breeds/*" 3 tmp_dir_out
elif test $1 = $ARG_FILE; then
    python3 image_collector_cui.py "sample/search_queries.txt" 3 tmp_file_out
elif test $1 = $ARG_QUERY; then
    python3 image_collector_cui.py "johnny depp" 5 tmp_query_out
else
    echo 'The argument should be one of "dir", "file", and "query".'
fi
