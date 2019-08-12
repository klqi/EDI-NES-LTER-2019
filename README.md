# EDI-NES-LTER-2019

## Overview
Kathy's project files for the NES-LTER project with EDI for 2019 Summer. This includes Python and R scripts for data analysis and publication. The purpose of this program is to run analyses on IFCB data for manual and automatic classifications, drawing data from the IFCB dashboard and NES-LTER rest API. 

This workflow is intended to be reproducible to other IFCB transect cruise
data. Additionally, the data produced will be packaged and submitted to several
online repositories such as Environmental Data Initiative (EDI), NASA SeaBASS,
BCO-DMO. 

For additional information, visit https://nes-lter.whoi.edu/


## Project members and collaboraters
Stace Beaulieu, Joe Futrelle, Heidi Sosik, Katherine Qi (klqi@ucsd.edu)


## Base Requiremeents

R, Python 3.6+, Anaconda, jupyter notebook, bash


## Installation

Clone this repository into your current working directory:

```
git clone https://github.com/klqi/EDI-NES-LTER-2019.git
```

Create a conda enviornment from EDI-NES-LTER repo:

```
conda env create -f environment.yml
```

Or use an existing, activated Python3 conda environment: 

```
conda env update -f environment.yml
```

## Workflow

See [current workflow
diagram](https://github.com/klqi/EDI-NES-LTER-2019/blob/master/NES-LTER%20Transect%20Analysis%20Workflow%20Diagram.png)

## Status

As of August 9, this complete version (Cruise EN608) was developed over Summer 2019 as an EDI
fellowship project. Further capabilities are developed to allow this workflow
to become more reproducible. 
