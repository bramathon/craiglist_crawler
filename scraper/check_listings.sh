#!/bin/bash
# cd /home/bram/craiglist_crawler/
python3 scraper/check_listings.py --metro "vancouver"
python3 scraper/check_listings.py --metro "portland"
python3 scraper/check_listings.py --metro "toronto"
python3 scraper/check_listings.py --metro "montreal"
