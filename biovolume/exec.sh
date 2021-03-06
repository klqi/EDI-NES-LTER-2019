#!/bin/bash

# get current wd absolute path
cd ..
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# check if new cruise is being run
if [ $1 = 'y' ]; then
    # clear files
    cd auto_join
    rm resolved_auto.csv resolved_manual.csv
    cd ../plot1
    rm resolved_auto.csv resolved_manual.csv
    rm level_1b.csv 
    rm percent_biovolume.png biovolume_concentration.png
    cd ..

fi
    
# make sure geographic script is executable
GEO_DIR="${BASE_DIR}/geographic_query/transect_geocheck.py"
chmod u+x $GEO_DIR
# change working directories (plot2 => geographic_query)
cd geographic_query
# run transect_geocheck.py to get geographic_subset.csv with 1km range
python3 -W ignore $GEO_DIR <<EOF
1
EOF
# copy desired output file to plot2 dir
cp geographic_subset.csv ../plot2
# copy list of auto samples to auto_join
cp query_samples.csv ../auto_join
ls

# make sure auto_join script is executable
JOIN_SCRIPT="${BASE_DIR}/auto_join/auto_extract.py"
chmod u+x $JOIN_SCRIPT
# change working directories (geographic_query => auto_join)
cd ../auto_join/
# run auto_extract to get file1_b.csv
python3 $JOIN_SCRIPT
cp level_1b.csv ../plot2
# clean up a little
rm names_ids.csv resolved.csv
# move files to plot2 directory
cp resolved_auto.csv ../plot2
cp resolved_manual.csv ../plot2
# return to plot2 wd
cd ../plot2/
ls
