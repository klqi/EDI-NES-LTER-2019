# author: Katherine Qi
# Organization: WHOI NES-LTER, EDI
# File header: Tool to check given files to verify whether given samples are
# valid within the complete transect line. Also can choose certain samples
# within a certain distance to output to a separate csv file

import pandas as pd
import folium
import geopy.distance

# files to check
all_samples_file = "NESLTER_transect_EN608_Jan2018_ifcb_locations.csv"
subset_file = "IFCB_count_manual_transect_winter_2018_20190530.csv"
# coordinates for station 5
st5 = (40.5133, -70.8833)
st5_long = -70.8833
# show station 5 as main marker
map = folium.Map(location=st5, zoom_start=14)
folium.Marker(st5, popup='<i>Station 5</i>').add_to(map)
# initialize data frames
all_samples = pd.read_csv(all_samples_file)
subset_samples = pd.read_csv(subset_file, usecols=['sample_identifier'])
columns = ['index', 'sample_identifier', 'latitude', 'longitude']
good_samples = pd.DataFrame(columns=columns)
all_samples['key'] = "NA"
# prompt user input to specify distance from longitude
ref_dist = int(input('Please enter an integer distance: '))
counter = 0
index = 0
# loop through all samples
for row in all_samples.iterrows():
    # collect geolocation data
    lat = all_samples.latitude[counter]
    long = all_samples.longitude[counter]
    # get coordinates from all_samples
    coords = (lat, long)
    ref_coord = (lat, st5_long)
    folium.CircleMarker(coords, radius=1, color='green').add_to(map)
    # put latitude and longitude into subset_samples
    whole = all_samples.pid[counter]
    cut = whole[-24:]
    all_samples.key[counter] = cut
    # only plot marker if sample is 1 km east/west from station 5
    dist = geopy.distance.vincenty(ref_coord, coords).km
    if (dist <= ref_dist):
        # make purple marker for good sample points
        folium.CircleMarker(coords, radius=3, color='purple').add_to(map)
        # put into coordinates with sample identifier in dataframe
        good_samples = good_samples.append({'index': index, 'sample_identifier': cut, 'latitude': lat, 'longitude': long}, ignore_index=True)
        # keep track of counter
        index += 1
    counter += 1

# merge subset_samples and all_samples based on key and pid
subset_samples = pd.merge(subset_samples, all_samples, how='left', left_on='sample_identifier', right_on='key')

# plot coordinates from oriignla subset sample onto map- quality check portion
counter = 0
for row in subset_samples.iterrows():
    lat = subset_samples.latitude[counter]
    long = subset_samples.longitude[counter]
    counter += 1
    # get coordinates
    coords = (lat, long)
    # Add marker to original subset coordinates
    folium.CircleMarker(coords, radius=1, color='yellow').add_to(map)
# save map
map.save("mymap.html")
# save information to csv files
good_samples.to_csv("good_transect_subset.csv", index=None, header=True)
subset_samples.to_csv("transect_subset.csv", index=None, header=True)
