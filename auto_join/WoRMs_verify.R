## ----setup, include=FALSE------------------------------------------------
knitr::opts_chunk$set(echo = TRUE)
library(taxize)
library(worrms)
library(plyr)
library(dplyr)
library(tcltk)


## ------------------------------------------------------------------------
# local development only
rm(list=ls())
# get and set current working director
base_dir <- dirname(getwd())
curr_dir <- paste(base_dir,"/auto_join/", sep="")
setwd(curr_dir)
#man.data <- read.csv(file.choose())
man.data <- read.csv(tk_choose.files(caption = "Choose a .csv file to validate"))
#man.data <- read.csv("20190529_classify_classlabel.csv")
my_path <- paste(curr_dir,"resolved.csv", sep="")


## ------------------------------------------------------------------------
# wrapper function to call taxize get_wormsid function and put data into appropriate column 
acquire_wormsid <- function(resolved_name, counter, man.data) {
  response <- taxize::get_wormsid_(
    resolved_name,
    searchtype = 'scientific',
    accepted = F,
    ask = F,
    messages = F
  )
  # check if name was able to return an id from worms
  response <- as.data.frame(response)
  if (!empty(response)) {
    # standardize resolved name to retrieve id
    resolved_name <- gsub(" ", ".", resolved_name, fixed=TRUE)
    resolved_name <- gsub("-", ".", resolved_name, fixed=TRUE)
    get.id <- paste(resolved_name, sep='.', "AphiaID")
    # Pull highest order taxon id
    resolved_id <- response[1, get.id]
    man.data$resolved_id_fromgnr[counter] <<- resolved_id
    # sets data_source column if original name could not be resolved through gnr 
    man.data$data_source[counter] <<- "World Register of Marine Species"
  } # else leave columns with original NA values
}


# retrieves taxon information based on name
name2taxoninfo <- function(tx_name, counter, man.data) {
  # use worms db to get taxon level
  taxon_level <- unlist(tax_rank(tx_name, db='worms', rows=1))
  man.data$resolved_taxon_level_fromgnr[counter] <<- taxon_level
  # use taxize classification function to get higher order (class, infraphylum, phylum)
  hierarchy <- taxize::classification(tx_name, db='worms', rows=1)
  # get class, infraphylum, and phylum
  hierarchy <- as.data.frame(hierarchy[[1]])
  class <- hierarchy$name[hierarchy$rank == "Class"]
  infphy <- hierarchy$name[hierarchy$rank == "Infraphylum"]
  phylum <- hierarchy$name[hierarchy$rank == "Phylum"]
  
  # check which of the three main groups tx_name falls under
  if (!identical(character(0), class) && class == "Bacillariophyceae") {
      man.data$resolved_higher_order_fromgnr[counter] <<- class
      man.data$resolved_higher_order_id[counter] <<- '148899'
  } else if (!identical(character(0), infphy) && infphy == "Dinoflagellata") {
      man.data$resolved_higher_order_fromgnr[counter] <<- infphy
      man.data$resolved_higher_order_id[counter] <<- '146203'
  } else if (!identical(character(0), phylum) && phylum == "Haptophyta") {
      man.data$resolved_higher_order_fromgnr[counter] <<- phylum
      man.data$resolved_higher_order_id[counter] <<- '369190'
  } else {
      man.data$resolved_higher_order_fromgnr[counter] <<- "other"
      man.data$resolved_higher_order_id[counter] <<- '-6666'
    }
}


# retrieves taxon info based on id: level, name, and higher order 
id2taxoninfo <- function(int_id, counter, man.data) {
  # populate taxon_level 
  taxon_level <- unlist(tax_rank(int_id, db='worms', rows=1))
  man.data$taxon_level_fromid[counter] <<- taxon_level
  # populate taxon_name
  taxon_name <- wm_id2name(id=int_id)
  man.data$taxon_name_fromid[counter] <<- taxon_name
  # populate higher_order
  hierarchy <- classification(int_id, db='worms', rows=1)
  # get id, class, infraphylum, and phylum
  hierarchy <- as.data.frame(hierarchy[[1]])

  class <- hierarchy$name[hierarchy$rank == "Class"]
  infphy <- hierarchy$name[hierarchy$rank == "Infraphylum"]
  phylum <- hierarchy$name[hierarchy$rank == "Phylum"]
  
  # check which of the three main groups tx_name falls under
  if (!identical(character(0), class) && class == "Bacillariophyceae") {
    man.data$higher_order_fromid[counter] <<- class
    man.data$higher_order_id[counter] <<- '148899'
  } else if (!identical(character(0), infphy) && infphy == "Dinoflagellata") {
    man.data$higher_order_fromid[counter] <<- infphy
    man.data$higher_order_id[counter] <<- '146203'
  } else if (!identical(character(0), phylum) && phylum == "Haptophyta") {
    man.data$higher_order_fromid[counter] <<- phylum
    man.data$higher_order_id[counter] <<- '369190'
  } else {
    man.data$higher_order_fromid[counter] <<- "other"
    man.data$higher_order_id[counter] <<- '-6666'
  }
  
  # sets data_source column if original name could not be resolved through gnr 
  man.data$data_source[counter] <<- "World Register of Marine Species"
}

# helper function to fill in information for abiotic classes
is_abiotic <- function(name, counter) {
  if (name == "bad" | name == "detritus" | name == "bead" | name == "bubble" | name == "pollen" | name == "camera spot") {
    man.data$alt_datasource[counter] <<- "OCB"
    man.data$alt_resolved_name[counter] <<- toString(name)
    return(TRUE)
  }
  return(FALSE)
}


## ---- echo=FALSE, include=FALSE------------------------------------------
# Resolve names 
counter <- 1
# column names 
man.data$resolved_names <- NA_character_
man.data$taxon_level_fromid <- NA_character_
man.data$taxon_name_fromid <- NA_character_
man.data$higher_order_fromid <- NA_character_
man.data$higher_order_id <- NA_character_
man.data$data_source <- NA_character_
man.data$resolved_id_fromgnr <- NA_character_
man.data$resolved_taxon_level_fromgnr <- NA_character_
man.data$resolved_higher_order_fromgnr <- NA_character_
man.data$resolved_higher_order_id <- NA_character_
man.data$name_match <- FALSE
man.data$id_match <- FALSE
man.data$higher_match <- FALSE
man.data$alt_datasource <- NA_character_
man.data$alt_resolved_name <- NA_character_
# reorder columns bcuz R is annoying
man.data[,c("name", "international_id", "resolved_names", "taxon_level_fromid", "taxon_name_fromid", "higher_order_fromid", "higher_order_id", "data_source", "resolved_id_fromgnr", "resolved_taxon_level_fromgnr", "resolved_higher_order_fromgnr", "resolved_higher_order_id", "name_match", "id_match", "higher_match", "alt_datasource", "alt_resolved_name")] 

# loop through all rows
for (row in 1:nrow(man.data)) {
  # first check if name is abiotic
  if (is_abiotic(man.data$name[counter], counter)) {
    # skip to next row if true
    counter <- counter + 1
    next
  }
  # try to resolve the name with gnr
  temp <- gnr_resolve(names = as.vector(man.data$name[counter]),  canonical = T,
                      best_match_only = T, preferred_data_sources = c(9, 4))
  # set primary data source
  primary_ds <- "World Register of Marine Species"
  # check if able to resolve name 
  if (!empty(temp)) {
    # add to resolved_names column
    resolved_name <- unlist(temp[1, 'matched_name2'])
    man.data$resolved_names[counter] <- resolved_name
    # add to data_source or alt_ds column
    authority <- unlist(temp[1, 'data_source_title'])
    # add to data_source if WORMs or alt_ds for other 
    if (authority == primary_ds) {
      man.data$data_source[counter] <- authority
    } else {
      man.data$alt_datasource[counter] <- authority
      man.data$alt_resolved_name[counter] <- resolved_name
    }
    
    # edge case: check if international_id does not exist in input file() taxon_level, name, higher order are false)
    if (man.data$international_id[counter] == -999 | is.na(man.data$international_id[counter])) {
      # call helper function to retrieve worms ID from resolved name 
      acquire_wormsid(resolved_name, counter, man.data)
      # retrieve taxon level from resolved_name
      name2taxoninfo(resolved_name, counter, man.data)
      # higher_match, id_match, and name_match remain false as original ID did not exist
    }
    # else internation_id does exist in input file
    else {
      # set resolved_id from resolved_name
      acquire_wormsid(resolved_name, counter, man.data)
      # call helper function to retrieve taxon info from id
      id2taxoninfo(man.data$international_id[counter], counter, man.data)
      # call helper function to retrieve taxon info from resolved_name 
      name2taxoninfo(resolved_name, counter, man.data)
      
      # check if taxon name matches with resolved
      if (man.data$taxon_name_fromid[counter] == man.data$resolved_names[counter]) {
        # set name_match to true
        man.data$name_match[counter] <- TRUE
      }
      # check if id matches with resolved
      if (man.data$international_id[counter] == man.data$resolved_id_fromgnr[counter]) {
        # set id_match to true
        man.data$id_match[counter] <- TRUE
      }
      # check if higher order matches with resolved
      if (man.data$higher_order_fromid[counter] == man.data$resolved_higher_order_fromgnr[counter]) {
        man.data$higher_match[counter] <- TRUE
      }
    }
  } else {
    # case: gnr unable to resolve by name, fill with NA 
    man.data$resolved_names[counter] <- NA_character_

    # edge case: check if international id is not empty for row 
    if(!is.na(man.data$international_id[counter])) {
      # fill in taxon info based on ID
      id <- man.data$international_id[counter]
      id2taxoninfo(id, counter, man.data)
      # leave resolved information as NA and check match columns false
    }
    # edge case: unable to resolve name and international id does not exist 
    else {
      # check if id can be resolved with original, unresolved name
      test_name <- man.data$name[counter]
      acquire_wormsid(test_name, counter, man.data)
      
      # see if id was able to be resolved
      if (!is.na(man.data$resolved_id_fromgnr[counter])) {
        # fill in taxon info from id
        id2taxoninfo(man.data$resolved_id_fromgnr[counter], counter, man.data)
        # leave resolved information as NA and check match columns false
      }
      # unable to get id from original name 
      else {
        # fill ID with NA
        man.data$resolved_id_fromgnr[counter] <- NA_character_
      }
    }
  }
  counter <- counter + 1
}

# collect all names with no resolved id
sosik_specific <- man.data$name[is.na(man.data$resolved_id_fromgnr)]
worms_verified <- man.data$name[!is.na(man.data$resolved_id_fromgnr)]

#convert to csv file 
write.csv(man.data, my_path)

