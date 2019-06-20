# author: Katherine Qi
# Organization: WHOI NES-LTER, EDI
# File Header: Python script to construct Level 1_b prototyping data tables for
# analyzing ROIs in automated vs. manual classification of phytoplankton datas
import pandas as pd


def merge_frames(f_df, c_df, id_df):
    # make substring key for matching
    c_df.pid = c_df.pid.str.slice(25, 30)
    c_df.pid = c_df.pid.str.lstrip("0")  # gets rid of leading zeros
    # get column with highest number (still need to implement tiebreaker)
    rem = c_df.iloc[:, 1:]
    c_df['most_likely'] = rem.idxmax(axis=1)
    # convert pid to int values for matching
    c_df.pid = pd.to_numeric(c_df.pid, downcast='integer')
    # only use most_likely and pid
    c1_df = c_df[['pid', 'most_likely']]
    # merge c_df and f_df using pid/roi_number as a key
    cnc_df = pd.merge(f_df, c1_df, how='left', left_on='roi_number', right_on='pid')
    # drop duplicate row
    cnc_df = cnc_df.drop('pid', axis=1)
    cnc_df = pd.merge(cnc_df, id_df, how='left', left_on='most_likely', right_on='name')
    return cnc_df


# pd.read_csv(f_url) need to fix ceritif first, use downloaded file for now
features_file = "D20180214T211809_IFCB010_features.csv"
class_file = "D20180213T234223_IFCB010_class_scores.csv"
classid_file = "20190529_classify_classlabel.csv"
# auto = pd.read_csv("D20180214T211809_IFCB010_features.csv")
# df = pd.DataFrame(file)
# extract ROI ID, class, area, biovolume, major/min axes
f_df = pd.read_csv(features_file, usecols=['roi_number', 'Area', 'Biovolume', 'EquivDiameter', 'MajorAxisLength', 'MajorAxisLength'])
c_df = pd.read_csv(class_file)
id_df = pd.read_csv(classid_file)
# call function to merge two dataframes
cnc_df = merge_frames(f_df, c_df, id_df)
# convert back into csv file
cnc_df.to_csv('joined.csv', index=None, header=True)
