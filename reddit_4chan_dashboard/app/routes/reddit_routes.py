from flask import Blueprint, render_template
from app.queries import queries_reddit_before_nov17, queries_reddit_after_nov17, database_urls
from app.utils import get_data_from_DB, mergeData, mergeWith3columns  # Add your utility functions here

reddit_bp = Blueprint("reddit", __name__)

# Reddit Routes
@reddit_bp.route("/posts_per_day")
def reddit_posts_per_day():
    data1 = get_data_from_DB(queries_reddit_before_nov17["posts_per_day"], database_urls["reddit"])
    data2 = get_data_from_DB(queries_reddit_after_nov17["posts_per_day"], database_urls["reddit"])
    merged_data_list = mergeData(data1, data2)
    chart_data = [{"date": row[0].isoformat(), "count": row[1]} for row in merged_data_list]
    return render_template("reddit/posts_per_day.html", title="Reddit - Posts Per day ", chart_data=chart_data)

@reddit_bp.route("/posts_per_day_pol")
def reddit_posts_per_day_pol():
    data1 = get_data_from_DB(queries_reddit_before_nov17["posts_per_day_pol"], database_urls["reddit"])
    data2 = get_data_from_DB(queries_reddit_after_nov17["posts_per_day_pol"], database_urls["reddit"])
    merged_data_list = mergeData(data1, data2)
    chart_data = [{"date": row[0].isoformat(), "count": row[1]} for row in merged_data_list]
    return render_template("reddit/posts_per_day_pol.html", title="Reddit - Posts Per day in r/politics", chart_data=chart_data)

@reddit_bp.route("/posts_per_subreddit")
def posts_per_subreddit():
    data1 = get_data_from_DB(queries_reddit_before_nov17["posts_per_subreddit"], database_urls["reddit"])
    data2 = get_data_from_DB(queries_reddit_after_nov17["posts_per_subreddit"], database_urls["reddit"])
    merged_data_list = mergeWith3columns(data1, data2)
    # chart_data = [{"date":row[0], "subreddit": row[1], "count": row[2]} for row in merged_data_list]
    return render_template("reddit/posts_per_subreddit.html", title="Reddit - Posts Per Subreddit", chart_data=merged_data_list)
