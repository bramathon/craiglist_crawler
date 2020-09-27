# Craigslist Crawler

This is a script that monitors the rss feed of craigslist to scrape rental apartment listings for Vancouver. It stores the listings in a database and extracts key characteristics such as area, location and ammenities.

## Getting started

To build the docker container:

```
docker build --tag crawler .
```

To run the script:

```
docker run --rm -it \
--volume "`pwd`:/home/craig/app" \
crawler \
scraper/check_listings.sh
```
