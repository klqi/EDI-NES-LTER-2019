# R script to clean the output of WoRMS_verify.Rmd

# This compares output of WoRMS_verify.Rmd to output of WoRMS taxon match GUI,
# adds 2 columns scientificName_Human_Observation and scientificNameID_Human_Observation as a look-up table for the Level 1b,
# fills preferentially with output of WoRMS_verify.Rmd: columns resolved_names and resolved_id_fromgnr,
# and, when needed, fills by HARD CODE

# Stace Beaulieu 2020-04-02

library(dplyr)

# input resolved_manual.csv commit bb1ecc6 into WoRMS taxon match GUI on 2020-04-01
# https://www.marinespecies.org/aphia.php?p=match
# GUI selections: when ambiguous, selected most recent
# open output file resolved_manual_matched.txt in EXCEL to fix column mis-alignment
# save edited EXCEL sheet as resolved_manual_matched.csv

resolved_manual_matched <- read.csv("resolved_manual_matched.csv")

# add column to indicate if resolved_id_fromgnr from WoRMS_verify.Rmd matches AphiaID_accepted from WoRMS GUI

resolved_manual_matched_matchIDs <- mutate(resolved_manual_matched, matchIDs = (resolved_id_fromgnr == AphiaID_accepted))

# change Taxon.status column to character helpful later in script

resolved_manual_matched_matchIDs <- mutate(resolved_manual_matched_matchIDs, status_char = as.character(Taxon.status))

# START THE LOOKUP TABLE TO BIND ADDITIONAL ROWS TO when need HARD CODE to fill
# filter(matchIDs == TRUE), deal with SPECIAL CASE FOR name == "Katodinium or Torodinium"
# add 2 columns scientificName_Human_Observation and scientificNameID_Human_Observation
# fill with columns resolved_names and LSID 

resolved_manual_matched_matchIDs_TRUE_wo_KorT <- resolved_manual_matched_matchIDs %>% filter(matchIDs == TRUE & name != "Katodinium or Torodinium")
resolved_manual_matched_matchIDs_TRUE_wo_KorT <- mutate(resolved_manual_matched_matchIDs_TRUE_wo_KorT, scientificName_Human_Observation = resolved_names, scientificNameID_Human_Observation = LSID)


# both WoRMS_verify and the WoRMS GUI fail, in the same way, for "Katodinium or Torodinium"
# note that although Emily provided an international_id we discovered that family 109410 only contained Torodinium
# have to go all the way up to class Dinophyceae 19542
KorT <- resolved_manual_matched_matchIDs %>% filter(name == "Katodinium or Torodinium")
KorT <- mutate(KorT, scientificName_Human_Observation = "Dinophyceae", scientificNameID_Human_Observation = "urn:lsid:marinespecies.org:taxname:19542")

resolved_manual_matched_matchIDs_LOOKUP <- bind_rows(resolved_manual_matched_matchIDs_TRUE_wo_KorT, KorT)


# then filter those (128-91=37) rows for which FALSE or NA in order to determine what to hard code

resolved_manual_matched_matchIDs_FALSE <- resolved_manual_matched_matchIDs %>% filter(matchIDs == FALSE | is.na(matchIDs))


# determined thru manual checking of WoRMS landing pages that it is o.k. to use ID from WoRMS_verify when GUI finds "alternate representation"
# filter the 8 "alternate representation", add the 2 columns, and bind to LOOKUP

alternate <- resolved_manual_matched_matchIDs_FALSE %>% filter(status_char == "alternate representation")
alternate <- mutate(alternate, scientificName_Human_Observation = resolved_names, scientificNameID_Human_Observation = paste('urn:lsid:marinespecies.org:taxname:',as.character(resolved_id_fromgnr),sep = ""))
resolved_manual_matched_matchIDs_LOOKUP <- bind_rows(resolved_manual_matched_matchIDs_LOOKUP, alternate)
# note error binding factor and character vector, coercing into character vector

# 29 categories remaining after filtering 8 alternate
resolved_manual_matched_matchIDs_FALSE_subset <- resolved_manual_matched_matchIDs_FALSE %>% filter(status_char != "alternate representation")


# There are 2 with status_char accepted.
# For Hemiaulus: HARD CODE the LSID AphiaID_accepted from the GUI; I do not know why the resolved_id_fromgnr failed.
# For Favella: Use the resolved_id_fromgnr. The GUI failed bc this is a case where there are 2 very different genera on Tree of Life with same name.

accepted <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(status_char == "accepted")
Hemiaulus <- accepted %>% filter(resolved_names == "Hemiaulus") %>% mutate(scientificName_Human_Observation = resolved_names, scientificNameID_Human_Observation = LSID)
Favella <- accepted %>% filter(resolved_names == "Favella") %>% mutate(scientificName_Human_Observation = resolved_names, scientificNameID_Human_Observation = paste('urn:lsid:marinespecies.org:taxname:',as.character(resolved_id_fromgnr),sep = ""))
resolved_manual_matched_matchIDs_LOOKUP <- bind_rows(resolved_manual_matched_matchIDs_LOOKUP, Hemiaulus, Favella)
# note when I complete this script can have single call to bind_rows

# For the 1 with status_char "nomen dubium"
# amoeba should be searched as common name, not genus. Both WoRMS_verify.Rmd and WoRMS GUI failed.
# HARD CODE Amoebozoa 391848 http://www.marinespecies.org/aphia.php?p=taxdetails&id=391848
amoeba <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(name == "amoeba") %>% mutate(scientificName_Human_Observation = "Amoebozoa", scientificNameID_Human_Observation = "urn:lsid:marinespecies.org:taxname:391848")


# For the 5 with status_char "uncertain"
# Looks like this resulted from ambiguous GUI selections; this led to same name but different authority

uncertain <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(status_char == "uncertain")

# For uncertain: Will NOT need to hard code 3 that filter out when international_id (provided by Emily) equals resolved_id_fromgnr (from WoRMS_verify)
# note resolved_names spelling for Chaetoceros curvisetus

uncertain_ok <- uncertain %>% filter(international_id == resolved_id_fromgnr)
uncertain_ok <- mutate(uncertain_ok, scientificName_Human_Observation = resolved_names, scientificNameID_Human_Observation = paste('urn:lsid:marinespecies.org:taxname:',as.character(resolved_id_fromgnr),sep = ""))

# Chaetoceros peruvianus HARD CODE the AphiaID_accepted from the GUI
# Chaetoceros debilis HARD CODE the AphiaID_accepted from the GUI

Cperu <- uncertain %>% filter(resolved_names == "Chaetoceros peruvianus") %>% mutate(scientificName_Human_Observation = resolved_names, scientificNameID_Human_Observation = LSID)
Cdebi <- uncertain %>% filter(resolved_names == "Chaetoceros debilis") %>% mutate(scientificName_Human_Observation = resolved_names, scientificNameID_Human_Observation = LSID)

# still have not bound amoeba or uncertain_ok
resolved_manual_matched_matchIDs_LOOKUP <- bind_rows(resolved_manual_matched_matchIDs_LOOKUP, amoeba, uncertain_ok, Cperu, Cdebi)
# note when I complete this script can have single call to bind_rows

# Of the 21 that lack resolved_names, 4 have international_id to HARD CODE as scientificNameID_Human_Observation
# for these 4 want to fill the scientificName_Human_Observation from the column taxon_name_fromid BUT that only works for zooplankton

no_resolved_names_but_id <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(!is.na(international_id) & is.na(resolved_names))

# zooplankton HARD CODE pull scientificName_Human_Observation from taxon_name_fromid
zooplankton <- no_resolved_names_but_id %>% filter(name == "zooplankton") %>% mutate(scientificName_Human_Observation = taxon_name_fromid, scientificNameID_Human_Observation = paste('urn:lsid:marinespecies.org:taxname:',as.character(international_id),sep = ""))

# mix elogated HARD CODE pull scientificName_Human_Observation from resolved_higher_order_fromgnr
# pennate HARD CODE pull scientificName_Human_Observation from resolved_higher_order_fromgnr
# Ciliate mix HARD CODE scientificName_Human_Observation Spirotrichea
mixelong <- no_resolved_names_but_id %>% filter(name == "mix elongated") %>% mutate(scientificName_Human_Observation = resolved_higher_order_fromgnr, scientificNameID_Human_Observation = paste('urn:lsid:marinespecies.org:taxname:',as.character(international_id),sep = ""))
pennate <- no_resolved_names_but_id %>% filter(name == "pennate") %>% mutate(scientificName_Human_Observation = resolved_higher_order_fromgnr, scientificNameID_Human_Observation = paste('urn:lsid:marinespecies.org:taxname:',as.character(international_id),sep = ""))
cilmix <- no_resolved_names_but_id %>% filter(name == "Ciliate mix") %>% mutate(scientificName_Human_Observation = "Spirotrichea", scientificNameID_Human_Observation = paste('urn:lsid:marinespecies.org:taxname:',as.character(international_id),sep = ""))

resolved_manual_matched_matchIDs_LOOKUP <- bind_rows(resolved_manual_matched_matchIDs_LOOKUP, zooplankton, mixelong, pennate, cilmix)
# note when I complete this script can have single call to bind_rows


# 17 remaining to consider for hard coding

resolved_manual_matched_matchIDs_FALSE_subset %>% arrange(resolved_id_fromgnr) -> resolved_manual_matched_matchIDs_FALSE_subsetSorted
# sorted to examine how filled resolved_id_fromgnr with -999999 for NOT ORGANISM but missed bad and other
# NOT ORGANISM is given a crazy number that can never be an AphiaID
# NOT ORGANISM 8: bad, bead, bubble, camera spot, detritus, fecal pellet, pollen, other

notorganism <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(resolved_id_fromgnr == -999999)
bad <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(name == "bad")
other <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(name == "other")
notorganism <- bind_rows(notorganism, bad, other)
notorganism <- mutate(notorganism, scientificName_Human_Observation = "NotApplicable", scientificNameID_Human_Observation = "NotApplicable")

# TO EUKARYOTE 5: flagellate, flagellate sp1, flagellate morphotype3, flagellate sp3, mix
# input file has 5 Eukaryote AlgaeBase LSID but missed flagellate morphotype3 and square unknown is incorrect
# HARD CODE scientificName_Human_Observation Eukaryota
# HARD CODE scientificNameID_Human_Observation urn:lsid:algaebase.org:taxname:86701
euk <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(resolved_id_fromgnr == "urn:lsid:algaebase.org:taxname:86701" & name != "square unknown")
flag3 <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(name == "flagellate morphotype3")
euk <- bind_rows(euk, flag3)
euk <- mutate(euk, scientificName_Human_Observation = "Eukaryota", scientificNameID_Human_Observation = "urn:lsid:algaebase.org:taxname:86701")

square <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(name == "square unknown")
square <- mutate(square, scientificName_Human_Observation = "Bacillariophyceae", scientificNameID_Human_Observation = "urn:lsid:marinespecies.org:taxname:148899")

resolved_manual_matched_matchIDs_LOOKUP <- bind_rows(resolved_manual_matched_matchIDs_LOOKUP, notorganism, euk, square)
# note when I complete this script can have single call to bind_rows


# TO DIATOM: pennate morphotype1
pen1 <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(name == "pennate morphotype1")
pen1 <- mutate(pen1, scientificName_Human_Observation = "Bacillariophyceae", scientificNameID_Human_Observation = "urn:lsid:marinespecies.org:taxname:148899")

# Calciosolenia brasiliensis: HARD CODE scientificName_Human_Observation (?from name, but I don't know why this name did not resolve into column resolved_names). The resolved_id_fromgnr is correct.
Cbra <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(name == "Calciosolenia brasiliensis")
Cbra <- mutate(Cbra, scientificName_Human_Observation = name, scientificNameID_Human_Observation = paste('urn:lsid:marinespecies.org:taxname:',as.character(resolved_id_fromgnr),sep = ""))

# TO SAME AS CILIATE MIX 1: ciliate
cil <- resolved_manual_matched_matchIDs_FALSE_subset %>% filter(name == "ciliate") %>% mutate(scientificName_Human_Observation = "Spirotrichea", scientificNameID_Human_Observation = "urn:lsid:marinespecies.org:taxname:1348")

resolved_manual_matched_matchIDs_LOOKUP <- bind_rows(resolved_manual_matched_matchIDs_LOOKUP, pen1, Cbra, cil)
# note when I complete this script can have single call to bind_rows

#MAYBE SORT BY NAME TO USE THE DATA PROVIDER CATEGORY ALPHABETICAL
resolved_manual_matched_matchIDs_LOOKUPsorted <- arrange(resolved_manual_matched_matchIDs_LOOKUP, name) 

write.csv(resolved_manual_matched_matchIDs_LOOKUPsorted, "c:/Users/sbeaulieu/Desktop/resolved_manual_matched_matchIDs_LOOKUPsorted.csv")



