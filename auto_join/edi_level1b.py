# script to quality control level_1b for EDI
import pandas as pd

level_1b = pd.read_csv("level_1b.csv")
# get samples with manual annotations 
manual_only = pd.read_csv("newMERGEDchar_20200320.csv", usecols=['bin', 'roi.y'])
# check if there are samples from manual list with automated annotations but no manual annotations
manual_only['roi.y'] = manual_only['roi.y'].astype(str).replace('\.0', '', regex=True).apply(lambda x: '{0:0>5}'.format(x))
manual_only['associatedMedia'] = 'http://ifcb-data.whoi.edu/NESLTER_transect/' + manual_only['bin'] + '_' + manual_only['roi.y'] + '.html'
# merge with level_1b file
merged = manual_only.merge(level_1b, on='associatedMedia', how='inner')
auto_only = merged[merged['data_provider_category_HumanObservation'].isna()]
# print result
if (auto_only.empty):
    print("All ROIs from manual list have manual annotations")
else:
    print("The following ROIs are missing manual annotations: ")
    print(merged.associatedMedia)
# for edi, remove all rows with only automatic observations and the 42 NAs from manual annotation database last summer
level_1b = level_1b[level_1b['data_provider_category_HumanObservation'].notna()]
# next remove automatic names and ids
level_1b = level_1b.drop(columns=['data_provider_category_MachineObservation', 'scientificNameID_MachineObservation'])

# save as new file
level_1b.to_csv("level_1b_manual.csv")