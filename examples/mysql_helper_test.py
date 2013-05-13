import python_utilities.database.MySQLdb_helper

# initialize database
#db_host = "localhost"
#db_port = 3306
#db_username = ""
#db_password = ""
#db_database = ""

test_helper = python_utilities.database.MySQLdb_helper.MySQLdb_Helper( db_username_IN = db_username, db_password_IN = db_password, db_database_IN = db_database )
test_conn = test_helper.get_connection()
test_cursor = test_helper.get_cursor()
test_query = "SELECT subreddit_name, subreddit_reddit_id, COUNT( * ) AS post_count FROM reddit_collect_post WHERE created_utc_dt BETWEEN '2013-04-15 00:00:00' AND '2013-04-15 01:00:00' GROUP BY subreddit_name;"
test_cursor.execute( test_query )
test_row = test_cursor.fetchone()
