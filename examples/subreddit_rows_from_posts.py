# imports
from reddit_data.data_creator import Data_Creator
from python_utilities.database.database_helper_factory import Database_Helper_Factory

# create Data_Creator instance
my_data_creator = Data_Creator()

# initialize database
#db_host = "localhost"
#db_port = 3306
#db_username = ""
#db_password = ""
#db_database = ""

# initialize the database.
#my_data_creator.db_initialize_mysql( db_host, db_port, db_username, db_password, db_database )
my_data_creator.db_initialize( Database_Helper_Factory.DATABASE_TYPE_MYSQLDB, db_host, db_port, db_username, db_password, db_database )

# turn on debug
my_data_creator.debug_flag = True

# call method.  Much easier than some of these.
#my_data_creator.create_subreddits_from_posts( limit_IN = 10 )
my_data_creator.create_subreddits_from_posts()

# close database connection
my_data_creator.my_db_helper.close()