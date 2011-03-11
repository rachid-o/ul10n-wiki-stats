import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import translationstatus_soup as translationstatus


def p(msg):
    print "%s<br />" % (msg)


# Welcome to http://rachidbm.appspot.com/
#import translationstatus

LAUNCHPAD_URL_DEFAULT = "https://translations.launchpad.net/ubuntu/natty/+lang/nl/?batch=10"
#LAUNCHPAD_URL_DEFAULT = "https://translations.launchpad.net/ubuntu/natty/+lang/nl/?batch=10"


#width = 700
#print "Width is %d " % (width)

class MainPage(webapp.RequestHandler):
    
    URL_WIKI_PAGE = "http://wiki.ubuntu-nl.org/Rachid/StatusTest/input"
    
    def p(self, msg):
        self.response.out.write('%s <br />' % (msg))
        
    """        
    def post(self):
        go = self.request.get('go')
        url_wiki = self.request.get('url_wiki')
        self.response.out.write("<br>go: "+go)
        self.response.out.write("<br>url_wiki: "+url_wiki)
        
        if(go == "true"):
            p("processing...: "+go)    
    """
        
    def get(self):
        go = self.request.get('go')
        url_wiki = self.request.get('url_wiki')
        #self.response.out.write("go: "+go)
        #self.response.out.write("<br>url_wiki: "+url_wiki + "<br>")
        wiki_table = ""
        if go == "true" and url_wiki != "":
            #self.response.out.write("<br />processing...: "+url_wiki)
            #self.response.out.write("<br />escaped...: "+cgi.escape(url_wiki))
            self.URL_WIKI_PAGE = url_wiki
            ts = translationstatus.TranslationStatus(url_wiki, LAUNCHPAD_URL_DEFAULT)
            wiki_table = ts.generate_wiki_table()
    
        
        self.response.out.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<title>Ubuntu Translations</title>
<body>
<h1>Ubuntu Translations</h1>
Here you can generate a wiki page for status on Launchpad translations. 
<br /><br />

<form method="get" action="/">
    URL to wiki page: <br />            
    <input type='text' id='url_wiki' name='url_wiki' value='%s' style='width:700px;' />
    <br />
    <input type='submit' value='Generate package list'  />
    <input type='hidden' id='go' name='go' value='true' />
</form>
<br />

<textarea id='output' style='width:800px; height:500px;'>%s</textarea>
<hr />
version: %s
</body>
</html>
        """ % (self.URL_WIKI_PAGE, wiki_table, translationstatus.VERSION))




application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
    
