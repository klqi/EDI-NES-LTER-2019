## ----setup, include=FALSE------------------------------------------------
knitr::opts_chunk$set(echo = TRUE)
rm(list=ls())
library(tidyverse)
library(stringr)
library(dplyr)


## ----helper functions, include=FALSE-------------------------------------
consolidate <- function() {
  # set column for ids to use from resolved_id and international_id
  format_long$use_id <<- format_long$resolved_id_fromgnr
  # consolidate column
  format_long$use_id[is.na(format_long$use_id)] <<- format_long$international_id[is.na(format_long$use_id)]
  # drop duplicates
  format_long$resolved_id_fromgnr <<- NULL
  format_long$international_id <<- NULL
  
  # set column for taxon levels to use from resolved_taxon_level and taxon_level
  format_long$use_taxon_level <<- as.character(format_long$resolved_taxon_level_fromgnr)
  # consolidate column
  format_long$use_taxon_level[is.na(format_long$use_taxon_level)] <<- as.character(format_long$taxon_level_fromid[is.na(format_long$use_taxon_level)])
  # drop duplicates
  format_long$resolved_taxon_level_fromgnr <<- NULL
  format_long$taxon_level_fromid <<- NULL

  # set column for taxon levels to use from resolved_taxon_level and taxon_level
  format_long$use_higher_rank <<- as.character(format_long$resolved_higher_order_fromgnr)
  # consolidate column
  format_long$use_higher_rank[is.na(format_long$use_higher_rank)] <<- as.character(format_long$higher_order_fromid[is.na(format_long$use_higher_rank)])
  # drop duplicates
  format_long$resolved_higher_order_fromgnr <<- NULL
  format_long$higher_order_fromid <<- NULL
}


## ----data cleaning, include=FALSE----------------------------------------
# get and set current working director
base_dir <- dirname(getwd())
curr_dir <- paste(base_dir,"/plot1/", sep="")
setwd(curr_dir)
# read in csv files 
transect<- read.csv("man_ann_for_kqi.csv")
ids <- read.csv("resolved.csv")
# only read selected columns
ids <- ids[,c("name", "international_id", "resolved_id_fromgnr", "resolved_taxon_level_fromgnr", "taxon_level_fromid", "resolved_higher_order_fromgnr", "higher_order_fromid")]
latlong <- read.csv("comparison.csv")
latlong <- latlong[,c("key", "gps_furuno_latitude", "gps_furuno_longitude")]

# convert to character vectors
transect$class_name <- as.character(transect$class_name)
ids$name <- as.character(ids$name)
# merge manual annotations with resolved data to get correct taxon info
format_long <- left_join(transect, ids, by=c("class_name" = "name"))

# restructure dataframe for organization
consolidate()

# left join based on sample_identifier
format_long$pid <- as.character(format_long$pid)
latlong$key <- as.character(latlong$key)
format_long <- left_join(format_long, latlong, by = c("pid" = "key"))


# write to output file- can change based on where you want the output file
output_path <- paste(curr_dir,"long_transect.csv", sep="")
write.csv(format_long, output_path)
