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
    rm resolved_auto.csv resolved_manual.csv volumes.csv
    cd ..
fi

# make sure geographic script is executable
GEO_DIR="${BASE_DIR}/geographic_query/transect_geocheck.py"
chmod u+x $GEO_DIR
# change working directories (plot1 => geographic_query)
cd geographic_query
# run transect_geocheck.py to get geographic_subset.csv with 1km range
python3 -W ignore $GEO_DIR <<EOF
1
EOF
# copy desired output file to plot1 dir
cp geographic_subset.csv ../plot1
# copy list of auto samples to auto_join
cp query_samples.csv ../auto_join
ls

# make sure auto_extract script is executable
JOIN_SCRIPT="${BASE_DIR}/auto_join/auto_extract.py"
chmod u+x $JOIN_SCRIPT
# change working directories (geographic_query => auto_join)
cd ../auto_join/
# run auto_extract to get file1_b.csv
python3 $JOIN_SCRIPT
cp level_1b.csv ../plot1
# also move to volume dir
cp level_1b.csv ../volume
# clean up a little
rm intermediate_names_ids.csv resolved.csv
# move files to plot1 directory
cp resolved_auto.csv ../plot1
cp resolved_manual.csv ../plot1


# call volume from pyifcb
VOL_SCRIPT="${BASE_DIR}/volume/get_volume.py"
# make sure script is executable
chmod u+x $VOL_SCRIPT
# change working directories (auto_join => volume)
cd ../volume/
# activate pyifcb environment
# CONDA_BASE=$(conda info --base)
# source $CONDA_BASE/etc/profile.d/conda.sh
# conda activate pyifcb
# run get_volume to get volumes.csv
python3 -W ignore $VOL_SCRIPT
# move volumes.csv to plot1 irectory
cp volumes.csv ../plot1
# return to plot1 wd
cd ../plot1/
ls
