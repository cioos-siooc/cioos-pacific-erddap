#!/bin/bash

# PARAMETERS
DATASET_XMLS_DIRS='datasets.d/'
FLAG_DIR='erddap/data/flag/'
HARD_FLAG_DIR='erddap/data/hardFlag/'
CONTAINER_NAME=${CONTAINER_NAME:-erddap}

# Documentation
Help()
{
   # Display Help
   echo "update-erddap.sh review any changes made between two commits and generate ERDDAP datasets flags for each associated datasets"
   echo
   echo "Syntax: update-erddap.sh [--sha *, --hardFlag, -h|--help]"
   echo "options:"
   echo "hardFlag  Generate Hard Flag. default flag"
   echo "sha       Git SHA to review change from. If not given use sha available in .last_update_sha or present git SHA."
   echo "help (h)  Print this Help."
   echo
}

# Argument Parsing
VALID_ARGS=$(getopt -o h --long sha:,hardFlag,help -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi

# Parse arguments
ADD_FLAG_DIR=$FLAG_DIR
eval set -- "$VALID_ARGS"
while [ : ]; do
   case "$1" in
      -h | --help) Help;exit;;
      --sha) SHA=$2; shift 2;;
      --hardFlag) ADD_FLAG_DIR=$HARD_FLAG_DIR; shift;;
      \?) # Invalid option
         echo "Error: Invalid option -> $option"
         exit;;
      -- ) shift; break ;;
   esac
done

# Define SHA to review from if not provided
if [ -z ${SHA} ] && [ -f .last_update_sha ]; then 
echo 'update based on .last_update_sha file'
SHA=$(cat .last_update_sha)
elif [ -z ${SHA} ]; then
echo 'Update based on present SHA'
SHA=$(git rev-parse HEAD)
fi

git pull
NEW_SHA=$(git rev-parse HEAD)

# Unchanged repository
if [ "$SHA" == "$NEW_SHA" ]; then
echo "No uncommitted changes were made"
exit 1
fi

# update datasets.xml
sudo docker exec $CONTAINER_NAME bash -c "/datasets.d.sh > /usr/local/tomcat/content/erddap/datasets.xml"
sudo docker exec $CONTAINER_NAME bash /init.d/replace-datasets-secrets.sh

# Get xml files that were modified[M] or added[A] since the last commit  and generate flag
DATASETS_IDS=$(git diff --diff-filter=AMCR --name-only --relative=$DATASET_XMLS_DIRS $SHA $NEW_SHA $DATASET_XMLS_DIRS | sed 's:.xml::')

echo modified $DATASETS_IDS
# generate a flag for each related datasetID
for file in $DATASETS_IDS 
do
    echo add hardFlag $file                                                                       
    touch "$HARD_FLAG_DIR$file"
done

# Save NEW_SHA to .last_update_sha
echo $NEW_SHA > .last_update_sha