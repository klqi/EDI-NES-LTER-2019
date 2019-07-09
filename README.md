# EDI-NES-LTER-2019
Kathy's project files for the NES-LTER project with EDI for 2019 Summer 

Project members and collaboraters: Stace Beaulieu, Joe Futrelle, Heidi Sosik, Katherine Qi

Includes Python and R scripts for data analysis and publication:

auto_join (currently under local development):
    This includes a Python script (auto_extract.py) that creates a file 1_b prototype that can be used for 
    analysis of features and classes from the automatic classifier.
    
    Dependencies and Requirements:
        - Python 3.6
        - Pandas
        - ssl
        - urllib
        - All csv files within folder 


namespace_validation (local development):
    This project uses an R Markdown file (WoRMS_verify.Rmd) to resolve and re-classisy given taxonomic
    groups to the WoRMS database (primary) or NCBI (secondary). It generates an output csv file with the 
    original and corrected information that can be manually edited for name space development for 
    further analysis. 
    
    Dependencies and Requirements:
        - R/RStudio
        - taxize
        - worrms
        - plyr
        - dplyr
        - tcltk
        - X11 server (if on MacOS)
        - Internet


geographic_validation (local development):
    This iteration includes a Python script (transect_geocheck.py) that
    generates 2 csv files and an html file. "transect_subset.csv" is the
    original samples given (~140) with location data and
    "good_transect_subset.csv" is the newly generated samples based on user
    inputted distance from the reference longitudinal line (station 5). The
    html file generated is a leaflet map with the entire sample set (green), the good
    transect subset (purple), and the original transect subset (yellow). 
    
    Dependencies and Requirements:
        - Python 3.6
        - Pandas
        - folium
        - geopy
        - ssl
        - urllib
        - Internet
