import cgi
import translationstatus_soup as translationstatus
from include import *

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.urlfetch import DownloadError 

DEFAULT_WIKI_PAGE = "http://wiki.ubuntu-nl.org/Rachid/TranslationTool"

class MainPage(webapp.RequestHandler):
    
    def get(self):
        go = self.request.get('go')
        url_wiki = self.request.get('url_wiki')
        
        wiki_table = ""
        wiki_edit_url = ""
        if url_wiki == "":
            url_wiki = DEFAULT_WIKI_PAGE
        #if url_wiki != "":
            #self.URL_WIKI_PAGE = url_wiki
        if go == "true":
            ts = translationstatus.TranslationStatus(url_wiki)  # LAUNCHPAD_URL_DEFAULT
            try:
                wiki_table = ts.generate_wiki_table() 
                wiki_edit_url = "<a href=\"%s?action=edit\" _target=\"_new\">Edit the wiki page</a>" % (url_wiki) 
            except DownloadError: 
                wiki_table = "ERROR: Occurred during fetching URL, please try again..."
                wiki_table += "\nNote: sometimes it has problems with fetching an URL, hit the button again and it'll probably work..."

        CONTENT =  """<h1>Home</h1>
        Here you can generate a wiki page for status on Launchpad translations.
            <ol>
                <li> Insert the URL to the wiki (status)page in the text field below. </li>  
                <li> Click on "Generate package list". </li>
                <li> When no errors, copy/paste the content of the output. </li>
                <li> Click the "Edit wiki page" to open the wiki page in edit mode. Paste the new content and Save. </li>
                <li> Voil&agrave;! </li>
            </ol>
             
            <br />
            <form method="get" action="/">
                URL:          
                <input type='text' id='url_wiki' name='url_wiki' value='%s' style='width:700px;' />
                <br />
                <input type='submit' value='Generate package list'  /> 
                <!--<span class="note">Note: sometimes it has problems with fetching an URL, but when you try it again it works...</span>-->
                <input type='hidden' id='go' name='go' value='true' />
            </form>
            <br />
            Output for wiki %s<br />
            <textarea id='output' style='width:900px; height:400px;'>%s</textarea>
        """  % (url_wiki, wiki_edit_url, wiki_table)
                        
        self.response.out.write(HEADER + CONTENT + FOOTER)


class Help(webapp.RequestHandler):
    def get(self):
        CONTENT = """<h1>Help</h1>

<p>Example output on a wiki: <a href="%s">%s</a> </p>
<h2>Create new status list</h2>
<p>
Create a wiki page and add the following line: <br />
## LAUNCHPAD_URL = https://translations.launchpad.net/ubuntu/natty/+lang/nl/?batch=300 <br />
Where the URL points to list of packages on Launchpad  <br />
<br />
Follow the instructions on the <a href='/'>homepage</a>. 
 <br />
  <br />
</p>
""" % (DEFAULT_WIKI_PAGE, DEFAULT_WIKI_PAGE)
        self.response.out.write(HEADER + CONTENT + FOOTER)



class About(webapp.RequestHandler):
    def get(self):
        CONTENT = """
<h1>About</h1>
<p>
    This script reads status of translations of packages from Launchpad and generates output to paste on a wiki
    <br />
    Now also available in your browser on <a href="http://rachidbm.appspot.com/">http://rachidbm.appspot.com/</a> <br />
    The code is hosted on Launchpad: <a href="http://bazaar.launchpad.net/~rachidbm/ubuntu-nl/translating-scripts/files">here</a>. 
</p>

<h2>Command Line</h2>
<p>
    This tool also can be used in your Terminal. Check out the code from Launchpad. And run ./getstatus.py 
</p>
"""
        self.response.out.write(HEADER + CONTENT + FOOTER)




application = webapp.WSGIApplication(
                                     [('/', MainPage), ('/about', About), ('/help', Help)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


