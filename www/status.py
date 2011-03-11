import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import translationstatus_soup as translationstatus


def p(msg):
    print "%s<br />" % (msg)


# Welcome to http://rachidbm.appspot.com/

LAUNCHPAD_URL_DEFAULT = "https://translations.launchpad.net/ubuntu/natty/+lang/nl/?batch=30"


class MainPage(webapp.RequestHandler):
    
    URL_WIKI_PAGE = "http://wiki.ubuntu-nl.org/Rachid/StatusTest/input"
    
    def get(self):
        go = self.request.get('go')
        url_wiki = self.request.get('url_wiki')
        
        wiki_table = ""
        wiki_edit_url = ""
        
        if url_wiki != "":
            self.URL_WIKI_PAGE = url_wiki
            if go == "true":
                ts = translationstatus.TranslationStatus(url_wiki, LAUNCHPAD_URL_DEFAULT)
                wiki_table = ts.generate_wiki_table()
                wiki_edit_url = "<a href=\"%s?action=edit\" _target=\"_new\">Edit the wiki page</a>" % (self.URL_WIKI_PAGE) 
        
        
        self.response.out.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<link rel="stylesheet" type="text/css" href="media/css/default.css" />
<title>Ubuntu Translations</title>
</head>

<body>
<header id="page-header">
    <div class="container" >
        <nav id="main-nav"></nav>
        <h1 id="top-logo">
            <a href="/">
                <img class="png" id="the-logo" src="http://www.ubuntu.com/sites/default/themes/ubuntu10/logo.png" alt="Ubuntu" width="118" height="27" />
                <span id="loco">Translation tool</span>
            </a>
        </h1>
    </div>
</header>

<br />
<section id="main-section">
    <div class="container" >
        <section id="content">
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
                <input type='hidden' id='go' name='go' value='true' />
            </form>
            Output for wiki %s<br />
            <textarea id='output' style='width:900px; height:400px;'>%s</textarea>
    
        </section>
    </div>
</section>

<footer id="page-footer">
    <details class="foot-note">
    <p>Version: %s</p>
    <p>This tool is developed by <a href="https://launchpad.net/~rachidbm" target="_new">RachidBM</a>
    <br /> 
    Ubuntu Website Template developed by Michael Hall
    <a href="https://launchpad.net/django-ubuntu-template" target="_blank">https://launchpad.net/django-ubuntu-template</a>
    </p>
    </details>
</footer>

</body>
</html>
        """ % (self.URL_WIKI_PAGE, wiki_edit_url, wiki_table, translationstatus.VERSION))



application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
