#!/bin/bash

# get current wd absolute path
cd ..
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# make sure geographic script is executable
GEO_DIR="${BASE_DIR}/geographic_query/transect_geocheck.py"
chmod u+x $GEO_DIR
# change working directories (plot2 => geographic_query)
cd geographic_query
# run transect_geocheck.py to get comparison.csv with 1km range
python3 -W ignore $GEO_DIR <<EOF
1
EOF
# copy desired output file to plot1 dir
cp comparison.csv ../plot1
ls

# make sure worms script is executable
WORMS_DIR="${BASE_DIR}/auto_join/WoRMs_verify.R"
chmod u+x $WORMS_DIR
# change working directories (geographic_query => auto_join)
cd ../auto_join/
# run worms script to get resolved.csv
Rscript $WORMS_DIR
cp resolved.csv ../plot1
# return to plot1 wd
cd ../plot1/
ls

# make sure wide2long script is executable
CLEAN_DIR="${BASE_DIR}/plot1/wide2long.R"
chmod u+x $CLEAN_DIR 
# run script 
Rscript wide2long.R
ls

