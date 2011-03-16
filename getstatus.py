#!/usr/bin/env python

# This script reads status of translations of packages from Launchpad 
#  and generates output to paste on a wiki
# Usage: ./getstatus.py URL
# Or even better: ./getstatus.py URL > wiki-table.txt
# 
# Configuration
#==============
# LAUNCHPAD_URL_DEFAULT The URL which is used by default to check Launchpad
# URL_WIKI_PAGE The URL of the page where this output is pasted on. 
# 		This will also be used to retrieve current translators/reviewers


# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


# This BeautifulSoup parser, much slower than LXML, but this works on Google App Engine
import sys
import translationstatus_soup as translationstatus


## Configuration ( you may change this)
LAUNCHPAD_URL_DEFAULT = "https://translations.launchpad.net/ubuntu/natty/+lang/nl/?batch=10"
#LAUNCHPAD_URL_DEFAULT = "https://translations.launchpad.net/ubuntu/natty/+lang/nl/?batch=10"
URL_WIKI_PAGE_DEFAULT = "http://wiki.ubuntu-nl.org/Rachid/StatusTest"
# next batch https://translations.launchpad.net/ubuntu/natty/+lang/nl/+index?start=300&batch=300


wiki_overrides = True
##  Start program 
URL_WIKI_PAGE = URL_WIKI_PAGE_DEFAULT
#LP_URL = LAUNCHPAD_URL_DEFAULT

if(len(sys.argv) < 2) :
	print "No location given, reading from default wiki: %s" % (URL_WIKI_PAGE)
	print "Usage ./getstatus.py http://WIKI [http://LAUNCHPAD]"
	print "URL to Launchpad is optional"
	# error  exit status
	sys.exit(1)
else:
	URL_WIKI_PAGE = sys.argv[1];
	
	
print "Wiki: %s" % (URL_WIKI_PAGE)
#print "Launchpad: %s" % (LP_URL)

ts = translationstatus.TranslationStatus(URL_WIKI_PAGE)
if(len(sys.argv) > 2) :
	ts.setLP_URL(sys.argv[2])
	wiki_overrides = False	# Gave LP_URL as parameter, so you really want this page
	print "Launchpad: %s" % (sys.argv[2])
	
ts.WIKI_OVERRIDES_LP_URL = wiki_overrides	

table = ts.generate_wiki_table()
print table

# Normal exit status
sys.exit(0)