import requests
import json
import os
from googleapiclient.discovery import build
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd

OMDB_KEY = "5ccb08a7"
YOUTUBE_KEY = "AIzaSyCjBMGEMudlG4nra1O-MTM3ePi7WZ7srIs"

CACHE_FILE = "cache.json"

omdb_cache = {}
trailers_cache = {}
video_stats_cache = {}


def load_cache():
    """Load cached data from CACHE_FILE if it exists"""
    global omdb_cache, trailers_cache, video_stats_cache

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                omdb_cache = data.get("omdb_cache", {})
                trailers_cache = data.get("trailers_cache", {})
                video_stats_cache = data.get("video_stats_cache", {})
        except Exception as e:
            print(f"Could not load cache file: {e}")
            omdb_cache = {}
            trailers_cache = {}
            video_stats_cache = {}
    else:
        omdb_cache = {}
        trailers_cache = {}
        video_stats_cache = {}


def save_cache():
    """Save the current caches to CACHE_FILE."""
    data = {
        "omdb_cache": omdb_cache,
        "trailers_cache": trailers_cache,
        "video_stats_cache": video_stats_cache
    }
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Could not save cache file: {e}")


def build_url(movie_title):
    """Construct the OMDB API URL given a movie title."""
    return f"http://www.omdbapi.com/?apikey={OMDB_KEY}&t={movie_title.replace(' ', '+')}"


def get_movie_omdb_data(movie_title):
    """Query OMDB for movie data, including Rotten Tomatoes rating, box office."""
    if movie_title in omdb_cache:
        return omdb_cache[movie_title]

    url = build_url(movie_title)
    try:
        response = requests.get(url)
        movie_data = response.json()

        if movie_data.get("Response") == "False":
            print(f"OMDB could not find: {movie_title}")
            omdb_cache[movie_title] = None
            return None

        rotten_tomatoes_score = None
        for rating_source in movie_data.get("Ratings", []):
            if rating_source['Source'] == 'Rotten Tomatoes':
                rt_str = rating_source['Value'].replace('%', '')
                rotten_tomatoes_score = int(rt_str)
                break

        box_office_str = movie_data.get("BoxOffice", "N/A")
        box_office_val = None
        if box_office_str not in ["N/A", ""]:
            box_office_val = int(box_office_str.replace('$', '').replace(',', ''))

        result = {
            "Title": movie_data.get("Title", movie_title),
            "Year": movie_data.get("Year", None),
            "RottenTomatoes": rotten_tomatoes_score,
            "BoxOffice": box_office_val,
        }

        omdb_cache[movie_title] = result
        return result

    except Exception as e:
        print(f"Error fetching OMDB data for {movie_title}: {e}")
        omdb_cache[movie_title] = None
        return None


def search_trailers(movie_title, max_results=5):
    """
    Search YouTube for up to `max_results` official trailers for the given `movie_title`.
    """
    if movie_title in trailers_cache:
        return trailers_cache[movie_title]

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    query = f"{movie_title} official trailer"

    search_response = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=max_results
    ).execute()

    video_info_list = []
    for item in search_response.get('items', []):
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        channel_title = item['snippet']['channelTitle']
        published_at = item['snippet']['publishedAt']

        video_info_list.append({
            'video_id': video_id,
            'title': title,
            'channel': channel_title,
            'published_at': published_at
        })

    trailers_cache[movie_title] = video_info_list
    return video_info_list


def get_video_stats(video_ids):
    """
    Get statistics (viewCount, likeCount, commentCount) for a list of YouTube video IDs.
    """
    to_fetch = [vid for vid in video_ids if vid not in video_stats_cache]

    if to_fetch:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
        response = youtube.videos().list(
            part="statistics,snippet",
            id=",".join(to_fetch)
        ).execute()

        for item in response.get('items', []):
            video_id = item['id']
            snippet = item.get('snippet', {})
            stats = item.get('statistics', {})
            video_stats_cache[video_id] = {
                'video_id': video_id,
                'title': snippet.get('title', 'N/A'),
                'viewCount': stats.get('viewCount', '0'),
                'likeCount': stats.get('likeCount', '0'),
                'commentCount': stats.get('commentCount', '0'),
            }

        found_ids = {item['id'] for item in response.get('items', [])}
        for missing_id in set(to_fetch) - found_ids:
            video_stats_cache[missing_id] = None

    stats_list = []
    for vid in video_ids:
        cached_stats = video_stats_cache.get(vid)
        if cached_stats:
            stats_list.append(cached_stats)
        else:
            stats_list.append({
                'video_id': vid,
                'title': 'N/A',
                'viewCount': '0',
                'likeCount': '0',
                'commentCount': '0'
            })

    return stats_list


def get_movie_viewcount(movie_title):
    """
    For a given movie title, sum the view counts among the top trailer results.
    """
    trailers = search_trailers(movie_title)
    if not trailers:
        return None

    video_ids = [t['video_id'] for t in trailers]
    stats = get_video_stats(video_ids)

    total_views = 0
    for s in stats:
        try:
            vcount = int(s['viewCount'])
            total_views += vcount
        except ValueError:
            pass

    return total_views if total_views > 0 else None


if __name__ == "__main__":
    load_cache()

    movie_titles = [
        "La La Land", "Moonlight", "Arrival", "Rogue One: A Star Wars Story", "John Wick: Chapter 2", "Get Out",
        "Logan", "Wonder Woman", "Dunkirk", "Black Panther", "Avengers: Infinity War", "A Star Is Born",
        "Bohemian Rhapsody", "Joker", "Parasite", "Knives Out", "1917", "Tenet", "Soul", "Nomadland",
        "Spider-Man: No Way Home", "Dune", "The Batman", "Everything Everywhere All at Once", "Top Gun: Maverick"
    ]

    results = []
    for title in movie_titles:
        omdb_data = get_movie_omdb_data(title)
        if not omdb_data:
            continue

        viewcount = get_movie_viewcount(title)
        if viewcount is not None:
            omdb_data["ViewCount"] = viewcount
            results.append(omdb_data)
        else:
            print(f"No trailer view count for {title}")

    save_cache()

    df = pd.DataFrame(results)
    print("\nCollected Data:")
    print(df)

    # Rotten Tomatoes vs. View Count
    rt_view_df = df.dropna(subset=["RottenTomatoes", "ViewCount"])
    plt.figure(figsize=(8, 5))
    plt.scatter(rt_view_df["RottenTomatoes"], rt_view_df["ViewCount"], color='blue')

    for i, row in rt_view_df.iterrows():
        plt.annotate(
            row["Title"],
            (row["RottenTomatoes"], row["ViewCount"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9
        )

    plt.title("Rotten Tomatoes % vs. Trailer View Count (Summed)")
    plt.xlabel("Rotten Tomatoes Rating (%)")
    plt.ylabel("Total Trailer View Count")
    plt.grid(True)
    plt.show()

    # Box Office vs. View Count
    bo_view_df = df.dropna(subset=["BoxOffice", "ViewCount"])
    plt.figure(figsize=(8, 5))
    plt.scatter(bo_view_df["BoxOffice"], bo_view_df["ViewCount"], color='red')

    for i, row in bo_view_df.iterrows():
        plt.annotate(
            row["Title"],
            (row["BoxOffice"], row["ViewCount"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9
        )

    plt.title("Box Office vs. Trailer View Count (Summed)")
    plt.xlabel("Box Office (USD)")
    plt.ylabel("Total Trailer View Count")
    plt.grid(True)
    plt.show()
