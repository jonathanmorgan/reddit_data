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
import sys

# django
from django.conf import settings
from django.db import models
import django.utils.encoding
from django.utils.encoding import python_2_unicode_compatible

# django_time_series
from django_time_series.models import AbstractTimeSeriesDataModel

# python_utilities
#from python_utilities.research.time_series_data import AbstractTimeSeriesDataModel
from python_utilities.database.database_helper_factory import Database_Helper_Factory
#from python_utilities.database.MySQLdb_helper import MySQLdb_Helper

# reddit_collect
import reddit_collect.models

# Create your models here.

# !TODO abstract parent class, since just about everything is identical between these.

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
    
    # Current database config
    SETTINGS_DATABASES = getattr( settings, "DATABASES", None )
    SETTINGS_DB_ENGINE = SETTINGS_DATABASES[ "default" ][ "ENGINE" ]
    

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
    subreddit_reddit_full_id = models.CharField( max_length = 255, null = True, blank = True, db_index = True )
    post_count = models.IntegerField( null = True, blank = True )
    self_post_count = models.IntegerField( null = True, blank = True )
    over_18_count = models.IntegerField( null = True, blank = True )
    unique_author_count = models.IntegerField( null = True, blank = True )
    score_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    score_min = models.IntegerField( null = True, blank = True )
    score_max = models.IntegerField( null = True, blank = True )
    score_variance = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    upvotes_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    upvotes_min = models.IntegerField( null = True, blank = True )
    upvotes_max = models.IntegerField( null = True, blank = True )
    upvotes_variance = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    downvotes_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    downvotes_min = models.IntegerField( null = True, blank = True )
    downvotes_max = models.IntegerField( null = True, blank = True )
    downvotes_variance = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    num_comments_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    num_comments_min = models.IntegerField( null = True, blank = True )
    num_comments_max = models.IntegerField( null = True, blank = True )    
    num_comments_variance = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    
    #============================================================================
    # class variables (always access via class, not instance).
    #============================================================================


    # database helper.
    my_db_helper = None


    #============================================================================
    # meta class
    #============================================================================
    
    
    '''
    class Meta:
        
        # multi-column indexes
        index_together = [
            [ "start_date", "end_date", "time_period_category", "time_period_type" ],
        ]

    #-- END Meta class --#
    '''
    
    #============================================================================
    # class methods
    #============================================================================


    @classmethod
    def db_close( cls ):
        
        # instance variables
        db_helper = None
        
        # get database helper
        db_helper = cls.my_db_helper
        
        # got anything?
        if ( ( db_helper ) and ( db_helper != None ) ):
        
            # yes.  Close it down.
            db_helper.close()
            
        #-- END check to see if helper is present --#
        
    #-- END method db_close() --#


    @classmethod
    def db_initialize_mysql( cls, db_host_IN = "localhost", db_port_IN = 3306, db_username_IN = "", db_password_IN = "", db_database_IN = "" ):
        
        # instance variables
        cls.db_initialize( Database_Helper_Factory.DATABASE_TYPE_MYSQLDB, db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END method db_initialize_mysql() --#


    @classmethod
    def db_initialize( cls, db_type_IN = "", db_host_IN = "localhost", db_port_IN = -1, db_username_IN = "", db_password_IN = "", db_database_IN = "" ):
        
        # instance variables
        cls.my_db_helper = Database_Helper_Factory.get_database_helper( db_type_IN, db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END method db_initialize() --#


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

        # exception handling
        exception_message = ""
        exception_status = ""

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
                            filter_sql = reddit_collect.models.Post.sql_text_filter( text_contains_and_IN, cls.SQL_AND )
                            
                            # got anything back?
                            if ( filter_sql != "" ):

                                current_select_sql += " AND ( " + filter_sql + " )"

                            #-- END check to make sure we got something back. --#
                        
                        #-- END check to see if we are AND-ing text
                        
                        # are we OR-ing any contains?
                        if ( len( text_contains_or_IN ) > 0 ):
                        
                            # we are.  output SQL.
                            filter_sql = reddit_collect.models.Post.sql_text_filter( text_contains_or_IN, cls.SQL_OR )
                            
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
                                    
                                    # process the exception
                                    exception_message = "ERROR - Exception caught in " + me + "():  save() processing filter for post " + str( current_post.id ) + " ( reddit ID: " + current_post.reddit_id + " )"
                                    exception_status = cls.process_exception( exception_IN = e, message_IN = exception_message, print_details_IN = True )
                                    
                                    # set status to description of exception
                                    status_OUT = exception_status
                
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
                        original_name_IN = "",
                        original_id_IN = "",
                        start_dt_IN = None,
                        end_dt_IN = None,
                        time_period_type_IN = "",
                        time_period_category_IN = "",
                        time_period_index_IN = -1,
                        subreddit_name_IN = "",
                        subreddit_reddit_id_IN = "",
                        subreddit_reddit_full_id_IN = "",
                        *args,
                        **kwargs ):

        '''
        Accepts a subreddit name and ID, start and end datetime, time period
           type, and time period category.  Uses these values to filter
           time-series records.  If you are working with existing time-series 
           records created with make_data, to make it more likely you'll get
           matches, pass the same values to these parameters that you did when
           you created the data (so same time period type, time period category,
           time period index, start and end date of the period, and subreddit
           name or full ID).
                    
        Parameters:
        - subreddit_name_IN - name of subreddit we are trying to find time-series record(s) for.
        - subreddit_reddit_id_IN - ID of subreddit we are trying to find time-series record(s) for (without prefix of "t5_".
        - subreddit_reddit_full_id_IN - full ID of subreddit we are trying to find time-series record(s) for (with prefix "t5_").
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - time_period_type_IN - (optional) time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_category_IN - (optional) category used in labeling.  If set, this was stored in time_period_category, appended to the front of an integer counter that counts up each time period, which was then stored in time_period_label.
        - time_period_index_IN - (optional) index to keep track of time periods within a category.  Generated values are non-zero, so only included in filter if value is greater than 0.
        '''
        
        # return reference
        rs_OUT = None
        
        # declare variables.
        
        # start out lookup by using parent to lookup for all shared fields.
        rs_OUT = super( Subreddit_Time_Series_Data, cls ).lookup_records( original_name_IN = original_name_IN,
                                                                          original_id_IN = original_id_IN,
                                                                          start_dt_IN = start_dt_IN,
                                                                          end_dt_IN = end_dt_IN,
                                                                          time_period_type_IN = time_period_type_IN,
                                                                          time_period_category_IN = time_period_category_IN,
                                                                          time_period_index_IN = time_period_index_IN )
        
        # for each parameter, check for a non-empty value, if present, filter.
        
        # subreddit name
        if ( ( subreddit_name_IN ) and ( subreddit_name_IN != "" ) ):
        
            rs_OUT = rs_OUT.filter( subreddit_name__iexact = subreddit_name_IN )
        
        #-- END check for subreddit name --#
        
        # subreddit reddit ID
        if ( ( subreddit_reddit_id_IN ) and ( subreddit_reddit_id_IN != "" ) ):
        
            rs_OUT = rs_OUT.filter( subreddit_reddit_id__iexact = subreddit_reddit_id_IN )
        
        #-- END check for subreddit reddit ID --#
        
        # subreddit_reddit_full_id_IN
        if ( ( subreddit_reddit_full_id_IN ) and ( subreddit_reddit_full_id_IN != "" ) ):
        
            rs_OUT = rs_OUT.filter( subreddit_reddit_id__iexact = subreddit_reddit_full_id_IN )
        
        #-- END check for subreddit reddit full ID --#
        
        return rs_OUT

    #-- END class method lookup_record --#
    

    @classmethod
    def make_data( cls,
                   start_dt_IN,
                   end_dt_IN,
                   interval_td_IN,
                   time_period_type_IN = "",
                   time_period_category_IN = "",
                   aggregate_counter_start_IN = 0,
                   include_filters_IN = True,
                   update_existing_IN = True,
                   do_batch_insert_IN = True,
                   output_details_IN = False,
                   process_inactive_subreddits_IN = True,
                   counter_start_IN = -1,
                   *args,
                   **kwargs ):
    
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
           
        Preconditions: For this to include all sub-reddits in each time period,
           even those that don't have posts in the time period, need to have
           used the data_creator to populate subreddit database from posts.
           An example of how to do this is in:
           /reddit_data/examples/subreddit_rows_from_posts.py 
            
        Parameters:
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - interval_td_IN - datetime.timedelta instance containing the amount of time you want each time slice to contain.
        - time_period_type_IN - time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_category_IN - (optional) label to use in labeling.  If set, this is appended to the front of an integer counter that counts up each time period, is stored in time_period_label.  If not set, the integer time period counter is the only thing stored in time period label.
        - aggregate_counter_start_IN - (optional) value you want aggregate counter to begin at for this set of data.  This lets you track increasing time-series across labels (before - 1 to 366 - and after - 367 and up - for instance).
        - include_filters_IN - (optional) Boolean - True if you want to use the posts' filter fields to set the time series values, False if you want to set them separately.  Defaults to True.
        - update_existing_IN - (optional) Boolean - True if you want to update existing records.  False if not.  Defaults to True.  If you are running for the first time on an empty database, set to False, and it should run more quickly.
        - do_batch_insert_IN = (optional) Boolean - True if you want to do batch insert, False if you want to save each new record one at a time.  Defaults to True.  If you choose to update existing, will always be False (no way to do a batch update).
        - output_details_IN = (optional) Boolean - True if you want the process to output detailed logging as it runs, False if not.  Defaults to False.
        - process_inactive_subreddits_IN = (optional) Boolean - True if you want to create rows for all subreddits present in your data set for each time period.  False if you want to just create rows for active subreddits.  Defaults to True.  If your data hasn't changed and you just add a few new fields, or if you pulled in comments and just want to update active rows, for example, you can set this to False.
        - counter_start_IN = (optional) integer - Base counter you want to start with.  Used if you have an error and want to start in the middle of a period.  Defaults to starting at one and counting up.
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
        include_filters = True
        result_count = -1
        row_counter = -1
        current_row = None
        current_subreddit_name = ""
        current_subreddit_id = ""
        current_subreddit_full_id = ""
        current_subreddit_post_count = -1
        subreddit_match_rs = None
        current_instance = None
        subreddit_instance = None
        bulk_create_list = None
        bulk_create_count = -1
        total_created_count = -1
        aggregate_counter = -1

        # update control
        update_existing = False
        do_batch_insert = False
        is_row_in_database = False
        do_call_save = False
        
        # exception handling
        exception_helper = None
        exception_message = ""
        exception_status = ""
        
        # database handling
        is_postgres = False
        
        # performance and auditing
        period_found_count = -1
        period_not_found_count = -1
        processed_count = -1
        found_count = -1
        not_found_count = -1
        start_dt = None        
        end_dt = None

        start_dt = datetime.datetime.now()

        # Set control variables from input parameters.
        
        # Include filters?
        include_filters = include_filters_IN
        
        # do batch insert?
        do_batch_insert = do_batch_insert_IN
        
        # update existing?
        update_existing = update_existing_IN
        #if ( ( update_existing ) and ( update_existing != None ) and ( update_existing == True ) ):
        
            # yes - no batch insert.
            #do_batch_insert = False
        
        #-- END check to see if updating existing --#
        
        # is it Postgres?
        if ( "psycopg" in cls.SETTINGS_DB_ENGINE ):
        
            # yes
            is_postgres = True
            
        #-- END check to see if DB ENGINE indicates postgresql --#
        
        # make sure we have start date, end date, and interval.
        if ( ( start_dt_IN ) and ( start_dt_IN != None ) ):
        
            if ( ( end_dt_IN ) and ( end_dt_IN != None ) ):
            
                if ( ( interval_td_IN ) and ( interval_td_IN != None ) ):

                    if ( output_details_IN == True ):

                        print( "In " + me + "() [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - category: '" + time_period_category_IN + "'; start dt: " + start_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + end_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; interval: " + str( interval_td_IN ) + "; filter?: " + str( include_filters ) + "; update?: " + str( update_existing ) + "; batch?: " + str( do_batch_insert ) )

                    #-- END check to see if we should output details --#

                    # create database connection - get database helper
                    mysqldb = cls.my_db_helper
                    
                    # create connection
                    my_connection = mysqldb.get_connection()
                    
                    # get read and write cursors.
                    my_read_cursor = mysqldb.get_cursor()
                    
                    # loop - go from start_dt_IN to end_dt_IN in increments of
                    #    interval_td_IN.
                    
                    # initialize variables
                    current_start_dt = start_dt_IN
                    current_end_dt = start_dt_IN + interval_td_IN
                    total_created_count = 0
                    processed_count = 0
                    found_count = 0
                    not_found_count = 0

                    # time period counter
                    time_period_counter = 0

                    # Got a counter start value passed in?
                    if ( ( counter_start_IN ) and ( counter_start_IN != None ) and ( counter_start_IN > 0 ) ):
                    
                        # we do.  Use it (subtract 1 so we increment to this
                        #    value in first pass through loop).
                        time_period_counter = counter_start_IN - 1
                    
                    #-- END check to see if counter start value passed in --#
                    
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
                    
                        if ( output_details_IN == True ):

                            print( "- At top of time period loop [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - start dt: " + current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) )

                        #-- END check to see if we should output details --#
                    
                        # increment counters
                        time_period_counter += 1
                        aggregate_counter += 1
                                                
                        # reset save list.
                        bulk_create_list = []
                        
                        # create SQL
                        current_select_sql = "SELECT subreddit_name"
                        current_select_sql += ", subreddit_reddit_id"
                        current_select_sql += ", COUNT( * ) AS post_count"
                        current_select_sql += ", COUNT( DISTINCT author_name ) AS unique_author_count"
                        current_select_sql += ", SUM( is_self"

                        # if postgres, cast booleans to int.
                        if ( is_postgres == True ):
                            current_select_sql += "::int"
                        #-- END check to see if postgreSQL

                        current_select_sql += " ) AS self_post_count"
                        current_select_sql += ", SUM( over_18"

                        # if postgres, cast booleans to int.
                        if ( is_postgres == True ):
                            current_select_sql += "::int"
                        #-- END check to see if postgreSQL

                        current_select_sql += " ) AS over_18_count"
                        current_select_sql += ", AVG( score ) AS score_average"
                        current_select_sql += ", MIN( score ) AS score_min"
                        current_select_sql += ", MAX( score ) AS score_max"
                        current_select_sql += ", VAR_SAMP( score ) AS score_variance"
                        current_select_sql += ", AVG( upvotes ) AS upvotes_average"
                        current_select_sql += ", MIN( upvotes ) AS upvotes_min"
                        current_select_sql += ", MAX( upvotes ) AS upvotes_max"
                        current_select_sql += ", VAR_SAMP( upvotes ) AS upvotes_variance"
                        current_select_sql += ", AVG( downvotes ) AS downvotes_average"
                        current_select_sql += ", MIN( downvotes ) AS downvotes_min"
                        current_select_sql += ", MAX( downvotes ) AS downvotes_max"
                        current_select_sql += ", VAR_SAMP( downvotes ) AS downvotes_variance"
                        current_select_sql += ", AVG( num_comments ) AS num_comments_average"
                        current_select_sql += ", MIN( num_comments ) AS num_comments_min"
                        current_select_sql += ", MAX( num_comments ) AS num_comments_max"
                        current_select_sql += ", VAR_SAMP( num_comments ) AS num_comments_variance"

                        # also aggregate filter flags - just MAX, SUM to count matches.
                        if ( include_filters == True ):
                        
                            # yes (for now, we always do).
                            current_select_sql += ", MAX( filter_1"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_1"
                            current_select_sql += ", SUM( filter_1"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_1"
                            current_select_sql += ", MAX( filter_2"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_2"
                            current_select_sql += ", SUM( filter_2"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_2"
                            current_select_sql += ", MAX( filter_3"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_3"
                            current_select_sql += ", SUM( filter_3"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_3"
                            current_select_sql += ", MAX( filter_4"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_4"
                            current_select_sql += ", SUM( filter_4"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_4"
                            current_select_sql += ", MAX( filter_5"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_5"
                            current_select_sql += ", SUM( filter_5"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_5"
                            current_select_sql += ", MAX( filter_6"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_6"
                            current_select_sql += ", SUM( filter_6"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_6"
                            current_select_sql += ", MAX( filter_7"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_7"
                            current_select_sql += ", SUM( filter_7"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_7"
                            current_select_sql += ", MAX( filter_8"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_8"
                            current_select_sql += ", SUM( filter_8"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_8"
                            current_select_sql += ", MAX( filter_9"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_9"
                            current_select_sql += ", SUM( filter_9"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_9"
                            current_select_sql += ", MAX( filter_10"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_10"
                            current_select_sql += ", SUM( filter_10"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_10"
                            
                        #-- END check to see if we include filters --#
                            
                        current_select_sql += " FROM reddit_collect_post"
                        current_select_sql += " WHERE created_utc_dt BETWEEN '"
                        current_select_sql += current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "' AND '"
                        current_select_sql += current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT )
                        current_select_sql += "' GROUP BY subreddit_name, subreddit_reddit_id";
                        current_select_sql += " ORDER BY subreddit_name ASC;"
                        
                        # if outputting details, output SQL
                        if ( output_details_IN == True ):

                            print( "<<< SQL: " + current_select_sql )

                        #-- END check to see if we output details. --#

                        # !execute SQL
                        my_read_cursor.execute( current_select_sql )
                        
                        # !loop over the results, creating a new instance of this
                        #    class for each.
                        result_count = int( my_read_cursor.rowcount )
                        row_counter = 0
                        period_found_count = 0
                        period_not_found_count = 0
                        for i in range( result_count ):
                        
                            # increment counter
                            row_counter += 1
                            
                            # initialize variables
                            do_call_save = False

                            # get row.
                            current_row = my_read_cursor.fetchone()
                            
                            # get values
                            current_subreddit_name = current_row[ 'subreddit_name' ]
                            current_subreddit_id = current_row[ 'subreddit_reddit_id' ]
                            current_subreddit_full_id = current_row[ 'subreddit_reddit_id' ]
                            current_subreddit_post_count = current_row[ 'post_count' ]
                            
                            if ( output_details_IN == True ):
                                print( "In " + me + "() - " + time_period_category_IN + " - " + time_period_type_IN + " - " + str( time_period_counter ) + " ===> row " + str( row_counter ) + " of " + str( result_count ) + " - " + current_subreddit_name + " ( " + current_subreddit_full_id + " ) - Updating? " + str( update_existing ) )                            
                                #print( "====> original_id_IN = " + str( current_subreddit_full_id ) )
                                #print( "====> start_dt_IN = " + str( current_start_dt ) )
                                #print( "====> end_dt_IN = " + str( current_end_dt ) )
                                #print( "====> time_period_type_IN = " + str( time_period_type_IN ) )
                                #print( "====> time_period_category_IN = " + str( time_period_category_IN ) )
                                #print( "====> time_period_index_IN = " + str( time_period_counter ) )
                                #print( "====> update_existing_IN = " + str( update_existing ) )
                            #-- END check to see if output details --#

                            # !get instance of this class
                            current_instance = cls.get_instance( original_id_IN = current_subreddit_full_id,
                                                                 start_dt_IN = current_start_dt,
                                                                 end_dt_IN = current_end_dt,
                                                                 time_period_type_IN = time_period_type_IN,
                                                                 time_period_category_IN = time_period_category_IN,
                                                                 time_period_index_IN = time_period_counter,
                                                                 update_existing_IN = update_existing )
                            
                            # check if row exists already.
                            if ( ( current_instance.pk ) and ( current_instance.pk > 0 ) ):
                            
                                # found.  Increment counter.
                                period_found_count += 1
                                
                                if ( output_details_IN == True ):
                                    print( "In " + me + "() - Found existing row ( id = " + str( current_instance.pk ) + " )." )
                                #-- END check to see if output details --#
                                
                                # set found flag.
                                is_row_in_database = True
                            
                            else:
                            
                                # not found.  Increment counter.
                                period_not_found_count += 1
                            
                                if ( output_details_IN == True ):
                                    print( "In " + me + "() - No existing row found - Updating? " + str( update_existing ) )
                                #-- END check to see if output details --#

                                # set found flag.
                                is_row_in_database = False
                            
                            #-- END check to see if found --#
                            
                            # populate values.
                            current_instance.start_date = current_start_dt
                            current_instance.end_date = current_end_dt
                            current_instance.time_period_type = time_period_type_IN
                            current_instance.time_period_index = time_period_counter
                            current_instance.time_period_category = time_period_category_IN

                            # time period label - starts out with value of time
                            #    period counter.
                            time_period_value = str( time_period_counter )
                            
                            # got a category?
                            if ( ( time_period_category_IN ) and ( time_period_category_IN != "" ) ):
                            
                                # yes - add to the beginning.
                                time_period_value = time_period_category_IN + "-" + time_period_value
                                
                            #-- END check to see if time-period label. --#
                            
                            # got a type?
                            if ( ( time_period_type_IN ) and ( time_period_type_IN != "" ) ):
                            
                                # yes - add to the beginning.
                                time_period_value = time_period_type_IN + "-" + time_period_value                            

                            #-- END check to see if we have a time period type --#
                            
                            current_instance.time_period_label = time_period_value
                            
                            current_instance.aggregate_index = aggregate_counter

                            #current_instance.filter_type = "" # - place to keep track of different filter types, if you want.  Example: "text_contains"
                            #current_instance.filter_value = ""
                            #current_instance.match_value = models.CharField( max_length = 255, null = True, blank = True )

                            # current_instance.subreddit = models.ForeignKey( Subreddit, null = True, blank = True )
                            current_instance.original_name = current_subreddit_name
                            current_instance.subreddit_name = current_subreddit_name
                            current_instance.original_id = current_subreddit_full_id
                            current_instance.subreddit_reddit_id = current_subreddit_id
                            current_instance.subreddit_reddit_full_id = current_subreddit_full_id
                            current_instance.post_count = current_subreddit_post_count
                            current_instance.self_post_count = current_row[ 'self_post_count' ]
                            current_instance.over_18_count = current_row[ 'over_18_count' ]
                            current_instance.unique_author_count = current_row[ 'unique_author_count' ]
                            current_instance.score_average = current_row[ 'score_average' ]
                            current_instance.score_min = current_row[ 'score_min' ]
                            current_instance.score_max = current_row[ 'score_max' ]
                            current_instance.score_variance = current_row[ 'score_variance' ]
                            current_instance.upvotes_average = current_row[ 'upvotes_average' ]
                            current_instance.upvotes_min = current_row[ 'upvotes_min' ]
                            current_instance.upvotes_max = current_row[ 'upvotes_max' ]
                            current_instance.upvotes_variance = current_row[ 'upvotes_variance' ]
                            # print ( "***===+++ - upvotes variance = " + str( current_instance.upvotes_variance ) )
                            current_instance.downvotes_average = current_row[ 'downvotes_average' ]
                            current_instance.downvotes_min = current_row[ 'downvotes_min' ]
                            current_instance.downvotes_max = current_row[ 'downvotes_max' ]
                            current_instance.downvotes_variance = current_row[ 'downvotes_variance' ]
                            current_instance.num_comments_average = current_row[ 'num_comments_average' ]
                            current_instance.num_comments_min = current_row[ 'num_comments_min' ]
                            current_instance.num_comments_max = current_row[ 'num_comments_max' ]
                            current_instance.num_comments_variance = current_row[ 'num_comments_variance' ]

                            # see if there is a subreddit instance for this ID.
                            subreddit_instance = None
                            try:
                            
                                # try to get subreddit instance
                                subreddit_instance = reddit_collect.models.Subreddit.objects.get( reddit_full_id = current_subreddit_full_id )
                                
                            except:
                            
                                # for now, do nothing.
                                subreddit_instance = None
                            
                            #-- END try/except to look up subreddit model instance. --#
                            
                            # got one?
                            if ( ( subreddit_instance ) and ( subreddit_instance != None ) ):
                            
                                # add to current_instance
                                current_instance.subreddit = subreddit_instance
                            
                            #-- END check to see if we have subreddit instance --#

                            # including filters?
                            if ( include_filters == True ):
                                
                                # yes. Set fields from query results.
                                current_instance.filter_1 = current_row[ 'filter_1' ]
                                current_instance.match_count_1 = current_row[ 'match_count_1' ]
                                current_instance.filter_2 = current_row[ 'filter_2' ]
                                current_instance.match_count_2 = current_row[ 'match_count_2' ]
                                current_instance.filter_3 = current_row[ 'filter_3' ]
                                current_instance.match_count_3 = current_row[ 'match_count_3' ]
                                current_instance.filter_4 = current_row[ 'filter_4' ]
                                current_instance.match_count_4 = current_row[ 'match_count_4' ]
                                current_instance.filter_5 = current_row[ 'filter_5' ]
                                current_instance.match_count_5 = current_row[ 'match_count_5' ]
                                current_instance.filter_6 = current_row[ 'filter_6' ]
                                current_instance.match_count_6 = current_row[ 'match_count_6' ]
                                current_instance.filter_7 = current_row[ 'filter_7' ]
                                current_instance.match_count_7 = current_row[ 'match_count_7' ]
                                current_instance.filter_8 = current_row[ 'filter_8' ]
                                current_instance.match_count_8 = current_row[ 'match_count_8' ]
                                current_instance.filter_9 = current_row[ 'filter_9' ]
                                current_instance.match_count_9 = current_row[ 'match_count_9' ]
                                current_instance.filter_10 = current_row[ 'filter_10' ]
                                current_instance.match_count_10 = current_row[ 'match_count_10' ]
                            
                            #-- END check to see if we include filters --#
                            
                            # !save to database.  Is it an update?
                            if ( is_row_in_database == False ):

                                # insert.  Are we batch inserting?
                                if ( do_batch_insert == True ):
                                
                                    # yes - Add to list of instances to bulk save.
                                    bulk_create_list.append( current_instance )
                                    
                                    # bulk.  No need to also call save.
                                    do_call_save = False
                                    
                                else:
                                
                                    # not bulk.  Call save method.
                                    do_call_save = True
                                    
                                #-- END check to see if batch insert. --#
                                
                            # if in database, if also are updating, set save() flag.
                            elif ( ( is_row_in_database == True ) and ( update_existing == True ) ):
                            
                                # not bulk, row is in database and we are
                                #    updating.  Call save method.
                                do_call_save = True

                            else:

                                # for all others (probably existing, but not
                                #    updating), don't save.
                                do_call_save = False
                                
                            #-- END check to see if we need to save or not.
                            
                            # Do we save?
                            if ( do_call_save == True ):

                                # yes.
                                current_instance.save()
                                
                            #-- END check to see if we call save(). --#
                            
                        #-- END loop over subreddit data for this time period. --#
                        
                        # doing batch insert?
                        if ( ( do_batch_insert == True ) and ( len( bulk_create_list ) > 0 ) ):

                            # try/except around saving rows for subreddits with
                            #    posts in our time period.
                            try:
            
                                # yes.
                                cls.objects.bulk_create( bulk_create_list )
                                
                                # increment total count
                                bulk_create_count = len( bulk_create_list )
                                total_created_count += bulk_create_count
    
                            except Exception as e:
                                
                                # error saving.  Probably encoding error.
                                
                                # process the exception
                                exception_message = "ERROR - Exception caught in " + me + ":  bulk_create() threw exception, making time-series data for period - start date: " + current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end date: " + current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; type:" + time_period_type_IN + "; category:" + time_period_category_IN + "; count of rows being bulk created = " + str( len( bulk_create_list ) )
                                exception_status = cls.process_exception( exception_IN = e, message_IN = exception_message, print_details_IN = True )
                                
                                # set status to description of exception
                                status_OUT = exception_status

                                # send email to let me know this crashed?
            
                                # throw exception?
                                raise( e )
                                    
                            #-- END try/except around saving. --#
                            
                        #-- END check to see if we are doing batch insert --#
                        
                        # clear caches, performance stuff, etc.  Try garbage
                        #    collecting, not clearing django cache, to start.
                        gc.collect()
                        # django.db.reset_queries()
                        
                        # do we process inactive subreddits (add missing rows)?
                        #    If you are running for the first time, you need to
                        #    create rows for all subreddits.  If your underlying
                        #    data has changed, you should also probably do this.
                        #    If you know what you are doing and you just want to
                        #    update information for subreddits that are active in
                        #    a given time period, though, set this to False.
                        if ( process_inactive_subreddits_IN == True ):

                            # Time series data needs all subreddits in data set in
                            #    all time periods.  Call function to pull in all
                            #    subreddits not already in our data for this time
                            #    period.
                            cls.make_data_add_missing_rows( start_dt_IN = current_start_dt,
                                                            end_dt_IN = current_end_dt,
                                                            time_period_type_IN = time_period_type_IN,
                                                            time_period_category_IN = time_period_category_IN,
                                                            time_period_index_IN = time_period_counter,
                                                            aggregate_counter_IN = aggregate_counter,
                                                            include_filters_IN = include_filters_IN,
                                                            update_existing_IN = update_existing_IN,
                                                            do_batch_insert_IN = do_batch_insert_IN,
                                                            output_details_IN = output_details_IN )

                        #-- END check to see if we process inactive rows --#

                        # increment start and end dt.
                        current_start_dt = current_end_dt
                        current_end_dt = current_start_dt + interval_td_IN
                    
                        # update the processed counter
                        processed_count += row_counter
                        found_count += period_found_count
                        not_found_count += period_not_found_count
                        
                        # output of time-period information should go here.
                        print( "====> Period Processed: " + str( row_counter ) )
                        print( "====> Period Batch-Inserted: " + str( bulk_create_count ) )
                        print( "====> Period Found: " + str( period_found_count ) )
                        print( "====> Period Not Found: " + str( period_not_found_count ) )
                        
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

        # print details?
        if ( output_details_IN == True ): 

            # a little overview
            end_dt = datetime.datetime.now()
            print( "==> Started at " + str( start_dt ) )
            print( "==> Finished at " + str( end_dt ) )
            print( "==> Duration: " + str( end_dt - start_dt ) )
            print( "==> Total Processed: " + str( processed_count ) )
            print( "==> Total Batch-Inserted: " + str( total_created_count ) )
            print( "==> Total Found: " + str( found_count ) )
            print( "==> Total Not Found: " + str( not_found_count ) )
                        
        #-- END check to see if we print details. --#

        return status_OUT
    
    #-- END method make_data() --#


    @classmethod
    def make_data_add_missing_rows( cls,
                                    start_dt_IN,
                                    end_dt_IN,
                                    time_period_type_IN = "",
                                    time_period_category_IN = "",
                                    time_period_index_IN = -1,
                                    aggregate_counter_IN = -1,
                                    include_filters_IN = True,
                                    update_existing_IN = True,
                                    do_batch_insert_IN = True,
                                    output_details_IN = False,
                                    *args,
                                    **kwargs ):
    
        '''
        Accepts a start and end datetime, an optional string time-period
           category, and the time period identifier/counter.  Uses this
           information to look for subreddits that are in our data set, but that
           did not appear within the time period we are looking at.  For each
           subreddit not present in the current time period, creates a row for
           that subreddit in the time period with all counts set to 0.  
           
        Preconditions: For this to include all sub-reddits in each time period,
           even those that don't have posts in the time period, need to have
           used the data_creator to populate subreddit database from posts.
           An example of how to do this is in:
           /reddit_data/examples/subreddit_rows_from_posts.py
           
        Postconditions: After this routine runs, all subreddits will have a row
           in the time series data for this time period.  Running it again
           should result in no further additions unless more data was added and
           the subreddit table updated.
            
        Parameters:
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - time_period_type_IN - time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_category_IN - label to use in labeling.  If set, this is appended to the front of an integer counter that counts up each time period, is stored in time_period_label.  If not set, the integer time period counter is the only thing stored in time period label.
        - time_period_index_IN - time_period_index value for this time period.
        - aggregate_counter_IN - aggregate counter value for this time period.
        - include_filters_IN - (optional) Boolean - True if you want to use the posts' filter fields to set the time series values, False if you want to set them separately.  Defaults to True.
        - update_existing_IN - (optional) Boolean - True if you want to update existing records.  False if not.  Defaults to True.  If you are running for the first time on an empty database, set to False, and it should run more quickly.
        - do_batch_insert_IN = (optional) Boolean - True if you want to do batch insert, False if you want to save each new record one at a time.  Defaults to True.  If you choose to update existing, defaults to False.
        - output_details_IN = (optional) Boolean - True if you want the process to output detailed logging as it runs, False if not.  Defaults to False.
        '''
    
        # return reference
        status_OUT = cls.STATUS_SUCCESS
        
        # declare variables
        me = "make_data_add_missing_rows"
        post_query = None
        mysqldb = None
        my_connection = None
        my_read_cursor = None
        time_period_counter = -1
        current_select_sql = ""
        include_filters = True
        result_count = -1
        row_counter = -1
        current_row = None
        current_subreddit_pk = -1
        current_subreddit_name = ""
        current_subreddit_id = ""
        current_subreddit_full_id = ""
        current_subreddit_post_count = -1
        current_instance = None
        subreddit_instance = None
        bulk_create_list = None
        bulk_create_count = -1
        total_created_count = -1
        aggregate_counter = -1
        
        # update control
        update_existing = False
        do_batch_insert = False
        
        # exception handling
        exception_helper = None
        exception_message = ""
        exception_status = ""

        # performance and auditing
        start_dt = None        
        end_dt = None
        add_count = -1
        existing_count = -1
        
        start_dt = datetime.datetime.now()
        
        # Set control variables from input parameters.
        
        # Include filters?
        include_filters = include_filters_IN

        # do batch insert?
        do_batch_insert = do_batch_insert_IN
        
        # update existing?
        update_existing = update_existing_IN
        if ( ( update_existing ) and ( update_existing != None ) and ( update_existing == True ) ):
        
            # yes - no batch insert.
            do_batch_insert = False
        
        #-- END check to see if updating existing --#
        
        # make sure we have start date, end date, and label.
        if ( ( start_dt_IN ) and ( start_dt_IN != None ) ):
        
            if ( ( end_dt_IN ) and ( end_dt_IN != None ) ):
            
                if ( ( time_period_category_IN ) and ( time_period_category_IN != None ) and ( time_period_category_IN != "" ) ):

                    if ( output_details_IN == True ):

                        print( "In " + me + "() [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - Label: '" + time_period_category_IN + "'; start dt: " + start_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + end_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; filter?: " + str( include_filters ) + "; update?: " + str( update_existing ) + "; batch?: " + str( do_batch_insert ) )

                    #-- END check to see if output details --#

                    # create database connection - get database helper
                    mysqldb = cls.my_db_helper
                    
                    # create connection
                    my_connection = mysqldb.get_connection()
                    
                    # get read and write cursors.
                    my_read_cursor = mysqldb.get_cursor()
                    
                    # get all subreddits that do not have rows in this time
                    #    period using SQL sub-query.

                    '''
                    Example query:
SELECT *
FROM reddit_collect_subreddit
WHERE NOT EXISTS
(
    SELECT 1
    FROM reddit_data_subreddit_time_series_data
    WHERE subreddit_reddit_id = reddit_collect_subreddit.reddit_full_id
        AND start_date = '2013-04-01 18:49:00'
        AND end_date = '2013-04-01 19:49:00'
        AND time_period_category = 'before'
        AND time_period_type = 'hourly'
        AND time_period_index = 1
)
                    '''
                    
                    # reset save list.
                    bulk_create_list = []
                    
                    # create SQL
                    current_select_sql = "SELECT *"
                    current_select_sql += " FROM reddit_collect_subreddit"
                    current_select_sql += " WHERE NOT EXISTS"
                    current_select_sql += " ("
                    current_select_sql += "     SELECT 1"
                    current_select_sql += "     FROM reddit_data_subreddit_time_series_data"
                    current_select_sql += "     WHERE subreddit_reddit_id = reddit_collect_subreddit.reddit_full_id"
                    current_select_sql += "         AND start_date = '" + start_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "'"
                    current_select_sql += "         AND end_date = '" + end_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "'"
                    
                    # category passed in?
                    if ( ( time_period_category_IN ) and ( time_period_category_IN != None ) and ( time_period_category_IN != "" ) ):
                        
                        # yes.  Check for it.
                        current_select_sql += "         AND time_period_category = '" + time_period_category_IN + "'"
                    
                    #-- END check to see if category --#
                    
                    # type passed in?
                    if ( ( time_period_type_IN ) and ( time_period_type_IN != None ) and ( time_period_type_IN != "" ) ):
                        
                        # yes.  Check for it.
                        current_select_sql += "         AND time_period_type = '" + time_period_type_IN + "'"
                        
                    #-- END check to see if type --#
                        
                    # index passed in?
                    if ( ( time_period_index_IN ) and ( time_period_index_IN != None ) and ( time_period_index_IN > 0 ) ):
                        
                        # yes.  Check for it.
                        current_select_sql += "         AND time_period_index = " + str( time_period_index_IN )
                        
                    #-- END check to see if type --#
                        
                    current_select_sql += " )"
                    current_select_sql += " ORDER BY reddit_full_id ASC;"
                    
                    if ( output_details_IN == True ):
                        print( "In " + me + "() before executing SQL: query = " + current_select_sql )
                    #-- END check to see if output details --#

                    # execute SQL
                    my_read_cursor.execute( current_select_sql )
                    
                    if ( output_details_IN == True ):
                        print( "In " + me + "() after executing SQL." )
                    #-- END check to see if output details --#

                    # ! initialize period and aggregate counters.
                    
                    # time period index (counter).
                    if ( ( time_period_index_IN ) and ( time_period_index_IN > 0 ) ):
                        
                        # we have a counter to use.
                        time_period_counter = time_period_index_IN
                        
                    else:
                        
                        # no counter to use.  Use 0 (error, whatever).
                        time_period_counter = -1
                        
                    #-- END check to see if counter passed in. --#
                    
                    # aggregate counter
                    if ( ( aggregate_counter_IN ) and ( aggregate_counter_IN > 0 ) ):
                        
                        # we have a counter to start with.  Subtract one?
                        aggregate_counter = aggregate_counter_IN
                        
                    else:
                        
                        # no counter to use.  Use 0 (error, whatever).
                        aggregate_counter = -1
                        
                    #-- END check to see if counter passed in. --#

                    # loop over the results, creating a new instance of this
                    #    class for each.
                    result_count = int( my_read_cursor.rowcount )
                    row_counter = 0
                    existing_count = 0
                    add_count = 0
                    for i in range( result_count ):
                    
                        # increment counter
                        row_counter += 1
                    
                        # get row.
                        current_row = my_read_cursor.fetchone()
                        
                        # get values
                        current_subreddit_pk = current_row[ 'id' ]
                        current_subreddit_name = current_row[ 'name' ]
                        current_subreddit_id = current_row[ 'reddit_full_id' ]
                        current_subreddit_full_id = current_row[ 'reddit_full_id' ]
                        current_subreddit_post_count = 0
                        
                        if ( output_details_IN == True ):
                            print( "In " + me + "() - " + time_period_category_IN + " - " + time_period_type_IN + " - " + str( time_period_index_IN ) + " ===> row " + str( row_counter ) + " of " + str( result_count ) + " - " + current_subreddit_name + " ( " + current_subreddit_full_id + " )" )
                        #-- END check to see if output details --#
    
                        # ! get instance of this class
                        current_instance = cls.get_instance( original_id_IN = current_subreddit_full_id,
                                                             start_dt_IN = start_dt_IN,
                                                             end_dt_IN = end_dt_IN,
                                                             time_period_type_IN = time_period_type_IN,
                                                             time_period_category_IN = time_period_category_IN,
                                                             time_period_index_IN = time_period_counter,
                                                             update_existing_IN = update_existing )
                                                             
                        # new or existing?
                        if ( ( current_instance.pk ) and ( current_instance.pk != None ) and ( current_instance.pk > 0 ) ):
                        
                            # existing.  Make a note, move on.
                            existing_count += 1
                            
                            if ( output_details_IN == True ):
                                print( "---- In " + me + "() - Existing row found ( ID: " + str( current_instance.pk ) + " )." )
                            #-- END check to see if output details --#

                        else:
                        
                            # new.  So, row for this subreddit wasn't already in
                            #    data set.  Add row for it, set all counts to 0.
                            add_count += 1

                            if ( output_details_IN == True ):
                                print( "---- In " + me + "() - No existing row found." )
                            #-- END check to see if output details --#

                            # populate values.
                            current_instance.start_date = start_dt_IN
                            current_instance.end_date = end_dt_IN
                            current_instance.time_period_type = time_period_type_IN
                            current_instance.time_period_index = time_period_counter
                            current_instance.time_period_category = time_period_category_IN
    
                            # time period label - starts out with value of time
                            #    period counter.
                            time_period_value = str( time_period_counter )
                            
                            # got a category?
                            if ( ( time_period_category_IN ) and ( time_period_category_IN != "" ) ):
                            
                                # yes - add to the beginning.
                                time_period_value = time_period_category_IN + "-" + time_period_value
                                
                            #-- END check to see if time-period label. --#
                            
                            # got a type?
                            if ( ( time_period_type_IN ) and ( time_period_type_IN != "" ) ):
                            
                                # yes - add to the beginning.
                                time_period_value = time_period_type_IN + "-" + time_period_value                            
    
                            #-- END check to see if we have a time period type --#
                            
                            current_instance.time_period_label = time_period_value
                            
                            current_instance.aggregate_index = aggregate_counter
    
                            #current_instance.filter_type = "" # - place to keep track of different filter types, if you want.  Example: "text_contains"
                            #current_instance.filter_value = ""
                            #current_instance.match_value = models.CharField( max_length = 255, null = True, blank = True )
    
                            # current_instance.subreddit = models.ForeignKey( Subreddit, null = True, blank = True )
                            current_instance.original_name = current_subreddit_name
                            current_instance.subreddit_name = current_subreddit_name
                            current_instance.original_id = current_subreddit_full_id
                            current_instance.subreddit_reddit_id = current_subreddit_id
                            current_instance.subreddit_reddit_full_id = current_subreddit_full_id
                            current_instance.post_count = 0
                            current_instance.self_post_count = 0
                            current_instance.over_18_count = 0
                            current_instance.unique_author_count = 0
                            current_instance.score_average = 0
                            current_instance.score_min = 0
                            current_instance.score_max = 0
                            current_instance.score_variance = 0
                            current_instance.upvotes_average = 0
                            current_instance.upvotes_min = 0
                            current_instance.upvotes_max = 0
                            current_instance.upvotes_variance = 0
                            current_instance.downvotes_average = 0
                            current_instance.downvotes_min = 0
                            current_instance.downvotes_max = 0
                            current_instance.downvotes_variance = 0
                            current_instance.num_comments_average = 0
                            current_instance.num_comments_min = 0
                            current_instance.num_comments_max = 0
                            current_instance.num_comments_variance = 0
    
                            # no need to look up subreddit.  We are updating
                            #    from a query of reddit_collect_subreddit - 
                            #    just put ID of current row in subreddit_id.
                            current_instance.subreddit_id = current_subreddit_pk

                            # no more:
                            # see if there is a subreddit instance for this ID.
                            #subreddit_instance = None
                            #try:
                            
                                # try to get subreddit instance
                            #    subreddit_instance = reddit_collect.models.Subreddit.objects.get( reddit_full_id = current_subreddit_full_id )
                                
                            #except:
                            
                                # for now, do nothing.
                            #    subreddit_instance = None
                            
                            #-- END try/except to look up subreddit model instance. --#
                            
                            # got one?
                            #if ( ( subreddit_instance ) and ( subreddit_instance != None ) ):
                            
                                # add to current_instance
                            #    current_instance.subreddit = subreddit_instance
                            
                            #-- END check to see if we have subreddit instance --#
    
                            # including filters?
                            if ( include_filters == True ):
                                
                                # yes. Set fields from query results.
                                current_instance.filter_1 = 0
                                current_instance.match_count_1 = 0
                                current_instance.filter_2 = 0
                                current_instance.match_count_2 = 0
                                current_instance.filter_3 = 0
                                current_instance.match_count_3 = 0
                                current_instance.filter_4 = 0
                                current_instance.match_count_4 = 0
                                current_instance.filter_5 = 0
                                current_instance.match_count_5 = 0
                                current_instance.filter_6 = 0
                                current_instance.match_count_6 = 0
                                current_instance.filter_7 = 0
                                current_instance.match_count_7 = 0
                                current_instance.filter_8 = 0
                                current_instance.match_count_8 = 0
                                current_instance.filter_9 = 0
                                current_instance.match_count_9 = 0
                                current_instance.filter_10 = 0
                                current_instance.match_count_10 = 0
                            
                            #-- END check to see if we include filters --#
                            
                            # doing batch insert?
                            if ( do_batch_insert == True ):
    
                                # yes - Add to list of instances to bulk save.
                                bulk_create_list.append( current_instance )
                                
                            else:
                            
                                # no - either updating, or just not doing batch.
                                current_instance.save()
                                
                            #-- END check to see if doing batch insert. --#
                        
                        #-- END check to see if new or existing --#

                    #-- END loop over subreddit data for this time period. --#
                    
                    # doing batch insert, and got something to insert?
                    bulk_create_count = len( bulk_create_list )
                    if ( ( do_batch_insert == True ) and ( bulk_create_count > 0 ) ):

                        # try/except around saving rows for subreddits with
                        #    posts in our time period.
                        try:
        
                            # yes.
                            cls.objects.bulk_create( bulk_create_list )
                            
                            # increment total count
                            total_created_count += bulk_create_count
    
                        except Exception as e:
                            
                            # error saving.  Probably encoding error.

                            # process the exception
                            exception_message = "ERROR - Exception caught in " + me + ":  bulk_create() threw exception, processing time-series data for period - start date: " + current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end date: " + current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; type:" + time_period_type_IN + "; category:" + time_period_category_IN + "; count of rows being bulk created = " + str( len( bulk_create_list ) )
                            exception_status = cls.process_exception( exception_IN = e, message_IN = exception_message, print_details_IN = True )
                            
                            # set status to description of exception
                            status_OUT = exception_status

                            # send email to let me know this crashed?
        
                            # throw exception?
                            raise( e )
                                
                        #-- END try/except around saving. --#
                    
                    #-- END check to see if we are batch updating --#
                    
                    # clear caches, performance stuff, etc.  Try garbage
                    #    collecting, not clearing django cache, to start.
                    gc.collect()
                    django.db.reset_queries()
                    
                    # Time series data needs all subreddits in data set in
                    #    all time periods.  Call function to pull in all
                    #    subreddits not already in our data for this time
                    #    period.
                                    
                else:
            
                    status_OUT = cls.STATUS_PREFIX_ERROR + "no category passed in, so can't target time-serires to look within, so can't fill in missing rows."

                #-- END check to make sure we have an interval. --#
                
            else:
            
                # no end date.  Error.
                status_OUT = cls.STATUS_PREFIX_ERROR + "no end date passed in, so can't fill in missing rows."
            
            #-- END check to see if end date passed in. --#
        
        else:
        
            # no start date.  Error.
            status_OUT = cls.STATUS_PREFIX_ERROR + "no start date passed in, so can't fill in missing rows."
        
        #-- END check to see if end date passed in. --#

        # print details?
        if ( output_details_IN == True ): 

            # a little overview
            end_dt = datetime.datetime.now()
            print( "==> Started at " + str( start_dt ) )
            print( "==> Finished at " + str( end_dt ) )
            print( "==> Duration: " + str( end_dt - start_dt ) )
            print( "==> Processed: " + str( row_counter ) )
            print( "==> Row exists: " + str( existing_count ) )
            print( "==> Added: " + str( add_count ) )
                        
        #-- END check to see if we print details. --#

        return status_OUT
    
    #-- END method make_data_add_missing_rows() --#


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
    
    # Current database config
    SETTINGS_DATABASES = getattr( settings, "DATABASES", None )
    SETTINGS_DB_ENGINE = SETTINGS_DATABASES[ "default" ][ "ENGINE" ]


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
    unique_author_count = models.IntegerField( null = True, blank = True )
    score_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    score_min = models.IntegerField( null = True, blank = True )
    score_max = models.IntegerField( null = True, blank = True )
    score_variance = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    upvotes_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    upvotes_min = models.IntegerField( null = True, blank = True )
    upvotes_max = models.IntegerField( null = True, blank = True )
    upvotes_variance = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    downvotes_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    downvotes_min = models.IntegerField( null = True, blank = True )
    downvotes_max = models.IntegerField( null = True, blank = True )
    downvotes_variance = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    num_comments_average = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    num_comments_min = models.IntegerField( null = True, blank = True )
    num_comments_max = models.IntegerField( null = True, blank = True )    
    num_comments_variance = models.DecimalField( max_digits = 19, decimal_places = 10, null = True, blank = True )
    
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
        cls.db_initialize( Database_Helper_Factory.DATABASE_TYPE_MYSQLDB, db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END method db_initialize_mysql() --#


    @classmethod
    def db_initialize( cls, db_type_IN = "", db_host_IN = "localhost", db_port_IN = -1, db_username_IN = "", db_password_IN = "", db_database_IN = "" ):
        
        # instance variables
        cls.my_db_helper = Database_Helper_Factory.get_database_helper( db_type_IN, db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END method db_initialize() --#


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

        # exception handling
        exception_message = ""
        exception_status = ""

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
                            filter_sql = reddit_collect.models.Post.sql_text_filter( text_contains_and_IN, cls.SQL_AND )
                            
                            # got anything back?
                            if ( filter_sql != "" ):

                                current_select_sql += " AND ( " + filter_sql + " )"

                            #-- END check to make sure we got something back. --#
                        
                        #-- END check to see if we are AND-ing text
                        
                        # are we OR-ing any contains?
                        if ( len( text_contains_or_IN ) > 0 ):
                        
                            # we are.  output SQL.
                            filter_sql = reddit_collect.models.Post.sql_text_filter( text_contains_or_IN, cls.SQL_OR )
                            
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
                                    exception_message = "ERROR - Exception caught in " + me + "():  save() processing filter for post " + str( current_post.id ) + " ( reddit ID: " + current_post.reddit_id + " )"
                                    exception_status = cls.process_exception( exception_IN = e, message_IN = exception_message, print_details_IN = True )
                                    
                                    # set status to description of exception
                                    status_OUT = exception_status

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
    def make_data( cls,
                   start_dt_IN,
                   end_dt_IN,
                   interval_td_IN,
                   time_period_type_IN = "",
                   time_period_category_IN = "",
                   aggregate_counter_start_IN = 0,
                   include_filters_IN = True,
                   *args,
                   **kwargs ):
    
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
        - time_period_category_IN - (optional) label to use in labeling.  If set, this is appended to the front of an integer counter that counts up each time period, is stored in time_period_label.  If not set, the integer time period counter is the only thing stored in time period label.
        - aggregate_counter_start_IN - (optional) value you want aggregate counter to begin at for this set of data.  This lets you track increasing time-series across labels (before - 1 to 366 - and after - 367 and up - for instance).
        - include_filters_IN - (optional) Boolean - True if you want to use the posts' filter fields to set the time series values, False if you want to set them separately.  Defaults to True.
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
        include_filters = True
        result_count = -1
        current_row = None
        current_subreddit_name = ""
        current_subreddit_id = ""
        current_subreddit_post_count = -1
        current_instance = None
        domain_instance = None
        bulk_create_list = None
        bulk_create_count = -1
        total_created_count = -1
        aggregate_counter = -1
        
        # exception handling
        exception_message = ""
        exception_status = ""

        # database handling
        is_postgres = False
        
        # Include filters?
        include_filters = include_filters_IN
        
        # is it Postgres?
        if ( "psycopg" in cls.SETTINGS_DB_ENGINE ):
        
            # yes
            is_postgres = True
            
        #-- END check to see if DB ENGINE indicates postgresql --#
        
        # make sure we have start date, end date, and interval.
        if ( ( start_dt_IN ) and ( start_dt_IN != None ) ):
        
            if ( ( end_dt_IN ) and ( end_dt_IN != None ) ):
            
                if ( ( interval_td_IN ) and ( interval_td_IN != None ) ):

                    print( "In " + me + "() [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "] - Category: '" + time_period_category_IN + "'; start dt: " + start_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + end_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; interval: " + str( interval_td_IN ) )

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
                        current_select_sql += ", SUM( is_self"

                        # if postgres, cast booleans to int.
                        if ( is_postgres == True ):
                            current_select_sql += "::int"
                        #-- END check to see if postgreSQL

                        current_select_sql += " ) AS self_post_count"
                        current_select_sql += ", SUM( over_18"

                        # if postgres, cast booleans to int.
                        if ( is_postgres == True ):
                            current_select_sql += "::int"
                        #-- END check to see if postgreSQL

                        current_select_sql += " ) AS over_18_count"
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

                        # also aggregate filter flags - just MAX, SUM to count matches.
                        if ( include_filters == True ):
                        
                            # yes (for now, we always do).
                            current_select_sql += ", MAX( filter_1"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_1"
                            current_select_sql += ", SUM( filter_1"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_1"
                            current_select_sql += ", MAX( filter_2"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_2"
                            current_select_sql += ", SUM( filter_2"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_2"
                            current_select_sql += ", MAX( filter_3"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_3"
                            current_select_sql += ", SUM( filter_3"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_3"
                            current_select_sql += ", MAX( filter_4"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_4"
                            current_select_sql += ", SUM( filter_4"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_4"
                            current_select_sql += ", MAX( filter_5"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_5"
                            current_select_sql += ", SUM( filter_5"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_5"
                            current_select_sql += ", MAX( filter_6"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_6"
                            current_select_sql += ", SUM( filter_6"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_6"
                            current_select_sql += ", MAX( filter_7"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_7"
                            current_select_sql += ", SUM( filter_7"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_7"
                            current_select_sql += ", MAX( filter_8"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_8"
                            current_select_sql += ", SUM( filter_8"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_8"
                            current_select_sql += ", MAX( filter_9"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_9"
                            current_select_sql += ", SUM( filter_9"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_9"
                            current_select_sql += ", MAX( filter_10"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS filter_10"
                            current_select_sql += ", SUM( filter_10"

                            # if postgres, cast booleans to int.
                            if ( is_postgres == True ):
                                current_select_sql += "::int"
                            #-- END check to see if postgreSQL
    
                            current_select_sql += " ) AS match_count_10"
                            
                        #-- END check to see if we include filters --#
                            
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
                            current_instance.time_period_category = time_period_category_IN

                            # time period label - starts out with value of time
                            #    period counter.
                            time_period_value = str( time_period_counter )
                            
                            # got a label?
                            if ( ( time_period_category_IN ) and ( time_period_category_IN != "" ) ):
                            
                                # yes - add to the beginning.
                                time_period_value = time_period_category_IN + "-" + time_period_value
                                
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

                            # see if there is a domain instance for this domain.
                            domain_instance = None
                            try:
                            
                                # try to get subreddit instance
                                domain_instance = reddit_collect.models.Domain.objects.get( name__iexact = current_name )
                                
                            except:
                            
                                # for now, do nothing.
                                domain_instance = None
                            
                            #-- END try/except to look up domain model instance. --#
                            
                            # got one?
                            if ( ( domain_instance ) and ( domain_instance != None ) ):
                            
                                # add to current_instance
                                current_instance.domain = domain_instance
                            
                            #-- END check to see if we have subreddit instance --#
                            
                            # including filters?
                            if ( include_filters == True ):
                                
                                # yes. Set fields from query results.
                                current_instance.filter_1 = current_row[ 'filter_1' ]
                                current_instance.match_count_1 = current_row[ 'match_count_1' ]
                                current_instance.filter_2 = current_row[ 'filter_2' ]
                                current_instance.match_count_2 = current_row[ 'match_count_2' ]
                                current_instance.filter_3 = current_row[ 'filter_3' ]
                                current_instance.match_count_3 = current_row[ 'match_count_3' ]
                                current_instance.filter_4 = current_row[ 'filter_4' ]
                                current_instance.match_count_4 = current_row[ 'match_count_4' ]
                                current_instance.filter_5 = current_row[ 'filter_5' ]
                                current_instance.match_count_5 = current_row[ 'match_count_5' ]
                                current_instance.filter_6 = current_row[ 'filter_6' ]
                                current_instance.match_count_6 = current_row[ 'match_count_6' ]
                                current_instance.filter_7 = current_row[ 'filter_7' ]
                                current_instance.match_count_7 = current_row[ 'match_count_7' ]
                                current_instance.filter_8 = current_row[ 'filter_8' ]
                                current_instance.match_count_8 = current_row[ 'match_count_8' ]
                                current_instance.filter_9 = current_row[ 'filter_9' ]
                                current_instance.match_count_9 = current_row[ 'match_count_9' ]
                                current_instance.filter_10 = current_row[ 'filter_10' ]
                                current_instance.match_count_10 = current_row[ 'match_count_10' ]
                            
                            #-- END check to see if we include filters --#
                            
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
                            # process the exception
                            exception_message = "ERROR - Exception caught in " + me + ":  bulk_create() threw exception, processing time-series data for period - start date: " + current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end date: " + current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; type:" + time_period_type_IN + "; category:" + time_period_category_IN + "; count of rows being bulk created = " + str( len( bulk_create_list ) )
                            exception_status = cls.process_exception( exception_IN = e, message_IN = exception_message, print_details_IN = True )
                            
                            # set status to description of exception
                            status_OUT = exception_status
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