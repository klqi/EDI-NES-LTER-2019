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
# local development only
setwd("~/Desktop/WHOI_LTER/projects/plot1/")
# read in csv files 
transect<- read.csv("IFCB_count_manual_transect_winter_2018_20190530.csv")
ids <- read.csv("resolved.csv")
# only read selected columns
ids <- ids[,c("name", "international_id", "resolved_id_fromgnr", "resolved_taxon_level_fromgnr", "taxon_level_fromid", "resolved_higher_order_fromgnr", "higher_order_fromid")]
latlong <- read.csv("comparison.csv")
latlong <- latlong[,c("key", "gps_furuno_latitude", "gps_furuno_longitude")]

# removes incorrectly formatted data row from transect
transect$date <- NULL

# convert to long format
format_long <- transect %>%
  gather(key="name", value="Abundance", Asterionellopsis_glacialis:Chaetoceros_danicus)

# reformat names to be merged
format_long$name <- gsub('_', ' ', format_long$name)
# remove rows with 0s for memory 
format_long <- format_long %>% filter(format_long$Abundance != 0)

# left join with ids, taxon level, and higher order based on name
format_long <- left_join(format_long, ids, by="name")

# restructure dataframe for organization
consolidate()

# left join based on sample_identifier
format_long$sample_identifier <- as.character(format_long$sample_identifier)
format_long <- left_join(format_long, latlong, by = c("sample_identifier" = "key"))


# write to output file- can change based on where you want the output file 
write.csv(format_long, "~/Desktop/WHOI_LTER/projects/plot1/long_transect.csv")


