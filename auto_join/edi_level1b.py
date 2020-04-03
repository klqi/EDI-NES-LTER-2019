# script to quality control level_1b for EDI
import pandas as pd

level_1b = pd.read_csv("level_1b.csv")
# get samples with manual annotations 
manual_only = pd.read_csv("20200320_man_query_data.csv", usecols=['pid', 'roi'])
# check if there are samples from manual list with automated annotations but no manual annotations
manual_only['roi'] = manual_only['roi'].astype(str).replace('\.0', '', regex=True).apply(lambda x: '{0:0>5}'.format(x))
manual_only['permalink'] = 'http://ifcb-data.whoi.edu/NESLTER_transect/' + manual_only.pid + '_' + manual_only.roi + '.html'
# merge with level_1b file
merged = manual_only.merge(level_1b, on='permalink', how='inner')
auto_only = merged[merged['data_provider_category_HumanObservation'].isna()]
# print result
if (auto_only.empty):
    print("All ROIs from manual list have manual annotations")
else:
    print("The following ROIs are missing manual annotations: ")
    print(merged.permalink)
# for edi, remove all rows with only automatic observations
level_1b = level_1b[level_1b['data_provider_category_HumanObservation'].notna()]
# next remove automatic names and ids
level_1b = level_1b.drop(columns=['data_provider_category_MachineObservation', 'scientificNameID_MachineObservation'])

# save as new file
level_1b.to_csv("level_1b_manual.csv")