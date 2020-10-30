"""
Prefect flow for getting listings

To do:
1. Use prefect loop for going through listings
2. Run using cloud UI
3. Schedule and deploy on home server
"""

import time
import sqlite3

from google.cloud import bigquery
from prefect import task, Flow, Parameter
from dotenv import load_dotenv
from check_listings import (
    get_listings,
    check_listing,
    get_listing_metadata,
    save_to_local,
    save_to_biqquery,
    listing_seen,
    fetch_page,
)

from parser import parse_listing

load_dotenv()


@task
def get_current_listings(city):
    listings = get_listings(city)
    return listings


@task
def fetch_pages(listings, city, db="listings-v3.db"):
    pages = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for entry in listings:
        # Grab some in info from the entry
        post_date, post_id, post_url, post_title = get_listing_metadata(entry)
        # check if the entry is already in the database
        if not listing_seen(post_url, post_date, c):
            try:
                page = fetch_page(post_url)
                pages.append(dict(post_url=post_url, post_date=post_date, post_id=post_id, post_title=post_title, page=page, city=city))
            except:
                continue

            time.sleep(1)
    conn.close()
    return pages


@task
def save_listings(listings, db="listings-v3.db"):
    conn = sqlite3.connect(db)

    client = bigquery.Client()
    table = client.get_table("bram-185008.craiglist_crawler.listings")
    for entry in listings:
        save_to_local(entry, conn)
        save_to_biqquery(entry, client, table)
    conn.close()


@task
def parse_listings(pages):
    parsed_data = []
    for page in pages:
        html = page.pop("page")

        entry = parse_listing(html)
        parsed_data.append({**page, **entry})
    return parsed_data


def main():
    with Flow("Check listings") as flow:
        city = Parameter("city")

        ## Extract
        # get the current listings
        listings = get_current_listings(city)
        # fetch the pages
        pages = fetch_pages(listings, city)

        ## Transform
        # parse the listings
        data = parse_listings(pages)

        # Load
        save_listings(data)

    flow.run(city="vancouver")


if __name__ == "__main__":
    main()
