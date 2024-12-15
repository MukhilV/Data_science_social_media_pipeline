from dotenv import load_dotenv
load_dotenv()

import os

DATABASE_URL_4CHAN = os.environ.get("DATABASE_URL_4CHAN")
DATABASE_URL_REDDIT = os.environ.get("DATABASE_URL_REDDIT")



# Database connection strings
database_urls = {
    "reddit": DATABASE_URL_REDDIT,
    "4chan": DATABASE_URL_4CHAN
}


queries_4chan = {
    'posts_per_day': """
        SELECT 
            to_timestamp((data->>'time')::BIGINT) :: DATE AS date,
            COUNT(*) AS count
        FROM 
            posts
        WHERE
            to_timestamp((data->>'time')::BIGINT) :: DATE BETWEEN '2024-11-01' AND '2024-12-31'
        GROUP BY 
            date
        ORDER BY 
            date;
        """,

        'posts_per_day_pol': """
        SELECT 
            to_timestamp((data->>'time')::BIGINT) :: DATE AS date,
            COUNT(*) AS count
        FROM 
            posts
        WHERE
            board = 'pol' 
            AND
            to_timestamp((data->>'time')::BIGINT) :: DATE BETWEEN '2024-11-01' AND '2024-12-31'
        GROUP BY 
            date
        ORDER BY 
            date;
        """,

        'engagement_vs_toxicity': """select 
            post_number, data->>'replies' as replies_count, toxic_score 
        from 
            posts
        where 
            toxic_class='flag' and data->>'replies' is not NULL 
        order by 
            data->>'replies' desc 
        limit 1000;""",

        'toxic_class_dist':"""select 
            toxic_class, count(*) as count 
        from 
            posts 
        where 
            toxic_class = 'flag' or toxic_class = 'normal'
        group by
            toxic_class;"""

}

queries_reddit_before_nov17 = {
    'posts_per_day': """SELECT DATE(created_at) as date , count(*) as count from posts group by date order by date;""",
    'posts_per_day_pol': """SELECT DATE(created_at) as date , count(*) as count from posts where subreddit='politics' group by date order by date;""",
    'posts_per_subreddit': """SELECT DATE(created_at) as date, subreddit, count(*) as count from posts group by DATE(created_at), subreddit order by date, subreddit;""",
    'toxic_class_dist': """
        select 
            toxic_class, count(*) as count
        from 
            comments 
        where 
            toxic_class = 'flag' or toxic_class = 'normal'
        group by
            toxic_class;
        """
}

queries_reddit_after_nov17 = {
    'posts_per_day': """SELECT DATE(created_at) as date , count(*) as count from posts_from_nov17 group by date order by date;""",
    'posts_per_day_pol': """SELECT DATE(created_at) as date , count(*) as count from posts_from_nov17 where subreddit='politics' group by date order by date;""",
    'posts_per_subreddit': """SELECT DATE(created_at) as date, subreddit, count(*) as count from posts_from_nov17 group by DATE(created_at), subreddit order by date, subreddit;""",
        'toxic_class_dist': """
        select 
            toxic_class, count(*) as count
        from 
            comments_from_nov17th 
        where 
            toxic_class = 'flag' or toxic_class = 'normal'
        group by
            toxic_class;
        """
}