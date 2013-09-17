# reddit_data = social science data creator for reddit data.

This code interacts with data from reddit in a database to build data that can be used for social science analysis.

## Installation

- install pip

        (sudo) easy_install pip

- install django

        (sudo) pip install django

- install South (data migration tool), if it isn't already installed.

        (sudo) pip install South

- in your work directory, create a django site.

        django-admin.py startproject <site_directory>
    
- cd into the site\_directory

        cd <site_directory>
    
- pull in reddiwrap

        git clone https://github.com/derv82/reddiwrap.git

- add empty file named "\_\_init\_\_.py" to the reddiwrap folder, so it can be accessed as a python module.

        touch reddiwrap/__init__.py

- pull in python\_utilities

        git clone https://github.com/jonathanmorgan/python_utilities.git

- pull in the python reddit\_collect code

        git clone https://github.com/jonathanmorgan/reddit_collect.git
    
- pull in the python django\_time\_series code

        git clone https://github.com/jonathanmorgan/django_time_series.git
    
- pull in the python django\_reference\_data code

        git clone https://github.com/jonathanmorgan/django_reference_data.git
    
- pull in the python reddit\_data code

        git clone https://github.com/jonathanmorgan/reddit_data.git
    
### Configure

- To start, setup and configure reddit\_collect, using the instructions in its README.md file.

- from the site\_directory, cd into the site configuration directory, where settings.py is located (it is named the same as site\_directory, but nested inside site\_directory, alongside all the other django code you pulled in from git - <site\_directory>/<same\_name\_as\_site\_directory>).

        cd <same_name_as_site_directory>

- in settings.py, set USE_TZ to false to turn off time zone support:

        USE_TZ = False

- configure the database in settings.py - for database configuration, this code assumes that you set up the database as directed in reddit\_collect's README.md file.

- in settings.py, add 'django\_time\_series', 'django\_reference\_data', and 'reddit\_data' to the INSTALLED\_APPS list.  Example:
    
        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            # Uncomment the next line to enable the admin:
            # 'django.contrib.admin',
            # Uncomment the next line to enable admin documentation:
            # 'django.contrib.admindocs',
            'south',
            'reddit_collect',
            'django_time_series',
            'django_reference_data',
            'reddit_data',
        )

- once you get settings.py configured, then run the following in your site directory to create database tables, set up indexes, etc.:

        python manage.py migrate django_time_series
        python manage.py migrate django_reference_data
        python manage.py migrate reddit_data

## Usage

### Getting started and initialization

The easiest way to run code from a shell is to go to your django sites folder and use manage.py to open a shell:

    python manage.py shell
    
If you choose, you can also just open the base python interpreter:

    python
    
Or you can install something fancier like ipython (`pip install ipython`. or install it using your OS's package manager), and then run ipython:

    ipython
    
If you don't use manage.py to open a shell (or if you are making a shell script that will be run on its own), you'll have to do a little additional setup to pull in and configure django:

    # make sure the site directory is in the sys path.
    import sys
    site_path = '<site_folder_full_path>'
    if site_path not in sys.path:
        
        sys.path.append( site_path )
        
    #-- END check to see if site path is in sys.path. --#
    
    # if not running in django shell (python manage.py shell), make sure django
    #    classes have access to settings.py
    # set DJANGO_SETTINGS_MODULE environment variable = "<site_folder_name>.settings".
    import os
    os.environ[ 'DJANGO_SETTINGS_MODULE' ] = "<site_folder_name>.settings"

Then, there are numerous examples in /examples you can use to try out different ways of making reddit data:

- domain\_create\_rows\_from\_posts.py - create domain instances from posts, then put domain model instance IDs back into the posts so the relations are available to django.
- domain\_mark\_is\_news.py - uses django\_reference\_data's ReferenceDomain model, populated with news domains from fixture django\_reference\_data/fixtures/reference\_domains\_news.json
- domain\_time\_series.py - create per-domain time series data from a set of reddit posts.
- mysql\_helper\_test.py - basic - how to use mysql_helper.
- subreddit\_filter.py - filters time series data based on a text match, then updates filter flag on time series records to record the filter matches.
- subreddit\_lookup.py - basic - lookup subreddit time series data using django.
- subreddit\_rows\_from\_posts.py - create subreddit instances from posts, then put subreddit model instance IDs back into the posts so the relations are available to django.
- subreddit\_time\_series.py - create per-subreddit time series data from a set of reddit posts.

### Mark reddit posts as news or not

- make sure to install the django\_reference\_data application.
- clear out the django\_reference\_data\_reference\_domain table, then load the fixture django\_reference\_data/fixtures/reference\_domains\_news.json:

        python manage.py loaddata django_reference_data/fixtures/reference_domains_news.json
        
- create reddit\_collect Domain rows for all domains in your posts (see django\_reference\_data/examples/domain\_create\_rows\_from\_posts.py)
    - this doesn't happen automatically when you collect reddit posts (to maximize performance).
    - this process creates the Domain records, then associates them with Reddit Posts and time series data that reference each domain.
    - this process can be re-run multiple times
- per the file reddit\_data/examples/domain\_mark\_is\_news.py, run the `mark_domains_as_news()` method to match reddit\_data Domains with news domains in reference data, and mark matches in the reddit\_data Domain set as `is_news = True`.
- now to update posts that have URLs that reference news domains.  To start, if you are making iterative changes to your domains, before you filter posts, clear out the flag you are setting each time you set flags, in case you changed the classification of any domains in such a way that posts that matched before will no longer match.

        UPDATE reddit_collect_post SET filter_2 = 0 WHERE filter_2 = 1;

- update one of the filters on each post (filter\_2 is updated below) based on the is_news flag of its associated domain.  SQL:

        /* first, run SELECT to see how many matches there are */
        /* SELECT * */
        SELECT COUNT( * )
        FROM reddit_collect_post rcp, reddit_collect_domain rcd
        WHERE rcp.domain_id = rcd.id
            AND rcd.is_news = 1;
            
        /* more detailed spot-check */
        SELECT rcp.id, rcp.domain_name, rcp.domain_id, rcd.id, rcd.name
        FROM reddit_collect_post rcp, reddit_collect_domain rcd
        WHERE rcp.domain_id = rcd.id
            AND rcd.is_news = 1
        LIMIT 25000, 100;
            
        /* if all looks OK, update */
        UPDATE reddit_collect_post rcp, reddit_collect_domain rcd
        SET rcp.filter_2 = 1
        WHERE rcp.domain_id = rcd.id
            AND rcd.is_news = 1;

### Create time series data tracking traits of subreddits over time

The basic steps for creating subreddit time series data:

- If you have generated subreddits for a subset of your posts before, you might want to:
    - wipe the subreddit_id column clean in all of your posts, so all subreddits are processed, even those that were created before.

            /* clean out subreddit IDs. */
            UPDATE reddit_collect_post
            SET subreddit_id = NULL;
            
            UPDATE reddit_collect_comment
            SET subreddit_id = NULL;
            
            UPDATE reddit_data_subreddit_time_series_data
            SET subreddit_id = NULL;

    - also delete all records in reddit\_collect\_subreddit (`DELETE FROM reddit_collect_subreddit;`, making sure to also reset the auto-increment value to 1 (`ALTER TABLE reddit_collect_subreddit AUTO_INCREMENT = 1;`).

- Populate the reddit\_collect\_subreddit table with the subreddits in your posts (see examples/subreddit\_rows\_from\_posts.py).  This process also updates the relations of posts, comments, and time series data so they reference the reddit\_collect\_subreddit row to which they are related.  If subreddits are already present in the reddit\_collect\_subreddit table, it will use them, not create duplicates, and so this process can be run multiple times without clearing out the subreddit table.
- configure variables so you get the time series data you want, and have it categorized and numbered appropriately.  You need to know:
    - start and end date of range you want to examine time periods within.
    - time-series interval: datetime.timedelta instance that contains the time-series interval (it could be a minute, an hour, or a week, depending on your data and what you want to compare).
    - time-series type: text description of the time-series interval you are using (so, if interval is one hour, say "hourly").  Could also be used for other typologies.
    - time-series label: label to describe the data.  For a before and after experiment, you could use "before" and "after", for example.
    - starting aggregate index: If, say, you have before and after, but you also want to keep a running count across labels, you can pass an aggregate index start value and keep a running count across runs of the time-series data creation.
    - Example:
        
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
            time_period_type = reddit_data.models.Subreddit_Time_Series_Data.TIME_PERIOD_HOURLY
            
            # time-period label: another place to document different parts of time-series
            #    data - in this case, will use to divide between before and after.
            time_period_label = "before"
            
            # aggregate counter start: you can tell the program to start its time period
            #    counter at other than 0, so you can have a continuous counter even if you
            #    break this processing into multiple stages (if, say, you want "before" and
            #    "after", but want the counter to be continuous across before and after).
            aggregate_counter_start = 0

- Before you run the time-series data creator, consider if you need to wipe existing rows.  If you've added posts to or removed posts from the time periods you are studying since doing an initial run of time series data, you might consider doing a fresh creation on a clean database (especially if you've removed posts).  To do this, simply delete the rows from the table (`DELETE FROM reddit_data_subreddit_time_series_data;`) then reset the auto-increment value (`ALTER TABLE reddit_data_subreddit_time_series_data AUTO_INCREMENT = 1;`).
- Actually run the time-series data creation.  If a given row already exists in the data set for a given time-series period, if there are posts associated with the subreddit, it will update the row.  If not, it will just leave the existing row alone.  If a given subreddit's posts are added to a given time period, then you should be able to re-run the process to just add new subreddits.  If a given subreddit's posts are removed from a time period, that time-period's data will, at the moment, either have to be cleaned up manually or wiped and re-generated.

        from python_utilities.database.database_helper_factory import Database_Helper_Factory

        # initialize database
        db_host = "localhost"
        db_port = 3306
        db_username = "<username>"
        db_password = "<password>"
        db_database = "<database>"
        
        reddit_data.models.Subreddit_Time_Series_Data.db_initialize( Database_Helper_Factory.DATABASE_TYPE_MYSQLDB, db_host, db_port, db_username, db_password, db_database )
        
        # call make_data.
        reddit_data.models.Subreddit_Time_Series_Data.make_data( start_date, end_date, time_series_interval, time_period_type, time_period_label, aggregate_counter_start, output_details_IN = True )

### Create time series data tracking traits of domains over time

## Thanks!

This work has been supported by the National Science Foundation under Grant IIS-0968495.

## License:

Copyright 2012, 2013 Jonathan Morgan

This file is part of [http://github.com/jonathanmorgan/reddit_data](http://github.com/jonathanmorgan/reddit_data).

reddit\_data is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

reddit\_data is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with [http://github.com/jonathanmorgan/reddit_data](http://github.com/jonathanmorgan/reddit_data).  If not, see
[http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).