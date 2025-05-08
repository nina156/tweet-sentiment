import requests
import csv
from datetime import datetime
import re

# === CONFIGURATION ===
API_KEY = ""  # <-- tu trzeba dodać klucz apo
MAX_PAGES = 999
query_phrase = "#Trzaskowski2025"  # dla hasztagow #{hashtag}, dla użytkowników:{username}
query_type = "Latest"  # "Latest" albo "Top"
since = "2025-04-28_00:00:00_UTC"  # start (YYYY-MM-DD_HH:MM:SS_UTC)
until = "2025-05-05_00:00:00_UTC"  # end (YYYY-MM-DD_HH:MM:SS_UTC)
url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
headers = {"X-API-Key": API_KEY}

# Construct query
query = f"{query_phrase} since:{since} until:{until}"
params = {
    "query": query,
    "queryType": query_type,
    "cursor": ""
}

# Sanitize query for filename
safe_query = re.sub(r'[^a-zA-Z0-9_]+', '_', query_phrase)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"results/tweets_{safe_query}_{timestamp}.csv"


def strip_new_line(text):
    return text.replace('\n', ' ').replace('\r', ' ').strip() if text else ''


def send_request():
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception("Request failed:", response.status_code, response.text)

    return response.json()


def write_to_file(writer, tweets):
    for tweet in tweets:
        writer.writerow({
            "id": tweet.get("id"),
            "url": tweet.get("url"),
            "content": strip_new_line(tweet.get("text")),
            "author": strip_new_line(tweet.get("author").get("userName")),
            "created_at": tweet.get("createdAt")
        })


def main():
    print("=== RUN CONFIGURATION ===")
    print(f"Query: {query_phrase}")
    print(f"Query type: {query_type}")
    print(f"Since: {since}")
    print(f"Until: {until}")
    print("==========================")

    all_tweets = 0
    page = 0

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "url", "content", "author", "created_at"])
        writer.writeheader()

        while page < MAX_PAGES:
            data = send_request()
            tweets = data.get("tweets", [])
            if not tweets:
                print("No tweets found, finishing...")
                break

            print(f'Received {len(tweets)} tweets on page {page}')
            all_tweets += len(tweets)

            write_to_file(writer=writer, tweets=tweets)

            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print("No next page, finishing...")
                break

            params["cursor"] = next_cursor
            page += 1

    print(f"Saved {all_tweets} tweets to {output_file}")


if __name__ == "__main__":
    main()
