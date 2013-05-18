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

- pull in Jon's python\_utilities

        git clone https://github.com/jonathanmorgan/python_utilities.git

- pull in the python reddit\_collect code

        git clone https://github.com/jonathanmorgan/reddit_collect.git
    
- pull in the python reddit\_data code

        git clone https://github.com/jonathanmorgan/reddit_data.git
    
### Configure

- To start, setup and configure reddit\_collect, using the instructions in its README.md file.

- from the site\_directory, cd into the site configuration directory, where settings.py is located (it is named the same as site\_directory, but nested inside site\_directory, alongside all the other django code you pulled in from git - <site\_directory>/<same\_name\_as\_site\_directory>).

        cd <same_name_as_site_directory>

- in settings.py, set USE_TZ to false to turn off time zone support:

        USE_TZ = False

- configure the database in settings.py - for database configuration, this code assumes that you set up the database as directed in reddit\_collect's README.md file.

- in settings.py, add 'reddit\_data' to the INSTALLED\_APPS list.  Example:
    
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
            'reddit_collect',
            'south',
            'reddit_data',
        )

- once you get settings.py configured, then run `python manage.py migrate reddit_data` in your site directory to create database tables.

### Set up database - all versions MySQL:

- Create indexes on columns we use to check for duplicates/look up existing records (reddit ID, for example).  _This is really important!  As your table grows, an un-indexed lookup will slow WAY down!_

    - columns on the reddit\_data\_subreddit\_time\_series\_data:

            ALTER TABLE `socs_reddit`.`reddit_data_subreddit_time_series_data` ADD INDEX `subreddit_reddit_id` (subreddit_reddit_id);

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

Then, regardless, you'll need to do the following to set up the collector:

## Notes

## TODO

## Questions

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