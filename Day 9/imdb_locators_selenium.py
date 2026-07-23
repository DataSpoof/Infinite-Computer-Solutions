"""
IMDb Top 250 Scraper using Selenium Locators
============================================

This script demonstrates how to scrape IMDb Top 250 movies
using Selenium.

Instead of parsing HTML with BeautifulSoup,
this script directly locates elements using

1. CSS Selectors
2. XPath

Required Installation

pip install selenium pandas

Selenium 4.6+ automatically downloads
the correct ChromeDriver.
"""

# -------------------------------------------------------
# Import Regular Expression module
# Used to extract IMDb ID and Rank from URL
# -------------------------------------------------------
import re

# -------------------------------------------------------
# Used for waiting while page loads
# -------------------------------------------------------
import time

# -------------------------------------------------------
# Pandas is used for storing data in DataFrame
# and exporting CSV
# -------------------------------------------------------
import pandas as pd

# -------------------------------------------------------
# Selenium WebDriver
# Controls Chrome browser
# -------------------------------------------------------
from selenium import webdriver

# -------------------------------------------------------
# Used for configuring Chrome options
# -------------------------------------------------------
from selenium.webdriver.chrome.options import Options

# -------------------------------------------------------
# By class tells Selenium HOW to locate elements

# Examples

# By.ID
# By.NAME
# By.CLASS_NAME
# By.CSS_SELECTOR
# By.XPATH
# -------------------------------------------------------
from selenium.webdriver.common.by import By

# -------------------------------------------------------
# Expected Conditions

# Used with explicit wait

# Example:
# Wait until element becomes visible
# -------------------------------------------------------
from selenium.webdriver.support import expected_conditions as EC

# -------------------------------------------------------
# Explicit Wait class

# Waits for certain conditions
# before continuing
# -------------------------------------------------------
from selenium.webdriver.support.ui import WebDriverWait


# IMDb Top 250 URL
URL = "https://www.imdb.com/chart/top/"


# =======================================================
# Locator Repository
# =======================================================
#
# Keeping all locators in one class is an
# Enterprise Automation best practice.
#
# If IMDb changes its HTML tomorrow,
# only this class needs updating.
#
# Instead of changing 100 lines,
# you'll change only one locator.
#
# =======================================================
class Loc:

    # ---------------------------------------------------
    # Movie Row Locator
    #
    # XPath Explanation
    #
    # //li
    #     Find every <li>
    #
    # .//
    #     Search inside current li
    #
    # a
    #     Anchor tag
    #
    # contains(@href,'/title/tt')
    #     href contains movie id
    #
    # Example
    #
    # /title/tt0111161/
    #
    # ---------------------------------------------------
    ROW = (
        By.XPATH,
        "//li[.//a[contains(@href,'/title/tt')]]"
    )

    # ---------------------------------------------------
    # CSS Selector
    #
    # Find title hyperlink
    #
    # a = anchor tag
    #
    # .ipc-title-link-wrapper
    # = class name
    # ---------------------------------------------------
    TITLE_LINK_CSS = (
        By.CSS_SELECTOR,
        "a.ipc-title-link-wrapper"
    )

    # ---------------------------------------------------
    # XPath version
    #
    # Relative XPath
    #
    # Search inside current row
    #
    # Find href containing
    #
    # /title/tt
    # ---------------------------------------------------
    TITLE_LINK_XPATH = (
        By.XPATH,
        ".//a[contains(@href,'/title/tt')]"
    )

    # ---------------------------------------------------
    # Rating Locator
    #
    # aria-label Example
    #
    # IMDb rating: 9.3
    #
    # starts-with()
    #
    # Very reliable because
    # accessibility attributes
    # rarely change.
    # ---------------------------------------------------
    RATING = (
        By.XPATH,
        ".//span[starts-with(@aria-label,'IMDb rating')]"
    )


# =======================================================
# Create Chrome Browser
# =======================================================
def make_driver():
    """
    Creates Chrome browser
    with required options.
    """

    # Chrome options object
    opts = Options()

    # Run browser without GUI
    opts.add_argument("--headless=new")

    # Browser size
    opts.add_argument("--window-size=1920,1080")

    # Reduce Selenium detection
    opts.add_argument("--disable-blink-features=AutomationControlled")

    # Fake browser identity
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Return Chrome browser
    return webdriver.Chrome(options=opts)


# =======================================================
# Wait until all movie rows load
# =======================================================
def wait_for_all_rows(driver, min_rows=25, timeout=45):

    """
    IMDb loads rows gradually.

    Instead of sleeping blindly,
    wait until enough rows appear.
    """

    # Wait until at least 25 rows exist
    WebDriverWait(driver, timeout).until(

        lambda d: len(
            d.find_elements(*Loc.ROW)
        ) >= min_rows
    )

    previous = -1
    stable_ticks = 0

    # Wait until row count stops increasing
    while stable_ticks < 3:

        # Count current rows
        count = len(driver.find_elements(*Loc.ROW))

        # If count hasn't changed
        if count == previous:
            stable_ticks += 1
        else:
            stable_ticks = 0

        previous = count

        # Wait half second
        time.sleep(0.5)

    # Return all movie rows
    return driver.find_elements(*Loc.ROW)


# =======================================================
# Safely extract text
# =======================================================
def text_or_none(row, locator):

    """
    Returns element text.

    If element doesn't exist,
    return None.

    Prevents
    NoSuchElementException.
    """

    # Find matching elements
    found = row.find_elements(*locator)

    # If element found
    if found:
        return found[0].text.strip()

    # Otherwise
    return None


# =======================================================
# Main Scraper
# =======================================================
def scrape():

    # Open Chrome
    driver = make_driver()

    try:

        # Open IMDb page
        driver.get(URL)

        # Wait until movies load
        rows = wait_for_all_rows(driver)

        print(f"Rows located: {len(rows)}")

        # Store movie data
        records = []

        # Loop through every movie
        for row in rows:

            # -----------------------------------------
            # Find title link using CSS
            #
            # If CSS fails,
            # use XPath
            # -----------------------------------------
            links = (
                row.find_elements(*Loc.TITLE_LINK_CSS)
                or
                row.find_elements(*Loc.TITLE_LINK_XPATH)
            )

            # Skip invalid row
            if not links:
                continue

            # First hyperlink
            link = links[0]

            # Movie title
            title = link.text.strip()

            # Movie URL
            href = link.get_attribute("href") or ""

            # -----------------------------------------
            # Extract IMDb Movie ID
            #
            # Example
            #
            # tt0111161
            # -----------------------------------------
            tt_match = re.search(
                r"/title/(tt\d+)/",
                href
            )

            # -----------------------------------------
            # Extract Rank
            #
            # Example
            #
            # chttp_t_1
            #
            # Rank = 1
            # -----------------------------------------
            rank_match = re.search(
                r"chttp_t_(\d+)",
                href
            )

            # Default values
            rating = None
            votes = None

            # Find rating element
            rating_els = row.find_elements(*Loc.RATING)

            if rating_els:

                # Example
                #
                # IMDb rating: 9.3
                #
                aria = rating_els[0].get_attribute(
                    "aria-label"
                ) or ""

                # Extract numeric rating
                r = re.search(
                    r"([\d.]+)",
                    aria
                )

                if r:
                    rating = float(r.group(1))

                # -------------------------------------
                # Visible Text Example
                #
                # 9.3 (3.2M)
                #
                # Extract
                #
                # 3.2M
                # -------------------------------------
                v = re.search(
                    r"\(([^)]+)\)",
                    rating_els[0].text
                )

                if v:
                    votes = v.group(1)

            # Store movie details
            records.append({

                "Rank":
                    int(rank_match.group(1))
                    if rank_match else None,

                "Title":
                    title,

                "Rating":
                    rating,

                "Votes":
                    votes,

                "IMDb ID":
                    tt_match.group(1)
                    if tt_match else None,

                # Remove tracking parameters
                "URL":
                    href.split("?")[0]
            })

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Sort by Rank
        df = df.sort_values("Rank")

        # Reset index
        df = df.reset_index(drop=True)

        print(f"\nMovies Scraped : {len(df)}\n")

        # Show first 10 movies
        print(df.head(10).to_string(index=False))

        # Export CSV
        df.to_csv(
            "imdb_top_250_locators.csv",
            index=False
        )

        print("\nCSV Saved Successfully")

        return df

    finally:

        # Always close browser
        driver.quit()


# =======================================================
# Program Entry Point
# =======================================================
if __name__ == "__main__":

    scrape()