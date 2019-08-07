# author: Katherine Qi
# Organization: WHOI NES-LTER, EDI
# File header: Tool to check given files to verify whether given samples are
# valid within the complete transect line. Also can choose certain samples
# within a certain distance to output to a separate csv file
# Requirements: pandas, folium, geopy.distance, request, ssl, internet
# Still under local development so needs clean up to accomodate more user
# interaction

import pandas as pd
import folium
import geopy.distance
import ssl
import urllib
import os

dir_path = os.path.dirname(os.path.abspath('__file__'))
all_samples_file = dir_path + '/NESLTER_transect_EN608_Jan2018_ifcb_locations.csv'
subset_file = dir_path + '/man_query_data.csv'
# for online access
ssl._create_default_https_context = ssl._create_unverified_context
underway_file = "https://nes-lter-data.whoi.edu/api/underway/en608.csv"
urllib.request.urlopen(underway_file)
# coordinates for station 5
st5 = (40.5133, -70.8833)
st5_long = -70.8833
# add station 5 as main marker
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
all_samples['offset'] = 0.0
all_samples['dist_from_ref'] = 0.0
subset_samples = pd.read_csv(subset_file, usecols=['pid'])
# initialize column headers with latitude/longitude from original file and
# ulatitude/ulongitude from gps_furuno data
columns = ['index', 'sample_identifier', 'latitude', 'longitude', 'ulatitude', 'ulongitude']
col = ['date', 'pid']
good_samples = pd.DataFrame(columns=columns)
# only includes data from underway for query
joes_samples = pd.DataFrame(columns=col)
# bad sample name
bad_IFCB = "IFCB109"
# prompt user input to specify distance from longitude
ref_dist = float(input('Please enter an distance (km): '))
# convert to float
ref_dist = float(ref_dist)
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
    # get sample identifier from last 24 characters of pid string
    whole = all_samples.pid[counter]
    cut = whole[-24:]
    check_IFCB = whole[-7:]
    all_samples.key[counter] = cut
    # only plot marker if sample is 1 km east/west from station 5
    dist = float(geopy.distance.geodesic(ref_coord, coords).km)
    udist = float(geopy.distance.geodesic(uref_coord, ucoords).km)
    # offset distance from dist and udist
    off_dist = float(geopy.distance.geodesic(ucoords, coords).m)
    all_samples.offset[counter] = off_dist
    all_samples.dist_from_ref[counter] = udist
    # if both coordinates are within the ref_dist range
    if (dist <= ref_dist and udist <= ref_dist and check_IFCB != bad_IFCB):
        # make purple marker for good sample points
        # folium.CircleMarker(coords, radius=1, color='purple').add_to(map)
        folium.CircleMarker(ucoords, radius=1, color='yellow').add_to(map)
        # put into coordinates with sample identifier in dataframe
        good_samples = good_samples.append({'index': index, 'sample_identifier': cut, 'latitude': lat, 'longitude': long, 'ulatitude': ulat, 'ulongitude': ulong}, ignore_index=True)
        # put old and new pids into joes_samples
        joes_samples = joes_samples.append({'date': all_samples.date[counter], 'pid': all_samples.key[counter]}, ignore_index=True)
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
    elif (dist > ref_dist and udist <= ref_dist and check_IFCB != bad_IFCB):
        # make purple marker for good sample points
        folium.CircleMarker(ucoords, radius=1, color='yellow').add_to(map)
        # put into coordinates with sample identifier in dataframe
        good_samples = good_samples.append({'index': index, 'sample_identifier': cut, 'latitude': 'NA', 'longitude': 'NA', 'ulatitude': ulat, 'ulongitude': ulong}, ignore_index=True)
        # put coordinates into joes_samples, only including underway data
        joes_samples = joes_samples.append({'date': all_samples.date[counter], 'pid': all_samples.key[counter]}, ignore_index=True)
        # keep track of counter
        index += 1
    counter += 1

# merge subset_samples and all_samples based on key and pids
subset_samples.rename(columns={'pid': 'key'}, inplace=True)
subset_samples = subset_samples.drop_duplicates(subset='key').reset_index()
subset_samples = pd.merge(subset_samples, all_samples, how='left', on='key')
'''old_pids = subset_samples[['date', 'pid_x']]
old_pids['date'] = pd.to_datetime(old_pids['date'])
joes_samples['date'] = pd.to_datetime(joes_samples['date'])
# merge subset_samples with joes_samples based on date
joes_samples = pd.merge(joes_samples, old_pids, how='outer', on='date')
joes_samples = joes_samples.replace(r'^\s*$', "NA", regex=True)
joes_samples.rename(columns={'pid': 'old_pids'}, inplace=True)'''
# plot coordinates from original subset sample onto map- quality check portion
counter = 0
for row in subset_samples.iterrows():
    lat = subset_samples.gps_furuno_latitude[counter]
    long = subset_samples.gps_furuno_longitude[counter]
    counter += 1
    # get coordinates
    ucoords = (lat, long)
    # Add marker to original subset coordinates
    folium.CircleMarker(ucoords, radius=1, color='purple').add_to(map)
# save map
map.save("IFCB_EN608_map.html")
# save information to csv files, comment out as necessary
good_samples.to_csv("good_transect_subset.csv", index=None, header=True)
subset_samples.to_csv("transect_subset.csv", index=None, header=True)
all_samples.to_csv("geographic_subset.csv", index=None, header=True)
joes_samples.to_csv("query_samples.csv", index=None, header=True)
