from datetime import datetime
import mechanize
from BeautifulSoup import BeautifulSoup
import cookielib
from config import KHCONF_URL

def khconfStatus():
 
 #Setup some variables which will be used to capture the data
 linkUp = 0
 telCount = 0
 phoneCount = 0

 now = datetime.now()

 # Setup 'browser' 
 br = mechanize.Browser()

 # Cookie Jar
 cj = cookielib.LWPCookieJar()
 br.set_cookiejar(cj)

 # Browser options
 br.set_handle_equiv(True)
 br.set_handle_gzip(True)
 br.set_handle_redirect(True)
 br.set_handle_referer(True)
 br.set_handle_robots(False)
 br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
 br.addheaders = [('User-agent', 'Chrome')]

 # First visit the login page to authenticate
 br.open(KHCONF_URL)

 #use the right form on the page
 br.select_form(nr=0)

 # User credentials
 br.form['username'] = 'autocheck'
 br.form['password'] = telConfSitePW

 # Login
 br.submit()

 # Now logged in, navigate to page and find the details
 urlToOpen="https://report.khconf.com/currentcalls.php"
 br.open(urlToOpen)

 # OK, so lets read the page in
 soup = BeautifulSoup(br.response().read())

 # First, read the page to see if 'Admin' is in logged in, ie is the phone up
 if len(soup.findAll(text=re.compile('Admin'), limit=1)) <> 0:
  linkUp = 1

 # Now to look and find how many people are reported logged in
 count = soup.findAll(text=re.compile('Total Count'), limit=1)
 print "countraw:", count
 phoneCount = string.split(count[0])[2]
 print "phonecount:", phoneCount
 return (linkUp, phoneCount)

