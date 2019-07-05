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
underway_file = "en608_underway.csv"
# coordinates for station 5
st5 = (40.5133, -70.8833)
st5_long = -70.8833
# show station 5 as main marker
map = folium.Map(location=st5, zoom_start=14)
folium.Marker(st5, popup='<i>Station 5</i>').add_to(map)
# initialize data frames
all_samples = pd.read_csv(all_samples_file)
# round all times down to last minute
all_samples['date'] = pd.to_datetime(all_samples['date'])
all_samples['date'] = pd.Series(all_samples['date']).dt.round("min")
all_samples['key'] = "NA"
# initialize underway dataframe
underway = pd.read_csv(underway_file, usecols=['date', 'gps_furuno_latitude', 'gps_furuno_longitude'])
underway['date'] = pd.to_datetime(underway['date'])
# round to minute/lag to underway
underway['date'] = pd.Series(underway['date']).dt.round("min")
# underway dataframe merge to get corrected coordinates from gps_furno
all_samples = pd.merge(all_samples, underway, how='left', left_on='date', right_on='date')
all_samples['offset'] = 0
subset_samples = pd.read_csv(subset_file, usecols=['sample_identifier'])
# samples within latitudinal range
columns = ['index', 'sample_identifier', 'latitude', 'longitude', 'ulatitude', 'ulongitude']
col = ['date', 'new_pid']
good_samples = pd.DataFrame(columns=columns)
joes_samples = pd.DataFrame(columns=col)
# prompt user input to specify distance from longitude
ref_dist = float(input('Please enter an distance (km): '))
counter = 0
index = 0
# loop through all samples
for row in all_samples.iterrows():
    # collect geolocation data from lag time
    lat = all_samples.latitude[counter]
    long = all_samples.longitude[counter]
    # geolocation data from underway data
    ulat = all_samples.gps_furuno_latitude[counter]
    ulong = all_samples.gps_furuno_longitude[counter]
    # get coordinates from all_samples
    coords = (lat, long)
    ucoords = (ulat, ulong)
    # reference coordinates from longituinal line
    ref_coord = (lat, st5_long)
    uref_coord = (ulat, st5_long)
    # markers for all samples on maps
    # folium.CircleMarker(coords, radius=1, color='green').add_to(map)
    folium.CircleMarker(ucoords, radius=1, color='crimson').add_to(map)
    # get sample identifier
    whole = all_samples.pid[counter]
    cut = whole[-24:]
    all_samples.key[counter] = cut
    # only plot marker if sample is 1 km east/west from station 5
    dist = geopy.distance.vincenty(ref_coord, coords).km
    udist = geopy.distance.vincenty(ref_coord, ucoords).km
    off_dist = geopy.distance.vincenty(ucoords, coords).m
    all_samples.offset[counter] = off_dist
    # if both coordinates are within the ref_dist range
    if (dist <= ref_dist and udist <= ref_dist):
        # make purple marker for good sample points
        # folium.CircleMarker(coords, radius=1, color='purple').add_to(map)
        folium.CircleMarker(ucoords, radius=1, color='yellow').add_to(map)
        # put into coordinates with sample identifier in dataframe
        good_samples = good_samples.append({'index': index, 'sample_identifier': cut, 'latitude': lat, 'longitude': long, 'ulatitude': ulat, 'ulongitude': ulong}, ignore_index=True)
        # put old and new pids into joes_samples
        joes_samples = joes_samples.append({'date': all_samples.date[counter], 'new_pid': all_samples.pid[counter]}, ignore_index=True)
        # keep track of counter
        index += 1
    # if only original coordinates are within ref_dist range
    elif (dist <= ref_dist and udist > ref_dist):
        # make purple marker for good sample points
        # folium.CircleMarker(coords, radius=1, color='purple').add_to(map)
        # put into coordinates with sample identifier in dataframe
        good_samples = good_samples.append({'index': index, 'sample_identifier': cut, 'latitude': lat, 'longitude': long, 'ulatitude': 'NA', 'ulongitude': 'NA'}, ignore_index=True)
        # keep track of counter
        index += 1
    # if only gps_furno coordinates are within ref_dist range
    elif (dist > ref_dist and udist <= ref_dist):
        # make purple marker for good sample points
        folium.CircleMarker(ucoords, radius=1, color='yellow').add_to(map)
        # put into coordinates with sample identifier in dataframe
        good_samples = good_samples.append({'index': index, 'sample_identifier': cut, 'latitude': 'NA', 'longitude': 'NA', 'ulatitude': ulat, 'ulongitude': ulong}, ignore_index=True)
        # put coordinates into joes_samples
        joes_samples = joes_samples.append({'date': all_samples.date[counter], 'new_pid': all_samples.pid[counter]}, ignore_index=True)
        # keep track of counter
        index += 1
    counter += 1

# merge subset_samples and all_samples based on key and pid
subset_samples = pd.merge(subset_samples, all_samples, how='left', left_on='sample_identifier', right_on='key')
old_pids = subset_samples[['date', 'pid']]
old_pids['date'] = pd.to_datetime(old_pids['date'])
joes_samples['date'] = pd.to_datetime(joes_samples['date'])
# merge subset_samples with joes_samples based on date
joes_samples = pd.merge(joes_samples, old_pids, how='outer', on='date')
joes_samples = joes_samples.replace(r'^\s*$', "NA", regex=True)
joes_samples.rename(columns={'pid': 'old_pids'}, inplace=True)
# plot coordinates from oriignla subset sample onto map- quality check portion
counter = 0
for row in subset_samples.iterrows():
    lat = subset_samples.latitude[counter]
    long = subset_samples.longitude[counter]
    counter += 1
    # get coordinates
    coords = (lat, long)
    # Add marker to original subset coordinates
    folium.CircleMarker(coords, radius=1, color='purple').add_to(map)
# save map
map.save("mymap.html")
# save information to csv files
good_samples.to_csv("good_transect_subset.csv", index=None, header=True)
subset_samples.to_csv("transect_subset.csv", index=None, header=True)
all_samples.to_csv("comparison.csv", index=None, header=True)
joes_samples.to_csv("query_samples.csv", index=None, header=True)
