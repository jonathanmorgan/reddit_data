# imports

# urllib
import urllib2

# beautifulsoup 4
from bs4 import BeautifulSoup

# python_utilties
#import python_utilities.beautiful_soup.beautiful_soup_helper

# reddit_data
import reddit_data.models

# declare variables
url_prefix = ""
url_category_path = ""
page_index = -1
current_url = ""
domain_list_html = None
domain_list_bs = None
li_list = None
current_li = None
current_domain_instance = None
temp_bs = None

# fields we collect per domain.
bs_helper = None
current_domain_name = ""
slash_index = ""
current_domain_path = ""
current_description = ""
current_source = ""
current_source_details = ""
current_domain_type = ""
current_is_news = True
current_rank = -1

# init beautiful soup helper
#bs_helper = python_utilities.beautiful_soup.beautiful_soup_helper.BeautifulSoupHelper()

# loop over URLs
url_prefix = "http://www.alexa.com/topsites/category;"
page_index = -1
#url_category_path = "/Top/News" # all news
#page_count = 21
url_category_path = "/Top/News/Magazines_and_E-zines" # magazines and e-zines
page_count = 4
#url_category_path = "/Top/News/Newspapers" # all newspapers
#url_category_path = "/Top/News/Newspapers/Regional" # regional newspapers
for page_index in range( page_count ):

    # read in page of results from alexa.
    current_url = url_prefix + str( page_index ) + url_category_path
    domain_list_html = urllib2.urlopen( current_url )
    
    print( "==> Current URL: " + current_url )
    
    # initialize beautifulsoup instance
    domain_list_bs = BeautifulSoup( domain_list_html )
    
    # Looking for all <li> tags like this:
    # <li class="site-listing">
    li_list = domain_list_bs.find_all( "li", "site-listing" )
    
    # loop over <li> elements, creating reference_domain for each.
    for current_li in li_list:
    
        # collect information - init
        current_domain_name = ""
        slash_index = ""
        current_domain_path = ""
        current_description = ""
        current_source = ""
        current_source_details = ""
        current_domain_type = ""
        current_is_news = True
        current_rank = -1
        
        # description
        temp_bs = current_li.find( "h2" )
        current_description = temp_bs.get_text()
        
        # domain name
        temp_bs = current_li.find( "span", "topsites-label" )
        current_domain_name = temp_bs.get_text()
        
        # strip off https://
        current_domain_name = current_domain_name.replace( "https://", "" )
        
        # strip off www
        current_domain_name = current_domain_name.replace( "www", "" )
        
        # domain path?
        slash_index = current_domain_name.find( "/" )
        if ( slash_index >= 0 ):
        
            # there is path information in domain.  Take string from "/" to end,
            #    store it as domain path.  Take string up to but not including
            #    the "/", keep that as domain.
            current_domain_path = current_domain_name[ slash_index : ]
            current_domain_name = current_domain_name[ : slash_index ]
        
        else:
        
            # no slashes - make sure path is empty.
            current_domain_path = ""
        
        #-- END check to see if path information. --#

        # rank
        temp_bs = current_li.find( "div", "count" )
        current_rank = int( temp_bs.get_text() )
        
        # always the same for these.
        current_source = "alexa"
        current_source_details = current_url
        current_domain_type = reddit_data.models.Reference_Domain.DOMAIN_TYPE_NEWS
        current_is_news = True
        
        # make Reference_Domain instance
        current_domain_instance = reddit_data.models.Reference_Domain()
        
        # set values
        current_domain_instance.domain_name = current_domain_name
        current_domain_instance.domain_path = current_domain_path
        # current_domain_instance.long_name = None
        current_domain_instance.description = current_description
        current_domain_instance.source = current_source
        current_domain_instance.source_details = current_source_details
        current_domain_instance.domain_type = current_domain_type
        current_domain_instance.is_news = current_is_news
        # current_domain_instance.is_multimedia = False
        current_domain_instance.rank = current_rank

        # save
        current_domain_instance.save()
    
    #-- END loop over <li> elements --#

#-- END loop over pages in list. --#