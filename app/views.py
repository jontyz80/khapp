from flask import render_template, request
from app import app
from flask import jsonify


@app.route('/')
@app.route('/index')
def index():
 return render_template('index.html',
                           title='Bobs Home')

@app.route('/_getPhoneStatus', methods=['GET'])
def getPhoneStatus():
    return jsonify( khconf() )

@app.route('/_getStreamingStatus', methods=['GET'])
def getStreamingStatus():
    return jsonify( getStreamingStatus() )


def getStreamingStatus():
 try:
  br = mechanize.Browser()
  cj = cookielib.LWPCookieJar()
  br.set_cookiejar(cj)
  br.set_handle_equiv(True)
  br.set_handle_redirect(True)
  br.set_handle_referer(True)
  br.set_handle_robots(False)
  br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
  br.addheaders = [('User-agent', 'Chrome')]
  urlToOpen='http://listen.northwood-kh.org.uk:8000/status-json.xsl'
  br.open(urlToOpen)
  parsed_json = json.loads(br.response().read())
  steamingCount = 0
  streamingCount = streamingCount + (parsed_json['icestats']['source']['listeners'])
 except:
  streamingCount = -1 
 return (streamingCount)



def khconf():
 from datetime import datetime
 import mechanize
 from BeautifulSoup import BeautifulSoup
 import cookielib
 from config import KHCONF_URL
 from config import KHCONF_PW_ENCODED
 import base64
 import re
 import string

 #Setup some variables which will be used to capture the data
 telCount = -1 
 now = datetime.now()

 # Setup 'browser'
 br = mechanize.Browser()

 # Cookie Jar
 cj = cookielib.LWPCookieJar()
 br.set_cookiejar(cj)

 # Browser options
 br.set_handle_equiv(True)
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
 br.form['password'] = base64.b64decode(KHCONF_PW_ENCODED) 

 # Login
 br.submit()

 # Now logged in, navigate to page and find the details
 urlToOpen="https://report.khconf.com/currentcalls.php"
 br.open(urlToOpen)

 # OK, so lets read the page in
 soup = BeautifulSoup(br.response().read())

 # First, read the page to see if 'Admin' is in logged in, ie is the phone up
 if len(soup.findAll(text=re.compile('Admin'), limit=1)) <> 0:
  telCount = telCount + 1 

 # Now to look and find how many people are reported logged in
 count = soup.findAll(text=re.compile('Total Count'), limit=1)
 phoneCount = string.split(count[0])[2]
 return (telCount + int(phoneCount))



@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
