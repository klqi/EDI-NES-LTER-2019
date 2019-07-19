#!/bin/bash

# make sure geographic script is executable
chmod u+x /Users/Kathy/Desktop/WHOI_LTER/projects/geographic_query/transect_geocheck.py
# change working directories (plot2 => geographic_query)
cd ../geographic_query
# run transect_geocheck.py to get comparison.csv with 1km range
python3 -W ignore /Users/Kathy/Desktop/WHOI_LTER/projects/geographic_query/transect_geocheck.py <<EOF
1
EOF
# copy desired output file to plot2 dir
cp comparison.csv ../plot2
ls

# make sure auto_join script is executable
chmod u+x /Users/Kathy/Desktop/WHOI_LTER/projects/auto_join/auto_extract.py
# change working directories (geographic_query => auto_join)
cd ../auto_join/
# run auto_extract to get file1_b.csv
python3 /Users/Kathy/Desktop/WHOI_LTER/projects/auto_join/auto_extract.py
# return to plot2 wd
cd ../plot2/
ls
