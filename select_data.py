import sqlite3
import os

DB_NAME = "movies_data.db"

def join_movie_video_data():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        SELECT M.title, M.rotten_tomatoes, M.box_office, V.view_count
        FROM Movies M
        JOIN Videos V ON M.id = V.movie_id
    ''')
    results = cur.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    data = join_movie_video_data()
    for row in data:
        print(row)
