from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.urlfetch import DownloadError

import os
import translationstatus_soup as translationstatus

DEFAULT_WIKI_PAGE = "http://wiki.ubuntu-nl.org/Rachid/TranslationTool"
LP_CODE_URL = "https://launchpad.net/ul10n-wiki-stats"
LP_PROJECT = "launchpad.net/ul10n-wiki-stats"

template_path = os.path.join(os.path.dirname(__file__), 'index.html')
template_values = {'version': translationstatus.VERSION }


class MainPage(webapp.RequestHandler):
    def get(self):
        go = self.request.get('go')
        url_wiki = self.request.get('url_wiki')
        
        wiki_table = ""
        wiki_edit_url = ""
        #if url_wiki == "":
         #   url_wiki = DEFAULT_WIKI_PAGE
        if go == "true":
            ts = translationstatus.TranslationStatus(url_wiki)  # LAUNCHPAD_URL_DEFAULT
            try:
                wiki_table = ts.generate_wiki_table() 
                wiki_edit_url = "<a href=\"%s?action=edit\" _target=\"_new\">Edit the wiki page</a>" % (url_wiki) 
            except DownloadError: 
                wiki_table = "ERROR: Occurred during fetching URL, please try again..."
                wiki_table += "\nNote: sometimes it has problems with fetching an URL, hit the button again and it'll probably work..."

        content = open("home.html", "r").read()
        template_values["content"] = content % (url_wiki, wiki_edit_url, wiki_table)

        self.response.out.write(template.render(template_path, template_values))



class Help(webapp.RequestHandler):
    def get(self):
        content = open("help.html", "r").read()
        template_values["content"] = content % (DEFAULT_WIKI_PAGE, DEFAULT_WIKI_PAGE)

        self.response.out.write(template.render(template_path, template_values))



class About(webapp.RequestHandler):
    def get(self):
        content = open("about.html", "r").read()
        template_values["content"] = content
        self.response.out.write(template.render(template_path, template_values))


application = webapp.WSGIApplication([('/', MainPage), ('/about', About), ('/help', Help)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


