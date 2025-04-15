from select_data import join_movie_video_data

def calculate_stats():
    data = join_movie_video_data()
    total_views = 0
    total_ratings = 0
    count_rating = 0

    for _, rt, _, views in data:
        if views:
            total_views += views
        if rt:
            total_ratings += rt
            count_rating += 1

    avg_rt = total_ratings / count_rating if count_rating else 0
    return {
        "total_views": total_views,
        "average_rt": round(avg_rt, 2)
    }

if __name__ == "__main__":
    stats = calculate_stats()
    print(f"Total Views: {stats['total_views']}")
    print(f"Average Rotten Tomatoes Rating: {stats['average_rt']}")
