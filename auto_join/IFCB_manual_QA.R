# R script IFCB_manual_QA.R to 'Confirm manual annotation from higher power user when annotation initially provided by lower power user.'
# Input: CSV file output from querying manual annotation database, with columns bin, class_name, initial_user, roi, tags, time, user_id, verifications. In cases where there was an initial annotation that differed from the winning one, the original user id is included in an initial_user column; otherwise the initial_user column is blank.
# Output: CSV file with subset list of ROIs for which an initial_user is provided, with an additional column to indicate when the initial_user and user_id do not match, i.e., an "override" occurred. We calculate how many and the percentage of "overrides" out of the total ROIs in the input data.
library(dplyr)
# read input csv file in from Slack
newSlackdata <- read.csv("C:/Users/sbeaulieu/Downloads/compiled.csv")

# the following couple steps are for EN608 in particular because need only a subset of 60 bins
# read csv file in from github
newmanquerydata <- read.csv("https://raw.githubusercontent.com/klqi/EDI-NES-LTER-2019/master/auto_join/new_man_query_data.csv")
# number of rows in newmanquerydata is total number of ROIs in dataset
totalROIs <- nrow(newmanquerydata)
print(totalROIs)
# add a column that concatenates two existing columns for ROI identifier
newmanquerydataIDs <- mutate(newmanquerydata, concat_column = paste(pid, roi, sep = '_'))
newSlackdataIDs <- mutate(newSlackdata, concat_column = paste(bin, roi, sep = '_'))
# what you think are strings may actually be factors so change those to character
newSlackdataIDschar <- mutate(newSlackdataIDs, class_char = as.character(class_name))
newmanquerydataIDschar <- mutate(newmanquerydataIDs, class_char = as.character(class_name))
# left join with newmanquerydata first bc want to only retain the 60 bins
newMERGEDchar <- left_join(newmanquerydataIDschar, newSlackdataIDschar, by = c("concat_column"))

# now we need to subset the rows for which original user id is included in an initial_user column
newMERGEDcharcheckusers <- newMERGEDchar %>% filter(initial_user > 0)
# add the column that checks whether initial user matches user_id for the winning annotation
newMERGEDcharcheckusers <- mutate(newMERGEDcharcheckusers, matchuser = (initial_user == user_id.y))
# number of ROIs for which initial user does not match user_id for the winning annotation
overrideROIs <- newMERGEDcharcheckusers %>% filter(initial_user != user_id.y)
overrideROIscount <- nrow(overrideROIs)
print(overrideROIscount)
fractionoverride <- overrideROIscount/totalROIs
print(fractionoverride)

# save both output files locally to csv
write.csv(newMERGEDchar, "c:/Users/sbeaulieu/Desktop/newMERGEDchar.csv")
write.csv(newMERGEDcharcheckusers, "c:/Users/sbeaulieu/Desktop/newMERGEDcharcheckusers.csv")
