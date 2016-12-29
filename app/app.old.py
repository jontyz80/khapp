from flask import Flask, render_template, json, request
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import mechanize
import cookielib
import html2text
import subprocess
import string
from time import gmtime, strftime
from datetime import datetime
import base64
import re
import os.path
import socket
import sys
import json
from BeautifulSoup import BeautifulSoup
from time import strftime

from dateutil.relativedelta import relativedelta
from datetime import datetime

now = datetime.now()
date_after_month = datetime.today()+ relativedelta(months=1)
date_after_month_2 = datetime.today()+ relativedelta(months=2)
nextMONTH = date_after_month.strftime("%Y%m")
nextMONTH_file = date_after_month.strftime("%b-%Y")
nextnextMONTH = date_after_month_2.strftime("%Y%m")
nextnextMONTH_file = date_after_month_2.strftime("%b-%Y")



mysql = MySQL()
app = Flask(__name__, static_url_path='/static')


# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'khapp'
app.config['MYSQL_DATABASE_PASSWORD'] = 'oolooZ4g'
app.config['MYSQL_DATABASE_DB'] = 'media'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'j1hew34ght'
#app.config['MYSQL_DATABASE_DB'] = 'BucketList'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

sqlQuery_orchestralVersion = "select mAlbum from mediaSongs where mTrackPosition = "

# Passwords, password is just obsured from casual eyes
telConfSitePW=base64.b64decode("U2hpYmJvbGV0aA==")

streamingCount = 0
telCount = 0


@app.route('/')

def main():
    now = datetime.now()
    currentDay = now.strftime("%d")
    currentMonth = now.strftime("%m")
    currentYear = now.strftime("%Y")
    print ('year:', currentYear)
    streamingCount = 0
    telCount = 0 
    # First, call 3 functions that get all our data
    metDets = getMeetingDetails()
    streamingActive, streamingCount = streamingStatus()
    telActive, telCount = khconfStatus()
    telCount = int(telCount) - 1
    webcamStream = check_server("127.0.0.1", 8554)
    recording = check_local_mp3recording()
    wirelessClients = wirelessCount()

    #Assign the songs, the date of the w/c and the WT Theme
    weekCommencing=metDets[0]
    print weekCommencing
    song1 = metDets[1]
    song2 = metDets[2]
    song3 = metDets[3]
    song4 = "Ask Chairman" 
    song5 = metDets[4]
    song6 = metDets[5]
    wtTitle = metDets[6]

    #print (sqlReturn_song1, sqlReturn_song2, sqlReturn_song3, sqlReturn_song5, sqlReturn_song6)

    #Now build the first tab info on the number of telephone and streaming users (needs to be ajax)
    if (int(telActive)): 
     alert1 = "alert-success"
     glyph1 = "glyphicon glyphicon-ok"
    else: 
     alert1 = "alert-danger"
     glyph1 = "glyphicon glyphicon-exclamation-sign"

    if (int(streamingActive)): 
     alert2 = "alert-success"
     glyph2 = "glyphicon glyphicon-ok"
    else: 
     alert2 = "alert-danger"
     glyph2 = "glyphicon glyphicon-exclamation-sign"
    
    if (recording): 
     alert3 = "alert-success"
     glyph3 = "glyphicon glyphicon-ok"
     status3 = "glyphicon glyphicon-ok"
    else: 
     alert3 = "alert-danger"
     glyph3 = "glyphicon glyphicon-exclamation-sign"
     status3 = "glyphicon glyphicon-remove"
    
    if (webcamStream): 
     alert4 = "alert-success"
     glyph4 = "glyphicon glyphicon-ok"
     status4 = "glyphicon glyphicon-ok"
    else: 
     alert4 = "alert-danger"
     glyph4 = "glyphicon glyphicon-exclamation-sign"
     status4 = "glyphicon glyphicon-remove"


    now = strftime("%Y-%m-%d %H:%M:%S", gmtime()) 

    return render_template('mainPage.html', song1=song1, song2=song2, song3=song3, song4=song4, song5=song5, song6=song6, telCount=telCount, streamingCount=streamingCount, scrapeTime=now, alert1Class=alert1, glyph1Class=glyph1, alert2Class=alert2, glyph2Class=glyph2, alertClass_recording=alert3, glyphClass_recording=glyph3, recordingStatus=status3, webcamStreaming=status4, alertClass_webcamStreaming=alert4, glyphClass_webcamStreaming=glyph4, weekCommencing=weekCommencing,wtTitle=wtTitle, month=currentMonth, wirelessClients=wirelessClients)


## New function - this logs on to the KH Conf website, and understands if the KH is dialed in, and then how many users are connected to it
def khconfStatus():

 now = datetime.now()

 # Logon to site
 br = mechanize.Browser()

 # Cookie Jar
 cj = cookielib.LWPCookieJar()
 br.set_cookiejar(cj)

 # Browser options
 br.set_handle_equiv(True)

 #br.set_handle_gzip(True)
 br.set_handle_redirect(True)
 br.set_handle_referer(True)
 br.set_handle_robots(False)
 br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
 br.addheaders = [('User-agent', 'Chrome')]

 # First visit the login page to authenticate
 urlToOpen="https://report.khconf.com/login.php"
 br.open(urlToOpen)

 #use the right form on the page
 br.select_form(nr=0)

 # User credentials
 br.form['username'] = 'autocheck'
 br.form['password'] = telConfSitePW

 # Login
 br.submit()

 #Setup some variables which will be used to capture the data
 telRunning = 0
 telCount = 0
 phoneCount = 0

 # Now logged in, navigate to page and find the details
 urlToOpen="https://report.khconf.com/currentcalls.php"
 br.open(urlToOpen)

 # OK, so lets read the page in
 soup = BeautifulSoup(br.response().read())
 # First, read the page to see if 'Admin' is in logged in, ie is the phone up
 checkRunning = soup.findAll(text=re.compile('Admin'), limit=1)
 if len(checkRunning) <> 0:
  telRunning = 1

 # Now to look and find how many people are reported logged in
 count = soup.findAll(text=re.compile('Total Count'), limit=1)
 print "countraw:", count
 phoneCount = string.split(count[0])[2]
 print "phonecount:", phoneCount
 return (telRunning, phoneCount)

###### New function to check if the steaming is runnig and if so how many

def streamingStatus():
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
  streamingRunning = 1
  streamingCount = (parsed_json['icestats']['source']['listeners'])
 except:
  streamingRunning, streamingCount = 0, 0
 print 'StreamingCount', streamingCount
 return (streamingRunning, streamingCount)


def extractNumbers ( source ):
	number = re.findall(r'\d+', source)
	#return (int(number[0]))
	return (number)
  
def stripHTML ( source ):   
	clean = str.split(re.sub("<.*?>", "", str(source)))
        return(clean)


def getMeetingDetails():
 currentDay = now.strftime("%d")
 currentMonth = now.strftime("%m")
 currentYear = now.strftime("%Y")

 br = mechanize.Browser()

 # Cookie Jar
 cj = cookielib.LWPCookieJar()
 br.set_cookiejar(cj)

 # Browser options
 br.set_handle_equiv(True)
 #br.set_handle_gzip(True)
 br.set_handle_redirect(True)
 br.set_handle_referer(True)
 br.set_handle_robots(False)
 br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

 br.addheaders = [('User-agent', 'Chrome')]

 # The site we will navigate into, handling it's session
 urlToOpen="http://wol.jw.org/en/wol/dt/r1/lp-e/"+currentYear+"/"+currentMonth+"/"+currentDay
 print urlToOpen
 br.open(urlToOpen)

 soup = BeautifulSoup(br.response().read())
 returnValues=[]
 if (currentYear == "2015"):
  weekCommencing = re.sub("<.*?>", "", str(soup.find('h2', id='p2')))
 else:
  weekCommencing = re.sub("<.*?>", "", str(soup.find('h1', id='p1')))

 weekCommencing = weekCommencing.decode("utf8", 'ignore')
 weekCommencing = weekCommencing.encode('ascii', 'ignore')
 #weekCommencing = weekCommencing.decode("utf8", 'ignore')
 #weekCommencing = weekCommencing.replace(u'\xa0', u' ')
 returnValues.append(str(weekCommencing))

 wc = soup.findAll(text=re.compile('Song'), limit=3)

 songs = soup.findAll(text=re.compile('Song'), limit=3)
 for song in songs:
  song = song.split()[1]
  returnValues.append(int(song))

 #find the url with tc/r1/le-e, and then the one with 40 to start to the date, which is the simplifed version
 for a in soup.findAll('a',href=True):
    if re.findall('tc/r1/lp-e', a['href']):
     if re.findall('4020', a['href']):
        br.open(a['href']) 
        soup2 = BeautifulSoup(br.response().read())
        wtsongs = soup2.findAll('p', id='p3')
        #strip out the html
        wtsongs = str.split(re.sub("<.*?>", "", str(wtsongs)))
        try: 
         wtsong = wtsongs[1].replace('\xc2\xa0', ' ')
         wtsong = extractNumbers(str(wtsong))
         song1 = (int(wtsong[0]))
         song2 = (int(wtsong[1]))
        except:
         song1 = extractNumbers(str(wtsongs[1]))
         song2 = extractNumbers(str(wtsongs[2]))
         song1 = (int(song1[0]))
         song2 = (int(song2[0]))
        returnValues.append(song1)
        returnValues.append(song2)
        #Whilst here, lets grap the title of the article
        wtTitle = soup2.find('li', {'class' : 'resultDocumentPubTitle'})
        wtTitle = wtTitle.text.encode('ascii', 'ignore')
	print (wtTitle)
        returnValues.append(wtTitle)

 return returnValues

def whichSongVersionsAvailable(sqlQuery):
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(sqlQuery)
        print('Total Row(s):', cursor.rowcount)
	cursor.close()
	conn.close()	
	return cursor.rowcount 

def check_server(address, port):
	# Create a TCP socket
	s = socket.socket()
	try:
		s.connect((address, port))
		return True
	except socket.error, e:
		return False

def check_local_mp3recording():
	if (os.path.isfile('/home/sounddesk/Music/recordings/recording.mp3')) :
		return True
	else:
		return False 

def wirelessCount():
	string=[]
	a = os.system ("snmpget -Os -c Shibboleth -v 1 172.16.0.2 .1.3.6.1.4.1.9.9.273.1.1.2.1.1.2")
	bg =  os.system ("snmpget -Os -c Shibboleth -v 1 172.16.0.2 .1.3.6.1.4.1.9.9.273.1.1.2.1.1.1")
	return ( 100 )


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5003,debug=True)
