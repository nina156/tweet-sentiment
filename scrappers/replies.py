import requests
import csv
from datetime import datetime

API_KEY = ""
MAX_PAGES = 999
tweet_id = "1916042720134471964"  # tweet id
url = "https://api.twitterapi.io/twitter/tweet/replies"
headers = {"X-API-Key": API_KEY}
params = {
    "tweetId": tweet_id,
    "cursor": ""
}

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"results/replies_{tweet_id}_{timestamp}.csv"


def strip_new_line(text):
    return text.replace('\n', ' ').replace('\r', ' ').strip() if text else ''


def send_request():
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception("Request failed:", response.status_code, response.text)

    return response.json()


def write_to_file(writer, replies):
    for reply in replies:
        writer.writerow({
            "id": reply.get("id"),
            "url": reply.get("url"),
            "content": strip_new_line(reply.get("text")),
            "author": strip_new_line(reply.get("author").get("userName")),
            "created_at": reply.get("createdAt")
        })


def main():
    print("=== RUN CONFIGURATION ===")
    print(f"Tweet id: {tweet_id}")
    print("==========================")

    all_replies = 0
    page = 0

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "url", "content", "author", "created_at"])
        writer.writeheader()

        while page < MAX_PAGES:
            data = send_request()
            replies = data.get("tweets", [])
            if not replies:
                print("No replies found, finishing...")
                break

            print(f'Received {len(replies)} replies on page {page}')
            all_replies += len(replies)

            write_to_file(writer=writer, replies=replies)

            next_cursor = data.get("next_cursor")
            if not next_cursor:
                print("No next page, finishing...")
                break

            params["cursor"] = next_cursor
            page += 1

    print(f"Saved {all_replies} replies to {output_file}")


if __name__ == "__main__":
    main()
