import requests
import sqlite3
import time
import argparse
import logging

from bs4 import BeautifulSoup
from google.cloud import bigquery
from dotenv import load_dotenv

from rss_feeds import supported_cities, rss_feeds
from parser import parse_listing

logger = logging.getLogger(__name__)


def get_listings(city):
    "Parse the main listings page to get the recent listings"
    # make sure this is a supported city
    assert city in supported_cities

    url = rss_feeds[city]
    r = requests.get(url)

    if r.status_code != 200:
        print("Bad Request")

    # pick out the listings
    stock = BeautifulSoup(r.text, "html.parser")
    listings = stock.find_all("li", class_="result-row")

    print(f"Found {len(listings)} listings")
    return listings


def fetch_page(post_url):
    logging.info(f"New Entry: {post_url} Parsing and adding to database")
    page = requests.get(post_url)
    if page.status_code != 200:
        logger.warn(f"Bad Request: {page.text}")
        raise Exception
    return page


def check_listing(post_url):
    "Parses a craiglist housing for rent ad"
    page = fetch_page(post_url)
    data = parse_listing(page)
    return data


def save_to_local(listing, conn):
    "listing is a dict with attributes matching columns"
    logger.debug(f"Saving listing: {listing['post_title']} to sqlite")
    l = listing
    conn.execute(
        "INSERT INTO listings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            l["post_date"],
            l["post_url"],
            l["post_title"],
            l["latitude"],
            l["longitude"],
            l["address"],
            l["date_available"],
            l["price"],
            l["area"],
            l["neighbourhood"],
            l["extras"],
            l["bedrooms"],
            l["bathrooms"],
            l["unit_type"],
            l["parking"],
            l["smoking"],
            l["pets"],
            l["laundry"],
            l["furnished"],
            l["muni"],
            l["location"],
            l["body"],
            l["city"],
        ],
    )
    conn.commit()
    logger.debug(f"Added entry {l['post_url']} to db")


def save_to_biqquery(listing, client, table):
    logger.debug(f"Saving listing: {listing['post_title']} to bigquery")
    l = listing
    response = client.insert_rows(
        table,
        [
            (
                l["post_date"],
                l["post_url"],
                l["post_title"],
                l["latitude"],
                l["longitude"],
                l["address"],
                l["date_available"],
                l["price"],
                l["area"],
                l["neighbourhood"],
                l["extras"],
                l["bedrooms"],
                l["bathrooms"],
                l["unit_type"],
                l["parking"],
                l["smoking"],
                l["pets"],
                l["laundry"],
                l["furnished"],
                l["muni"],
                l["location"],
                l["body"],
                l["city"],
            )
        ],
    )
    logger.debug(f"Added entry to BigQuery {response}")


def get_listing_metadata(listing):
    post_info = listing.div
    post_date = post_info.time.get("datetime")
    post_id = post_info.a.get("data-id")
    post_url = post_info.a.get("href")
    post_title = post_info.a.text
    return post_date, post_id, post_url, post_title


def listing_seen(post_url, post_date, cursor):
    sql = "SELECT * FROM listings WHERE id = ? AND date = ?"
    cursor.execute(sql, [post_url, post_date])
    if cursor.fetchone():
        logging.debug("Already in db...")
        return True
    else:
        return False


def main(city, db="listings-v3.db"):

    listings = get_listings(city)

    conn = sqlite3.connect(db)
    c = conn.cursor()

    client = bigquery.Client()
    table = client.get_table("bram-185008.craiglist_crawler.listings")

    for entry in listings:
        # Grab some in info from the entry
        post_date, post_id, post_url, post_title = get_listing_metadata(entry)

        logger.debug(f"Listing: {post_title}")
        # check if the entry is already in the database
        if not listing_seen(post_url, post_date, conn):
            try:
                listing = check_listing(post_url)
            except:
                continue

            listing["post_date"] = post_date
            listing["post_url"] = post_url
            listing["post_title"] = post_title
            listing["city"] = city

            save_to_local(listing, conn)

            save_to_biqquery(listing, client, table)
            time.sleep(1)


if __name__ == "__main__":
    # SETTINGS
    parser = argparse.ArgumentParser(description="Download the latest data")
    parser.add_argument("--metro", default="vancouver", type=str, help="Which metro area should we grab data for?")
    parser.add_argument("--log", default="info", type=str, help="Set the logging level")
    parser.add_argument("--db", default="listings-v3.db", type=str, help="Path to sqlite3 database file")
    args = parser.parse_args()

    # Set log level to specified arg
    loglevel = args.log
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(level=numeric_level)

    load_dotenv()
    city = args.metro

    main(city, args.db)
