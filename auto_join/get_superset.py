import pandas as pd

def unique_annotations(file_name, column):
    # requires manual annotations query and 
    all_annotations = pd.read_csv(file_name, usecols=[column])
    classes = all_annotations[column].unique()
    # get rid of nan values if exist
    classes = [x for x in classes if str(x) != "nan"]
    return classes

# make new compiled file
new_samples = unique_annotations("newMERGEDchar_20200320.csv", "class_char.y")
new_samples = pd.DataFrame(new_samples, columns=["name"])
# merge with original manual classifications file
old_samples = pd.read_csv("20190529_classify_classlabel.csv")
superset = old_samples.merge(new_samples, how='outer', on="name")
superset.to_csv("2019-2020_superset.csv")
