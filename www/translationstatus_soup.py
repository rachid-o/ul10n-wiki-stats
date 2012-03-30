# Author RachidBM <https://launchpad.net/~rachidbm>

# This class uses BeautifulSoup parser, much slower than LXML, but this works on Google App Engine 
import urllib2, re
import datetime
from BeautifulSoup import BeautifulSoup

VERSION="0.4.8"

URL_PREFIX = "https://translations.launchpad.net/"
NEWLINE = "\n"
TOOL_URL = "http://rachidbm.appspot.com/"
"""
TODO: 
 - Pass function or "thing to call" to print messages for logging to (CLI=stdout, HTML=string writer?)
"""

class TranslationStatus:
    """
    Retrieve information from a wiki page and current status of translations from Launchpad. 
    Combine them to output a table in wiki syntax
    """

    # public
    PRINT_FINISHED_TRANSLATIONS = False
    """True, print finished packages (with 0 untranslated strings).
    This means always print all packages from Launchpad URL"""

    PRINT_NEEDSREVIEW_TRANSLATIONS = False
    """True, print packages with new suggestions (needs review is > 0)"""

    PRINT_RESERVED_PACKAGES = True
    """True, print packages which were already reserved on the wiki by a translator or reviewer"""

    WIKI_OVERRIDES_LP_URL = True
    """True, URL to Launchpad will be overridden by an URL found on the wiki (if found)"""
    
    STDOUT_DEBUG_MESSAGES = False
    """True, print debug messages"""

    # private   
    __WIKI_URL = ""
    __WIKI_URL_RAW = ""
    __LP_URL = ""
    __WIKI_CONTENT = ""
    __wikidata = {}

    def __init__(self, WIKI_URL):
        self.__WIKI_URL = WIKI_URL
        self.__WIKI_URL_RAW = WIKI_URL + "?action=raw"
        #self.__LP_URL = LP_URL

    def setLP_URL(self, LP_URL):
        self.__LP_URL = LP_URL

    def addline(self, line):
        """Adds a line to the wiki content"""
        self.__WIKI_CONTENT += line + NEWLINE

    def generate_wiki_table(self):
        """Return a table which can be inserted into a wiki page. """

        self.process_wiki()
        #Retrieve HTML from Launchpad
        #htmlfile = urllib2.urlopen(self.__LP_URL)
        #self.addline("## __ Opening: "+self.__LP_URL)
        #return self.__WIKI_CONTENT

        response = self.get_response_from_url(self.__LP_URL)
        if response == "":
            return self.__WIKI_CONTENT

        htmlfile = response.read()
        #print htmlfile
        #f = open('test-soup.html', 'r')
        #htmlfile = f.read()
        soup = BeautifulSoup(htmlfile)

#       doc = etree.parse(htmlfile, etree.HTMLParser()).getroot()
#       tbl = doc.xpath("/html//table[2]//tr")
        tbl = soup.html.body.findAll("table")[1]

        # Print header of the wiki table
        url_wiki_edit  = "||<style=\"text-align:left; border:0;\" colspan=\"3\"> [[%s?action=edit|Manually edit this list]] ||" % (self.__WIKI_URL)
        url_lp_sync = "<style=\"text-align:right; border:0;\" colspan=\"3\"> [[%s?url_wiki=%s|Synchronize this list with Launchpad|target=\"_new\"]] ||" % (TOOL_URL, self.__WIKI_URL) 

        self.addline(url_wiki_edit + url_lp_sync)
        self.addline("||'''Package''' || '''Untranslated''' || '''Needs Review''' || '''Translator''' || '''Reviewer'''||'''Remark'''||")

        total_untr = 0
        total_review = 0
        total_untr_upstream = 0
        total_review_upstream = 0

        packages_processed = 0      # Count the processed packages (rows)
        packages_added = 0      # Count the added packages (rows)

        ## Read the HTML <table>, loop all rows and process packages
        for tr in tbl.findAll("tr"):
            tds =  tr.findAll("td")

            if(len(tds) > 7):

                packages_processed+=1
                ## Name and LP_URL
                tp = tds[0].findAll('a')[0]
                
                p_url = tp['href']
                p_name = tp.contents[0]

                ## Untranslated
                p_untr_name = "0"
                p_untr_url = ""
                tu = tds[3].findAll('a')
                if len(tu) > 0:
                    p_untr_name = tu[0].contents[0]
                    p_untr_url = tu[0]['href']

                ## Review
                p_review_name = "0"
                p_review_url = ""
                trev = tds[4].findAll('a')
                if len(trev) > 0:
                    p_review_name = trev[0].contents[0]
                    p_review_url = trev[0]['href']

                ## Fill in current data from wiki           
                p_translator = ""
                p_reviewer = ""

                if p_name in self.__wikidata:
                    p_translator = self.__wikidata[p_name][0]
                    p_reviewer = self.__wikidata[p_name][1]

                ## Some logic to determine if we may print this row to wiki table
                may_print = False

                if int(p_untr_name) > 0: 
                    # If there are untranslated strings, always print
                    may_print = True
                elif self.PRINT_FINISHED_TRANSLATIONS:
                    # If you want to print untranslated strings
                    may_print = True
                elif self.PRINT_RESERVED_PACKAGES and (len(p_translator) > 0 
                    or len(p_reviewer) > 0):
                    # If it was reserved already on the wiki let it stay on the list
                    may_print = True
                elif self.PRINT_NEEDSREVIEW_TRANSLATIONS and int(p_review_name) > 0:
                    may_print = True

                # Print the row
                if may_print:
                    self.addline(self.get_wiki_row(p_name, p_untr_name, p_untr_url, p_review_name, p_review_url, p_translator, p_reviewer))
                    packages_added += 1

                    total_untr = total_untr + int(p_untr_name)
                    total_review = total_review + int(p_review_name)

                    if p_name in self.__wikidata:
                        if self.__wikidata[p_name][4] == True: 
                            total_untr_upstream = total_untr_upstream + int(p_untr_name)
                            total_review_upstream = total_review_upstream + int(p_review_name)

                #else:
                #   debug ("## %s is skipped" % (p_name))

        # Add some information
        self.addline("||<style=\"border:0;\"> Total untranslated ||<style=\"border:0;\"> %s ||<style=\"border:0;\"> %s ||<style=\"border:0; colspan=3;\">  ||" % (total_untr, total_review))
        self.addline("||<style=\"border:0;\"> Total upstream ||<style=\"border:0;\"> %s ||<style=\"border:0;\"> %s ||<style=\"border:0; colspan=3;\"> ||" % (total_untr_upstream, total_review_upstream))
        self.addline("||<style=\"border:0;\"> TODO ||<style=\"border:0;\"> '''%s''' ||<style=\"border:0;\"> '''%s''' ||<style=\"border:0; colspan=3;\"> ||" % (total_untr-total_untr_upstream, total_review-total_review_upstream))

        self.addline("%sLast synchronization with Launchpad: %s (UTC)" % (NEWLINE+NEWLINE, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")))
        self.addline("<<BR>>%d packages in this list" % (packages_added))
        self.addline("## %d were packages processed" % (packages_processed))
        self.addline("## Version of the tool: %s" % (VERSION))
        return self.__WIKI_CONTENT
    ## END: generate_wiki_table()


    def process_wiki(self):
        """
        Reads the wiki page from __WIKI_URL_RAW and filter useful data from it
        In certain conditions it will search for LP_URL   
        Return a dictionary with wikidata. key is package_name, values are (translator, review)     
        """

        self.__wikidata = {}

        #response = urllib2.urlopen(self.__WIKI_URL_RAW)
        response = self.get_response_from_url(self.__WIKI_URL_RAW)
        if response == "":
            return ""

        #response = open("/tmp/test.txt", "r")
        lines = response.readlines()
        SEARCH_WIKI_FOR_LP_URL = True
        for line in lines:


            # First retrieve URL to Launchpad 
            if SEARCH_WIKI_FOR_LP_URL and self.WIKI_OVERRIDES_LP_URL:

                # Copy comments from the wiki
                if(line.find("##") == 0):
                    self.addline(line.strip())

                #debug(find(line, "LAUNCHPAD_URL"))
                if(line.find("LAUNCHPAD_URL") > 0):
                    # TODO instead of regex do: split("=")[1].strip()
                    #self.__LP_URL = re.sub("##\s*LAUNCHPAD_URL\s*=\s*", "", line).strip()  # Get the URL
                    u = re.sub("##\s*LAUNCHPAD_URL\s*=\s*", "", line).strip()   # Get the URL
                    #self.addline("## Found: "+u)
                    self.__LP_URL = u
                    SEARCH_WIKI_FOR_LP_URL = False
                    #debug("Found Launchpad URL on the wiki page: %s " %(__LP_URL))

            else:
                tokens = line.split("||")
                # Only when enough tokens AND NOT the header of the table
                if(len(tokens) >= 7 and not tokens[1].startswith("'''")):
                    review = False
                    upstream = False
                    pname = tokens[1].strip()

                    # GAE does not support flags=re.IGNORECASE
                    #package_name = re.sub("<#cccccc>", "", pname, flags=re.IGNORECASE).strip()   # Strip upstream?
                    package_name = re.sub("<#cccccc>", "", pname).strip()   # Strip upstream?
                    if package_name != pname:
                        upstream = True
                    else: 
                        package_name = re.sub("<#00AAFF>", "", pname).strip()   # Strip review?
                        if package_name != pname:
                            review = True
                        else:
                            package_name = re.sub("<[^>]*>", "", tokens[1].strip())     # Strip color code

                    translator = tokens[4].strip()
                    reviewer = tokens[5].strip()
                    remark = tokens[6].strip()

                    # If 1 of the fields is filled in
                    if len(translator) > 0 or len(reviewer) > 0 or len(remark) > 0 or upstream or review:
                        self.__wikidata[package_name] = (translator, reviewer, remark, review, upstream)

    ## END: process_wiki()


    def get_wiki_row(self, name, u_nr, u_url, r_nr, r_url, translator, reviewer):
        """Return a row in wiki-syntax."""
        u = u_nr
        r = r_nr

        ## Fill in current data from wiki
        remark = ""
        review = False
        upstream = False
                
        if name in self.__wikidata:
            remark = self.__wikidata[name][2]
            review = self.__wikidata[name][3]
            upstream = self.__wikidata[name][4]

        color = "<#FF5555>"         # Default color is red
        if upstream:
            color = "<#cccccc>"     # grey
        elif u_nr == "0":
            if r_nr != "0":
                color = "<#00AAFF>"     # blue
                r = "[["+URL_PREFIX+r_url+"|"+r_nr+"|target=\"_new\"]]"
            else:
                color = "<#55FF55>"     # green
        elif review:
            color = "<#00AAFF>"     # blue
            u = "[["+URL_PREFIX+u_url+"|"+u_nr+"|target=\"_new\"]]"
        else:
            color = "<#FF5555>"     # red
            u = "[["+URL_PREFIX+u_url+"|"+u_nr+"|target=\"_new\"]]"

        if r_nr != "0" and not upstream:
            r = "[["+URL_PREFIX+r_url+"|"+r_nr+"|target=\"_new\"]]"

        name = color+name
        return "||%s ||%s ||%s || %s || %s || %s ||" % (name, u, r, translator, reviewer, remark)
    #END get_wiki_row


    def get_response_from_url(self, url):
        response = ""
        # response = urllib2.urlopen(url)
        opener = urllib2.build_opener()
        # headers = {'Cache-Control' : 'max-age=240'}
        opener.addheaders = [('Cache-Control', 'max-age=10')]
        response = opener.open(url)

        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            self.addline('The server couldn\'t fulfill the request to '+url)
            self.addline('Error code: '+ str(e.code))
            return "";
        except urllib2.URLError, e:
            self.addline('We failed to reach the server on ' + url)
            self.addline('Reason: ' + str(e.reason))
            return "";
        except ValueError, e:
            #print e
            self.addline('invalid url')

        return response
    #END: get_response_from_url

#END: TranslationStatus


def debug(message):
    """Print a DEBUG message"""
    if(STDOUT_DEBUG_MESSAGES):
        print "DEBUG: %s" % (message)
#END debug      
