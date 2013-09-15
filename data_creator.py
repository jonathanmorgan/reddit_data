'''
Copyright 2012, 2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/reddit_data.

reddit_data is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

reddit_data is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/reddit_data. If not, see http://www.gnu.org/licenses/.
'''

#!/usr/bin/python

#================================================================================
# imports
#================================================================================

# base python libraries
import datetime
import gc
import sys
import time

# django imports
import django.db
from django.db.models import Q

# site-specific imports.
#site_path = '/home/socs/socs_reddit/'
#if site_path not in sys.path:
#    sys.path.append( site_path )

#import myLib

# import reddit_collect models.
import reddit_collect.models

# import reddit_data models.
import reddit_data.models

# python_utilities
# from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited
from python_utilities.strings.string_helper import StringHelper
from python_utilities.database.database_helper_factory import Database_Helper_Factory
#from python_utilities.database.MySQLdb_helper import MySQLdb_Helper


# ReddiWrapper
# from reddiwrap.ReddiWrap import ReddiWrap

# Time Series Data imports
import django_time_series.models

# Django reference data (news domains)
import django_reference_data.models


#================================================================================
# class RedditCollector
#================================================================================

class Data_Creator( object ):


    #============================================================================
    # CONSTANTS-ish
    #============================================================================


    STATUS_SUCCESS = "Success!"
    STATUS_PREFIX_ERROR = "ERROR: "
    
    # DEBUG - changed to instance variable.
    #DEBUG_FLAG = False


    #============================================================================
    # instance variables
    #============================================================================


    # debug_flag
    debug_flag = False
    
    # database connection helper.
    my_db_helper = None
    
    
    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------

    
    def __init__( self ):
        
        '''
        Constructor
        '''

        my_db_helper = None       

    #-- END constructor --#


    #============================================================================
    # instance methods
    #============================================================================
    

    def create_domains_from_posts( self, include_all_IN = True, limit_IN = -1, do_update_existing_IN = True, *args, **kwargs ):
    
        '''
        Uses an SQL query to get all domains from posts in the database.  For
            each, creates a domain model instance, saves it, gets ID, then uses
            SQL to update all posts and data rows that reference the domain
            with its ID.
            
        Parameters:
        - include_all_IN - Boolean, if True, includes all domains.  If false, only includes those where post rows don't already have a domain_id.  Defaults to True (includes all).
        - limit_IN - integer limit on number of domains to process.  If less than or equal to 0, does not limit.  Defaults to -1.
        - do_update_exsiting_IN - Boolean.  If True, updates existing domain records.  If false, does not update existing domain records themselves.

        Preconditions: Expects to be run on reddit_collect databases where posts
            have been collected but no related records were created, for
            performance, and so where you have to subsequently build model
            instances and relations by hand to use django's relational tools.
            Also assumes that you have initialized a database helper instance.
        '''
        
        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables
        me = "create_domains_from_posts"

        # overview information
        start_dt = None
        end_dt = None
        existing_domain_count = -1
        
        # reading in domain information.
        db_helper = None
        db_conn = None
        db_read_cursor = None
        sql_string = ""
        result_count = -1
        current_row = None
        domain_instance = None
        current_domain_name = ""
        current_use_count = -1
        domain_counter = -1
        domain_model_id = -1
        do_update_and_save = False
        
        # set start datetime
        start_dt = datetime.datetime.now()
        
        # UPDATE-ing posts and comments.
        sql_update = ""
        
        # First, get a connection and a cursor
        db_helper = self.my_db_helper
        db_conn = db_helper.get_connection()
        db_read_cursor = db_helper.get_cursor()
        db_write_cursor = db_helper.get_cursor()
        
        # create SQL string.
        sql_string = "SELECT domain_name, COUNT( * ) AS use_count, SUM( num_comments ) AS comment_sum, AVG( num_comments ) AS comment_mean, MIN( num_comments ) AS comment_min, MAX( num_comments ) AS comment_max"
        sql_string += " FROM reddit_collect_post"
        sql_string += " WHERE"
        sql_string += " ( ( domain_name != '' ) AND ( domain_name IS NOT NULL ) )"
        
        # Include all?
        if ( include_all_IN == False ):
    
            # No - just include those without an ID.
            sql_string += " AND ( ( domain_id IS NULL ) OR ( domain_id <= 0 ) )"
            
        #-- END check to see if include all --#

        sql_string += " GROUP BY domain_name"
        sql_string += " ORDER BY domain_name ASC"
        
        # got a limit?
        if ( ( limit_IN ) and ( limit_IN > 0 ) ):
    
            # we do.  Add it.
            sql_string += " LIMIT " + str( limit_IN )
        
        #-- END check to see if we have a limit. --#
        
        sql_string += ";"

        if ( self.debug_flag == True ):
        
            # output SQL
            print( "In " + me + "() - SQL: " + sql_string )
        
        #-- END DEBUG check --#
        
        # execute the query
        db_read_cursor.execute( sql_string )
        
        # get number of domains.
        result_count = int( db_read_cursor.rowcount )

        # loop.
        domain_counter = 0
        for i in range( result_count ):

            # increment counter
            domain_counter += 1

            # get row.
            current_row = db_read_cursor.fetchone()
            
            # get values.
            current_domain_name = current_row[ 'domain_name' ]
            current_use_count = current_row[ 'use_count' ]
            
            # initialize update and save flag.
            do_update_and_save = False
            
            try:
            
                # lookup to see if domain already in database.
                domain_instance = reddit_collect.models.Domain.objects.get( name__iexact = current_domain_name )
            
                # already in database.  Move on.
                existing_domain_count += 1
                print( "- Domain " + current_domain_name + " is already in the database ( ID = " + str( domain_instance.id ) + " )." )
                
                # update?
                if ( do_update_existing_IN == True ):
                
                    # yes.
                    do_update_and_save = True
                
                else:
                
                    # no.
                    do_update_and_save = False
                
                #-- END check tos ee if we update existing. --#
            
            except Exception as e:            
            
                # not in database.  Add it.
                domain_instance = reddit_collect.models.Domain()
                
                # always update and save new instance.
                do_update_and_save = True
            
            #-- END try/except to see if domain already in database. --#

            # update and save?
            if ( do_update_and_save == True ):

                # set values
                domain_instance.name = current_domain_name
                domain_instance.use_count = current_use_count

                # domain name longer than 255?
                if ( len( current_domain_name ) > 255 ):

                    # yes - store in long name, as well.
                    domain_instance.long_name = current_domain_name
                
                #-- END check to see if long domain name --#
                
                # start with "self."?
                if ( current_domain_name.lower().find( "self." ) == 0 ):
                
                    # yes - set flag.
                    domain_instance.is_self_post = True
                    
                #-- END check to see if self-post --#
               
                # save it.
                domain_instance.save()

            #-- END check to see if we update and save --#

            # get ID from instance.
            domain_model_id = domain_instance.id
            
            # got an ID?
            if ( ( domain_model_id ) and ( domain_model_id != None ) and ( domain_model_id > 0 ) ):
            
                # we do.  Update relation in posts, comments fields.
                
                # UPDATE posts
                db_write_cursor.execute( "UPDATE `reddit_collect_post` SET domain_id = %s WHERE domain_name = %s;", ( domain_model_id, current_domain_name ) )
                
                # UPDATE domain time-series data
                db_write_cursor.execute( "UPDATE `reddit_data_domain_time_series_data` SET domain_id = %s WHERE domain_name = %s;", ( domain_model_id, current_domain_name ) )

                # commit changes
                db_conn.commit()
            
            #-- END check to see if model ID --#
            
            if ( self.debug_flag == True ):
            
                print( "- Processed domain " + str( domain_counter ) + " of " + str( result_count ) + " ( " + str( datetime.datetime.now() ) + " ) - ID: " + str( domain_model_id ) + "; name = " + current_domain_name + "; use_count = " + str( current_use_count ) )
            
            #-- END DEBUG check --#
            
            # clear caches, performance stuff, etc.  Try garbage
            #    collecting, not clearing django cache, to start.
            gc.collect()
            django.db.reset_queries()

        #-- END loop over domains. --#
        
        # a little overview
        end_dt = datetime.datetime.now()
        print( "==> Started at " + str( start_dt ) )
        print( "==> Finished at " + str( end_dt ) )
        print( "==> Duration: " + str( end_dt - start_dt ) )
        print( "==> Domains: " + str( domain_counter ) )
        
        return status_OUT
    
    #-- END method create_domains_from_posts() --#
    
    
    def create_subreddits_from_posts( self,
                                      include_all_IN = False,
                                      limit_IN = -1,
                                      update_related_IN = True,
                                      *args,
                                      **kwargs ):
    
        '''
        Uses an SQL query to get all subreddit names and IDs from posts in the
            database.  For each, creates a subreddit model instance, saves it,
            gets ID, then uses SQL to update all posts and data rows that
            reference the subreddit with its ID.
            
        Parameters:
        - include_all_IN - Boolean.  Defaults to False.  If True, includes all subreddits. If false, only processes subreddits in posts that don't yet have a subreddit ID.
        - update_related_IN - Boolean.  Defaults to True.  If True, related rows are updated for each subreddit we find.  If False, subreddit rows are created, but related rows are not updated with the relational subreddit ID for their subreddit.
        - limit_IN - integer limit on number of subreddits to process.  If less than or equal to 0, does not limit.  Defaults to -1.

        Preconditions: Expects to be run on reddit_collect databases where posts
            have been collected but no related records were created, for
            performance, and so where you have to subsequently build model
            instances and relations by hand to use django's relational tools.
            Also assumes that you have initialized a database helper instance.
        '''
        
        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables
        me = "create_subreddits_from_posts"
        
        # reading in subreddit names and IDs.
        db_helper = None
        db_conn = None
        db_read_cursor = None
        sql_string = ""
        result_count = -1
        current_row = None
        subreddit_instance = None
        subreddit_name = ""
        subreddit_id = ""
        subreddit_path = ""
        subreddit_counter = -1
        subreddit_model_id = -1
        
        # UPDATE-ing posts and comments.
        sql_update = ""
        
        # First, get a connection and a cursor
        db_helper = self.my_db_helper
        db_conn = db_helper.get_connection()
        db_read_cursor = db_helper.get_cursor()
        db_write_cursor = db_helper.get_cursor()
        
        # create SQL string.
        sql_string = "SELECT DISTINCT subreddit_name, subreddit_reddit_id"
        sql_string += " FROM reddit_collect_post"
        sql_string += " WHERE"
        sql_string += " ("
        sql_string += " ( ( subreddit_name != '' ) AND ( subreddit_name IS NOT NULL ) )"
        sql_string += " AND ( ( subreddit_reddit_id != '' ) AND ( subreddit_reddit_id IS NOT NULL ) )"
        sql_string += " )"
        
        # Include all?
        if ( include_all_IN == False ):
    
            # No - just include those without an ID.
            sql_string += " AND ( ( subreddit_id IS NULL ) OR ( subreddit_id <= 0 ) )"
            
        #-- END check to see if include all --#

        sql_string += " ORDER BY subreddit_name"
        
        # got a limit?
        if ( ( limit_IN ) and ( limit_IN > 0 ) ):
    
            # we do.  Add it.
            sql_string += " LIMIT " + str( limit_IN )
        
        #-- END check to see if we have a limit. --#
        
        sql_string += ";"

        if ( self.debug_flag == True ):
        
            # output SQL
            print( "In " + me + "() - SQL: " + sql_string )
        
        #-- END DEBUG check --#
        
        # execute the query
        db_read_cursor.execute( sql_string )
        
        # get number of subreddits.
        result_count = int( db_read_cursor.rowcount )

        # loop.
        subreddit_counter = 0
        for i in range( result_count ):

            # increment counter
            subreddit_counter += 1

            # get row.
            current_row = db_read_cursor.fetchone()
            
            # get values.
            subreddit_name = current_row[ 'subreddit_name' ]
            subreddit_id = current_row[ 'subreddit_reddit_id' ]
             
            try:
            
                # lookup to see if subreddit already in database.
                subreddit_instance = reddit_collect.models.Subreddit.objects.get( reddit_full_id__iexact = subreddit_id )
            
                # already in database.  Move on.    
            
            except Exception as e:            
            
                # not in database.  Add it.
                subreddit_instance = reddit_collect.models.Subreddit()
                
                # set values
                subreddit_instance.reddit_id = subreddit_id[ 3 : ]    # 2qh0u
                subreddit_instance.reddit_full_id = subreddit_id # t5_2qh0u
                subreddit_instance.name = subreddit_name         # pics
                subreddit_instance.display_name = subreddit_name # pics
                
                # subreddit path, based on name.
                subreddit_path = "/r/%s" % subreddit_name
                subreddit_instance.title = subreddit_path        # /r/Pics
                subreddit_instance.url = subreddit_path + "/"    # /r/pics/
                
                # save it.
                subreddit_instance.save()
            
            #-- END try/except to see if subreddit already in database. --#

            # get ID from instance.
            subreddit_model_id = subreddit_instance.id
            
            # got an ID?
            if ( ( subreddit_model_id ) and ( subreddit_model_id != None ) and ( subreddit_model_id > 0 ) ):
            
                # we do.  Are we updating related?
                if ( update_related_IN == True ):
                
                    # Update relation in posts, comments fields.
                
                    # UPDATE posts
                    db_write_cursor.execute( "UPDATE `reddit_collect_post` SET subreddit_id = %s WHERE subreddit_reddit_id = %s;", ( subreddit_model_id, subreddit_id ) )
                    
                    # UPDATE comments
                    db_write_cursor.execute( "UPDATE `reddit_collect_comment` SET subreddit_id = %s WHERE subreddit_reddit_id = %s;", ( subreddit_model_id, subreddit_id ) )
    
                    # UPDATE subreddit time-series data
                    db_write_cursor.execute( "UPDATE `reddit_data_subreddit_time_series_data` SET subreddit_id = %s WHERE subreddit_reddit_id = %s;", ( subreddit_model_id, subreddit_id ) )
    
                    # commit changes
                    db_conn.commit()
                    
                #-- END check to see if we are updating. --#
            
            #-- END check to see if model ID --#
            
            if ( self.debug_flag == True ):
            
                print( "- Processed subreddit " + str( subreddit_counter ) + " of " + str( result_count ) + " ( " + str( datetime.datetime.now() ) + " ) - ID: " + str( subreddit_model_id ) + "; name = " + subreddit_name + "; reddit ID = " + subreddit_id )
            
            #-- END DEBUG check --#
            
            # clear caches, performance stuff, etc.  Try garbage
            #    collecting, not clearing django cache, to start.
            gc.collect()
            django.db.reset_queries()

        #-- END loop over subreddits. --#
        
        return status_OUT
    
    #-- END method create_subreddits_from_posts() --#
    
    
    def create_time_periods_from_ts_data( self, include_all_IN = True, limit_IN = -1, do_update_existing_IN = True, project_name_IN = "", project_category_IN = "", *args, **kwargs ):
    
        '''
        Uses an SQL query to get all time periods from posts in the database. For
            each, creates a time period model instance, saves it, gets ID, then
            uses SQL to update all time-series dataa rows that reference the time
            period with its ID.  This is a pretty specific example of making time
            periods, so might not be useful in and of itself, but more used as a
            pattern for other implementations.
            
        Parameters:
        - include_all_IN - Boolean, if True, includes all time periods. If false, only includes those where post rows don't already have a time_period_id.  Defaults to True (includes all).
        - limit_IN - integer limit on number of time periods to process.  If less than or equal to 0, does not limit.  Defaults to -1.
        - do_update_exsiting_IN - Boolean.  If True, updates existing time period records.  If false, does not update existing time period records themselves.
        - project_name_IN - Project name to assign to time periods created.
        - project_category_IN - Project category value to assign to time periods created.
            
        Preconditions: Expects to be run on reddit_collect databases where posts
            have been collected but no related records were created, for
            performance, and so where you have to subsequently build model
            instances and relations by hand to use django's relational tools.
            Also assumes that you have initialized a database helper instance.
        '''
        
        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables
        me = "create_time_periods_from_ts_data"

        # overview information
        start_dt = None
        end_dt = None
        existing_time_period_count = -1
        time_period_counter = -1
        
        # reading in time period information.
        db_helper = None
        db_conn = None
        db_read_cursor = None
        sql_string = ""
        result_count = -1
        current_row = None
        time_period_instance = None
        
        # time period information
        current_start_date = None
        current_end_date = None
        current_time_period_type = ""
        current_time_period_index = -1
        current_time_period_category = ""
        current_time_period_label = ""
        current_aggregate_index = ""

        # update related rows
        time_period_model_id = -1
        do_update_and_save = False
        
        # set start datetime
        start_dt = datetime.datetime.now()
        
        # UPDATE-ing posts and comments.
        sql_update = ""
        
        # First, get a connection and a cursor
        db_helper = self.my_db_helper
        db_conn = db_helper.get_connection()
        db_read_cursor = db_helper.get_cursor()
        db_write_cursor = db_helper.get_cursor()
        
        # create SQL string.
        # SELECT DISTINCT start_date, end_date, time_period_type, time_period_index, time_period_category, time_period_label, aggregate_index FROM reddit_data_domain_time_series_data ORDER BY aggregate_index ASC
        sql_string = "SELECT DISTINCT start_date, end_date, time_period_type, time_period_index, time_period_category, time_period_label, aggregate_index"
        sql_string += " FROM reddit_data_domain_time_series_data"
        
        #sql_string += " WHERE"
        #sql_string += " ( ( domain_name != '' ) AND ( domain_name IS NOT NULL ) )"
        
        # Include all?
        if ( include_all_IN == False ):
    
            # No - just include those without an ID.
            sql_string += " WHERE ( ( time_period_id IS NULL ) OR ( time_period_id <= 0 ) )"
            
        #-- END check to see if include all --#

        sql_string += " ORDER BY aggregate_index ASC"
        
        # got a limit?
        if ( ( limit_IN ) and ( limit_IN > 0 ) ):
    
            # we do.  Add it.
            sql_string += " LIMIT " + str( limit_IN )
        
        #-- END check to see if we have a limit. --#
        
        sql_string += ";"

        if ( self.debug_flag == True ):
        
            # output SQL
            print( "In " + me + "() - SQL: " + sql_string )
        
        #-- END DEBUG check --#
        
        # execute the query
        db_read_cursor.execute( sql_string )
        
        # get number of time periods.
        result_count = int( db_read_cursor.rowcount )

        # loop.
        time_period_counter = 0
        for i in range( result_count ):

            # increment counter
            time_period_counter += 1

            # get row.
            current_row = db_read_cursor.fetchone()
            
            # get values.
            current_start_date = current_row[ 'start_date' ]
            current_end_date = current_row[ 'end_date' ]
            current_time_period_type = current_row[ 'time_period_type' ]
            current_time_period_index = current_row[ 'time_period_index' ]
            current_time_period_category = current_row[ 'time_period_category' ]
            current_time_period_label = current_row[ 'time_period_label' ]
            current_aggregate_index = current_row[ 'aggregate_index' ]
            
            # initialize update and save flag.
            do_update_and_save = False
            
            try:
            
                # lookup to see if time_period already in database.
                # !TODO - figure this out.  Project plus aggregate index?  time period label?
                time_period_instance = django_time_series.models.Time_Period.objects.get( time_period_label__iexact = current_time_period_label )
            
                # already in database.  Move on.
                existing_time_period_count += 1
                print( "- Time Period " + current_time_period_label + " is already in the database ( ID = " + str( time_period_instance.id ) + " )." )
                
                # update?
                if ( do_update_existing_IN == True ):
                
                    # yes.
                    do_update_and_save = True
                
                else:
                
                    # no.
                    do_update_and_save = False
                
                #-- END check to see if we update existing. --#
            
            except Exception as e:            
            
                # not in database.  Add it.
                time_period_instance = django_time_series.models.Time_Period()
                
                # always update and save new instance.
                do_update_and_save = True
            
            #-- END try/except to see if time period already in database. --#

            # update and save?
            if ( do_update_and_save == True ):

                # set values
                time_period_instance.start_date = current_start_date
                time_period_instance.end_date = current_end_date
                time_period_instance.time_period_type = current_time_period_type
                time_period_instance.time_period_index = current_time_period_index
                time_period_instance.time_period_category = current_time_period_category
                time_period_instance.time_period_label = current_time_period_label
                time_period_instance.aggregate_index = current_aggregate_index
                time_period_instance.project_name = project_name_IN
                time_period_instance.project_category = project_category_IN
               
                # save it.
                time_period_instance.save()

            #-- END check to see if we update and save --#

            # get ID from instance.
            time_period_model_id = time_period_instance.id
            
            # got an ID?
            if ( ( time_period_model_id ) and ( time_period_model_id != None ) and ( time_period_model_id > 0 ) ):
            
                # we do.  Update relation in posts, comments fields.
                
                # !TODO - update WHERE to match instance lookup criteria - time period label?
                
                # UPDATE domain time-series data
                db_write_cursor.execute( "UPDATE `reddit_data_domain_time_series_data` SET time_period_id = %s WHERE time_period_label = %s;", ( time_period_model_id, current_time_period_label ) )

                # UPDATE subreddit time-series data
                db_write_cursor.execute( "UPDATE `reddit_data_subreddit_time_series_data` SET time_period_id = %s WHERE time_period_label = %s;", ( time_period_model_id, current_time_period_label ) )

                # commit changes
                db_conn.commit()
            
            #-- END check to see if model ID --#
            
            if ( self.debug_flag == True ):
            
                print( "- Processed domain " + str( domain_counter ) + " of " + str( result_count ) + " ( " + str( datetime.datetime.now() ) + " ) - ID: " + str( domain_model_id ) + "; name = " + current_domain_name + "; use_count = " + str( current_use_count ) )
            
            #-- END DEBUG check --#
            
            # clear caches, performance stuff, etc.  Try garbage
            #    collecting, not clearing django cache, to start.
            gc.collect()
            django.db.reset_queries()

        #-- END loop over domains. --#
        
        # a little overview
        end_dt = datetime.datetime.now()
        print( "==> Started at " + str( start_dt ) )
        print( "==> Finished at " + str( end_dt ) )
        print( "==> Duration: " + str( end_dt - start_dt ) )
        print( "==> Domains: " + str( domain_counter ) )
        
        return status_OUT
    
    #-- END method create_time_periods_from_ts_data() --#
    
    
    def db_initialize_mysql( self, db_host_IN = "localhost", db_port_IN = 3306, db_username_IN = "", db_password_IN = "", db_database_IN = "" ):
        
        # instance variables
        self.db_initialize( Database_Helper_Factory.DATABASE_TYPE_MYSQLDB, db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END method db_initialize_mysql() --#


    def db_initialize( self, db_type_IN = "", db_host_IN = "localhost", db_port_IN = -1, db_username_IN = "", db_password_IN = "", db_database_IN = "" ):
        
        # instance variables
        self.my_db_helper = Database_Helper_Factory.get_database_helper( db_type_IN, db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END method db_initialize() --#


    def mark_domains_as_news( self, *args, **kwargs ):
    
        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables.

        # auditing
        start_dt = None
        end_dt = None
        
        # interacting with domains
        news_domains_rs = None
        news_domain_count = -1
        news_domain_counter = -1
        current_news_domain = None
        current_news_domain_name = ""
        matching_domain_rs = None
        match_count = -1
        matched_domains_count = -1
        current_reddit_domain = None
        total_match_count = -1
        
        # start datetime
        start_dt = datetime.datetime.now()
        
        # get list of news domains from reference domain table.
        news_domains_rs = django_reference_data.models.Reference_Domain.objects.filter( domain_type = django_reference_data.models.Reference_Domain.DOMAIN_TYPE_NEWS )
        
        # loop over the domains.
        news_domain_count = news_domains_rs.count()
        news_domain_counter = 0
        matched_domains_count = 0
        total_match_count = 0
        for current_news_domain in news_domains_rs:
        
            # increment counter
            news_domain_counter += 1
        
            # get name (converted to lower case)
            current_news_domain_name = current_news_domain.domain_name.lower()

            # look for domains in the reddit domains table that either equal the
            #    domain name or contain "." + domain name (subdomains).
            matching_domains_rs = reddit_collect.models.Domain.objects.filter( Q( name__icontains = "." + current_news_domain_name ) | Q( name__iexact = current_news_domain_name ) )
            
            # got matches?
            match_count = matching_domains_rs.count()
            total_match_count += match_count
            
            # output
            print( "- domain " + str( news_domain_counter ) + " of " + str( news_domain_count ) + ": " + current_news_domain_name + " - matches: " + str( match_count ) )
            
            if ( match_count > 0 ):
            
                # increment matched domains count.
                matched_domains_count += 1
            
                # yes - loop, update each so is_news is True, then save.
                for current_reddit_domain in matching_domains_rs:
                
                    # set is_news flag to true.
                    current_reddit_domain.is_news = True
                    
                    # save.
                    current_reddit_domain.save()
                
                #-- END loop over matching domains. --#
            
            #-- END check to see if matching domains --#
        
        #-- END loop over domains. --#
        
        # summary.
        end_dt = datetime.datetime.now()
        print( "==> News domains processed: " + str( news_domain_count ) )
        print( "==> News domains matched: " + str( matched_domains_count ) )
        print( "==> Total domains updated: " + str( total_match_count ) )
        print( "==> Started at: " + str( start_dt ) )
        print( "==> Ended at: " + str( end_dt ) )
        print( "==> Duration: " + str( end_dt - start_dt ) )
        
        return status_OUT
    
    #-- END method mark_domains_as_news  


#-- END class Data_Creator --#