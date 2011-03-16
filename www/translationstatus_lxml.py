# Author RachidBM <https://launchpad.net/~rachidbm>

# This script uses LMXL way more faster than the BeautifulSoup parser
# But the BeautifulSoup is more up-to-date 
import urllib2, re
from lxml import etree
import datetime

VERSION="0.2"

SHOW_DEBUG_MESSAGES = True			# False for don't printing debug messages, True for showing debug messages   
PRINT_FINISHED_TRANSLATIONS = False	# True then also print packages with 0 untranslated strings 
PRINT_RESERVED_PACKAGES = True		# True print packages which are already reserved on the wiki by a translator or reviewer

URL_PREFIX = "https://translations.launchpad.net/"
NEWLINE = "\n"	

# TODO: Retrieve LP_URL from wiki page
		
class TranslationStatus:
	"""
	Retrieve information from a wiki page and current status of translations from Launchpad. 
	Combine them to output a table in wiki syntax
	"""
	
	__wiki_data	= {}	# Private attribute containing the workmen from the wiki
	__WIKI_URL = ""
	__WIKI_URL_RAW = ""
	__LP_URL = ""
	__WIKI_CONTENT = ""
	
	def __init__(self, WIKI_URL, LP_URL):
		self.__WIKI_URL = WIKI_URL
		self.__WIKI_URL_RAW = WIKI_URL + "?action=raw"
		self.__LP_URL = LP_URL
		#print("wiki: " + self.__WIKI_URL)
		#print("Launchpad: " + self.__LP_URL)
		

	def addline(self, line):
		"""Adds a line to the wiki content"""
		self.__WIKI_CONTENT += line + NEWLINE
		
	#END addline
	def process_wiki(self):
		"""
		Reads the wiki page from __WIKI_URL_RAW and filter useful data from it
		Return a dictionary with wikidata. key is package_name, values are (translator, review)		
		"""
		#debug("Get names from: %s" % (URL_WIKI_PAGE))
		txtfile = urllib2.urlopen(self.__WIKI_URL_RAW)
		#txtfile = open("/tmp/test.txt", "r")
		lines = txtfile.readlines()
		#debug("lines: %d" % (len(lines)))
		wikidata = {}
		check_for_lp_url = True
		for line in lines:
			
			
			# Copy comments from the wiki
			if(line.find("##") == 0):
				self.addline(line.strip())
				
			# First retrieve URL to Launchpad 
			if(check_for_lp_url):
				#debug(find(line, "LAUNCHPAD_URL"))
				if(line.find("LAUNCHPAD_URL") > 0):
					# TODO instead of regex do: split("=")[1].strip()
					__LP_URL = re.sub("##\s*LAUNCHPAD_URL\s*=\s*", "", line).strip() 	# Get the URL
					check_for_lp_url = False
					#debug("Found Launchpad URL on the wiki page: %s " %(__LP_URL))
					
			else:
				tokens = line.split("||")
				# Only when enough tokens AND NOT the header of the table
				if(len(tokens) >= 7 and not tokens[1].startswith("'''")):
					package_name = re.sub("<[^>]*>", "", tokens[1].strip()) 	# Strip color code 
					translator = tokens[4].strip()
					reviewer = tokens[5].strip()
					remark = tokens[6].strip()
					
					# If 1 of the fields is filled in
					if(len(translator) > 0 or len(reviewer) > 0 or len(remark) > 0):
						wikidata[package_name] = (translator, reviewer, remark)
					
		return wikidata
	## END: process_wiki()
	
	
	def generate_wiki_table(self):
		"""Return a table which can be inserted into a wiki page. """
		
		workmen = self.process_wiki()
		
		#Retrieve HTML from Launchpad
		htmlfile = urllib2.urlopen(self.__LP_URL)
		
		doc = etree.parse(htmlfile, etree.HTMLParser()).getroot()
		tbl = doc.xpath("/html//table[2]//tr")
		
		counter = 0		# Count the processed packages (rows)
		added_packages = 0		# Count the added packages (rows)
	
		# Print header of the wiki table
		# print ("||'''Package''' || '''Untranslated''' || '''Needs Review''' || '''Translator''' || '''Reviewer'''||'''Remark'''||")
		self.addline("||'''Package''' || '''Untranslated''' || '''Needs Review''' || '''Translator''' || '''Reviewer'''||'''Remark'''||")
		
		## Read the HTML <table>
		for tr in tbl:
			td = tr.xpath(".//td")
			if(len(tr.attrib) > 0 and len(td) > 5): 
				counter+=1
				## Name and LP_URL
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
				# if this packages was reserved
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
					#self.__WIKI_CONTENT += get_wiki_row(p_name, p_untr_name, p_untr_url, p_review_name, p_review_url, p_translator, p_reviewer, p_remark)
					self.addline(get_wiki_row(p_name, p_untr_name, p_untr_url, p_review_name, p_review_url, p_translator, p_reviewer, p_remark))
					added_packages += 1
				#else:
				#	debug ("## %s is skipped" % (p_name))
		self.addline("%s## %d packages in this list" % (NEWLINE, added_packages))
		self.addline("## Created on %s " % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
		#debug("processed rows: %d" % (counter))
		return self.__WIKI_CONTENT
		
	## END: generate_wiki_table()


	
def get_wiki_row(name, u_nr, u_url, r_nr, r_url, translator, reviewer, remark):
	"""Return a row in wiki-syntax."""
	 
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
	return "||%s ||%s ||%s || %s || %s || %s ||" % (name, u, r, translator, reviewer, remark)
#END get_wiki_row

def debug(message):
	"""Print a DEBUG message"""
	if(SHOW_DEBUG_MESSAGES):
		print "DEBUG: %s" % (message)
#END debug		