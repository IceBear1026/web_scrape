import requests
from pprint import pprint

subreddit = 'CISSP'

url = f"https://www.reddit.com/r/{subreddit}/top.json?t=all"

headers = {
    'User-Agent': 'scraperBot'
}

response = requests.get(url, headers = headers)

data = response.json()
pprint(data)

