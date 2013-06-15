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
state_list_url = ""
state_list_html = None
state_list_bs = None
data_box_div_list = None
state_list_div = None
state_a_list = None
state_name = ""
state_url = ""

# only process certain states
# skip 'Texas'.
#states_to_process_list = [ 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming', 'American Samoa', 'Federated States of Micronesia', 'Guam', 'Northern Mariana Islands', 'Puerto Rico', 'US Virgin Islands' ]
states_to_process_list = [ 'Massachusetts', ]

# processing a state's page.
state_html = None
state_bs = None
data_box_div_list = None
station_list_div = None
station_list_container = None


state_paper_list = None
state_paper_li = None
paper_name = ""
paper_url = ""
current_domain_instance = None

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

# first, pull in list of state pages on this site.
state_list_url = "http://www.usnpl.com/index_radio.php"
state_list_html = urllib2.urlopen( state_list_url )

# create beautifulsoup instance for state list.
#bs_parser = "html.parser"
#bs_parser = "lxml"
bs_parser = "html5lib"
state_list_bs = BeautifulSoup( state_list_html, bs_parser )

# get list of state URLs.

# first, get first <div id="data_box">
data_box_div_list = state_list_bs.find_all( "div", id = "data_box" )
state_list_div = data_box_div_list[ 0 ]

# get list of all <a> inside
state_a_list = state_list_div.find_all( "a" )

# loop over states, opening up each's page and processing newspapers within.
for state_a in state_a_list:

    # get values
    state_name = state_a.get_text()
    state_url = state_a[ 'href' ]
    
    # process this state?
    if ( ( len( states_to_process_list ) == 0 ) or ( ( len( states_to_process_list ) > 0 ) and ( state_name in states_to_process_list ) ) ):

        # print next state:
        print( "==> processing " + state_name + ": " + state_url )
        
        # load the state's URL
        state_html = urllib2.urlopen( state_url )
        
        # let BeautifulSoup parse it.
        state_bs = BeautifulSoup( state_html, "html.parser" )
        
        # get list of data_boxes.
        data_box_div_list = state_bs.find_all( "div", id = "data_box" )
        
        # get div that contains station list
        station_list_div = data_box_div_list[ 1 ]
        
        # inside that <div> is an entire HTML document - get body.
        station_list_container = station_list_div.html.body
        
        # get list of descendants
        descendant_list = list( station_list_container.descendants )
        
        item_counter = 0
        for item in descendant_list:
        
            item_counter += 1
            
            print( "====================== item " + str( item_counter ) )
            
            print( item )
        
        #-- END loop over descendents --#

        # a giant mess.  Bail out now!
        
        '''
        state_paper_list = state_bs.find_all( "li", "linewspapers" )
        
        # loop over papers.
        for state_paper_li in state_paper_list:
        
            # get values
            paper_name = state_paper_li.get_text()
            paper_url = state_paper_li.a[ 'href' ]
        
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
        '''

    else:
    
        # print next state:
        print( "==> skipping " + state_name + ": " + state_url )
    
    #-- END check to see if we proces this state. --#

#-- END loop over states in state list --#