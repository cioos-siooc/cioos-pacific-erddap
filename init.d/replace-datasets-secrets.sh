#!/bin/bash
# Replace secrets in dataset.xml by their corresponding 
#  environment variables ERDDAP_SECRET_(.*)
while read -r e; do
  k=$(echo "$e" | cut -d= -f1);
  v=$(echo "$e" | cut -d= -f2-);
  sed -i "s@$k@$v@g" /usr/local/tomcat/content/erddap/datasets.xml
done < <(env | grep -oP '(?<=^ERDDAP_SECRET_).*')
