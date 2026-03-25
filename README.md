# Characterizing the Landscape of Open-Source Satellite Software

This repository contains the dataset and source code used in our empirical study on open-source satellite-related software projects.
The primary goal of this repository is to enhance research transparency, reproducibility, and reusability, and to facilitate future studies that build upon our work.

Specifically, this repository provides:
- Scripts for automated data collection and preprocessing of OSS projects;
- Supporting code for data analysis, including language distribution calculations;
- The final datasets used to answer our research questions (RQs).

---

## Repository Structure

The repository is organized into two main parts:
1. **Code for data collection and processing**
2. **Datasets used in the empirical study**

Each component is described in detail below.

---

## Code for Data Collection and Processing

The following scripts were used to collect, filter, and preprocess OSS satellite-related projects:

- **`1-data_collection.py`**  
  Downloads all open-source software projects related to satellites.  
  This script serves as the initial data collection step and generates the raw project list with some attributions.

- **`2-check_IsEnglish_readme.py`**  
  Automatically checks whether an accessible project contains a README file written in English.  
  Projects without an English README are excluded from subsequent analysis.

- **`3-check_Iscontent.py`**  
  Verifies whether a project contains additional content beyond the README file  
  (e.g., source code, documentation).  
  This step helps filter out trivial or inactive repositories.

In addition, we provide a supporting analysis script:

- **`language_distribution_calculation.py`**  
  Calculates the programming language distribution for selected categories of projects.  
  This script was used to support language-related analyses reported in the paper.

---

## Datasets Used in the Study

We release the datasets used to answer our research questions to support replication and secondary analysis.

- **`All Satellite Projects for RQ1.xlsx`**  
  Contains **22,286** open-source satellite-related projects.  
  This dataset was used to address **RQ1** and represents the full set of collected projects after basic filtering.

- **`Selected Projects for RQ2 + RQ3.xlsx`**  
  Contains **646** randomly selected open-source satellite projects.  
  This curated dataset was used to address **RQ2** and **RQ3**.
