from select_data import join_movie_video_data
from collections import defaultdict

def calculate_stats():
    data = join_movie_video_data()
    
    movie_views = defaultdict(int)
    rt_scores = {}

    for title, rt, _, views in data:
        if views is not None:
            movie_views[title] += views
        if rt is not None and title not in rt_scores:
            rt_scores[title] = rt  # Assume one RT score per movie

    total_views = sum(movie_views.values())
    avg_rt = sum(rt_scores.values()) / len(rt_scores) if rt_scores else 0

    return {
        "total_views": total_views,
        "average_rt": round(avg_rt, 2),
        "views": movie_views
    }

if __name__ == "__main__":
    stats = calculate_stats()
    print(f"Total Views: {stats['total_views']}")
    print(f"Average Rotten Tomatoes Rating: {stats['average_rt']}")
