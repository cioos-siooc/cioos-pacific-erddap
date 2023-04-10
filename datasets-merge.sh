#!/bin/sh

# use this script to combine XML snippets

DATASET_DIR=$1

if [ $# -eq 0 ]; then
    echo "No DATASET DIR supplied"
    exit
fi

{
    echo '<?xml version="1.0" encoding="UTF-8" ?><erddapDatasets>'
    cat "$DATASET_DIR"/*.xml
    echo '</erddapDatasets>'
} | xmllint --format -
