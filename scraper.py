import requests
from pprint import pprint
import sqlite3

def create_tables(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id NEXT PRIMARY KEY,
            title TEXT,
            score INTEGER,
            author TEXT,
            date REAL,
            url TEXT,
            comments TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS state (
            after TEXT
        )
    ''')
    conn.commit()

def get_last_after(conn):
    c = conn.cursor()
    c.execute('SELECT after FROM state')
    res = c.fetchone()
    return res[0] if res else ''

def set_last_after(conn, after):
    c = conn.cursor()
    c.execute('DELETE FROM state')
    c.execute('INSERT INTO state VALUES (?)', (after,))
    conn.commit()

def parse(subreddit, after='', conn = None):
    url_template = 'https://www.reddit.com/r/{}/top.json?t=all{}'

    headers = {
    'User-Agent': 'scraperBot'
    }

    params = f'&after={after}' if after else ''

    
    url = url_template.format(subreddit, params)
    response = requests.get(url, headers=headers)

    if response.ok:
        c = conn.cursor()
        data = response.json()['data']
        for post in data['children']:
            pdata = post['data']
            post_id = pdata['id']
            title = pdata['title']
            score = pdata['score']
            author = pdata['author']
            date = pdata['created_utc']
            url = pdata.get('url_overridden_by_dest')
            selftext = pdata['selftext']
            c.execute('INSERT OR IGNORE INTO posts VALUES (?,?,?,?,?,?,?)',
                      (post_id, title, score, author, date, url, selftext))
        conn.commit()
        return data['after']
    else:
        print(f'Error {response.status_code}')
        return None

def main():
    subreddit = 'CISSP'

    conn = sqlite3.connect('reddit-posts.db')
    create_tables(conn)
    after = get_last_after(conn)
    try:
        while True:
            after = parse(subreddit, after, conn)
            if not after:
                break
            set_last_after(conn, after)
    except KeyboardInterrupt:
        print('Exiting...')
    finally:
        conn.close()

if __name__ == '__main__':
    main()

