# imports
import reddit_data.models
import datetime
from python_utilities.database.database_helper_factory import Database_Helper_Factory

# initialize database
#db_host = "localhost"
#db_port = 3306
#db_username = ""
#db_password = ""
#db_database = ""

#reddit_data.models.Subreddit_Time_Series_Data.db_initialize( Database_Helper_Factory.DATABASE_TYPE_MYSQLDB, db_host, db_port, db_username, db_password, db_database )
reddit_data.models.Subreddit_Time_Series_Data.db_initialize( Database_Helper_Factory.DATABASE_TYPE_PSYCOPG2, db_host, db_port, db_username, db_password, db_database )

#--------------------------------------------------------------------------------
# setup, independent of particular time period
#--------------------------------------------------------------------------------

# boston_date
boston_date = datetime.datetime( 2013, 4, 15, 18, 49, 0 )

# 14 day time period create 14-day timedelta
td_14_days = datetime.timedelta( days = 14 )

# time-series interval is 1 hour - 1-hour interval
time_series_interval = datetime.timedelta( hours = 1 )

# time-period type: description of time interval, documentation for someone
#    just looking at data file.
time_period_type = reddit_data.models.Subreddit_Time_Series_Data.TIME_PERIOD_HOURLY

#--------------------------------------------------------------------------------
# set up date range in which we want to gather data.
#--------------------------------------------------------------------------------

# before

# to start, go from 14 days before Boston to boston.
start_date = boston_date - td_14_days

# end date - all time periods up to the bombing
end_date = boston_date

# OR, to test, set end date to 2 hours after start date.
#end_date = start_date + time_series_interval

# time-period label: another place to document different parts of time-series
#    data - in this case, will use to divide between before and after.
time_period_label = "before"

# aggregate counter start: you can tell the program to start its time period
#    counter at other than 0, so you can have a continuous counter even if you
#    break this processing into multiple stages (if, say, you want "before" and
#    "after", but want the counter to be continuous across before and after).
aggregate_counter_start = 0

# call make_data.
reddit_data.models.Subreddit_Time_Series_Data.make_data( start_date, end_date, time_series_interval, time_period_type, time_period_label, aggregate_counter_start, output_details_IN = True )

# if you are creating data from scratch, to make this run faster, pass flag to
#    not update existing:
#reddit_data.models.Subreddit_Time_Series_Data.make_data( start_date, end_date, time_series_interval, time_period_type, time_period_label, aggregate_counter_start, update_existing_IN = False, output_details_IN = True )

#--------------------------------------------------------------------------------
# now after.
#--------------------------------------------------------------------------------

start_date = boston_date
end_date = boston_date + td_14_days
time_period_label = "after"
aggregate_counter_start = 337
reddit_data.models.Subreddit_Time_Series_Data.make_data( start_date, end_date, time_series_interval, time_period_type, time_period_label, aggregate_counter_start, output_details_IN = True )

'''
# if there is an error, you can start in the middle, too...
#start_date = boston_date
start_date = datetime.datetime( 2013, 4, 16, 4, 49, 0 )
end_date = boston_date + td_14_days
time_period_label = "after"
aggregate_counter_start = 347
start_index = 11

# add start index (counter_start_IN)
reddit_data.models.Subreddit_Time_Series_Data.make_data( start_date, end_date, time_series_interval, time_period_type, time_period_label, aggregate_counter_start, output_details_IN = True, counter_start_IN = start_index )
'''

# close the database
reddit_data.models.Subreddit_Time_Series_Data.db_close()