# imports
import reddit_data.models
import datetime

# initialize database
#db_host = "localhost"
#db_port = 3306
#db_username = ""
#db_password = ""
#db_database = ""

reddit_data.models.Domain_Time_Series_Data.db_initialize_mysql( db_host, db_port, db_username, db_password, db_database )

# set up date range in which we want to gather data.
boston_date = datetime.datetime( 2013, 4, 15, 18, 49, 0 )

# create 14-day timedelta
td_14_days = datetime.timedelta( days = 14 )

# to start, go from 14 days before Boston to boston.
start_date = boston_date - td_14_days

# time-series interval is 1 hour
time_series_interval = datetime.timedelta( hours = 1 )

# end date - all time periods up to the bombing
end_date = boston_date

# OR, to test, set end date to 2 hours after start date.
#end_date = start_date + time_series_interval
#end_date = end_date + time_series_interval

# time-period type: description of time interval, documentation for someone
#    just looking at data file.
time_period_type = reddit_data.models.Domain_Time_Series_Data.TIME_PERIOD_HOURLY

# time-period label: another place to document different parts of time-series
#    data - in this case, will use to divide between before and after.
time_period_label = "before"

# aggregate counter start: you can tell the program to start its time period
#    counter at other than 0, so you can have a continuous counter even if you
#    break this processing into multiple stages (if, say, you want "before" and
#    "after", but want the counter to be continuous across before and after).
aggregate_counter_start = 0

# call make_data.
reddit_data.models.Domain_Time_Series_Data.make_data( start_date, end_date, time_series_interval, time_period_type, time_period_label, aggregate_counter_start )

# now after.
start_date = boston_date
end_date = boston_date + td_14_days
time_period_label = "after"
aggregate_counter_start = 337
reddit_data.models.Domain_Time_Series_Data.make_data( start_date, end_date, time_series_interval, time_period_type, time_period_label, aggregate_counter_start )