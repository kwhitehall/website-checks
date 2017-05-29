 # Licensed to the Apache Software Foundation (ASF) under one
 # or more contributor license agreements.  See the NOTICE file
 # distributed with this work for additional information
 # regarding copyright ownership.  The ASF licenses this file
 # to you under the Apache License, Version 2.0 (the
 # "License"); you may not use this file except in compliance
 # with the License.  You may obtain a copy of the License at
 #
 #     http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from pyvirtualdisplay import Display
from tika import parser
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from reppy.cache import RobotsCache
from reppy.exceptions import ServerError

import sys, os, time, getopt, re, collections, nltk

'''
Purpose:: To check the quality of website pages that have been released to public
Requires:: selenium, PhantomJS, pyvirtualdisplay, tika, reppy, nltk
'''

class testHtmlPage(object):
	def __init__(self):
		self.display = Display(visible=0, size=(800, 600))
		self.display.start()
		self.driver = webdriver.PhantomJS()
		#self.driver = webdriver.Firefox() 
		self.verificationErrors = []
		self.accept_next_alert = True
		self.log = os.getcwd()+'/htmlPageChecker.log'
		self.f = open(self.log,'ab+')
		self.NWORDS = ''
		self.alphabet = ''

	def is_element_present(self, what):
		try: 
			return self.driver.find_elements_by_tag_name(what)
		except NoSuchElementException, e: 
			return False

	def is_alert_present(self):
		try: 
			self.driver.switch_to_alert()
		except NoAlertPresentException, e: 
			return False
		return True

	def close_alert_and_get_its_text(self):
		try:
			alert = self.driver.switch_to_alert()
			alert_text = alert.text
			if self.accept_next_alert:
				alert.accept()
			else:
				alert.dismiss()
			return alert_text
		finally: self.accept_next_alert = True

	def tearDown(self):
		self.f.close()
		self.driver.quit()
		self.display.stop()
		
	def check_img_alt_tags(self, page):
		driver = self.driver
		driver.implicitly_wait(3)
		driver.get(page)
		allImgTags = self.is_element_present('img')
		self.f.write('--- checking for alt text in %s\n' %page)
		altTagsPassed = True

		if allImgTags:
			for img in allImgTags:
				try:
					currAltText = img.get_attribute('alt').encode('utf-8')
					if not(currAltText and currAltText.strip()): 
						print img.get_attribute('src'),': img tag alt attribute missing text'
						self.f.write('%s :img tag alt attribute missing text\n' %img.get_attribute('src'))
						altTagsPassed = False
				except:
					print 'Some img tags are missing alt TEXT attribute. Please check!'	
					self.f.write('Some img tags are missing alt TEXT attribute. Please check!\n')
					return False

			if altTagsPassed == True:
				print 'img alt TEXT test cleared'
				self.f.write('img alt TEXT test cleared\n')
		else:
			print 'This page has no img tags'
			self.f.write('This page has no img tags\n')
		
		return altTagsPassed

	def check_pdf_text(self,page):
		driver = self.driver
		driver.implicitly_wait(2)
		driver.get(page)
		allaTags = self.is_element_present('a')
		self.f.write('--- checking for pdf links in %s\n' %page)
		pdf = False
		adobe = False
		adobeDload = False
		
		if allaTags:
			for a in allaTags:
				try:
					if a.get_attribute('href'):
						currhref = (a.get_attribute('href').encode('utf-8')).lower()
						if '.pdf' in currhref:
							pdf = True
						elif 'http://www.adobe.com' in currhref:
							adobe = True
						elif 'https://get.adobe.com/reader' in currhref:
							adobeDload = True
				except:
					return False
			if pdf == True and adobe == False and adobeDload == False:
				print 'pdf found but no mention of Adobe or download link for Adobe'
				self.f.write('pdf found but no mention of Adobe or download link for Adobe\n')
			elif pdf == True and adobe == True and adobeDload == False:
				print 'pdf found. Adobe is mentioned, but download link for Adobe missing'
				self.f.write('pdf found. Adobe is mentioned, but download link for Adobe missing\n')
			elif pdf == True and adobe == False and adobeDload == True:
				print 'pdf found. Link to download Adobe found, but not mention of Adobe needed'
				self.f.write('pdf found. Link to download Adobe found, but not mention of Adobe needed\n')
			else:
				print 'pdf check cleared'
				self.f.write('pdf check cleared\n')
		else:
			print 'This page has no a tags'
			self.f.write('This page has no a tags\n')
		
		return True

	def check_for_robot_file(self, rfile):
		self.f.write('--- checking robots.txt')
		if os.path.isfile(rfile):
			print 'robots.txt file is present'
			self.f.write('robot.txt file is present \n')
			if os.stat(rfile).st_size == 0:
				print 'robots.txt file is empty!'
				self.f.write('robot.txt file is empty! \n')
		else:
			print 'robots.txt file is missing!'
			self.f.write('robots.txt file is missing! \n')


	def check_for_robot_access(self, page):
		self.f.write('--- checking for robots %s\n' %page)
		robots = RobotsCache()
		try:
			if robots.allowed(page+'robots.txt', 'my-agent'):
				print page
				print 'robots allowed'
				self.f.write('robots allowed. \n')
				return True
		except ServerError, r:
			print 'error on website ', r
			return False

	def spell_checker(self, page, stopwordsList):
		driver = self.driver
		driver.implicitly_wait(2)
		driver.get(page)
		self.f.write('--- checking for spelling %s\n' %page)
		allTextOnPage = parser.from_file(page)['content'].encode('utf-8')
		allTextOnPage = re.findall('[a-z]+', allTextOnPage.lower()) 
		stopwordsList.extend(stopwords.words('english'))
		allTextOnPage = [w for w in allTextOnPage if not w in stopwordsList]

		for word in allTextOnPage:
			if not wordnet.synsets(word):
				print 'Is this correct? ', word
				self.f.write('Is this word correct? %s\n' %word)
				

	def check_images_exist(self, page):
		driver = self.driver
		driver.implicitly_wait(2)
		driver.get(page)
		allImgTags = self.is_element_present('img')
		self.f.write('--- checking images references in %s\n' %page)
		allSources = True
		
		if allImgTags:
			for img in allImgTags:
				try:
					location = img.get_attribute('src').encode('utf-8')
					if not(location and location.strip()): 
						print img.get_attribute('src'),': image source text is missing'
						self.f.write('image source text is missing. \n')
						allSources = False
					elif not os.path.isfile((os.path.normpath(location)).split(':')[1]): 
						print img.get_attribute('src'),': image source is missing'
						self.f.write('%s :image source missing text\n' %img.get_attribute('src'))
						allSources = False			
				except:
					print img, ' img tag is missing src attribute. Please check!'	
					self.f.write('%s img tags is missing src attribute. Please check!\n' %img)
					allSources = False

			if allSources == True:
				print 'image sources exists test cleared'
				self.f.write('image sources exists test cleared\n')
		else:
			print 'This page has no img tags'
			self.f.write('%s has no img tags\n' %page)
		
		return allSources
	
def _usage():
	print ('*')*80
	print 'USAGE of htmlPageChecker'
	print 'python htmlPageChecker -h'
	print ('*')*80
	print 'To check only pages: run \n\t''python htmlPageChecker.py -p <[htmlPage]>'''
	print '\te.g. python htmlPageChecker.py -p ../cflbajans/index.html'
	print '\t     python htmlPageChecker.py -p ''../cflbajans/index.html, ../cflbajans/index.html'''
	print '\t     python htmlPageChecker.py -p ../cflbajans/*.html'
	print '\nTo check the full website folder: run \n\t''python htmlPageChecker.py -s <site-dir>'''
	print '\te.g. python htmlPageChecker.py -s ../cflbajans'
	print '\nTo run checks on the website (remote): run \n\t''python htmlPageChecker.py -w <website domain>'''
	print '\te.g. python htmlPageChecker.py -w www.cflbajans.com'


def main(argv):
	reload(sys)
	sys.setdefaultencoding('utf8')
	pages = [] 
	sloc = ''
	baseUrl = ''
	dictionary = [line.rstrip() for line in open('specialDict.txt')]
	
	try:
		opts, args = getopt.getopt(argv,"hpsw:")
		if len(opts) == 1:
			for opt, arg in opts:
				if opt in '-h':
					_usage()
					sys.exit()
				elif opt in '-p':	
					if '*' in arg:
						pages = [arg.split('*')[0]+'/'+i for i in os.listdir(arg.split('*')[0]) if 'html' in i]
					else:
						pages = [i for i in arg.split(',')]
				elif opt in '-s':	
					pages = [arg.split('*')[0]+'/'+i for i in os.listdir(arg.split('*')[0]) if 'html' in i]
					sloc = arg
				elif opt in '-w':	
					baseUrl = arg
	except:
		_usage()

	t = testHtmlPage()

	if baseUrl:
		testHtmlPage.check_for_robot_access(t, baseUrl)
		testHtmlPage.tearDown(t)
	else:
		if sloc:
			#--- for the robots.txt check ---  
			testHtmlPage.check_for_robot_file(t, sloc+'/robots.txt')

		#--- check the pages ---	
		for eachPage in pages:
			print 'working on ',eachPage
			t = testHtmlPage()
			testHtmlPage.check_images_exist(t, eachPage)
			testHtmlPage.check_img_alt_tags(t, eachPage)
			testHtmlPage.check_pdf_text(t, eachPage)
			testHtmlPage.spell_checker(t, eachPage, dictionary)
			testHtmlPage.tearDown(t)
	

if __name__ == "__main__":
	main(sys.argv[1:])

