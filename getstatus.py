#!/usr/bin/env python
# version 0.1

# This script reads status of translations of packages from Launchpad 
#  and generates output to paste on a wiki
# Usage: ./status.py URL
# Or: ./status.py URL > wiki-table.txt


import urllib
import sys
from lxml import etree

URL_PREFIX = "https://translations.launchpad.net/"
URL_DEFAULT = "https://translations.launchpad.net/ubuntu/natty/+lang/nl/?batch=30"
URL = URL_DEFAULT

## Print a row in wiki-syntax
def print_wiki_row_5(name, u_nr, u_url, r_nr, r_url): 
	u = u_nr
	r = r_nr
	color = "<#ff0000>" 	# Default color is red
	if(u_nr == "0"):
		color = "<#00ff00>"  # green
		if(r_nr != "0"):
			color = "<#00AAFF>"  # blue
	else:
		u = "[["+URL_PREFIX+u_url+"|"+u_nr+"|target=\"_new\"]]"
		color = "<#ff0000>"

	if(r_nr != "0"):
		r = "[["+URL_PREFIX+r_url+"|"+r_nr+"|target=\"_new\"]]"

	name = color+name
	print "||%s ||%s ||%s ||  ||  ||" % (name, u, r)


##  Start 

if(len(sys.argv) < 2) :
	print "## Using default URL: %s" % (URL)
else:
	URL = sys.argv[1]
	print "## Using URL: %s" % (URL)

# Print header of the wiki table
print ("||'''Naam''' || '''Onvertaald''' || '''Review nodig''' || '''Vertaler''' || '''Reviewer'''||")

webfile = urllib.urlopen(URL)

#doc = etree.parse(path, etree.HTMLParser()).getroot()
doc = etree.parse(webfile, etree.HTMLParser()).getroot()

tbl = doc.xpath("/html//table[2]//tr")

## Read the HTML <table>
for tr in tbl:  
	td = tr.xpath(".//td")
	if(len(td) > 5): 
		## Name and URL
		link = td[0].xpath("./a")
		if(len(link) > 0): 
			p_name = link[0].text
			p_url = link[0].get('href')

		## Untranslated
		_untr_url = td[3].xpath("./a")
		p_untr_name = ""
		p_untr_url = ""
		if(len(_untr_url) > 0): 
			p_untr_name = _untr_url[0].text
			p_untr_url = _untr_url[0].get('href')
		else:
			p_untr_name = "0"

		## Review
		_review_url = td[4].xpath("./a")
		p_review_name = ""
		p_review_url = ""
		if(len(_review_url) > 0): 
			p_review_name = _review_url[0].text
			p_review_url = _review_url[0].get('href')
		else:
			p_review_name = "0"

		#print '%s, %s' % (p_review_name, p_review_url)
		print_wiki_row_5(p_name, p_untr_name, p_untr_url, p_review_name, p_review_url)

#print "...Done"


