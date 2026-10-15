# This script is compatible with older docker-erddap 
#  container without the datasets.d feature
echo "<?xml version=\"1.0\" encoding=\"UTF-8\" ?><erddapDatasets> $(cat ./datasets.d/*.xml)</erddapDatasets>" > erddap/content/datasets.xml
