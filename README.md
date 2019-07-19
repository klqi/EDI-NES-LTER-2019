# EDI-NES-LTER-2019
Kathy's project files for the NES-LTER project with EDI for 2019 Summer 

Project members and collaboraters: Stace Beaulieu, Joe Futrelle, Heidi Sosik, Katherine Qi

Includes Python and R scripts for data analysis and publication:

auto_join:
    This includes a Python script (auto_extract.py) that creates a file 1_b prototype that can be used for 
    analysis of features and classes from the automatic classifier.
    
    Dependencies and Requirements:
        - Python 3.6
        - Pandas
        - ssl
        - urllib
        - All csv files within folder 


namespace_validation:
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


geographic_validation:
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


plot1 (local development):
    This includes 2 scripts, wide2long.Rmd and
    concentration_geographic_analysis.ipynb, that take a subset of IFCB sample
    data and plot the concentration against distance offshore. It groups the
    species into Diatoms, Dinoflagellates, Haptophytes, and other, then graphs
    them across latitude. 

    Dependncies and Requirements:
        - RStudio
        - tidyverse
        - stringr
        - dplyr
        - Python 3.6
        - JupyterLab
        - matplotlib
        - pandas
        - numpy


plot2:
    This includes the script, biovolume_geographic_analysis.ipynb, which takes
    the outputs from transect_geocheck.py and auto_extract.py to make a plot
    analyzing the percent biovolume of higher ranking groups in samplesi
    across latitude.
    Currently, it draws data from the automatic classifier data from the IFCB
    dashboard, but it can use manual classification data as well. 

    Dependencies and Requirements:
        - Python 3.6
        - JupyterLab
        - pandas
        - numpy
        - matplotlib
        - Unix Shell
        - current file hierarchy of this repo
        - Internet
