#!/usr/bin/env python
version=0.2

# This script reads status of translations of packages from Launchpad 
#  and generates output to paste on a wiki
# Usage: ./getstatus.py URL
# Or even better: ./getstatus.py URL > wiki-table.txt
# 
# Config
#=======
# URL_DEFAULT The URL which is used by default to check
# URL_WIKI_PAGE The URL of the page where this output is pasted on. 
# 		This will also be used to retrieve current translators/reviewers
 

import sys, urllib2, re
from lxml import etree

## Configuration ( you may change this)
URL_DEFAULT = "https://translations.launchpad.net/ubuntu/natty/+lang/nl/?batch=5"
URL_WIKI_PAGE = "http://wiki.ubuntu-nl.org/Rachid/StatusTest/test2"

# next batch https://translations.launchpad.net/ubuntu/natty/+lang/nl/+index?start=300&batch=300


## Technical configuration, better leave this alone if you're not sure what you're doing. 
URL_PREFIX = "https://translations.launchpad.net/"
URL_WIKI_PAGE_RAW = URL_WIKI_PAGE + "?action=raw"

SHOW_DEBUG_MESSAGES = True		# False for don't printing debug messages, True for showing debug messages   
PRINT_FINISHED_TRANSLATIONS = False		# True then also print packages with 0 untranslated strings 
PRINT_RESERVED_PACKAGES = True		# True print packages which are already reserved on the wiki by a translator or reviewer
					 				# Note: PRINT_RESERVED_PACKAGES overrides the value of PRINT_FINISHED_TRANSLATIONS 
URL = URL_DEFAULT


def debug(message):
	if(SHOW_DEBUG_MESSAGES):
		print "DEBUG: %s" % (message)


## Print a row in wiki-syntax
def print_wiki_row(name, u_nr, u_url, r_nr, r_url, translator, reviewer, remark): 
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
	print "||%s ||%s ||%s || %s || %s || %s ||" % (name, u, r, translator, reviewer, remark)
#END print_wiki_row


# Returns a dictionary.  key is package_name, values are (translator, review)
def get_names_from_wiki():
	#debug("Get names from: %s" % (URL_WIKI_PAGE))
	txtfile = urllib2.urlopen(URL_WIKI_PAGE_RAW)
	#txtfile = open("/tmp/test.txt", "r")
	lines = txtfile.readlines()
	#debug("lines: %d" % (len(lines)))
	dict = {}
	for line in lines:
		tokens = line.split("||")
		
		# Only when enough tokens AND NOT the header of the table
		if(len(tokens) >= 7 and not tokens[1].startswith("'''")):
			package_name = re.sub("<.*>", "", tokens[1].strip()) 	# Strip color code 
			translator = tokens[4].strip()
			reviewer = tokens[5].strip()
			remark = tokens[6].strip()
			
			#if(package_name == "ubiquity-debconf"):
			if(len(translator) > 0 or len(reviewer) > 0):
				#debug("'%s', '%s', '%s'" % (package_name, translator, reviewer))
				dict[package_name] = (translator, reviewer, remark)
	return dict
## END: get_names_from_wiki()


def generate_wiki_table():
	# Print header of the wiki table
	
	workmen = get_names_from_wiki()
	
	htmlfile = urllib2.urlopen(URL)
	
	#doc = etree.parse(path, etree.HTMLParser()).getroot()
	doc = etree.parse(htmlfile, etree.HTMLParser()).getroot()
	tbl = doc.xpath("/html//table[2]//tr")
	
	counter = 0		# Count the processed packages (rows)
	print ("||'''Package''' || '''Untranslated''' || '''Needs Review''' || '''Translator''' || '''Reviewer'''||'''Remark'''||")
	## Read the HTML <table>
	for tr in tbl:
		td = tr.xpath(".//td")
		if(len(tr.attrib) > 0 and len(td) > 5): 
			counter+=1
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
				
				
			## Fill in current translators/reviews			
			p_translator = ""
			p_reviewer = ""
			p_remark = ""
			if(p_name in workmen):
				p_translator = workmen[p_name][0]
				p_reviewer = workmen[p_name][1]
				p_remark = workmen[p_name][2]
			
			## Some logic to determine if we may print this row to wjki table
			may_print = False
			
			if(len(_untr_url) > 0): 
				# If there are untranslated strings always print 
				may_print = True
			elif(PRINT_FINISHED_TRANSLATIONS):
				# If you want to print untranslated strings
				may_print = True
			elif(PRINT_RESERVED_PACKAGES and (len(p_translator) > 0 or len(p_reviewer) > 0) ):
				# If it was reserved already on the wiki let it stay on the list
				may_print = True
			
			# Print the row
			if(may_print):
				print_wiki_row(p_name, p_untr_name, p_untr_url, p_review_name, p_review_url, p_translator, p_reviewer, p_remark)
			else:
				print "## %s is skipped" % (p_name)
									
	debug("processed rows: %d" % (counter))
## END: generate_wiki_table()

	
##  Start program 
print "## This table is generated by getstatus.py version %s" %(version)

if(len(sys.argv) < 2) :
	print "## No location given, reading from default location: %s" % (URL)
else:
	URL = sys.argv[1]
	print "## Reading from given location: %s" % (URL)

generate_wiki_table()

