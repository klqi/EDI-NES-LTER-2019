# script to quality control level_1b for EDI
import pandas as pd

level_1b = pd.read_csv("level_1b.csv")
# first remove all rows with only automatic observations
level_1b = level_1b[level_1b['data_provider_category_HumanObservation'].notna()]
# next remove automatic names and ids
level_1b = level_1b.drop(columns=['data_provider_category_MachineObservation', 'scientificNameID_MachineObservation'])

# save as new file
level_1b.to_csv("level_1b_manual.csv")