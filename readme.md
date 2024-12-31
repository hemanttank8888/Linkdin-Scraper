# Web and LinkedIn URL Scraper

## Overview

This script is designed to search with websites for LinkedIn profiles based on user input and then get  industry details from linkdin profile , and then generate a excel file containing the LinkedIn URLs found and industry details. The script is split into two parts:

Main Script main.py: Calls and runs the get_linkdin_url functions.
Helper function linkdin_window, setup_chrome_options : Contains functions that are called by the get_linkdin_url function to perform  for get LinkedIn url.

## Features:
    1. Search for websites based on a query.
    2. Perform LinkedIn profile searches based on the results from the website search.
    3. Output LinkedIn URLs use for get industry details in a xlsx format for easy extraction.

## Requirements
we have Requirements.txt file for install dependencies
Before running the script, ensure you have the following installed:
run command for install dependencies  : `requirments.txt`

Example command:
```python
pip install -r requirements.txt
```

## File Structure

```bash
your_script_directory/
│
├── main         # Main function which executes the program
├── get_linkdin_url        # Helper functions for scraping LinkedIn url
├── output.xlsx              # Output xlsx file containing LinkedIn URLs
├── input.xlsx              # input xlsx file containing websites of company's URLs
├── README.md  
```

## How to Use
Clone or Download the Repository from this github url : "url_path"

Run the Main Script
Run the migration_linkdin.py file to start the process. This file will:

Call functions from migration_linkdin.py to search for websites.
read `input.xlsx` file and use input file web site list
Extract LinkedIn URLs from the results and then using url of linkdin extract industry details.
Save the LinkedIn URLs in a xlsx file.

Example command: 
```python
python main.py
```

The script will ask for a search query. You can enter a term related to the websites you're interested in.
The script will then perform a LinkedIn search based on the websites found.
The final result will be a xlsx file (`output.xlsx`) containing the LinkedIn URLs


How It Works
Main Script (`migration_linkdin.py`)
The main file handles user input, calls the functions from the helper function.


