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

# site-specific imports.
#site_path = '/home/socs/socs_reddit/'
#if site_path not in sys.path:
#    sys.path.append( site_path )

#import myLib
import reddit_collect.models

# python_utilities
# from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited
from python_utilities.strings.string_helper import StringHelper
from python_utilities.database.MySQLdb_helper import MySQLdb_Helper

# ReddiWrapper
# from reddiwrap.ReddiWrap import ReddiWrap


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
    

    def create_domains_from_posts( self, include_all_IN = False, limit_IN = -1, *args, **kwargs ):
    
        '''
        Uses an SQL query to get all domains from posts in the database.  For
            each, creates a domain model instance, saves it, gets ID, then uses
            SQL to update all posts and data rows that reference the domain
            with its ID.
            
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
        
        # reading in subreddit names and IDs.
        db_helper = None
        db_conn = None
        db_read_cursor = None
        sql_string = ""
        result_count = -1
        current_row = None
        domain_instance = None
        domain_name = ""
        domain_counter = -1
        domain_model_id = -1
        
        # UPDATE-ing posts and comments.
        sql_update = ""
        
        # First, get a connection and a cursor
        db_helper = self.my_db_helper
        db_conn = db_helper.get_connection()
        db_read_cursor = db_helper.get_cursor()
        db_write_cursor = db_helper.get_cursor()
        
        # create SQL string.
        sql_string = "SELECT DISTINCT domain"
        sql_string += " FROM reddit_collect_post"
        sql_string += " WHERE"
        sql_string += " ( ( domain != '' ) AND ( domain IS NOT NULL ) )"
        
        # Include all?
        if ( include_all_IN == False ):
    
            # No - just include those without an ID.
            sql_string += " AND ( ( domain_id IS NULL ) OR ( domain_id <= 0 ) )"
            
        #-- END check to see if include all --#

        sql_string += " ORDER BY domain"
        
        # got a limit?
        if ( ( limit_IN ) and ( limit_IN > 0 ) ):
    
            # we do.  Add it.
            sql_string += " LIMIT 10"
        
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
        domain_counter = 0
        for i in range( result_count ):

            # increment counter
            domain_counter += 1

            # get row.
            current_row = db_read_cursor.fetchone()
            
            # get values.
            domain_name = current_row[ 'domain' ]
             
            try:
            
                # lookup to see if domain already in database.
                domain_instance = reddit_collect.models.Domain.objects.get( domain_name__iexact = domain_name )
            
                # already in database.  Move on.    
            
            except Exception as e:            
            
                # not in database.  Add it.
                domain_instance = reddit_collect.models.Domain()
                
                # set values
                domain_instance.domain_name = domain_name

                # domain name longer than 255?
                if ( len( domain_name ) > 255 ):

                    # yes - store in long name, as well.
                    domain_instance.domain_long_name = domain_name
                
                #-- END check to see if long domain name --#
                
                # start with "self."?
                if ( domain_name.lower().find( "self." ) == 0 ):
                
                    # yes - set flag.
                    domain_instance.is_self_post = True
                    
                #-- END check to see if self-post --#
               
                # save it.
                domain_instance.save()
            
            #-- END try/except to see if domain already in database. --#

            # get ID from instance.
            domain_model_id = domain_instance.id
            
            # got an ID?
            if ( ( domain_model_id ) and ( domain_model_id != None ) and ( domain_model_id > 0 ) ):
            
                # we do.  Update relation in posts, comments fields.
                
                # UPDATE posts
                db_write_cursor.execute( "UPDATE `reddit_collect_post` SET domain_id = %s WHERE domain_name = %s;", ( domain_model_id, domain_name ) )
                
                # UPDATE domain time-series data
                db_write_cursor.execute( "UPDATE `reddit_data_domain_time_series_data` SET domain_id = %s WHERE domain_name = %s;", ( domain_model_id, domain_name ) )

                # commit changes
                db_conn.commit()
            
            #-- END check to see if model ID --#
            
            if ( self.debug_flag == True ):
            
                print( "- Processed domain " + str( subreddit_counter ) + " of " + str( result_count ) + " ( " + str( datetime.datetime.now() ) + " ) - ID: " + str( domain_model_id ) + "; name = " + domain_name )
            
            #-- END DEBUG check --#
            
            # clear caches, performance stuff, etc.  Try garbage
            #    collecting, not clearing django cache, to start.
            gc.collect()
            django.db.reset_queries()

        #-- END loop over domains. --#
        
        return status_OUT
    
    #-- END method create_domains_from_posts() --#
    
    
    def create_subreddits_from_posts( self, include_all_IN = False, limit_IN = -1, *args, **kwargs ):
    
        '''
        Uses an SQL query to get all subreddit names and IDs from posts in the
            database.  For each, creates a subreddit model instance, saves it,
            gets ID, then uses SQL to update all posts and data rows that
            reference the subreddit with its ID.
            
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
            sql_string += " LIMIT 10"
        
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
                subreddit_instance = reddit_collect.models.Subreddit.objects.get( reddit_full_id__iexact = subreddit_reddit_id )
            
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
            
                # we do.  Update relation in posts, comments fields.
                
                # UPDATE posts
                db_write_cursor.execute( "UPDATE `reddit_collect_post` SET subreddit_id = %s WHERE subreddit_reddit_id = %s;", ( subreddit_model_id, subreddit_id ) )
                
                # UPDATE comments
                db_write_cursor.execute( "UPDATE `reddit_collect_comment` SET subreddit_id = %s WHERE subreddit_reddit_id = %s;", ( subreddit_model_id, subreddit_id ) )

                # UPDATE subreddit time-series data
                db_write_cursor.execute( "UPDATE `reddit_data_subreddit_time_series_data` SET subreddit_id = %s WHERE subreddit_reddit_id = %s;", ( subreddit_model_id, subreddit_id ) )

                # commit changes
                db_conn.commit()
            
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
    
    
    def db_initialize_mysql( self, db_host_IN = "localhost", db_port_IN = 3306, db_username_IN = "", db_password_IN = "", db_database_IN = "" ):
        
        # instance variables
        self.my_db_helper = MySQLdb_Helper( db_host_IN, db_port_IN, db_username_IN, db_password_IN, db_database_IN )
        
    #-- END class method db_initialize_mysql() --#

    
#-- END class Data_Creator --#