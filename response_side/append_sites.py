import random
import re


def append_sites(text):
    product_mapping = {
        "tltp_main_course": {
            "name": "TLTP Program",
            "website": "https://www.tradelikethepros.com/regular"
        },
        "trade_journal_offer": {
            "name": "Trade Journal",
            "website": "https://www.tradelikethepros.com/trade-journal"
        },
        "tltp_toolkit_mid_ticket_offer": {
            "name": "TLTP Toolkit",
            "website": "https://www.tradelikethepros.com/"
        },
        "tltp_offers_description": "All TLTP Offers & Brief Descriptions",
        "7_day_funded_trader_challenge": {
            "name": "7 day Funded Trader Challenge",
            "website": "https://www.tradelikethepros.com/challenge"
        },
        "faq": "Frequently Asked Questions & Answers"
    }

    # Check if text already contains a website (e.g., "http", "www", ".com")
    if re.search(r'http[s]?://|www\.|\.com', text, re.IGNORECASE):
        return text

    print('no website yet')

    # Variations for appending the website
    variations = [
        "See {url} for more details!",
        "Check out {url} to learn more!",
        "Learn more at {url}!"
    ]

    # Normalize text by removing spaces and converting to lowercase for comparison
    text_normalized = text.lower().replace(" ", "").replace("-", "")

    # List to store all matching products with websites
    matches = []

    # Check each product in the mapping
    for product_info in product_mapping.values():
        if isinstance(product_info, dict):
            product_name = product_info["name"]
            website = product_info.get("website")
        else:
            product_name = product_info
            website = None

        # Normalize product name by removing spaces and converting to lowercase
        product_name_normalized = product_name.lower().replace(" ", "").replace("-", "")

        # If normalized product name is in normalized text and has a website, add to matches
        if product_name_normalized in text_normalized and website:
            matches.append(website)

    # If there are matches, prioritize the hierarchy
    if matches:
        # Define the priority URL
        priority_url = "https://www.tradelikethepros.com"

        # Check if the priority URL is in the matches (either directly or as a substring)
        if any(priority_url in url for url in matches):
            selected_url = priority_url
        else:
            # If priority URL isn't found, select the first match as fallback
            selected_url = matches[0]

        selected_variation = random.choice(variations).format(url=selected_url)
        return f"{text} {selected_variation}"

    # If no product with a website is found, return the original text
    print('no product with website')
    return text
