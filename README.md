# About
We should get products URLs and other product data from XLSX file, and after enriching its with data from site, collect all products to CSV file.  
The goal of this scraper is to fetch products description and download their images.  
Also all downloaded images should be renamed according with product names after transliting it from cyrilic.  

# Features
1. Multithreading downloading files.
2. Using module system allows you to change export/import to TXT, CSV, XLS, GoogleSheets and so on.
3. There is save/continue scraper process from last URL.
4. If it's needed, you may plug Selenium library as mean of getting page sources.
5. You may configure XLS tables structure according with columns you need in config file.

# How to install and run
1. activate your virtualenv
2. pip install -r requirements.txt
3. python run_scraper.py

## Dependencies
1. beautifulsoup4
2. requests
3. openpyxl
4. transliterate