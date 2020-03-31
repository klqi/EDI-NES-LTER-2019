import pandas as pd

def unique_annotations(file_name, column):
    # requires manual annotations query and 
    all_annotations = pd.read_csv(file_name, usecols=[column])
    classes = all_annotations[column].unique()
    # get rid of nan values if exist
    classes = [x for x in classes if str(x) != "nan"]
    return classes
