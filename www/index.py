from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.urlfetch import DownloadError

import os
import translationstatus_soup as translationstatus
#import json
from django.utils import simplejson as json
import urllib2

DEFAULT_WIKI_PAGE = "http://wiki.ubuntu-nl.org/Rachid/TranslationTool"
LP_CODE_URL = "https://launchpad.net/ul10n-wiki-stats"
LP_PROJECT = "launchpad.net/ul10n-wiki-stats"

template_path = os.path.join(os.path.dirname(__file__), 'index.html')
template_values = {'version': translationstatus.VERSION }


class MainPage(webapp.RequestHandler):
    def get(self):
        #go = self.request.get('go')
        url_wiki = self.request.get('url_wiki')
        
        content = open("home.html", "r").read()
        template_values["content"] = content % (url_wiki)                

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


class jGet(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        url_wiki = self.request.get('url_wiki')

        ts = translationstatus.TranslationStatus(url_wiki)  # LAUNCHPAD_URL_DEFAULT
        errors = ""
        retry = False
        wiki_table = ""
        wiki_edit_url = ""
        try:
            wiki_table = ts.generate_wiki_table() 
            wiki_edit_url = "<a href=\"%s?action=edit\" _target=\"_new\">Edit the wiki page</a>" % (url_wiki) 
        except DownloadError:
            retry = True 
            errors = "Failed fetching URL, it will automatically try again..." 
             #+ "\nNote: sometimes it has problems with fetching an URL, hit the button again and it'll probably work..."
        except urllib2.HTTPError, e:
            errors = 'The server couldn\'t fulfill the request to url, error code: ' + str(e.code)
        except urllib2.URLError, e:
            errors = 'We failed to reach the server on url, reason: ' + str(e.reason)
        except ValueError, e:
            errors = "Invalid URL (make sure the wiki page contains the LAUNCHPAD_URL) "
            
        jsonData = {'wiki_table': wiki_table, 'wiki_edit_url': wiki_edit_url, 'errors':errors, 'retry':retry}        
        self.response.out.write(json.dumps(jsonData))


application = webapp.WSGIApplication([('/', MainPage), ('/about', About), ('/help', Help), ('/get', jGet)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


