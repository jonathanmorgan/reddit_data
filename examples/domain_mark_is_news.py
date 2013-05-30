# imports
from reddit_data.data_creator import Data_Creator

# create Data_Creator instance
my_data_creator = Data_Creator()

# turn on debug
my_data_creator.debug_flag = True

# call method.  Much easier than some of these.
# my_data_creator.create_domains_from_posts( limit_IN = 10 )
my_data_creator.mark_domains_as_news()