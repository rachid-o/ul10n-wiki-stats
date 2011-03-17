import translationstatus_soup as translationstatus

"""
Common used strings
"""

DEFAULT_WIKI_PAGE = "http://wiki.ubuntu-nl.org/Rachid/TranslationTool"
LP_CODE_URL = "https://code.launchpad.net/~rachidbm/ubuntu-nl/translating-scripts/"


HEADER = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<link rel="shortcut icon" href="media/images/favicon.ico" type="image/ico" />
<link rel="stylesheet" type="text/css" href="media/css/default.css" />
<title>Ubuntu Translation Tool</title>
</head>
<body>
<header id="page-header">
    <div class="container" >
        <nav id="main-nav">
            <a href="/" title="Home" class="main-nav-item ">Home</a>
            <a href="/help" title="Help" class="main-nav-item ">Help</a>
            <a href="/about" title="About" class="main-nav-item ">About</a>
        </nav>
        <h1 id="top-logo">
            <a href="/">
                <img class="png" id="the-logo" src="http://www.ubuntu.com/sites/default/themes/ubuntu10/logo.png" alt="Ubuntu" width="118" height="27" />
                <span id="loco">Translation tool</span>
            </a>
        </h1>
    </div>
</header>
<section id="main-section">
    <div class="container" >
        <section id="content">
"""        


FOOTER = """    
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
</html>""" % (translationstatus.VERSION)

