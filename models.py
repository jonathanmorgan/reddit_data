from __future__ import unicode_literals

'''
Copyright 2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/reddit_data.

reddit_data is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

reddit_data is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with http://github.com/jonathanmorgan/reddit_data.  If not, see
<http://www.gnu.org/licenses/>.
'''

# imports

# base python
import datetime
import gc

# django
from django.db import models
import django.utils.encoding
from django.utils.encoding import python_2_unicode_compatible

# python_utilities
#from python_utilities.research.time_series_data import AbstractTimeSeriesDataModel
from django_time_series.models import AbstractTimeSeriesDataModel
from python_utilities.database.MySQLdb_helper import MySQLdb_Helper

# reddit_collect
import reddit_collect.models

# Create your models here.

@python_2_unicode_compatible
class Subreddit_Time_Series_Data( AbstractTimeSeriesDataModel ):

    #============================================================================
    # constants-ish
    #============================================================================

    
    # status values
    STATUS_SUCCESS = "Success!"
    STATUS_PREFIX_ERROR = "ERROR - "
    
    # MYSQL strftime date-time format
    MYSQL_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # SQL constants
    SQL_AND = "AND"
    SQL_OR = "OR"
    

    #============================================================================
    # Django model fields from parent.
    #============================================================================
    
    #start_date = models.DateTimeField( null = True, blank = True )
    #end_date = models.DateTimeField( null = True, blank = True )
    #time_period_type = models.CharField( max_length = 255, null = True, blank = True ) # - hourly, by minute, etc.
    #filter_type = models.CharField( max_length = 255, null = True, blank = True ) # - place to keep track of different filter types, if you want.  Example: "text_contains"
    #filter_value = models.CharField( max_length = 255, null = True, blank = True )
    #time_period_label = models.CharField( max_length = 255, null = True, blank = True ) # could give each hour, etc. a separate identifier "start+1", "start+2", etc. - not naming _id to start, so you leave room for this to be a separate table.
    #match_value = models.CharField( max_length = 255, null = True, blank = True )

    subreddit = models.ForeignKey( reddit_collect.models.Subreddit, null = True, blank = True )
    subreddit_name = models.TextField( null = True, blank = True )
    subreddit_reddit_id = models.CharField( max_length = 255, null = True, blank = True, db_index = True )
    post_count = models.IntegerField( null = True, blank = True )
    self_post_count = models.IntegerField( null = True, blank = True )
    over_18_count = models.IntegerField( null = True, blank = True )
    score_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    score_min = models.IntegerField( null = True, blank = True )
    score_max = models.IntegerField( null = True, blank = True )
    upvotes_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    upvotes_min = models.IntegerField( null = True, blank = True )
    upvotes_max = models.IntegerField( null = True, blank = True )
    downvotes_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    downvotes_min = models.IntegerField( null = True, blank = True )
    downvotes_max = models.IntegerField( null = True, blank = True )
    num_comments_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    num_comments_min = models.IntegerField( null = True, blank = True )
    num_comments_max = models.IntegerField( null = True, blank = True )    
    
    #============================================================================
    # class variables (always access via class, not instance).
    #============================================================================


    # database helper.
    my_db_helper = None


    #============================================================================
    # class methods
    #============================================================================


    @classmethod
    def db_initialize_mysql( cls, db_host_IN = "localhost", db_port_IN = 3306, db_username_IN = "", db_password_IN = "", db_database_IN = "" ):
        
        # instance variables
        cls.my_db_helper = MySQLdb_Helper( db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END class method db_initialize_mysql() --#

    
    @classmethod
    def filter_data_on_text( cls,
                     start_dt_IN,
                     end_dt_IN,
                     interval_td_IN,
                     time_period_type_IN = "",
                     time_period_category_IN = "",
                     text_contains_and_IN = [],
                     text_contains_or_IN = [],
                     filter_number_IN = 1,
                     *args,
                     **kwargs ):
    
        '''
        Accepts a start and end datetime, the interval you want captured in time-
           series data in a timedelta instance, and optional string time-period
           type, time period label, and where you want an aggregate counter to
           start counting if other than zero.  This works on existing time-series
           records created with make_data, so for parameters to this method that
           are shared with make_data, you need to set the same values so this
           method can filter your data.  Loops over interval-sized time slices
           from your start datetime to your end datetime, filtering the posts in
           each time slice based on the filter criteria passed in.  For each
           subreddit that matches filter criteria passed in, sets filter flag in
           that sub-reddit's time-series record to True.  Loops until the end
           date of a time slice is greater than the end date you specified.
                    
        Parameters:
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - interval_td_IN - datetime.timedelta instance containing the amount of time you want each time slice to contain.
        - time_period_type_IN - (optional) time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_category_IN - (optional) label to use in labeling.  If set, this is appended to the front of an integer counter that counts up each time period, is stored in time_period_label.  If not set, the integer time period counter is the only thing stored in time period label.
        - text_contains_and_IN = list of text strings you want to search for inside any text field in the post (title, self_text), AND-ed together.
        - text_contains_or_IN = list of text strings you want to search for inside any text field in the post (title, self_text), OR-ed together.
        - filter_number_IN = the parent class has 10 filter booleans - lets you specify which to store the flag for this filter in.  Defaults to 1.
        '''
    
        # return reference
        status_OUT = cls.STATUS_SUCCESS
        
        # declare variables
        me = "filter_data_on_text"
        started_at_dt = None
        ended_at_dt = None
        duration_td = None
        post_query = None
        mysqldb = None
        my_connection = None
        my_read_cursor = None

        # counters.
        time_period_counter = -1
        total_match_count = -1
        total_updated_count = -1
        period_updated_count = -1

        # building SQL.
        filter_sql = ""
        current_start_dt = None
        current_end_dt = None
        current_select_sql = ""
        current_prefix = ""

        # results
        period_match_count = -1
        current_row = None
        current_subreddit_name = ""
        current_subreddit_id = ""
        current_subreddit_post_count = -1

        # updating
        lookup_rs = None
        lookup_count = -1
        current_instance = None
        filter_column_name = ""
        match_count_column_name = ""

        # start time.        
        started_at_dt = datetime.datetime.now()
 
        # make sure we have start date, end date, and interval.
        if ( ( start_dt_IN ) and ( start_dt_IN != None ) ):
        
            if ( ( end_dt_IN ) and ( end_dt_IN != None ) ):
            
                if ( ( interval_td_IN ) and ( interval_td_IN != None ) ):

                    print( "In " + me + "() [" + started_at_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - Category: '" + time_period_category_IN + "'; start dt: " + start_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + end_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; interval: " + str( interval_td_IN ) )

                    # create database connection - get database helper
                    mysqldb = cls.my_db_helper
                    
                    # create connection
                    my_connection = mysqldb.get_connection()
                    
                    # get read and write cursors.
                    my_read_cursor = mysqldb.get_cursor()
                    
                    # loop - go from start_dt_IN to end_dt_IN in increments of
                    #    interval_td_IN.
                    
                    # initialize variables
                    time_period_counter = 0
                    current_start_dt = start_dt_IN
                    current_end_dt = start_dt_IN + interval_td_IN
                    total_match_count = 0
                    total_updated_count = 0
                    
                    # continue as long as the end date is less than or equal to
                    #   the overall end datetime.
                    while ( current_end_dt <= end_dt_IN ):
                    
                        print( "- At top of time period loop [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - start dt: " + current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) )
                    
                        # increment counters
                        time_period_counter += 1
                        period_updated_count = 0
                                                
                        # create SQL
                        current_select_sql = "SELECT subreddit_name"
                        current_select_sql += ", subreddit_reddit_id"
                        current_select_sql += ", COUNT( * ) AS post_count"
                        current_select_sql += " FROM reddit_collect_post"
                        current_select_sql += " WHERE created_utc_dt BETWEEN '"
                        current_select_sql += current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "' AND '"
                        current_select_sql += current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "'"
                        
                        # are we AND-ing any contains?
                        if ( len( text_contains_and_IN ) > 0 ):
                        
                            # we are.  output SQL.
                            filter_sql = cls.sql_text_filter( text_contains_and_IN, cls.SQL_AND )
                            
                            # got anything back?
                            if ( filter_sql != "" ):

                                current_select_sql += " AND ( " + filter_sql + " )"

                            #-- END check to make sure we got something back. --#
                        
                        #-- END check to see if we are AND-ing text
                        
                        # are we OR-ing any contains?
                        if ( len( text_contains_or_IN ) > 0 ):
                        
                            # we are.  output SQL.
                            filter_sql = cls.sql_text_filter( text_contains_or_IN, cls.SQL_OR )
                            
                            # got anything back?
                            if ( filter_sql != "" ):

                                current_select_sql += " AND ( " + filter_sql + " )"

                            #-- END check to make sure we got something back. --#
                        
                        #-- END check to see if we are OR-ing text

                        current_select_sql += " GROUP BY subreddit_name;"
                        
                        print( "SQL: " + current_select_sql )
                        
                        # execute SQL
                        my_read_cursor.execute( current_select_sql )
                        
                        # loop over the results.
                        period_match_count = int( my_read_cursor.rowcount )

                        for i in range( period_match_count ):

                            # get row.
                            current_row = my_read_cursor.fetchone()
                            
                            # get values
                            current_subreddit_name = current_row[ 'subreddit_name' ]
                            current_subreddit_id = current_row[ 'subreddit_reddit_id' ]
                            current_subreddit_post_count = current_row[ 'post_count' ]
                            
                            # look up instance for this time period and subreddit.
                            # !TODO - look up instance, potentially abstract this.
                            lookup_rs = cls.lookup_records( current_subreddit_name, current_subreddit_id, current_start_dt, current_end_dt, time_period_type_IN, time_period_category_IN )
                            
                            # got something?
                            lookup_count = lookup_rs.count()
                            print( "====> In " + me + "() - lookup ( for name: " + current_subreddit_name + "; id: " + current_subreddit_id + "; start date: " + str( current_start_dt ) + "; end date: " + str( current_end_dt ) + "; period type: " + time_period_type_IN + "; period category: " + time_period_category_IN + " ) returned " + str( lookup_count ) + " matches." )
                        
                            if ( lookup_count == 1 ):
                            
                                # get instance.
                                current_instance = lookup_rs[ 0 ]
                                
                                # populate values.  Just set filter and match
                                #    count for filter number passed in.

                                # generate column names
                                filter_column_name = "filter_" + str( filter_number_IN )
                                match_count_column_name = "match_count_" + str( filter_number_IN )

                                # set attributes.
                                setattr( current_instance, filter_column_name, True )
                                setattr( current_instance, match_count_column_name, current_subreddit_post_count )                                
    
                                # try/except around saving.
                                try:
                
                                    # save method.
                                    current_instance.save()
                                    
                                    # increment total count
                                    period_updated_count += 1
        
                                except Exception as e:
                                    
                                    # error saving.  Probably encoding error.
                
                                    # get exception details:
                                    exception_type, exception_value, exception_traceback = sys.exc_info()
                                    print( "====> In " + me + "() - bulk_create() threw exception, processing comments for post " + str( current_post.id ) + " ( reddit ID: " + current_post.reddit_id + " ); count of comments being bulk created = " + str( django_bulk_create_count ) )
                                    print( "      - args = " + str( e.args ) )
                                    print( "      - type = " + str( exception_type ) )
                                    print( "      - value = " + str( exception_value ) )
                                    print( "      - traceback = " + str( exception_traceback ) )
                                    
                                    # send email to let me know this crashed?
                
                                    # throw exception?
                                    raise( e )
                                        
                                #-- END try/except around saving. --#

                            else:
                            
                                # either no matches or more than one.  Either
                                #    way, error.
                                print( "====> In " + me + "() - lookup ( for name: " + current_subreddit_name + "; id: " + current_subreddit_id + "; start date: " + str( current_start_dt ) + "; end date: " + str( current_end_dt ) + "; period type: " + time_period_type_IN + "; period category: " + time_period_category_IN + " ) returned " + str( lookup_count ) + " matches, not 1.  Can't update this row." )
                            
                            #-- END check to see if we can find matching record to update. --#

                        #-- END loop over subreddit data for this time period. --#

                        print( "    - found " + str( period_match_count ) + " matches, updated " + str( period_updated_count ) + " records." )

                        # update total counts.
                        total_match_count += period_match_count
                        total_updated_count += period_updated_count

                        # clear caches, performance stuff, etc.  Try garbage
                        #    collecting, not clearing django cache, to start.
                        gc.collect()
                        django.db.reset_queries()
                        
                        # increment start and end dt.
                        current_start_dt = current_end_dt
                        current_end_dt = current_start_dt + interval_td_IN
                    
                    #-- END loop over increments of time --#

                else:
                
                    status_OUT = cls.STATUS_PREFIX_ERROR + "no interval time-delta passed in, so can't create time-series data."

                #-- END check to make sure we have an interval. --#
                
            else:
            
                # no end date.  Error.
                status_OUT = cls.STATUS_PREFIX_ERROR + "no end date passed in, so can't create time-series data."
            
            #-- END check to see if end date passed in. --#
        
        else:
        
            # no start date.  Error.
            status_OUT = cls.STATUS_PREFIX_ERROR + "no start date passed in, so can't create time-series data."
        
        #-- END check to see if end date passed in. --#

        # output overall summary
        print( "==> Matches found: " + str( total_match_count ) )
        print( "==> Matches updated: " + str( total_updated_count ) )
        print( "==> Filtering started: " + str( started_at_dt ) )

        ended_at_dt = datetime.datetime.now()
        print( "==> Filtering ended: " + str( ended_at_dt ) )
        
        duration_td = ended_at_dt - started_at_dt
        print( "==> Duration: " + str( duration_td ) )

        return status_OUT
    
    #-- END method filter_data() --#


    @classmethod
    def lookup_records( cls,
                        subreddit_name_IN = "",
                        subreddit_reddit_id_IN = "",
                        start_dt_IN = None,
                        end_dt_IN = None,
                        time_period_type_IN = "",
                        time_period_category_IN = "",
                        *args,
                        **kwargs ):

        '''
        Accepts a subreddit name and ID, start and end datetime, time period
           type, and time period label.  Uses these values to filter time-series
           records.  If you are working with existing time-series records
           created with make_data, to make it more likely you'll get matches,
           pass the same values to these parameters that you did when you created
           the data (so same time period type, time period label, start and
           end date of the period).
                    
        Parameters:
        - subreddit_name_IN - name of subreddit we are trying to find time-series record(s) for.
        - subreddit_reddit_id_IN - name of subreddit we are trying to find time-series record(s) for.
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - time_period_type_IN - (optional) time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_category_IN - (optional) category used in labeling.  If set, this was stored in time_period_category, appended to the front of an integer counter that counts up each time period, which was then stored in time_period_label.
        '''
        
        # return reference
        rs_OUT = None
        
        # declare variables.
        
        # start out lookup by using parent to lookup for all shared fields.
        rs_OUT = super( Subreddit_Time_Series_Data, cls ).lookup_records( subreddit_name_IN, subreddit_reddit_id_IN, start_dt_IN, end_dt_IN, time_period_type_IN, time_period_category_IN )
        
        # for each parameter, check for a non-empty value, if present, filter.
        
        # subreddit name
        if ( ( subreddit_name_IN ) and ( subreddit_name_IN != "" ) ):
        
            rs_OUT = rs_OUT.filter( subreddit_name__iexact = subreddit_name_IN )
        
        #-- END check for subreddit name --#
        
        # subreddit reddit ID
        if ( ( subreddit_reddit_id_IN ) and ( subreddit_reddit_id_IN != "" ) ):
        
            rs_OUT = rs_OUT.filter( subreddit_reddit_id__iexact = subreddit_reddit_id_IN )
        
        #-- END check for subreddit reddit ID name --#
        
        return rs_OUT

    #-- END class method lookup_record --#
    

    @classmethod
    def make_data( cls, start_dt_IN, end_dt_IN, interval_td_IN, time_period_type_IN = "", time_period_label_IN = "", aggregate_counter_start_IN = 0, *args, **kwargs ):
    
        '''
        Accepts a start and end datetime, the interval you want captured in time-
           series data in a timedelta instance, and optional string time-period
           type, time period label, and where you want an aggregate counter to
           start counting if other than zero.  Loops over interval-sized time
           slices from your start datetime to your end datetime, calculating
           aggregate information for each subreddit posted to within that time
           period, then saving the time-slice data to the database.  Loops until
           the end date of a time slice is greater than the end date you
           specified.
            
        Parameters:
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - interval_td_IN - datetime.timedelta instance containing the amount of time you want each time slice to contain.
        - time_period_type_IN - time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_label_IN - (optional) label to use in labeling.  If set, this is appended to the front of an integer counter that counts up each time period, is stored in time_period_label.  If not set, the integer time period counter is the only thing stored in time period label.
        - aggregate_counter_start_IN - (optional) value you want aggregate counter to begin at for this set of data.  This lets you track increasing time-series across labels (before - 1 to 366 - and after - 367 and up - for instance).
        '''
    
        # return reference
        status_OUT = cls.STATUS_SUCCESS
        
        # declare variables
        me = "make_data"
        post_query = None
        mysqldb = None
        my_connection = None
        my_read_cursor = None
        time_period_counter = -1
        current_start_dt = None
        current_end_dt = None
        current_select_sql = ""
        result_count = -1
        current_row = None
        current_subreddit_name = ""
        current_subreddit_id = ""
        current_subreddit_post_count = -1
        current_instance = None
        bulk_create_list = None
        bulk_create_count = -1
        total_created_count = -1
        aggregate_counter = -1
        
        # make sure we have start date, end date, and interval.
        if ( ( start_dt_IN ) and ( start_dt_IN != None ) ):
        
            if ( ( end_dt_IN ) and ( end_dt_IN != None ) ):
            
                if ( ( interval_td_IN ) and ( interval_td_IN != None ) ):

                    print( "In " + me + "() [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - Label: '" + time_period_label_IN + "'; start dt: " + start_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + end_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; interval: " + str( interval_td_IN ) )

                    # create database connection - get database helper
                    mysqldb = cls.my_db_helper
                    
                    # create connection
                    my_connection = mysqldb.get_connection()
                    
                    # get read and write cursors.
                    my_read_cursor = mysqldb.get_cursor()
                    
                    # loop - go from start_dt_IN to end_dt_IN in increments of
                    #    interval_td_IN.
                    
                    # initialize variables
                    time_period_counter = 0
                    current_start_dt = start_dt_IN
                    current_end_dt = start_dt_IN + interval_td_IN
                    total_created_count = 0
                    
                    # aggregate counter.
                    aggregate_counter = aggregate_counter_start_IN
                    if ( aggregate_counter > 0 ):
                    
                        # value passed in is starting counter.  Subtract 1 so we
                        #    start with this value once counter is incremented at
                        #    the top of the loop.
                        aggregate_counter -= 1
                    
                    #-- END check to see if aggregate counter set (> 0) --#

                    # continue as long as the end date is less than or equal to
                    #   the overall end datetime.
                    while ( current_end_dt <= end_dt_IN ):
                    
                        print( "- At top of time period loop [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - start dt: " + current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) )
                    
                        # increment counters
                        time_period_counter += 1
                        aggregate_counter += 1
                        
                        # reset save list.
                        bulk_create_list = []
                        
                        # create SQL
                        current_select_sql = "SELECT subreddit_name"
                        current_select_sql += ", subreddit_reddit_id"
                        current_select_sql += ", COUNT( * ) AS post_count"
                        current_select_sql += ", SUM( is_self ) AS self_post_count"
                        current_select_sql += ", SUM( over_18 ) AS over_18_count"
                        current_select_sql += ", AVG( score ) AS score_average"
                        current_select_sql += ", MIN( score ) AS score_min"
                        current_select_sql += ", MAX( score ) AS score_max"
                        current_select_sql += ", AVG( upvotes ) AS upvotes_average"
                        current_select_sql += ", MIN( upvotes ) AS upvotes_min"
                        current_select_sql += ", MAX( upvotes ) AS upvotes_max"
                        current_select_sql += ", AVG( downvotes ) AS downvotes_average"
                        current_select_sql += ", MIN( downvotes ) AS downvotes_min"
                        current_select_sql += ", MAX( downvotes ) AS downvotes_max"
                        current_select_sql += ", AVG( num_comments ) AS num_comments_average"
                        current_select_sql += ", MIN( num_comments ) AS num_comments_min"
                        current_select_sql += ", MAX( num_comments ) AS num_comments_max"
                        current_select_sql += " FROM reddit_collect_post"
                        current_select_sql += " WHERE created_utc_dt BETWEEN '"
                        current_select_sql += current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "' AND '"
                        current_select_sql += current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "' GROUP BY subreddit_name;"
                        
                        # execute SQL
                        my_read_cursor.execute( current_select_sql )
                        
                        # loop over the results, creating a new instance of this
                        #    class for each.
                        result_count = int( my_read_cursor.rowcount )
                        for i in range( result_count ):
                        
                            # get row.
                            current_row = my_read_cursor.fetchone()
                            
                            # get values
                            current_subreddit_name = current_row[ 'subreddit_name' ]
                            current_subreddit_id = current_row[ 'subreddit_reddit_id' ]
                            current_subreddit_post_count = current_row[ 'post_count' ]
                            
                            # create new instance of this class.
                            current_instance = cls()
                            
                            # populate values.
                            current_instance.start_date = current_start_dt
                            current_instance.end_date = current_end_dt
                            current_instance.time_period_type = time_period_type_IN
                            current_instance.time_period_index = time_period_counter
                            current_instance.time_period_category = time_period_label_IN

                            # time period label - starts out with value of time
                            #    period counter.
                            time_period_value = str( time_period_counter )
                            
                            # got a label?
                            if ( ( time_period_label_IN ) and ( time_period_label_IN != "" ) ):
                            
                                # yes - add to the beginning.
                                time_period_value = time_period_label_IN + "-" + time_period_value
                                
                            #-- END check to see if time-period label. --#
                            current_instance.time_period_label = time_period_value
                            
                            current_instance.aggregate_index = aggregate_counter

                            #current_instance.filter_type = "" # - place to keep track of different filter types, if you want.  Example: "text_contains"
                            #current_instance.filter_value = ""
                            #current_instance.match_value = models.CharField( max_length = 255, null = True, blank = True )

                            # current_instance.subreddit = models.ForeignKey( Subreddit, null = True, blank = True )
                            current_instance.original_name = current_subreddit_name
                            current_instance.subreddit_name = current_subreddit_name
                            current_instance.original_id = current_subreddit_id
                            current_instance.subreddit_reddit_id = current_subreddit_id
                            current_instance.post_count = current_subreddit_post_count
                            current_instance.self_post_count = current_row[ 'self_post_count' ]
                            current_instance.over_18_count = current_row[ 'over_18_count' ]
                            current_instance.score_average = current_row[ 'score_average' ]
                            current_instance.score_min = current_row[ 'score_min' ]
                            current_instance.score_max = current_row[ 'score_max' ]
                            current_instance.upvotes_average = current_row[ 'upvotes_average' ]
                            current_instance.upvotes_min = current_row[ 'upvotes_min' ]
                            current_instance.upvotes_max = current_row[ 'upvotes_max' ]
                            current_instance.downvotes_average = current_row[ 'downvotes_average' ]
                            current_instance.downvotes_min = current_row[ 'downvotes_min' ]
                            current_instance.downvotes_max = current_row[ 'downvotes_max' ]
                            current_instance.num_comments_average = current_row[ 'num_comments_average' ]
                            current_instance.num_comments_min = current_row[ 'num_comments_min' ]
                            current_instance.num_comments_max = current_row[ 'num_comments_max' ]    

                            # Add to list of instances to bulk save.
                            bulk_create_list.append( current_instance )                            
                            
                        #-- END loop over subreddit data for this time period. --#
                        
                        # try/except around saving.
                        try:
        
                            # yes.
                            cls.objects.bulk_create( bulk_create_list )
                            
                            # increment total count
                            bulk_create_count = len( bulk_create_list )
                            total_created_count += bulk_create_count

                        except Exception as e:
                            
                            # error saving.  Probably encoding error.
        
                            # get exception details:
                            exception_type, exception_value, exception_traceback = sys.exc_info()
                            print( "====> In " + me + ": bulk_create() threw exception, processing comments for post " + str( current_post.id ) + " ( reddit ID: " + current_post.reddit_id + " ); count of comments being bulk created = " + str( django_bulk_create_count ) )
                            print( "      - args = " + str( e.args ) )
                            print( "      - type = " + str( exception_type ) )
                            print( "      - value = " + str( exception_value ) )
                            print( "      - traceback = " + str( exception_traceback ) )
                            
                            # send email to let me know this crashed?
        
                            # throw exception?
                            raise( e )
                                
                        #-- END try/except around saving. --#
                        
                        # clear caches, performance stuff, etc.  Try garbage
                        #    collecting, not clearing django cache, to start.
                        gc.collect()
                        # django.db.reset_queries()
                        
                        # increment start and end dt.
                        current_start_dt = current_end_dt
                        current_end_dt = current_start_dt + interval_td_IN
                    
                    #-- END loop over increments of time --#

                else:
                
                    status_OUT = cls.STATUS_PREFIX_ERROR + "no interval time-delta passed in, so can't create time-series data."

                #-- END check to make sure we have an interval. --#
                
            else:
            
                # no end date.  Error.
                status_OUT = cls.STATUS_PREFIX_ERROR + "no end date passed in, so can't create time-series data."
            
            #-- END check to see if end date passed in. --#
        
        else:
        
            # no start date.  Error.
            status_OUT = cls.STATUS_PREFIX_ERROR + "no start date passed in, so can't create time-series data."
        
        #-- END check to see if end date passed in. --#

        return status_OUT
    
    #-- END method make_data() --#

    @classmethod
    def sql_text_filter( cls, filter_list_IN = [], and_or_or_IN = SQL_OR, *args, **kwargs ):

        # return reference
        sql_OUT = ""
        
        # declare variables
        current_prefix = ""
        current_filter = ""
        current_filter_lower = ""
        
        # does filter list have something in it?
        if ( len( filter_list_IN ) > 0 ):
        
            # it does.  output SQL.
            current_prefix = ""
            
            # loop over filters.
            for current_filter in filter_list_IN:
            
                # convert to lower case
                current_filter_lower = current_filter.lower()
            
                # add to SQL
                sql_OUT += current_prefix
                sql_OUT += " ("
                sql_OUT += " ( LOWER( title ) LIKE '%" + current_filter_lower + "%' )"
                sql_OUT += " OR ( LOWER( selftext ) LIKE '%" + current_filter_lower + "%' )"
                sql_OUT += " )"
                
                # update the current prefix
                current_prefix = " " + and_or_or_IN

            #-- END loop over filter text --#

        #-- END check to see if filter list have something in it --#
        
        return sql_OUT
    
    #-- END method sql_text_filter() --#

    
    #============================================================================
    # instance methods
    #============================================================================


    def __str__(self):
        
        # return reference
        string_OUT = ""
        
        # id?
        if ( ( self.id ) and ( self.id != None ) and ( self.id > 0 ) ):
        
            string_OUT += str( self.id )
        
        #-- END check to see if id --#
        
        # start date?
        if( self.start_date ):
        
            string_OUT += " - " + str( self.start_date )
        
        #-- END check to see if start_date --#

        # end date?
        if( self.end_date ):
        
            string_OUT += " --> " + str( self.end_date )
        
        #-- END check to see if end_date --#
        
        # label.
        if ( self.time_period_label ):
        
            string_OUT += " - " + self.time_period_label
        
        #-- END check to see if time_period_label --#

        # original ID.
        if ( self.original_id ):
        
            string_OUT += " - ID: " + self.original_id
        
        #-- END check to see if original_id --#

        # original name.
        if ( self.original_name ):
        
            string_OUT += " - Name: " + self.original_name
        
        #-- END check to see if original_name --#

        return string_OUT

    #-- END __str__() method --#


#-- END class SubredditTimeSeriesData --#


@python_2_unicode_compatible
class Domain_Time_Series_Data( AbstractTimeSeriesDataModel ):

    #============================================================================
    # constants-ish
    #============================================================================

    
    # status values
    STATUS_SUCCESS = "Success!"
    STATUS_PREFIX_ERROR = "ERROR - "
    
    # MYSQL strftime date-time format
    MYSQL_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # SQL constants
    SQL_AND = "AND"
    SQL_OR = "OR"
    

    #============================================================================
    # Django model fields from parent.
    #============================================================================
    
    #start_date = models.DateTimeField( null = True, blank = True )
    #end_date = models.DateTimeField( null = True, blank = True )
    #time_period_type = models.CharField( max_length = 255, null = True, blank = True ) # - hourly, by minute, etc.
    #filter_type = models.CharField( max_length = 255, null = True, blank = True ) # - place to keep track of different filter types, if you want.  Example: "text_contains"
    #filter_value = models.CharField( max_length = 255, null = True, blank = True )
    #time_period_label = models.CharField( max_length = 255, null = True, blank = True ) # could give each hour, etc. a separate identifier "start+1", "start+2", etc. - not naming _id to start, so you leave room for this to be a separate table.
    #match_value = models.CharField( max_length = 255, null = True, blank = True )

    domain = models.ForeignKey( reddit_collect.models.Domain, null = True, blank = True )
    domain_name =  models.CharField( max_length = 255, null = True, blank = True, db_index = True )
    domain_long_name = models.TextField( null = True, blank = True )
    post_count = models.IntegerField( null = True, blank = True )
    self_post_count = models.IntegerField( null = True, blank = True )
    over_18_count = models.IntegerField( null = True, blank = True )
    score_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    score_min = models.IntegerField( null = True, blank = True )
    score_max = models.IntegerField( null = True, blank = True )
    upvotes_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    upvotes_min = models.IntegerField( null = True, blank = True )
    upvotes_max = models.IntegerField( null = True, blank = True )
    downvotes_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    downvotes_min = models.IntegerField( null = True, blank = True )
    downvotes_max = models.IntegerField( null = True, blank = True )
    num_comments_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    num_comments_min = models.IntegerField( null = True, blank = True )
    num_comments_max = models.IntegerField( null = True, blank = True )    
    
    #============================================================================
    # class variables (always access via class, not instance).
    #============================================================================


    # database helper.
    my_db_helper = None


    #============================================================================
    # class methods
    #============================================================================


    @classmethod
    def db_initialize_mysql( cls, db_host_IN = "localhost", db_port_IN = 3306, db_username_IN = "", db_password_IN = "", db_database_IN = "" ):
        
        # instance variables
        cls.my_db_helper = MySQLdb_Helper( db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END class method db_initialize_mysql() --#

    
    @classmethod
    def filter_data_on_text( cls,
                     start_dt_IN,
                     end_dt_IN,
                     interval_td_IN,
                     time_period_type_IN = "",
                     time_period_category_IN = "",
                     text_contains_and_IN = [],
                     text_contains_or_IN = [],
                     filter_number_IN = 1,
                     *args,
                     **kwargs ):
    
        '''
        Accepts a start and end datetime, the interval you want captured in time-
           series data in a timedelta instance, and optional string time-period
           type, time period label, and where you want an aggregate counter to
           start counting if other than zero.  This works on existing time-series
           records created with make_data, so for parameters to this method that
           are shared with make_data, you need to set the same values so this
           method can filter your data.  Loops over interval-sized time slices
           from your start datetime to your end datetime, filtering the posts in
           each time slice based on the filter criteria passed in.  For each
           subreddit that matches filter criteria passed in, sets filter flag in
           that sub-reddit's time-series record to True.  Loops until the end
           date of a time slice is greater than the end date you specified.
                    
        Parameters:
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - interval_td_IN - datetime.timedelta instance containing the amount of time you want each time slice to contain.
        - time_period_type_IN - (optional) time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_category_IN - (optional) label to use in labeling.  If set, this is appended to the front of an integer counter that counts up each time period, is stored in time_period_label.  If not set, the integer time period counter is the only thing stored in time period label.
        - text_contains_and_IN = list of text strings you want to search for inside any text field in the post (title, self_text), AND-ed together.
        - text_contains_or_IN = list of text strings you want to search for inside any text field in the post (title, self_text), OR-ed together.
        - filter_number_IN = the parent class has 10 filter booleans - lets you specify which to store the flag for this filter in.  Defaults to 1.
        '''
    
        # return reference
        status_OUT = cls.STATUS_SUCCESS
        
        # declare variables
        me = "filter_data_on_text"
        started_at_dt = None
        ended_at_dt = None
        duration_td = None
        post_query = None
        mysqldb = None
        my_connection = None
        my_read_cursor = None

        # counters.
        time_period_counter = -1
        total_match_count = -1
        total_updated_count = -1
        period_updated_count = -1

        # building SQL.
        filter_sql = ""
        current_start_dt = None
        current_end_dt = None
        current_select_sql = ""
        current_prefix = ""

        # results
        period_match_count = -1
        current_row = None
        current_domain_name = ""
        current_post_count = -1

        # updating
        lookup_rs = None
        lookup_count = -1
        current_instance = None
        filter_column_name = ""
        match_count_column_name = ""

        # start time.        
        started_at_dt = datetime.datetime.now()
 
        # make sure we have start date, end date, and interval.
        if ( ( start_dt_IN ) and ( start_dt_IN != None ) ):
        
            if ( ( end_dt_IN ) and ( end_dt_IN != None ) ):
            
                if ( ( interval_td_IN ) and ( interval_td_IN != None ) ):

                    print( "In " + me + "() [" + started_at_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - Category: '" + time_period_category_IN + "'; start dt: " + start_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + end_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; interval: " + str( interval_td_IN ) )

                    # create database connection - get database helper
                    mysqldb = cls.my_db_helper
                    
                    # create connection
                    my_connection = mysqldb.get_connection()
                    
                    # get read and write cursors.
                    my_read_cursor = mysqldb.get_cursor()
                    
                    # loop - go from start_dt_IN to end_dt_IN in increments of
                    #    interval_td_IN.
                    
                    # initialize variables
                    time_period_counter = 0
                    current_start_dt = start_dt_IN
                    current_end_dt = start_dt_IN + interval_td_IN
                    total_match_count = 0
                    total_updated_count = 0
                    
                    # continue as long as the end date is less than or equal to
                    #   the overall end datetime.
                    while ( current_end_dt <= end_dt_IN ):
                    
                        print( "- At top of time period loop [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - start dt: " + current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) )
                    
                        # increment counters
                        time_period_counter += 1
                        period_updated_count = 0
                                                
                        # create SQL
                        current_select_sql = "SELECT domain_name"
                        current_select_sql += ", COUNT( * ) AS post_count"
                        current_select_sql += " FROM reddit_collect_post"
                        current_select_sql += " WHERE created_utc_dt BETWEEN '"
                        current_select_sql += current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "' AND '"
                        current_select_sql += current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "'"
                        
                        # are we AND-ing any contains?
                        if ( len( text_contains_and_IN ) > 0 ):
                        
                            # we are.  output SQL.
                            filter_sql = cls.sql_text_filter( text_contains_and_IN, cls.SQL_AND )
                            
                            # got anything back?
                            if ( filter_sql != "" ):

                                current_select_sql += " AND ( " + filter_sql + " )"

                            #-- END check to make sure we got something back. --#
                        
                        #-- END check to see if we are AND-ing text
                        
                        # are we OR-ing any contains?
                        if ( len( text_contains_or_IN ) > 0 ):
                        
                            # we are.  output SQL.
                            filter_sql = cls.sql_text_filter( text_contains_or_IN, cls.SQL_OR )
                            
                            # got anything back?
                            if ( filter_sql != "" ):

                                current_select_sql += " AND ( " + filter_sql + " )"

                            #-- END check to make sure we got something back. --#
                        
                        #-- END check to see if we are OR-ing text

                        current_select_sql += " GROUP BY domain_name;"
                        
                        print( "SQL: " + current_select_sql )
                        
                        # execute SQL
                        my_read_cursor.execute( current_select_sql )
                        
                        # loop over the results.
                        period_match_count = int( my_read_cursor.rowcount )

                        for i in range( period_match_count ):

                            # get row.
                            current_row = my_read_cursor.fetchone()
                            
                            # get values
                            current_domain_name = current_row[ 'domain_name' ]
                            current_post_count = current_row[ 'post_count' ]
                            
                            # look up instance for this time period and subreddit.
                            # !TODO - look up instance, potentially abstract this.
                            lookup_rs = cls.lookup_records( current_domain_name, "", current_start_dt, current_end_dt, time_period_type_IN, time_period_category_IN )
                            
                            # got something?
                            lookup_count = lookup_rs.count()
                            print( "====> In " + me + "() - lookup ( for name: " + current_domain_name + "; start date: " + str( current_start_dt ) + "; end date: " + str( current_end_dt ) + "; period type: " + time_period_type_IN + "; period category: " + time_period_category_IN + " ) returned " + str( lookup_count ) + " matches." )
                        
                            if ( lookup_count == 1 ):
                            
                                # get instance.
                                current_instance = lookup_rs[ 0 ]
                                
                                # populate values.  Just set filter and match
                                #    count for filter number passed in.

                                # generate column names
                                filter_column_name = "filter_" + str( filter_number_IN )
                                match_count_column_name = "match_count_" + str( filter_number_IN )

                                # set attributes.
                                setattr( current_instance, filter_column_name, True )
                                setattr( current_instance, match_count_column_name, current_post_count )                                
    
                                # try/except around saving.
                                try:
                
                                    # save method.
                                    current_instance.save()
                                    
                                    # increment total count
                                    period_updated_count += 1
        
                                except Exception as e:
                                    
                                    # error saving.  Probably encoding error.
                
                                    # get exception details:
                                    exception_type, exception_value, exception_traceback = sys.exc_info()
                                    print( "====> In " + me + "() - bulk_create() threw exception, processing comments for post " + str( current_post.id ) + " ( reddit ID: " + current_post.reddit_id + " ); count of comments being bulk created = " + str( django_bulk_create_count ) )
                                    print( "      - args = " + str( e.args ) )
                                    print( "      - type = " + str( exception_type ) )
                                    print( "      - value = " + str( exception_value ) )
                                    print( "      - traceback = " + str( exception_traceback ) )
                                    
                                    # send email to let me know this crashed?
                
                                    # throw exception?
                                    raise( e )
                                        
                                #-- END try/except around saving. --#

                            else:
                            
                                # either no matches or more than one.  Either
                                #    way, error.
                                print( "====> In " + me + "() - lookup ( for name: " + current_domain_name + "; start date: " + str( current_start_dt ) + "; end date: " + str( current_end_dt ) + "; period type: " + time_period_type_IN + "; period category: " + time_period_category_IN + " ) returned " + str( lookup_count ) + " matches, not 1.  Can't update this row." )
                            
                            #-- END check to see if we can find matching record to update. --#

                        #-- END loop over subreddit data for this time period. --#

                        print( "    - found " + str( period_match_count ) + " matches, updated " + str( period_updated_count ) + " records." )

                        # update total counts.
                        total_match_count += period_match_count
                        total_updated_count += period_updated_count

                        # clear caches, performance stuff, etc.  Try garbage
                        #    collecting, not clearing django cache, to start.
                        gc.collect()
                        django.db.reset_queries()
                        
                        # increment start and end dt.
                        current_start_dt = current_end_dt
                        current_end_dt = current_start_dt + interval_td_IN
                    
                    #-- END loop over increments of time --#

                else:
                
                    status_OUT = cls.STATUS_PREFIX_ERROR + "no interval time-delta passed in, so can't create time-series data."

                #-- END check to make sure we have an interval. --#
                
            else:
            
                # no end date.  Error.
                status_OUT = cls.STATUS_PREFIX_ERROR + "no end date passed in, so can't create time-series data."
            
            #-- END check to see if end date passed in. --#
        
        else:
        
            # no start date.  Error.
            status_OUT = cls.STATUS_PREFIX_ERROR + "no start date passed in, so can't create time-series data."
        
        #-- END check to see if end date passed in. --#

        # output overall summary
        print( "==> Matches found: " + str( total_match_count ) )
        print( "==> Matches updated: " + str( total_updated_count ) )
        print( "==> Filtering started: " + str( started_at_dt ) )

        ended_at_dt = datetime.datetime.now()
        print( "==> Filtering ended: " + str( ended_at_dt ) )
        
        duration_td = ended_at_dt - started_at_dt
        print( "==> Duration: " + str( duration_td ) )

        return status_OUT
    
    #-- END method filter_data() --#


    @classmethod
    def lookup_records( cls,
                        domain_name_IN = "",
                        domain_long_name_IN = "",
                        start_dt_IN = None,
                        end_dt_IN = None,
                        time_period_type_IN = "",
                        time_period_category_IN = "",
                        *args,
                        **kwargs ):

        '''
        Accepts a subreddit name and ID, start and end datetime, time period
           type, and time period label.  Uses these values to filter time-series
           records.  If you are working with existing time-series records
           created with make_data, to make it more likely you'll get matches,
           pass the same values to these parameters that you did when you created
           the data (so same time period type, time period label, start and
           end date of the period).
                    
        Parameters:
        - domain_name_IN - name of domain we are trying to find time-series record(s) for.
        - domain_long_name_IN - long-name of domain we are trying to find time-series record(s) for.
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - time_period_type_IN - (optional) time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_category_IN - (optional) category used in labeling.  If set, this was stored in time_period_category, appended to the front of an integer counter that counts up each time period, which was then stored in time_period_label.
        '''
        
        # return reference
        rs_OUT = None
        
        # declare variables.
        
        # start out lookup by using parent to lookup for all shared fields.
        rs_OUT = super( Domain_Time_Series_Data, cls ).lookup_records( domain_name_IN, "", start_dt_IN, end_dt_IN, time_period_type_IN, time_period_category_IN )
        
        # for each parameter, check for a non-empty value, if present, filter.
        
        # subreddit name
        if ( ( domain_name_IN ) and ( domain_name_IN != "" ) ):
        
            rs_OUT = rs_OUT.filter( domain_name__iexact = domain_name_IN )
        
        #-- END check for domain name --#
        
        # subreddit reddit ID
        if ( ( domain_long_name_IN ) and ( domain_long_name_IN != "" ) ):
        
            rs_OUT = rs_OUT.filter( domain_long_name_IN__iexact = domain_long_name_IN )
        
        #-- END check for domain long name --#
        
        return rs_OUT

    #-- END class method lookup_record --#
    

    @classmethod
    def make_data( cls, start_dt_IN, end_dt_IN, interval_td_IN, time_period_type_IN = "", time_period_label_IN = "", aggregate_counter_start_IN = 0, *args, **kwargs ):
    
        '''
        Accepts a start and end datetime, the interval you want captured in time-
           series data in a timedelta instance, and optional string time-period
           type, time period label, and where you want an aggregate counter to
           start counting if other than zero.  Loops over interval-sized time
           slices from your start datetime to your end datetime, calculating
           aggregate information for each subreddit posted to within that time
           period, then saving the time-slice data to the database.  Loops until
           the end date of a time slice is greater than the end date you
           specified.
            
        Parameters:
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - interval_td_IN - datetime.timedelta instance containing the amount of time you want each time slice to contain.
        - time_period_type_IN - time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_label_IN - (optional) label to use in labeling.  If set, this is appended to the front of an integer counter that counts up each time period, is stored in time_period_label.  If not set, the integer time period counter is the only thing stored in time period label.
        - aggregate_counter_start_IN - (optional) value you want aggregate counter to begin at for this set of data.  This lets you track increasing time-series across labels (before - 1 to 366 - and after - 367 and up - for instance).
        '''
    
        # return reference
        status_OUT = cls.STATUS_SUCCESS
        
        # declare variables
        me = "make_data"
        post_query = None
        mysqldb = None
        my_connection = None
        my_read_cursor = None
        time_period_counter = -1
        current_start_dt = None
        current_end_dt = None
        current_select_sql = ""
        result_count = -1
        current_row = None
        current_subreddit_name = ""
        current_subreddit_id = ""
        current_subreddit_post_count = -1
        current_instance = None
        bulk_create_list = None
        bulk_create_count = -1
        total_created_count = -1
        aggregate_counter = -1
        
        # make sure we have start date, end date, and interval.
        if ( ( start_dt_IN ) and ( start_dt_IN != None ) ):
        
            if ( ( end_dt_IN ) and ( end_dt_IN != None ) ):
            
                if ( ( interval_td_IN ) and ( interval_td_IN != None ) ):

                    print( "In " + me + "() [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - Label: '" + time_period_label_IN + "'; start dt: " + start_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + end_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; interval: " + str( interval_td_IN ) )

                    # create database connection - get database helper
                    mysqldb = cls.my_db_helper
                    
                    # create connection
                    my_connection = mysqldb.get_connection()
                    
                    # get read and write cursors.
                    my_read_cursor = mysqldb.get_cursor()
                    
                    # loop - go from start_dt_IN to end_dt_IN in increments of
                    #    interval_td_IN.
                    
                    # initialize variables
                    time_period_counter = 0
                    current_start_dt = start_dt_IN
                    current_end_dt = start_dt_IN + interval_td_IN
                    total_created_count = 0
                    
                    # aggregate counter.
                    aggregate_counter = aggregate_counter_start_IN
                    if ( aggregate_counter > 0 ):
                    
                        # value passed in is starting counter.  Subtract 1 so we
                        #    start with this value once counter is incremented at
                        #    the top of the loop.
                        aggregate_counter -= 1
                    
                    #-- END check to see if aggregate counter set (> 0) --#

                    # continue as long as the end date is less than or equal to
                    #   the overall end datetime.
                    while ( current_end_dt <= end_dt_IN ):
                    
                        print( "- At top of time period loop [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - start dt: " + current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) )
                    
                        # increment counters
                        time_period_counter += 1
                        aggregate_counter += 1
                        
                        # reset save list.
                        bulk_create_list = []
                        
                        # create SQL
                        current_select_sql = "SELECT domain_name"
                        current_select_sql += ", COUNT( * ) AS post_count"
                        current_select_sql += ", SUM( is_self ) AS self_post_count"
                        current_select_sql += ", SUM( over_18 ) AS over_18_count"
                        current_select_sql += ", AVG( score ) AS score_average"
                        current_select_sql += ", MIN( score ) AS score_min"
                        current_select_sql += ", MAX( score ) AS score_max"
                        current_select_sql += ", AVG( upvotes ) AS upvotes_average"
                        current_select_sql += ", MIN( upvotes ) AS upvotes_min"
                        current_select_sql += ", MAX( upvotes ) AS upvotes_max"
                        current_select_sql += ", AVG( downvotes ) AS downvotes_average"
                        current_select_sql += ", MIN( downvotes ) AS downvotes_min"
                        current_select_sql += ", MAX( downvotes ) AS downvotes_max"
                        current_select_sql += ", AVG( num_comments ) AS num_comments_average"
                        current_select_sql += ", MIN( num_comments ) AS num_comments_min"
                        current_select_sql += ", MAX( num_comments ) AS num_comments_max"
                        current_select_sql += " FROM reddit_collect_post"
                        current_select_sql += " WHERE created_utc_dt BETWEEN '"
                        current_select_sql += current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "' AND '"
                        current_select_sql += current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "' GROUP BY domain_name;"
                        
                        # execute SQL
                        my_read_cursor.execute( current_select_sql )
                        
                        # loop over the results, creating a new instance of this
                        #    class for each.
                        result_count = int( my_read_cursor.rowcount )
                        for i in range( result_count ):
                        
                            # get row.
                            current_row = my_read_cursor.fetchone()
                            
                            # get values
                            current_name = current_row[ 'domain_name' ]
                            current_post_count = current_row[ 'post_count' ]
                            
                            # create new instance of this class.
                            current_instance = cls()
                            
                            # populate values.
                            current_instance.start_date = current_start_dt
                            current_instance.end_date = current_end_dt
                            current_instance.time_period_type = time_period_type_IN
                            current_instance.time_period_index = time_period_counter
                            current_instance.time_period_category = time_period_label_IN

                            # time period label - starts out with value of time
                            #    period counter.
                            time_period_value = str( time_period_counter )
                            
                            # got a label?
                            if ( ( time_period_label_IN ) and ( time_period_label_IN != "" ) ):
                            
                                # yes - add to the beginning.
                                time_period_value = time_period_label_IN + "-" + time_period_value
                                
                            #-- END check to see if time-period label. --#
                            current_instance.time_period_label = time_period_value
                            
                            current_instance.aggregate_index = aggregate_counter

                            #current_instance.filter_type = "" # - place to keep track of different filter types, if you want.  Example: "text_contains"
                            #current_instance.filter_value = ""
                            #current_instance.match_value = models.CharField( max_length = 255, null = True, blank = True )

                            # current_instance.subreddit = models.ForeignKey( Subreddit, null = True, blank = True )
                            current_instance.original_name = current_name
                            current_instance.domain_name = current_name
                            #current_instance.original_id = current_subreddit_id
                            #current_instance.domain_long_name = current_name
                            current_instance.post_count = current_post_count
                            current_instance.self_post_count = current_row[ 'self_post_count' ]
                            current_instance.over_18_count = current_row[ 'over_18_count' ]
                            current_instance.score_average = current_row[ 'score_average' ]
                            current_instance.score_min = current_row[ 'score_min' ]
                            current_instance.score_max = current_row[ 'score_max' ]
                            current_instance.upvotes_average = current_row[ 'upvotes_average' ]
                            current_instance.upvotes_min = current_row[ 'upvotes_min' ]
                            current_instance.upvotes_max = current_row[ 'upvotes_max' ]
                            current_instance.downvotes_average = current_row[ 'downvotes_average' ]
                            current_instance.downvotes_min = current_row[ 'downvotes_min' ]
                            current_instance.downvotes_max = current_row[ 'downvotes_max' ]
                            current_instance.num_comments_average = current_row[ 'num_comments_average' ]
                            current_instance.num_comments_min = current_row[ 'num_comments_min' ]
                            current_instance.num_comments_max = current_row[ 'num_comments_max' ]    

                            # Add to list of instances to bulk save.
                            bulk_create_list.append( current_instance )                            
                            
                        #-- END loop over subreddit data for this time period. --#
                        
                        # try/except around saving.
                        try:
        
                            # yes.
                            cls.objects.bulk_create( bulk_create_list )
                            
                            # increment total count
                            bulk_create_count = len( bulk_create_list )
                            total_created_count += bulk_create_count

                        except Exception as e:
                            
                            # error saving.  Probably encoding error.
        
                            # get exception details:
                            exception_type, exception_value, exception_traceback = sys.exc_info()
                            print( "====> In " + me + ": bulk_create() threw exception, processing comments for post " + str( current_post.id ) + " ( reddit ID: " + current_post.reddit_id + " ); count of comments being bulk created = " + str( django_bulk_create_count ) )
                            print( "      - args = " + str( e.args ) )
                            print( "      - type = " + str( exception_type ) )
                            print( "      - value = " + str( exception_value ) )
                            print( "      - traceback = " + str( exception_traceback ) )
                            
                            # send email to let me know this crashed?
        
                            # throw exception?
                            raise( e )
                                
                        #-- END try/except around saving. --#
                        
                        # clear caches, performance stuff, etc.  Try garbage
                        #    collecting, not clearing django cache, to start.
                        gc.collect()
                        # django.db.reset_queries()
                        
                        # increment start and end dt.
                        current_start_dt = current_end_dt
                        current_end_dt = current_start_dt + interval_td_IN
                    
                    #-- END loop over increments of time --#

                else:
                
                    status_OUT = cls.STATUS_PREFIX_ERROR + "no interval time-delta passed in, so can't create time-series data."

                #-- END check to make sure we have an interval. --#
                
            else:
            
                # no end date.  Error.
                status_OUT = cls.STATUS_PREFIX_ERROR + "no end date passed in, so can't create time-series data."
            
            #-- END check to see if end date passed in. --#
        
        else:
        
            # no start date.  Error.
            status_OUT = cls.STATUS_PREFIX_ERROR + "no start date passed in, so can't create time-series data."
        
        #-- END check to see if end date passed in. --#

        return status_OUT
    
    #-- END method make_data() --#

    @classmethod
    def sql_text_filter( cls, filter_list_IN = [], and_or_or_IN = SQL_OR, *args, **kwargs ):

        # return reference
        sql_OUT = ""
        
        # declare variables
        current_prefix = ""
        current_filter = ""
        current_filter_lower = ""
        
        # does filter list have something in it?
        if ( len( filter_list_IN ) > 0 ):
        
            # it does.  output SQL.
            current_prefix = ""
            
            # loop over filters.
            for current_filter in filter_list_IN:
            
                # convert to lower case
                current_filter_lower = current_filter.lower()
            
                # add to SQL
                sql_OUT += current_prefix
                sql_OUT += " ("
                sql_OUT += " ( LOWER( title ) LIKE '%" + current_filter_lower + "%' )"
                sql_OUT += " OR ( LOWER( selftext ) LIKE '%" + current_filter_lower + "%' )"
                sql_OUT += " )"
                
                # update the current prefix
                current_prefix = " " + and_or_or_IN

            #-- END loop over filter text --#

        #-- END check to see if filter list have something in it --#
        
        return sql_OUT
    
    #-- END method sql_text_filter() --#

    
    #============================================================================
    # instance methods
    #============================================================================


    def __str__(self):
        
        # return reference
        string_OUT = ""
        
        # id?
        if ( ( self.id ) and ( self.id != None ) and ( self.id > 0 ) ):
        
            string_OUT += str( self.id )
        
        #-- END check to see if id --#
        
        # start date?
        if( self.start_date ):
        
            string_OUT += " - " + str( self.start_date )
        
        #-- END check to see if start_date --#

        # end date?
        if( self.end_date ):
        
            string_OUT += " --> " + str( self.end_date )
        
        #-- END check to see if end_date --#
        
        # label.
        if ( self.time_period_label ):
        
            string_OUT += " - " + self.time_period_label
        
        #-- END check to see if time_period_label --#

        # original ID.
        if ( self.original_id ):
        
            string_OUT += " - ID: " + self.original_id
        
        #-- END check to see if original_id --#

        # original name.
        if ( self.original_name ):
        
            string_OUT += " - Name: " + self.original_name
        
        #-- END check to see if original_name --#

        return string_OUT

    #-- END __str__() method --#


#-- END class DomainTimeSeriesData --#