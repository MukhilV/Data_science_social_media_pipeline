
from flask import Blueprint, render_template
from app.queries import queries_4chan, database_urls, queries_reddit_before_nov17, queries_reddit_after_nov17
from app.utils import get_data_from_DB, mergeData

inter_platform_bp = Blueprint("inter_platform", __name__)

# Inter platform Routes
@inter_platform_bp.route('/posts_per_day')
def inter_platform_posts_per_day():
    # Query data from Reddit
    data_reddit1 = get_data_from_DB(queries_reddit_before_nov17["posts_per_day"], database_urls["reddit"])
    data_reddit2 = get_data_from_DB(queries_reddit_after_nov17["posts_per_day"], database_urls["reddit"])
    data_reddit = mergeData(data_reddit1, data_reddit2)
    data_reddit = [{"date": row[0].isoformat(), "count": row[1]} for row in data_reddit]

    # Query data from 4chan
    chan_data = get_data_from_DB(queries_4chan["posts_per_day"], database_urls["4chan"])
    chan_data = [{"date": row[0].isoformat(), "count": row[1]} for row in chan_data]

    # Send both datasets to the template
    return render_template("inter_platform/posts_per_day.html", 
                           data_reddit=data_reddit, 
                           chan_data=chan_data, 
                           title="Posts per day in Reddit and 4chan")


# Inter platform Routes
@inter_platform_bp.route('/posts_per_day_pol')
def inter_platform_posts_per_day_pol():
    # Query data from Reddit
    data_reddit1 = get_data_from_DB(queries_reddit_before_nov17["posts_per_day_pol"], database_urls["reddit"])
    data_reddit2 = get_data_from_DB(queries_reddit_after_nov17["posts_per_day_pol"], database_urls["reddit"])
    data_reddit = mergeData(data_reddit1, data_reddit2)
    data_reddit = [{"date": row[0].isoformat(), "count": row[1]} for row in data_reddit]

    # Query data from 4chan
    chan_data = get_data_from_DB(queries_4chan["posts_per_day_pol"], database_urls["4chan"])
    chan_data = [{"date": row[0].isoformat(), "count": row[1]} for row in chan_data]

    # Send both datasets to the template
    return render_template("inter_platform/posts_per_day_pol.html", 
                           data_reddit=data_reddit, 
                           chan_data=chan_data, 
                           title="Posts per day in politics board and subreddit")

@inter_platform_bp.route("/toxicity_by_platform")
def inter_toxic_class_dist():
    data_reddit1 = get_data_from_DB(queries_reddit_before_nov17["toxic_class_dist"], database_urls["reddit"])
    data_reddit2 = get_data_from_DB(queries_reddit_after_nov17["toxic_class_dist"], database_urls["reddit"])
    data_reddit = mergeData(data_reddit1, data_reddit2)
    chan_data = get_data_from_DB(queries_4chan["toxic_class_dist"], database_urls["4chan"])
    return render_template("inter_platform/toxicity_by_platform.html", 
                           data_reddit=data_reddit, 
                           chan_data=chan_data, 
                           title="Toxicity by platform")
