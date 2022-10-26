# Research_Scraper

---

Scraper for scientific publications
Description
Intro -> insert graphics


## Table of content

## Installation
I use Python 3.9.19
Please install following libraries on your PC or virtual environment:
- autopep8
- bs4
- cloudscraper
- jupyter
- matplotlib
- numpy
- pandas
- pylint
- requests
- scholarly

For Helium:
1. Install as usual with pip
2. Download the latest version of ChromeDriver from https://chromedriver.chromium.org/downloads
3. Replace old Helium-Chromedriver with your new ChromeDriver at following directory:
   - `<Research_Scraper_Python_Env_PATH >/lib/python3.9/site-packages/helium/_impl/webdrivers`

Make sure you are using the VPN of your university or institute.


### Virtual Environment
- Create a virtual environment with Python 3.9.19 if you do not want to install the libraries on your PC
- I can recommend using Anaconda for this purpose

## Features
- scrape publications for by DOI or URL (Springer Link, ScienceDirect, IEEE Xplore)
- download publications as PDF
- find URLs of publication with Scholarly
- several notebooks for experimenting with the scraper
  - for every publication website there is a notebook

