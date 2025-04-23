import csv
from select_data import join_movie_video_data
from calculate_data import calculate_stats

def write_to_csv():
    data = join_movie_video_data()
    stats = calculate_stats()

    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "RottenTomatoes", "BoxOffice", "ViewCount"])
        writer.writerows(data)

        writer.writerow([])

        for movie, views in stats['views'].items():
            writer.writerow([movie, views])

        writer.writerow([])
        writer.writerow(["TOTAL VIEWS", stats['total_views']])
        writer.writerow(["AVERAGE ROTTEN TOMATOES", stats['average_rt']])

if __name__ == "__main__":
    write_to_csv()
    print("Results written to results.csv")
