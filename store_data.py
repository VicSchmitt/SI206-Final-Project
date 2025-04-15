import sqlite3
import json
import os

CACHE_FILE = "cache.json"
DB_NAME = "movies_data.db"
LIMIT_PER_RUN = 25

def load_cache_file():
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_tables():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            year TEXT,
            rotten_tomatoes INTEGER,
            box_office INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER,
            video_id TEXT,
            title TEXT,
            view_count INTEGER,
            FOREIGN KEY(movie_id) REFERENCES Movies(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_existing_titles():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT title FROM Movies")
    existing = set(title for (title,) in cur.fetchall())
    conn.close()
    return existing

def store_data_from_cache():
    data = load_cache_file()
    omdb_cache = data.get("omdb_cache", {})
    trailers_cache = data.get("trailers_cache", {})

    existing_titles = get_existing_titles()
    new_count = 0

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + DB_NAME)
    cur = conn.cursor()

    for title, info in omdb_cache.items():
        if new_count >= LIMIT_PER_RUN:
            break

        if not info or title in existing_titles:
            continue

        rt = info.get("RottenTomatoes")
        bo = info.get("BoxOffice")
        year = info.get("Year")
        views = info.get("ViewCount")

        try:
            cur.execute('''
                INSERT OR IGNORE INTO Movies (title, year, rotten_tomatoes, box_office)
                VALUES (?, ?, ?, ?)
            ''', (title, year, rt, bo))
            conn.commit()

            cur.execute("SELECT id FROM Movies WHERE title = ?", (title,))
            movie_id = cur.fetchone()[0]

            cur.execute('''
                INSERT OR IGNORE INTO Videos (movie_id, video_id, title, view_count)
                VALUES (?, ?, ?, ?)
            ''', (movie_id, "cached", f"{title} trailer", views))
            conn.commit()

            new_count += 1
            print(f"Stored: {title}")

        except Exception as e:
            print(f"Failed for {title}: {e}")

    conn.close()
    print(f"Inserted {new_count} new movies this run.")

if __name__ == "__main__":
    create_tables()
    store_data_from_cache()
