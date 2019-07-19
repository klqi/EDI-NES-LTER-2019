# author: Katherine Qi
# Organization: WHOI NES-LTER, EDI
# File Header: Python script to construct Level 1_b prototyping data tables for
# analyzing ROIs in automated vs. manual classification of phytoplankton datas
import pandas as pd
import ssl
import urllib
import subprocess
import tkinter as tk
from tkinter import filedialog
import os


def merge_frames(f_df, c_df, id_df):
    # get column with highest number (still need to implement tiebreaker)
    rem = c_df.iloc[:, 1:]
    winner = rem.idxmax(axis=1)
    c_df['winner'] = winner
    # weighted.loc[weighted['probability']==weighted['probability'].max()].T

    # make substring key for matching
    c_df.pid = c_df.pid.str.slice(25, 30)
    c_df.pid = c_df.pid.str.lstrip("0")  # gets rid of leading zeros
    # convert pid to int values for matching
    c_df.pid = pd.to_numeric(c_df.pid, downcast='integer')
    # only use most_likely and pid
    c_df = c_df[['pid', 'winner']]
    # merge class and id files first
    cid_df = pd.merge(c_df, id_df, how='left', left_on='winner', right_on='name')
    # then merge features and cid_df
    cnc_df = pd.merge(f_df, cid_df, how='left', left_on='roi_number', right_on='pid')
    # drop duplicate column
    cnc_df = cnc_df.drop('pid', axis=1)
    # make sure grouped columns are all strings
    cnc_df[['winner', 'resolved_names', 'resolved_id_fromgnr', 'resolved_higher_order_fromgnr']] = cnc_df[['winner', 'resolved_names', 'resolved_id_fromgnr', 'resolved_higher_order_fromgnr']].astype(str)
    # group columns by ties, keeping original columns
    winners = cnc_df.groupby(
        ['sample_identifier', 'roi_number']).agg(
                {
                    'winner': '|'.join,
                    'resolved_names': '|'.join,
                    'resolved_id_fromgnr': '|'.join,
                    'resolved_higher_order_fromgnr': '|'.join,
                    'Area': 'first',
                    'Biovolume': 'first',
                    'EquivDiameter': 'first',
                    'MajorAxisLength': 'first',
                    'MinorAxisLength': 'first'
                }
            ).reset_index()
    return winners


# pd.read_csv(f_url) will loop through all urls, use one for now for testing
# files to check
root = tk.Tk()
# gets rid of annoying window
root.withdraw()
# bring gui to front
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)
# close window when done
root.update()
# prompt user input for all samples file
file_name = filedialog.askopenfilename(initialdir=".", title="Choose csv file with all samples")
root.destroy()
# initialize samples data frame
samples = pd.read_csv(file_name, usecols=["new_pid"])
# initialize features and class data frames
columns = ['sample_identifier', 'roi_number', 'Area', 'Biovolume', 'EquivDiameter', 'MajorAxisLength', 'MinorAxisLength']
f_df = pd.DataFrame(columns=columns)
# initialize id data frame
'''id_df = pd.read_csv("resolved.csv", usecols=['name', 'resolved_names', 'resolved_higher_order_fromgnr', 'resolved_id_fromgnr'])'''
# initialize merged data frame
columns = ['sample_identifier', 'roi_number', 'winner', 'resolved_names', 'resolved_id_fromgnr', 'resolved_higher_order_fromgnr', 'Area', 'Biovolume', 'EquivDiameter', 'MajorAxisLength', 'MinorAxisLength']
cnc_df = pd.DataFrame(columns=columns)
# initialize counter and loop through all samples
counter = 0
for row in samples.iterrows():
    # skip if empty
    if (pd.isnull(samples.new_pid[counter])):
        break
    # get access to get online files
    ssl._create_default_https_context = ssl._create_unverified_context
    # get features and class files from IFCB dashboard
    features_file = '{}_features.csv'.format(samples.new_pid[counter])
    urllib.request.urlopen(features_file)
    class_file = '{}_class_scores.csv'.format(samples.new_pid[counter])
    # extract ROI ID, class, area, biovolume, major/min axes
    f_df = pd.read_csv(features_file, usecols=['roi_number', 'Area', 'Biovolume', 'EquivDiameter', 'MajorAxisLength', 'MinorAxisLength'])
    f_df['sample_identifier'] = samples.new_pid[counter]
    # get autoclass scores
    c_df = pd.read_csv(class_file)
    # make id file only during first iteration
    if (counter == 0):
        # initialize dataframe to read ids
        id_df = pd.DataFrame({'name': list(c_df.columns), 'international_id': 'NA'})
        id_df.to_csv("names_ids.csv", index=None, header=True)
        # run WoRMs_verify.R
        command = 'Rscript'
        dir_path =  os.path.dirname(os.path.abspath('__file__'))
        path2script = dir_path + '/WoRMs_verify.R'
        cmd = [command, path2script]
        print("Running worms verification...")
        # choose names_ids.csv during prompt
        subprocess.run(cmd)
        print("Done")
        # reinitialize id_df from output of WoRMs_verify
        resolved = dir_path + '/resolved.csv'
        id_df = pd.read_csv(resolved, usecols=['name', 'resolved_names', 'resolved_higher_order_fromgnr', 'resolved_id_fromgnr'])
    print("Merging...")
    # call function to merge two dataframes
    merged = merge_frames(f_df, c_df, id_df)
    # print progress every 5 merges
    if ((counter+1) % 5 == 0):
        print("Finished current merge, {} left to run".format(len(samples.index) - (counter+1)))
    # append to the end to be merged later
    cnc_df = pd.concat([cnc_df, merged], ignore_index=True, sort=True)
    counter += 1

# convert back into csv file
out_filename = 'file_1b.csv'
cnc_df.to_csv(out_filename, index=None, header=True)
print("Output generated")
