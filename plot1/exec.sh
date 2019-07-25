#!/bin/bash

# get current wd absolute path
cd ..
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# make sure geographic script is executable
GEO_DIR="${BASE_DIR}/geographic_query/transect_geocheck.py"
chmod u+x $GEO_DIR
# change working directories (plot1 => geographic_query)
cd geographic_query
# run transect_geocheck.py to get comparison.csv with 1km range
python3 -W ignore $GEO_DIR <<EOF
1
EOF
# copy desired output file to plot1 dir
cp comparison.csv ../plot1
ls

# make sure auto_extract script is executable
JOIN_SCRIPT="${BASE_DIR}/auto_join/auto_extract.py"
chmod u+x $JOIN_SCRIPT
# change working directories (geographic_query => auto_join)
cd ../auto_join/
# run auto_extract to get file1_b.csv
python3 $JOIN_SCRIPT
cp level_1b.csv ../plot1
# clean up a little
rm names_ids.csv resolved.csv
# move files to plot1 directory
mv resolved_auto.csv ../plot1
mv resolved_manual.csv ../plot1
# return to plot1 wd
cd ../plot1/
ls
