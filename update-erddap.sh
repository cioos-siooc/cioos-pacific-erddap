#!/bin/bash

# SHA=$(git rev-parse HEAD)
DATASET_XMLS_DIRS='datasets.d/'
DATASET_XML_FILE='erddap/content/datasets.xml'
HARD_FLAG_DIR='erddap/data/hardFlag/'
ERDDAP_CONTAINER_NAME='erddap'

# Define SHA to review from
if [ -z $1 ]; then 
SHA=$(git rev-parse HEAD)
else
echo review specific sha $1
SHA=$1
fi

git pull
NEW_SHA=$(git rev-parse HEAD)

# Unchanged repository
if [ "$SHA" == "$NEW_SHA" ]; then
echo "No new changes were made"
exit 1
fi

# update datasets.xml
sudo docker exec $ERDDAP_CONTAINER_NAME bash -c "/datasets.d.sh > /usr/local/tomcat/content/erddap/datasets.xml"
sudo docker exec $ERDDAP_CONTAINER_NAME bash /init.d/replace-datasets-secrets.sh

# Get xml files that were modified[M] or added[A] since the last commit  and generate flag
DATASETS_IDS=$(git diff --diff-filter=AMCR --name-only --relative=$DATASET_XMLS_DIRS $SHA $NEW_SHA $DATASET_XMLS_DIRS | sed 's:.xml::')

echo modified $DATASETS_IDS
# generate a flag for each related datasetID
for file in $DATASETS_IDS 
do
    echo add hardFlag $file                                                                       
    touch "$HARD_FLAG_DIR$file"
done
