import json
import random
import re
import time
import ast
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import logging
from config import Configurator
from requests.exceptions import Timeout

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
cfg = Configurator()
# Configuration
USER_AGENTS_PATH = cfg.get_user_agents_path()
HOTEL_DF_PATH = cfg.get_hotel_df_path()
REVIEWS_OUTPUT_PATH = cfg.get_out_path()
# HOTELS_URL = "https://www.tripadvisor.com.tr/Hotels-g297962-Antalya_Turkish_Mediterranean_Coast-Hotels.html"


def get_user_agents(path):
    """Load user agents from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        user_agents_data = json.load(f)
    return [entry["ua"] for entry in user_agents_data]


def fetch_html(url, user_agents):
    """Fetch HTML content from a URL using random user agents."""
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }
    max_retries = 30
    retries = 0
    while retries < max_retries:
        try:
            proxy = proxy_generator()
            response = requests.get(url=url, proxies=proxy, headers=headers, timeout=15)
            logging.info(f"Status Code: {response.status_code}")
            response.raise_for_status()
            return response.content
        except:
            logging.error(f"Error fetching HTML from URL: {url}")
        retries += 1
    logging.error(f"Failed to fetch HTML after {max_retries} retries.")
    return None


def proxy_generator():
    """Generate a random proxy from sslproxies.org."""
    response = requests.get("https://sslproxies.org/")
    soup = bs(response.content, 'html.parser')
    proxies = soup.find_all("tbody")[0].find_all("tr")
    proxies_array = []

    for i in proxies:
        try:
            ip = i.find_all("td")[0].text
            port = i.find_all("td")[1].text
            proxies_array.append({"https": f"http://{ip}:{port}"})
        except Exception as e:
            logging.error(f"Error parsing proxy: {e}")

    if proxies_array:
        return random.choice(proxies_array)
    else:
        logging.error("No valid proxies found.")
        return None


def parse_html(content):
    """Parse HTML content using BeautifulSoup."""
    if content:
        return bs(content, "lxml")
    logging.error(f"Error parsing HTML")
    return None


def get_names_and_count(soup):
    """Extract hotel names and review counts from the parsed HTML."""
    hotel_names_with_numbers = [
        hotel.get_text(strip=True) for hotel in soup.find_all(name="div", class_="nBrpc o W")
    ]
    cleaned_hotel_names = [
        re.sub(r'[^\w\s]', '', re.sub(r'^\d+\.', '', hotel)) for hotel in hotel_names_with_numbers
    ]

    review_counts = []
    for count_review in soup.find_all("span", class_="biGQs _P pZUbB hmDzD"):
        span_tag = count_review.find("span", class_="S4")
        if span_tag:
            review_counts.append(span_tag.text)

    review_counts_int = [
        int(re.sub(r'\.', '', re.search(r'\d+(\.\d+)*', review).group())) for review in review_counts
    ]

    return pd.DataFrame({"name": cleaned_hotel_names, "count": review_counts_int})


def get_button_hrefs(soup):
    """Extract href links from button elements in the parsed HTML."""
    hrefs = []
    buttons = soup.find_all('button', class_='ypcsE _S wSSLS')
    for button in buttons:
        a_tag = button.find('a', href=True)
        if a_tag:
            hrefs.append(a_tag['href'])
    return hrefs


def get_dynamic_links(hotels):
    """Generate dynamic review links for hotels."""
    root = "https://www.tripadvisor.com.tr"
    hotel_review_links = [root + hotel for hotel in hotels]
    return [
        link[:link.find('Reviews') + 7] + "-or{}" + link[link.find('Reviews') + 7:]
        for link in hotel_review_links
    ]


def get_review_by_url(url):
    """Fetch and extract reviews from a given URL."""
    try:
        user_agents = get_user_agents(USER_AGENTS_PATH)
        review_page = parse_html(fetch_html(url, user_agents))
        if review_page:
            reviews = review_page.find_all("div", class_="_T FKffI bmUTE")
            return [review.find("span", class_="orRIx Ci _a C").text for review in reviews if
                    review.find("span", class_="orRIx Ci _a C") is not None]
        return None
    except requests.exceptions.RequestException as err:
        logging.error(f"HTTP Error {err}")
        return None


def get_all_dynamic_links(hotel_df):
    """Generate all dynamic review links for a dataframe of hotels."""
    results = []
    for _, row in hotel_df.iterrows():
        links = [
            row["review_link"].format(rng)
            for rng in range(5, row["count"], 5)
        ]
        results.append(links)
    return results


# def create_hotel_df(user_agents_path, output_path):
#     """Create a dataframe of hotels with their dynamic review links."""
#     user_agents = get_user_agents(user_agents_path)
#     response = fetch_html(url=HOTELS_URL, user_agents=user_agents)
#
#     if response:
#         hotels = get_button_hrefs(parse_html(response))
#         hotel_review_links = get_dynamic_links(hotels)
#         hotel_df = get_names_and_count(parse_html(response))
#         hotel_df["review_link"] = hotel_review_links
#         hotel_df["dynamic_links"] = get_all_dynamic_links(hotel_df)
#         hotel_df.to_csv(output_path, index=False)
#     else:
#         logging.error("Failed to fetch hotel data.")


def scrape_reviews(hotel_df, output_path):
    """Scrape reviews for each hotel and save them to a JSON file."""
    hotel_df["dynamic_links"] = hotel_df["dynamic_links"].apply(ast.literal_eval)
    hotel_df["filtered_links"] = hotel_df["filtered_links"].apply(ast.literal_eval)

    text_list = []
    for idx, row in hotel_df.iterrows():
        text = []
        for i, url in enumerate(row["filtered_links"]):
            reviews = get_review_by_url(url)
            logging.info(f"Hotel Name: {row['name']} Count: {(i + 1) * 5}")
            logging.info(f"Review url: {url}")
            logging.info(f"Review: {reviews}")
            logging.info(5 * "--------------------------------------------------")
            if reviews:
                text.extend(reviews)
                hotel_review = {"name": row["name"], "review_list": reviews}
                with open(output_path, "a", encoding="utf-8") as f:
                    json.dump(hotel_review, f, ensure_ascii=False)
                    f.write(",\n")
            time.sleep(10)
        text_list.append({"name": row["name"], "review_list": text})
    logging.info(text_list)


if __name__ == "__main__":
    # Create hotel dataframe with dynamic links
    # create_hotel_df(USER_AGENTS_PATH, HOTEL_DF_PATH)

    # Scrape reviews and save to JSON file
    scrape_reviews(pd.read_csv(HOTEL_DF_PATH), REVIEWS_OUTPUT_PATH)
