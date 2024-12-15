from flask import Blueprint, render_template
from app.queries import queries_4chan, database_urls
from app.utils import get_data_from_DB

chan_bp = Blueprint("4chan", __name__)

# 4chan Routes
@chan_bp.route("/posts_per_day")
def chan_posts_per_day():
    data = get_data_from_DB(queries_4chan["posts_per_day"], database_urls["4chan"])
    chart_data = [{"date": row[0].isoformat(), "count": row[1]} for row in data]
    return render_template("4chan/posts_per_day.html", title="4chan - Posts per day", chart_data=chart_data)

@chan_bp.route("/posts_per_day_pol")
def chan_posts_per_day_pol():
    data = get_data_from_DB(queries_4chan["posts_per_day_pol"], database_urls["4chan"])
    chart_data = [{"date": row[0].isoformat(), "count": row[1]} for row in data]
    return render_template("4chan/posts_per_day_pol.html", title="4chan - Posts per day in Politics", chart_data=chart_data)

@chan_bp.route("/engagement_vs_toxicity")
def chan_engagement_vs_toxicity():
    data = get_data_from_DB(queries_4chan["engagement_vs_toxicity"], database_urls["4chan"])
    chart_data = [
        {
            "post_number": row[0],
            "replies_count": int(row[1]),
            "toxic_score": float(row[2])
        } for row in data
    ]
    return render_template("4chan/engagement_vs_toxicity.html", title="4chan - Engagement vs toxicity", chart_data=chart_data)

