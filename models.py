from __future__ import unicode_literals

'''
Copyright 2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/reddit_data.

reddit_data is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
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
from python_utilities.research.time_series_data import AbstractTimeSeriesDataModel
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
    MYSQL_DATE_TIME_FORMAT = "%Y-%m-%d %H-%M-%S"
    

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
    subreddit_reddit_id = models.CharField( max_length = 255, null = True, blank = True )
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
    my_mysql_helper = None


    #============================================================================
    # class methods
    #============================================================================


    @classmethod
    def db_initialize( cls, db_host_IN = "localhost", db_port_IN = 3306, db_username_IN = "", db_password_IN = "", db_database_IN = "" ):
        
        # instance variables
        cls.my_mysql_helper = MySQLdb_Helper( db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END class method db_initialize() --#

    
    @classmethod
    def make_data( cls, start_dt_IN, end_dt_IN, interval_td_IN, time_period_type_IN = "", time_period_label_IN = "", aggregate_counter_start_IN = 0, *args, **kwargs ):
    
        '''
        Accepts a start and end datetime and an optional result set of the posts
            we want to include in our time series.  If no result set passed in,
            just grabs all posts in the time period.  
            
        Parameters:
        - start_dt_IN - datetime.datetime instance of date and time on which you want to start deriving time-series data.
        - end_dt_IN - datetime.datetime instance of date and time on which you want to stop deriving time-series data.
        - interval_td_IN - datetime.timedelta instance containing the amount of time you want each time slice to contain.
        - time_period_type_IN - time period type value you want stored in each time-series record.  Defaults to empty string.
        - time_period_label_IN - (optional) label to use in labeling.  If set, this is appended to the front of an integer counter that counts up each time period, is stored in time_period_label.  If not set, the integer time period counter is the only thing stored in time period label.
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

                    print( "In " + me + "() [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "]: start dt: " + start_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + end_dt_IN.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; interval: " + str( interval_td_IN ) )

                    # create database connection - get database helper
                    mysqldb = cls.my_mysql_helper
                    
                    # create connection
                    my_connection = mysqldb.get_connection()
                    
                    # get read and write cursors.
                    my_read_cursor = mysqldb.get_cursor()
                    
                    # loop - go from start_dt_IN to end_dt_IN in increments of
                    #    interval_td_IN.
                    time_period_counter = 0
                    aggregate_counter = aggregate_counter_start_IN
                    current_start_dt = start_dt_IN
                    current_end_dt = start_dt_IN + interval_td_IN
                    total_created_count = 0

                    # continue as long as the end date is less than or equal to
                    #   the overall end datetime.
                    while ( current_end_dt <= end_dt_IN ):
                    
                        print( "- At top of time period loop [" + datetime.datetime.now().strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "].  Label: " + time_period_label_IN + "; start dt: " + current_start_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) + "; end dt: " + current_end_dt.strftime( cls.MYSQL_DATE_TIME_FORMAT ) )
                    
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
                            current_instance.start_date = start_dt_IN
                            current_instance.end_date = end_dt_IN
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
                            current_instance.subreddit_name = current_subreddit_name
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

    
#-- END class SubredditTimeSeriesData --#


#@python_2_unicode_compatible
#class Domain_Time_Series_Data( AbstractTimeSeriesDataModel ):

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

    #domain = models.TextField( null = True, blank = True )
    #post_count = models.IntegerField( null = True, blank = True )
    
#-- END class DomainTimeSeriesData --# 
