# imports
import reddit_data.models
import datetime

start_date = datetime.datetime( 2013, 4, 1, 18, 49, 0 )
end_date = datetime.datetime( 2013, 4, 1, 19, 49, 0 )
time_period_type = reddit_data.models.Subreddit_Time_Series_Data.TIME_PERIOD_HOURLY
time_period_category = "before"
subreddit_name = "boston"
subreddit_reddit_id = "t5_2qh3r"
rs = reddit_data.models.Subreddit_Time_Series_Data.lookup_records( subreddit_name, subreddit_reddit_id, start_date, end_date, time_period_type, time_period_category )