# Craigslist Crawler

This is a script that monitors the rss feed of craigslist to scrape rental apartment listings for Vancouver. It stores the listings in a database and extracts key characteristics such as area, location and ammenities.

## Getting started

A Docker container is available, but craigslist seems to reject requests from it in some circumstances. Thus, advise against using for now.

To build the docker container:

```bash
docker build --tag crawler .
```

To run the script:

```bash
docker run --rm -it \
--volume "`pwd`:/home/craig/app" \
crawler \
scraper/check_listings.sh
```

### Install conda

To install conda silently

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
# activate in your shell
eval "$(/Users/jsmith/anaconda/bin/conda shell.YOUR_SHELL_NAME hook)"
```

### gcloud Credentals

Make sure your gcloud credentials are provided in the .env file:

eg:

```bash
GOOGLE_APPLICATION_CREDENTIALS='/home/bram/Documents/craiglist-crawler-a7aff758fc9d.json'
```

## Database

A local sqlite database scraper/listings-v3.db keeps track of all the listings for quick lookup. The schema is shown below:

```sql
CREATE TABLE IF NOT EXISTS "listings" (
  "date" TEXT,
  "id" TEXT,
  "title" TEXT,
  "latitude" REAL,
  "longitude" REAL,
  "address" TEXT,
  "date_available" TEXT,
  "price" REAL,
  "area" REAL,
  "neighbourhood" TEXT,
  "extras" TEXT,
  "bedrooms" REAL,
  "bathrooms" REAL,
  "unit_type" TEXT,
  "parking" TEXT,
  "smoking" REAL,
  "pets" TEXT,
  "laundry" TEXT,
  "furnished" INTEGER,
  "City" TEXT,
  "location" TEXT,
  "body" TEXT,
  "metro" TEXT
);
CREATE INDEX listings_id on listings (id);
CREATE INDEX listings_date on listings (id,date);
CREATE INDEX listings_date_metro on listings (id,date,metro);
```

The listings are also saved to bigquery
