# author: Katherine Qi
# Organization: WHOI NES-LTER, EDI
# File Header: Python script to construct Level 1_b prototyping data tables for
# analyzing ROIs in automated vs. manual classification of phytoplankton datas
# Requirements:
# csv file with column headers: "pid", "class_name", "roi", "user_id", and
# "verifications"
# pid must only contain the sample id, not the entire link as this script
# constructs the url from hard coding to the IFCBB dashboard

import pandas as pd
import ssl
import urllib
import subprocess
import tkinter as tk
from tkinter import filedialog
import os


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
                    'MajorAxisLength': 'first',
                    'MinorAxisLength': 'first'
                }
            ).reset_index()
    # drop unnecessary columns
    winners = winners.drop(['sample_identifier', 'roi_number'], axis=1)
    # reset permalink
    winners['permalink'] = 'http://ifcb-data.whoi.edu/NESLTER_transect/' + winners['permalink'].astype(str)
    # rename column headers
    winners = winners.rename(columns={"winner": "namespace_automated", "resolved_id_fromgnr": "identification_automated"})
    return winners


# helper function to construct automated classifications
def auto_construct(all_samples, level_1b):
    # subset samples so that each sample will only be called once
    samples = all_samples.drop_duplicates(subset='pid').reset_index()
    # initialize features and class data frames
    columns = ['permalink', 'sample_identifier', 'roi_number', 'Area', 'Biovolume', 'MajorAxisLength', 'MinorAxisLength']
    f_df = pd.DataFrame(columns=columns)

    # initialize counter and loop through all samples
    counter = 0
    for row in samples.iterrows():
        # skip if empty
        if (pd.isnull(samples.pid[counter])):
            break
        # get access to get online files
        ssl._create_default_https_context = ssl._create_unverified_context
        # get features and class files from IFCB dashboard
        link = 'http://ifcb-data.whoi.edu/NESLTER_transect/{}'.format(samples.pid[counter])
        features_file = '{}_features.csv'.format(link)
        urllib.request.urlopen(features_file)
        class_file = '{}_class_scores.csv'.format(link)
        # extract ROI ID, class, area, biovolume, major/min axes
        f_df = pd.read_csv(features_file, usecols=['roi_number', 'Area', 'Biovolume', 'MajorAxisLength', 'MinorAxisLength'])
        # set sample_identifier for merge with auto_class names later
        f_df['sample_identifier'] = samples.pid[counter]
        # get autoclass name
        c_df = pd.read_csv(class_file)
        # make id dataframe to get automated names_ids
        if (counter == 0):
            # initialize dataframe to read ids
            id_df = pd.DataFrame({'name': list(c_df.columns), 'international_id': 'NA'})
            # output csv to be input for WoRMs_verify script
            id_df.to_csv("names_ids.csv", index=None, header=True)
            # run WoRMs_verify.R
            command = 'Rscript'
            dir_path = os.path.dirname(os.path.abspath('__file__'))
            path2script = dir_path + '/WoRMs_verify.R'
            cmd = [command, path2script]
            print("Running worms verification...")
            # choose names_ids.csv during prompt
            subprocess.run(cmd)
            print("Done")
            # reinitialize id_df from output of WoRMs_verify
            resolved = dir_path + '/resolved.csv'
            id_df = pd.read_csv(resolved)
            # output resolved file
            id_df.to_csv('resolved_auto.csv', index=None, header=True)
            id_df = id_df[['name', 'resolved_names', 'resolved_id_fromgnr']]
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
    samples = all_samples.drop_duplicates(subset='class_name').reset_index()

    # initialize dataframe to read ids
    id_df = pd.DataFrame({'name': list(samples.class_name), 'international_id': 'NA'})
    id_df.to_csv("names_ids.csv", index=None, header=True)
    # run WoRMs_verify.R
    command = 'Rscript'
    dir_path = os.path.dirname(os.path.abspath('__file__'))
    path2script = dir_path + '/WoRMs_verify.R'
    cmd = [command, path2script]
    print("Running worms verification...")
    # choose names_ids.csv during prompt
    subprocess.run(cmd)
    print("Done")
    # reinitialize id_df from output of WoRMs_verify
    resolved = dir_path + '/resolved.csv'
    # get name, ids, higher ranks, and higher rank ids
    id_df = pd.read_csv(resolved)
    # output resolved file
    id_df.to_csv('resolved_manual.csv', index=None, header=True)
    id_df = id_df[['name', 'resolved_id_fromgnr', 'resolved_higher_order_fromgnr', 'resolved_higher_order_id']]

    # merge ids with names from manual data
    samples = pd.merge(all_samples, id_df, how='left', left_on='class_name', right_on='name')
    # fill in unpopulated manual namespace columns
    level_1b['namespace_manual'] = samples['class_name']
    # fill in manual ids
    level_1b['identification_manual'] = samples['resolved_id_fromgnr']
    # fill in higher ranks
    level_1b['worms_higher_order_manual'] = samples['resolved_higher_order_fromgnr']
    # fill in higher rank ids
    level_1b['higher_order_id'] = samples['resolved_higher_order_id']
    return level_1b


# prompt user for csv file containing all samples to query from dashboard
root = tk.Tk()
# gets rid of annoying window
root.withdraw()
# bring gui to front
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)
# close window when done
root.update()
# prompt user input for all samples file, man_ann format
file_name = filedialog.askopenfilename(initialdir=".", title="Choose csv file with all samples")
root.destroy()

# initialize samples dataframe from input files
all_samples = pd.read_csv(file_name)
# drop verifications and user_id columns for now
all_samples = all_samples.drop(['user_id', 'verifications'], axis=1)
# initialize level 1b formatted DataFrame
columns = ['permalink', 'namespace_automated', 'identification_automated', 'namespace_manual', 'identification_manual', 'worms_higher_order_manual', 'higher_order_id', 'Area', 'Biovolume', 'MajorAxisLength', 'MinorAxisLength']
level_1b = pd.DataFrame(columns=columns)

# first construct for automated classifications
level_1b = auto_construct(all_samples, level_1b)
# then construct manual classifications half
level_1b = manual_construct(all_samples, level_1b)
# rearrange columns back to order
level_1b = level_1b[columns]
# convert back into csv file
out_filename = 'level_1b.csv'
level_1b.to_csv(out_filename, index=None, header=True)
print("Output generated")
