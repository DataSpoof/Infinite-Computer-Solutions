"""
IMDb Top 250 Movie Scraper
--------------------------
This script uses Selenium to load the IMDb Top 250 page because IMDb
uses JavaScript and AWS WAF (Web Application Firewall), which may block
normal requests.

Required Libraries:
    pip install selenium beautifulsoup4 pandas

Also install ChromeDriver compatible with your Chrome version.
"""

# Import HTML module to decode HTML entities
# Example: Schindler&apos;s List -> Schindler's List
import html

# Import JSON module to parse JSON-LD data embedded in the webpage
import json

# Import time module for delays while waiting for page rendering
import time

# Pandas is used for creating DataFrames and saving CSV files
import pandas as pd

# BeautifulSoup is used to parse HTML
from bs4 import BeautifulSoup

# Selenium WebDriver controls Chrome browser
from selenium import webdriver

# Used to configure Chrome browser options
from selenium.webdriver.chrome.options import Options


# IMDb Top 250 URL
url = "https://www.imdb.com/chart/top/"


def get_rendered_html(url, timeout=25):
    """
    Opens IMDb page using Selenium.

    Since IMDb loads content using JavaScript,
    Selenium waits until the JSON-LD data appears.

    Parameters
    ----------
    url : str
        IMDb page URL

    timeout : int
        Maximum waiting time in seconds

    Returns
    -------
    str
        Fully rendered HTML page
    """

    # Create Chrome configuration object
    opts = Options()

    # Run browser in headless mode (without GUI)
    opts.add_argument("--headless=new")

    # Set browser window size
    opts.add_argument("--window-size=1920,1080")

    # Reduce Selenium detection
    opts.add_argument("--disable-blink-features=AutomationControlled")

    # Set custom User-Agent so IMDb thinks it's a real browser
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Launch Chrome browser
    driver = webdriver.Chrome(options=opts)

    try:
        # Open IMDb webpage
        driver.get(url)

        # Wait until JSON-LD appears
        for _ in range(timeout):

            # Get current HTML source
            page = driver.page_source

            # IMDb embeds movie data in JSON-LD
            if "application/ld+json" in page and "itemListElement" in page:
                return page

            # Wait one second before checking again
            time.sleep(1)

        # Raise exception if timeout occurs
        raise TimeoutError("Timed out waiting for IMDb page to render.")

    finally:
        # Always close browser
        driver.quit()


def parse_duration(iso):
    """
    Converts ISO-8601 duration into minutes.

    Example:
        PT2H22M  -> 142

    Parameters
    ----------
    iso : str

    Returns
    -------
    int
        Total duration in minutes
    """

    # If duration doesn't exist
    if not iso:
        return None

    hours = 0
    minutes = 0
    num = ""

    # Remove PT prefix
    iso = iso.replace("PT", "")

    # Read each character
    for ch in iso:

        # If digit, keep building number
        if ch.isdigit():
            num += ch

        # Hour indicator
        elif ch == "H":
            hours = int(num)
            num = ""

        # Minute indicator
        elif ch == "M":
            minutes = int(num)
            num = ""

    # Convert to total minutes
    return hours * 60 + minutes


def main():
    """
    Main function
    """

    # Download fully rendered webpage
    page_html = get_rendered_html(url)

    # Print HTML size
    print("Rendered HTML Length:", len(page_html))

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(page_html, "html.parser")

    # Find JSON-LD script
    ld_tag = soup.find(
        "script",
        {"type": "application/ld+json"}
    )

    # Convert JSON text into Python dictionary
    data = json.loads(ld_tag.string)

    # Get movie list
    items = data["itemListElement"]

    print("Movies Found:", len(items))

    # Empty list for storing movie information
    rows = []

    # Enumerate gives movie rank starting from 1
    for rank, entry in enumerate(items, start=1):

        # Movie details
        movie = entry["item"]

        # Rating dictionary
        rating = movie.get("aggregateRating") or {}

        # Store all required fields
        rows.append({

            # Movie ranking
            "Rank": rank,

            # Decode HTML entities
            "Title": html.unescape(movie.get("name", "")),

            # IMDb Rating
            "Rating": rating.get("ratingValue"),

            # Number of Votes
            "Votes": rating.get("ratingCount"),

            # Genre
            "Genre": movie.get("genre"),

            # PG-13, R, etc.
            "Content Rating": movie.get("contentRating"),

            # Runtime in minutes
            "Runtime (Minutes)": parse_duration(
                movie.get("duration")
            ),

            # IMDb URL
            "URL": movie.get("url")
        })

    # Convert list into DataFrame
    df = pd.DataFrame(rows)

    # Print first 10 movies
    print("\nFirst 10 Movies\n")
    print(df.head(10).to_string(index=False))

    # Save CSV
    df.to_csv(
        "imdb_top_250.csv",
        index=False
    )

    print("\nCSV File Saved Successfully!")

    print("Total Movies Saved:", len(df))


# Standard Python entry point
if __name__ == "__main__":
    main()