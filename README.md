# Craigslist Crawler

This is a script that monitors the rss feed of craigslist to scrape rental apartment listings for Vancouver. It stores the listings in a database and extracts key characteristics such as area, location and ammenities.

## Getting started

Make sure docker engine is installed and pipenv is installed.

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

### gcloud Credentals

Make sure your gcloud credentials are provided in the .env file:

eg:

```bash
GOOGLE_APPLICATION_CREDENTIALS='/home/bram/Documents/craiglist-crawler-a7aff758fc9d.json'
```

### Installing a new package

When a package is added to the Pipfile, we need to regenerate the lock file, then rebuild the docker container
```bash
pipenv lock
```

### Using pipenv

If you don't want to use docker, use pipenv to manage environment. Activate the pipenv envionrment with:
```bash
pipenv install
pipenv shell
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
