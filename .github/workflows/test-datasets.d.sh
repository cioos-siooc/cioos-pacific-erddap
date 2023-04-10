#!/bin/bash

DATASET_XMLS_DIRS=datasets.d/
DATASET_IDS=$(grep -rwo --regexp="datasetID=\"[^\"]*\"" $DATASET_XMLS_DIRS*.xml)
bad_name_flag=0
for file in $DATASET_IDS
do
    filename=${file%:*}
    datasetID=$(echo "${file#*=}" | tr -d '"')
    expected_file=$(echo $DATASET_XMLS_DIRS$datasetID.xml)
    if [ "$expected_file" != "$filename" ]; then
        echo "ERROR file=${filename} doesn't match datasetID=$datasetID, expected=$expected_file" >&2
        bad_name_flag=1
    fi
done

exit $bad_name_flag