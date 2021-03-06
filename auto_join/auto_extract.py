# author: Katherine Qi
# Organization: WHOI NES-LTER, EDI
# File Header: Python script to construct Level 1_b prototyping data tables for
# analyzing ROIs in automated vs. manual classification of phytoplankton datas
# Requirements:
# csv file with column headers: "pid", "class_char.y", "roi", "user_id", and
# "verifications", resolved manual/automated annotation files (manually checked)
# pid must only contain the sample id, not the entire link as this script
# constructs the url from hard coding to the IFCBB dashboard

import pandas as pd
import numpy as np
import ssl
import urllib
import subprocess
import os
from os import path
import sys


# helper function for merging automated classifications
def merge_frames(f_df, c_df, id_df):
    # get column with highest number (still need to implement tiebreaker)
    rem = c_df.iloc[:, 1:]
    winner = rem.idxmax(axis=1)
    c_df['winner'] = winner
    # set permalink for level 1b format
    f_df['permalink'] = c_df['pid']
    # make substring key for matching
    c_df.pid = c_df.pid.str.slice(25, 30)
    c_df.pid = c_df.pid.str.lstrip("0")  # gets rid of leading zeros
    # convert pid to int values for matching
    c_df.pid = pd.to_numeric(c_df.pid, downcast='integer')
    # only use most_likely and pid
    c_df = c_df[['pid', 'winner']]
    # first merge with class and id by name
    cid_df = pd.merge(c_df, id_df, how='left', left_on='winner', right_on='name')
    # then merge features and cid_df
    cnc_df = pd.merge(f_df, cid_df, how='left', left_on='roi_number', right_on='pid')
    # drop duplicate column
    cnc_df = cnc_df.drop('pid', axis=1)
    # make sure grouped columns are all strings
    cnc_df[['winner', 'resolved_id_fromgnr']] = cnc_df[['winner',  'resolved_id_fromgnr']].astype(str)
    # group columns by ties, keeping original columns
    winners = cnc_df.groupby(
        ['sample_identifier', 'roi_number']).agg(
                {
                    'permalink': 'first',
                    'winner': '|'.join,
                    'resolved_id_fromgnr': '|'.join,
                    'Area': 'first',
                    'Biovolume': 'first',
                    'maxFeretDiameter': 'first',
                    'minFeretDiameter': 'first'
                }
            ).reset_index()
    # drop unnecessary columns
    winners = winners.drop(['sample_identifier', 'roi_number'], axis=1)
    # reset pid
    # winners['pid'] = winners['permalink']
    # reset permalink
    winners['permalink'] = 'http://ifcb-data.whoi.edu/NESLTER_transect/' + winners['permalink'].astype(str) + '.html'
    # rename column headers
    winners = winners.rename(columns={"winner": "data_provider_category_MachineObservation", "resolved_id_fromgnr": "scientificNameID_MachineObservation", "permalink": "associatedMedia"})
    return winners



# helper function to construct automated classifications
def auto_construct(level_1b):
    # subset samples so that each sample will only be called once
    samples = pd.read_csv('query_samples.csv')
    # initialize features and class data frames
    columns = ['permalink', 'sample_identifier', 'roi_number', 'Area', 'Biovolume', 'maxFeretDiameter', 'minFeretDiameter']
    f_df = pd.DataFrame(columns=columns)
    # initialize counter and loop through all samples
    counter = 0
    for row in samples.iterrows():
        # skip if empty
        if (pd.isnull(samples.pid[counter])):
            continue
        # get access to get online files
        ssl._create_default_https_context = ssl._create_unverified_context
        # get features and class files from IFCB dashboard
        link = 'http://ifcb-data.whoi.edu/NESLTER_transect/{}'.format(samples.pid[counter])
        features_file = '{}_features.csv'.format(link)
        urllib.request.urlopen(features_file)
        class_file = '{}_class_scores.csv'.format(link)
        # extract ROI ID, class, area, biovolume, major/min axes
        f_df = pd.read_csv(features_file, usecols=['roi_number', 'Area', 'Biovolume', 'maxFeretDiameter', 'minFeretDiameter'])
        # set sample_identifier for merge with auto_class names later
        f_df['sample_identifier'] = samples.pid[counter]
        # get autoclass name
        c_df = pd.read_csv(class_file)
        # make id dataframe to get automated names_ids from first automated class file
        if (not path.exists('resolved_auto.csv')):
            print("Resolved taxonomic annotations for automated classes required")
            sys.exit()
        elif path.exists('resolved_auto.csv'):
            # initialize id data frame from existing file
            id_df = pd.read_csv('resolved_auto.csv', usecols=['name', 'resolved_names', 'resolved_id_fromgnr'])
        print("Merging...")
        # call function to merge two dataframes
        merged = merge_frames(f_df, c_df, id_df)
        # print progress every 10 merges
        if ((len(samples.index) - counter) % 10 == 0):
            print("{} files left to query".format(len(samples.index) - counter))
        # append to the end to be returned later
        level_1b = pd.concat([level_1b, merged], ignore_index=True, sort=True)
        counter += 1

    print("Finished automated classifications and features merge, starting manual classifications")
    return level_1b


# helper function to populate manual sections of level 1b file
def manual_construct(all_samples, level_1b):
    # subset samples so that each name will only be called once
    samples = all_samples.drop_duplicates(subset='class_char.y').reset_index()

    # check if resolved doesn't exist
    if not (path.exists('resolved_manual_matched_matchIDs_LOOKUPsorted.csv')):
        print("Resolved taxonomic annotations for manual classes required")
        sys.exit()
    else:
        id_df = pd.read_csv('resolved_manual_matched_matchIDs_LOOKUPsorted.csv', 
                            usecols=['name', 'scientificName_HumanObservation', 'scientificNameID_HumanObservation', 
                                    'resolved_higher_order_fromgnr'])

    # merge ids with names from manual data
    samples = pd.merge(all_samples, id_df, how='left', left_on='class_char.y', right_on='name')
    # make pre_level_1b dataframe from level_1b
    pre_level_1b = level_1b[['associatedMedia', 'data_provider_category_MachineObservation', 
                            'scientificNameID_MachineObservation', 'Area', 
                            'Biovolume', 'maxFeretDiameter', 'minFeretDiameter']]
    samples['roi.y'] = samples['roi.y'].astype(int)
    samples['roi.y'] = samples['roi.y'].apply(lambda x: '{0:0>5}'.format(x))
    # make key to merge on
    samples['permalink'] = "http://ifcb-data.whoi.edu/NESLTER_transect/"+samples['bin'].astype(str)+"_"+samples['roi.y'].astype(str)+".html"
    samples.rename(columns={'permalink': 'associatedMedia'}, inplace=True)
    pre_level_1b = pd.merge(pre_level_1b, samples, how='left', on='associatedMedia')
    # rename manual column headers
    pre_level_1b.rename(columns={"class_char.y": "data_provider_category_HumanObservation", 
                                "resolved_higher_order_fromgnr": "higherClassification_group", 
                                "resolved_higher_order_id": "higher_order_id"}, inplace=True)
    # drop unnecessary columns
    level_1b = pre_level_1b.drop(['bin', 'roi.y'], axis=1)
    return level_1b


# read in file directly- take in as cli arg later
file_name = "newMERGEDchar_20200320.csv"

# initialize samples dataframe from input files
cols = ['bin', 'class_char.y', 'roi.y']
all_samples = pd.read_csv(file_name, usecols=cols)
# drop verifications and user_id columns for now
# all_samples = all_samples.drop(['user_id', 'verifications'], axis=1)
# drop all blank rows
all_samples.dropna(axis=0, how='all', inplace=True)

# initialize level 1b formatted DataFrame
columns = ['associatedMedia', 'data_provider_category_MachineObservation',
            'scientificNameID_MachineObservation',
            'data_provider_category_HumanObservation', 'scientificName_HumanObservation',
            'scientificNameID_HumanObservation', 'higherClassification_group', 
            'Area', 'Biovolume', 'maxFeretDiameter', 'minFeretDiameter']
level_1b = pd.DataFrame(columns=columns)


# first construct for automated classifications
level_1b = auto_construct(level_1b)
# then construct manual classifications half
level_1b = manual_construct(all_samples, level_1b)
# rearrange columns back to order
level_1b = level_1b[columns]
# convert pixels to micrometers
# 1 um = 2.77 pixels
pixels = 2.77
# convert Area- (SQRT(Area)/2.77)^2
level_1b.Area = ((np.sqrt(level_1b.Area.astype(float)))/pixels)**2
level_1b.Area = level_1b.Area.round(3)
# convert Biovolume- ((Biovolume^(1/3))/2.77)^3
level_1b.Biovolume = ((level_1b.Biovolume**(1/3))/pixels)**3
level_1b.Biovolume= level_1b.Biovolume.round(3)
# convert AxisLengths- AxisLength/3
level_1b.maxFeretDiameter = level_1b.maxFeretDiameter/pixels
level_1b.maxFeretDiameter = level_1b.maxFeretDiameter.round(3)
level_1b.minFeretDiameter = level_1b.minFeretDiameter/pixels
level_1b.minFeretDiameter = level_1b.minFeretDiameter.round(3)

# convert features to NaN if they are zero (failed features processing)
level_1b.loc[level_1b['Biovolume'] == 0,['Area','Biovolume', 'maxFeretDiameter', 'minFeretDiameter']] = np.nan
out_filename = 'level_1b.csv'
zero_features = level_1b[level_1b.Biovolume.isna()]

zero_features.to_csv("zero_features.csv", index=None, header=True)
level_1b.to_csv(out_filename, index=None, header=True)
print("Output generated")
