# Project Overview
Business Problem: To improve user engagement and user experience on digital platforms by analyzing and creating visualizations of clickstream data.

Datasets used: 
* A 2008 clickstream dataset from an online store offering clothing for pregnant women 
Source: https://archive.ics.uci.edu/dataset/553/clickstream+data+for+online+shopping

* Clickstream data for June 2025 for Wikipedia from a Wikimedia data dump
Source: https://dumps.wikimedia.org/other/clickstream/2020-06/

Techniques employed: Removed N/A values and added placeholder values while cleaning and transforming data

Outputs: Two cleaned clickstream datasets stored in the processed section/folder of the data folder
# Setup Instructions

To clone this repository, run the git command below in your SSH client:
```
git clone git@github.com:mliu1076/inst414-final-project-maxwell-liu.git
```

To set up a Virtual Python Environment in VSCode, use the following commands in the terminal:
```
python -m venv venv

.venv\Scripts\activate
```

You can also setup a virtual environment by using the keyboard shortcut Ctrl+Shift+P on VSCode
and selecting "Python: Create Environment"

To install dependencies for this project, run the following command in the terminal:
```
pip install -r requirements.txt
```

# Running the Project
To run the project, simply run the main.py file by using the following command:
```
python main.py
```

# Code Package Structure

Here is the following structure of this package

inst414-final-project-maxwell-liu

├── data/

│   ├── extracted/ - stores extracted data from the sources (flat files in this case)

│   ├── processed/ - stores transformed and cleaned data

│   ├── outputs/ - stores outputs, analyzed data, and models

│   ├── reference-tables/ - stores the reference tables

├── etl/ - each py file is named after the respective step in the ETL process

│   ├── extract.py

│   ├── transform.py

│   ├── load.py

├── analysis/

│   ├── model.py - creates and saves analytical models based off business problem and datasets

│   ├── evaluate.py

├── vis/

│   ├── visualizations.py - this file creates visualizations

├── main.py - this file will run the entire project workflow

├── README.md

├── requirements.txt