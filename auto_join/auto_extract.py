# author: Katherine Qi
# Organization: WHOI NES-LTER, EDI
# File Header: Python script to construct Level 1_b prototyping data tables for
# analyzing ROIs in automated vs. manual classification of phytoplankton datas
import pandas as pd
import ssl
import urllib
'''import tkinter as tk
from tkinter import filedialog
'''


def merge_frames(f_df, c_df, id_df):
    # get column with highest number (still need to implement tiebreaker)
    rem = c_df.iloc[:, 1:]
    winner = rem.idxmax(axis=1)
    c_df['winner'] = winner
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
    cnc_df[['winner', 'name', 'id', 'international_id']] = cnc_df[['winner', 'name', 'id', 'international_id']].astype(str)
    # group columns by ties, keeping original columns
    winners = cnc_df.groupby(
        ['sample_identifier', 'roi_number']).agg(
                {
                    'winner': '|'.join,
                    'name': '|'.join,
                    'id': '|'.join,
                    'international_id': '|'.join,
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
'''root = tk.Tk()
# gets rid of annoying window
root.withdraw()
# close window when done
root.update()
# bring gui to front
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)
# prompt user input for all samples file
file_name = filedialog.askopenfilename(initialdir=".", title="Choose csv file with all samples")'''
file_name = "use_for_testing.csv"
# read in file with ids
classid_file = "20190529_classify_classlabel.csv"
# initialize samples data frame
samples = pd.read_csv(file_name, usecols=["new_pid"])
# initialize features and class data frames
columns = ['sample_identifier', 'roi_number', 'Area', 'Biovolume', 'EquivDiameter', 'MajorAxisLength', 'MinorAxisLength']
#  cnc_df = pd.DataFrame(columns=columns)
f_df = pd.DataFrame(columns=columns)
# initialize counter and loop through all samples
counter = 0
for row in samples.iterrows():
    ssl._create_default_https_context = ssl._create_unverified_context
    # features_file = "http://ifcb-data.whoi.edu/NESLTER_transect/D20180131T180620_IFCB109_features.csv"
    features_file = '{}_features.csv'.format(samples.new_pid[counter])
    urllib.request.urlopen(features_file)
    class_file = '{}_class_scores.csv'.format(samples.new_pid[counter])
    # extract ROI ID, class, area, biovolume, major/min axes
    temp_ft = pd.read_csv(features_file, usecols=['roi_number', 'Area', 'Biovolume', 'EquivDiameter', 'MajorAxisLength', 'MinorAxisLength'])
    temp_ft['sample_identifier'] = samples.new_pid[counter]
    temp_cl = pd.read_csv(class_file)
    # append to end of f_df and c_df to be merged later
    f_df = pd.concat([f_df, temp_ft], ignore_index=True, sort=True)
    if (counter == 0):
        c_df = temp_cl
    else:
        c_df = pd.concat([c_df, temp_cl], ignore_index=True)
    counter += 1

# initialize dataframe to read ids
id_df = pd.read_csv(classid_file)
# call function to merge two dataframes
cnc_df = merge_frames(f_df, c_df, id_df)
# convert back into csv file
out_filename = 'test_join.csv'
cnc_df.to_csv(out_filename, index=None, header=True)
