from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.urlfetch import DownloadError

import os
import translationstatus_soup as translationstatus

DEFAULT_WIKI_PAGE = "http://wiki.ubuntu-nl.org/Rachid/TranslationTool"
LP_CODE_URL = "https://code.launchpad.net/~rachidbm/ubuntu-translations/ul10n-wiki-stats"

template_path = os.path.join(os.path.dirname(__file__), 'index.html')
template_values = {'version': translationstatus.VERSION }


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

        template_values["content"] =  """<h1>Home</h1>
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

        self.response.out.write(template.render(template_path, template_values))



class Help(webapp.RequestHandler):
    def get(self):
        template_values["content"] = """<h1>Help</h1>
<p>
    Example output on a wiki: <a href="%s" target="_new">%s</a> 
</p>

<h2>Create new status list</h2>
<p>
    Create a wiki page and add the following line: <br />
    ## LAUNCHPAD_URL = https://translations.launchpad.net/ubuntu/natty/+lang/nl/?batch=300 <br />
    Where the URL points to list of packages on Launchpad  <br />
    <br />
    Follow the instructions on the <a href='/'>homepage</a>. 
</p>

<h2>How does it work</h2>
<p>
    When you see this tool working for the first time, it might look like abracadabra. 
    Here I'll try to explain what happens under the hood. <br />  
    <br />
    First, data from the given wiki page will be collected. Most important is that the wiki page contains a line starting with: '## LAUNCHPAD_URL ='
    <br />
    When the data from the wiki is collected, the Launchpad page will be fetched. 
    <br /> 
    The tool will run through all the packages retrieved from Launchpad and do some logic. This logic determines if and how the package will be printed in the status list.
<br />  1. A package is <b>always</b> printed when there was something filled in by hand on the wiki (i.e. the field Translator, Reviewer or Remark contains text).
<br />  2. Otherwise, when a package has 0 untranslated strings, the package will be skipped.
<br />  3. When a package was grey (translated upstream), the package'll stay grey.
</p>
<h3>Control</h3>
<p>
    You may have noticed that the behavior of the tool is based on the wiki page. By changing manually the wiki page you'll change the output for the next time you run this tool.
    <br />
    For example, when you have green (0 untranslated) packages and you want to get rid of them. Just remove the names or remarks from the wiki, and next time this tool will skip those packages.
</p>
""" % (DEFAULT_WIKI_PAGE, DEFAULT_WIKI_PAGE)

        self.response.out.write(template.render(template_path, template_values))



class About(webapp.RequestHandler):
    def get(self):
        template_values["content"] = """
<h1>About</h1>
<p>
    This tool reads status of translations of packages from Launchpad and generates output to paste on a wiki.
    <br />
    The code is available under the <a href="http://en.wikipedia.org/wiki/GNU_General_Public_License" target="_new">GNU GPL license</a> on Launchpad: <a href="%s" target="_new">here</a>. 
</p>

<h2>Command Line</h2>
<p>
    This tool also can be used in your Terminal. Check out the code from Launchpad. And run ./getstatus.py 
</p>
<h2>Contact</h2>
<p>
     For suggestions, bugs, feature request or anything else, you can contact <a href="https://launchpad.net/~rachidbm/+contactuser" target="_new">Rachid via Launchpad</a>.
</p>

""" % (LP_CODE_URL)
        self.response.out.write(template.render(template_path, template_values))


application = webapp.WSGIApplication([('/', MainPage), ('/about', About), ('/help', Help)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


