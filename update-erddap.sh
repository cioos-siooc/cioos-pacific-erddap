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
   echo "Syntax: update-erddap.sh [--sh *, --hardFlag, -h|--help, --mode|-m]"
   echo "options:"
   echo "  mode      (all|pull|commited) Method used to determinate which commits to compare:"
   echo "       - all: any active changes including none committed ones since the last update."
   echo "       - pull (default): run git pull and get changes since the last update"
   echo "       - no-pull: no git pull and get changes since the last update"
   echo "  hardFlag  Generate Hard Flag. Default to flag"
   echo "  sha       Git SHA to review changes from. If not given use sha available in .last_update_sha or present git SHA."
   echo "  help,h    Print this Help."
   echo
}

# Argument Parsing
VALID_ARGS=$(getopt -o hm --long sha:,hardFlag,help,mode: -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi

# Parse arguments
ADD_FLAG_DIR=$FLAG_DIR
MODE='pull'
eval set -- "$VALID_ARGS"
while [ : ]; do
   case "$1" in
      -h | --help) Help;exit;;
      --sha) SHA=$2; shift 2;;
      --hardFlag) ADD_FLAG_DIR=$HARD_FLAG_DIR; shift;;
      \?) # Invalid option
         echo "Error: Invalid option -> $option"
         exit;;
      -m | --mode) MODE=$2; echo "run mode=$MODE"; shift 2;;
      -- ) shift; break ;;
   esac
done

# Define SHA to review from if not provided
if [ -z ${SHA} ] && [ -f .last_update_sha ]; then 
SHA=$(cat .last_update_sha)
echo "update based on file .last_update_sha = $SHA"
elif [ -z ${SHA} ]; then
echo 'Update based on present SHA'
SHA=$(git rev-parse HEAD)
fi

if [ "$MODE" == 'all' ] ; then
    NEW_SHA=''
elif [ "$MODE" == 'pull' ]; then
    echo 'pull from origin'
    git pull
    NEW_SHA=$(git rev-parse HEAD) 
elif [ "$MODE" == 'no-pull' ]; then
    NEW_SHA=$(git rev-parse HEAD)
else 
    echo "Error! Unknown MODE=$MODE"
    exit
fi

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
if $APPLY_HARD_FLAG_DIR; then
for DATASETS_ID in $DATASETS_IDS 
do
    echo add hardFlag $DATASETS_ID                                                                       
    sudo touch "$HARD_FLAG_DIR$DATASETS_ID"
done
fi

# Save NEW_SHA to .last_update_sha
if [ "$NEW_SHA" != '' ]; then
    echo $NEW_SHA > .last_update_sha
fi