Test scripts to check htmls
===========================

Required:
Python 2.7+
PhantomJS 

Python libs
* selenium
* pyvirtualdisplay
* tika
* reppy
* nltk

These checks cover:
* check for robots.txt file
* check for alt TEXT in img tags
* check for PDF text and download links where PDF links are given
* simple spell checker 
* check that images linked to exisit


USAGE of htmlPageChecker
`python htmlPageChecker -h`
To check only pages: run `python htmlPageChecker.py -p <[htmlPage]>`
    e.g. `python htmlPageChecker.py -p ../cflbajans/index.html`
	      `python htmlPageChecker.py -p '../cflbajans/index.html, ../cflbajans/index.html'`
          `python htmlPageChecker.py -p ../cflbajans/*.html`
To check the full website folder: run `python htmlPageChecker.py -s <site-dir>`
	e.g. `python htmlPageChecker.py -s ../cflbajans`
To run checks on the website (remote): run `python htmlPageChecker.py -w <website domain>`
	e.g. `python htmlPageChecker.py -w www.cflbajans.com`

Note that you can add or remove words in specialDict.txt for spellchecking. Be sure the words are all lowercase.

** I'm addressing an issue here. If you want run on site on the web, please use Firefox. For local files, use PhantomJS. 
Todo this change self.driver = webdriver.PhantomJS() to self.driver = webdriver.Firefox() and vice versa

TODOS
=====
* the browser issue
* better spell checking
* increase num of tests
