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
            video_id TEXT UNIQUE,
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

def get_row_counts():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Movies")
    movie_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Videos")
    video_count = cur.fetchone()[0]
    conn.close()
    return movie_count, video_count

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

        try:
            # Insert movie info
            cur.execute('''
                INSERT OR IGNORE INTO Movies (title, year, rotten_tomatoes, box_office)
                VALUES (?, ?, ?, ?)
            ''', (title, year, rt, bo))
            conn.commit()

            cur.execute("SELECT id FROM Movies WHERE title = ?", (title,))
            movie_id = cur.fetchone()[0]

            # Store all trailers for the movie individually
            trailers = trailers_cache.get(title, [])
            for trailer in trailers:
                video_id = trailer.get("video_id")
                video_title = trailer.get("title", "Untitled Trailer")
                
                # Get view count from video_stats_cache
                view_count = 0
                if video_id in data.get("video_stats_cache", {}):
                    try:
                        view_count = int(data["video_stats_cache"][video_id]["viewCount"])
                    except (KeyError, ValueError, TypeError):
                        view_count = 0

                cur.execute('''
                    INSERT OR IGNORE INTO Videos (movie_id, video_id, title, view_count)
                    VALUES (?, ?, ?, ?)
                ''', (movie_id, video_id, video_title, view_count))
                conn.commit()


            new_count += 1
            print(f"Stored: {title} with {len(trailers)} trailer(s)")

        except Exception as e:
            print(f"Failed for {title}: {e}")

    conn.close()
    movie_total, video_total = get_row_counts()
    print(f"\nInserted {new_count} new movies this run.")
    print(f"Total Movies in DB: {movie_total}")
    print(f"Total Trailers in DB: {video_total}")

if __name__ == "__main__":
    create_tables()
    store_data_from_cache()
