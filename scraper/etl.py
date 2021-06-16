"""
Prefect flow for getting listings

To do:
1. Use prefect loop for going through listings
2. Run using cloud UI
3. Schedule and deploy on home server
"""

import time
import sqlite3
import os

from google.cloud import bigquery
from prefect import task, Flow, Parameter
from prefect.run_configs import DockerRun
from prefect.engine.executors import DaskExecutor
from prefect.environments import LocalEnvironment
from prefect.run_configs import LocalRun
from prefect.environments.storage import Docker

# from dotenv import load_dotenv
from scraper.check_listings import (
    get_listings,
    get_listing_metadata,
    save_to_local,
    save_to_biqquery,
    listing_seen,
    fetch_page,
)

from scraper.parser import parse_listing

# load_dotenv()
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/bram/Documents/craiglist_crawler/craiglist-crawler-a7aff758fc9d.json"


@task
def get_current_listings(city):
    listings = get_listings(city)
    entries = []
    for entry in listings:
        e = {}
        e["post_date"], e["post_id"], e["post_url"], e["post_title"] = get_listing_metadata(entry)
        entries.append(e)
    return entries


@task
def fetch_pages(listings, city, db="listings-v3.db"):
    pages = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for entry in listings:
        # Grab some in info from the entry
        post_date, post_id, post_url, post_title = entry["post_date"], entry["post_id"], entry["post_url"], entry["post_title"]
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
    with Flow("Check listings", environment=LocalEnvironment(executor=DaskExecutor())) as flow:
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

    # flow.storage = Docker(registry_url="bramevert/craig")

    # flow.run_config = DockerRun(
    #     env={"GOOGLE_APPLICATION_CREDENTIALS": "/home/app/craiglist-crawler-a7aff758fc9d.json"},
    #     image="craig:latest",
    #     labels=["bram-desktop"],
    # )
    # flow.register(project_name="Craiglist Crawler")

    # flow.run_agent()
    flow.run(city="vancouver")


if __name__ == "__main__":
    main()
