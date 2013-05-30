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

# processing state list.
state_name = ""
state_url = ""
state_file_path = ""
state_file = None

# processing a state's page.
state_html = None
state_bs = None
state_paper_list = None
state_paper_li = None
paper_name = ""
paper_url = ""
current_domain_instance = None
paper_counter = -1

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

# clean out broken texas domain rows.
'''
DELETE from `reddit_data_reference_domain`
WHERE source_details LIKE '%in-texas%';
'''

state_name = "Texas"
state_url = "http://www.listofnewspapers.com/en/north-america/texan-newspapers-in-texas.html"
state_file_path = "texan-newspapers-in-texas-TIDY.html"

# print next state:
print( "==> processing " + state_name + ": " + state_file_path )

# load the state's HTML
state_file = open( state_file_path, "r" )
state_html = state_file.read()

# let BeautifulSoup parse it.
state_bs = BeautifulSoup( state_html, "html.parser" )

# get list of papers.
state_paper_list = state_bs.find_all( "li", "linewspapers" )

print( "- paper count: " + str( len( state_paper_list ) ) )

# loop over papers.
paper_counter = 0
for state_paper_li in state_paper_list:

    paper_counter += 1

    print( "- paper " + str( paper_counter ) + ": " + str( state_paper_li ) )

    # get values
    paper_name = state_paper_li.get_text()
    paper_url = state_paper_li.a[ 'href' ]
    
    print( "    - " + paper_name + ": " + paper_url )

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
    current_description = paper_name
    
    # domain name
    current_domain_name = paper_url
    
    # strip off https://
    current_domain_name = current_domain_name.replace( "https://", "" )
    
    # strip off http://
    current_domain_name = current_domain_name.replace( "http://", "" )
    
    # strip off www.
    current_domain_name = current_domain_name.replace( "www.", "" )
    
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
    
    # is path just "/"?  If so, set to "".
    if ( current_domain_path == "/" ):
    
        # yup. Set to "".
        current_domain_path = ""
    
    #-- END check to see if path is just "/" --#

    # no rank
    
    # always the same for these.
    current_source = "listofnewspapers.com"
    current_source_details = state_url
    current_domain_type = reddit_data.models.Reference_Domain.DOMAIN_TYPE_NEWS
    current_is_news = True
    
    # make Reference_Domain instance
    current_domain_instance = reddit_data.models.Reference_Domain()
    
    # set values
    current_domain_instance.domain_name = current_domain_name
    current_domain_instance.domain_path = current_domain_path
    #current_domain_instance.long_name = None
    current_domain_instance.description = current_description
    current_domain_instance.source = current_source
    current_domain_instance.source_details = current_source_details
    current_domain_instance.domain_type = current_domain_type
    current_domain_instance.is_news = current_is_news
    #current_domain_instance.is_multimedia = False
    #current_domain_instance.rank = current_rank

    # save
    current_domain_instance.save()

#-- END loop over papers. --#