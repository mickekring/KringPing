import requests, yaml, socket, os, time, paramiko
from time import strftime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import email
import email.mime.application
import smtplib
import time as t
from tinydb import TinyDB, Query


### Print formatting
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


### Reads passwords, paths, sites to monitor and stuff from file

conf = yaml.load(open('credentials.yml'), Loader=yaml.FullLoader)


### Variables

humanErrorMess = "..." # Init global variable used for a more human error explanation
connection = 0 # Init variable to test if script has got an internet connection
pauseTime = 10 # Number of seconds to wait before main loop runs again
pauseTimeSite = 2 # Number of seconds to wait between looping though sites to test 

localUrlPath = conf['paths']['localurlpath'] # Local path of php-files on the machine running the script - in credentials.xml
remoteUrlPath = conf['paths']['remoteurlpath'] # Remote path on SFTP server for php-files - in credentials.xml

sitesDown = [] # Init list to store sites that are down

global conDown
conDown = 0 # Variable in main loop for connection down and cleansing of sitesDown list if internet was down


### Init style for web page

styleColor = "green"
styleMessage ="All systems GO"


### Database anf tables setup

db = TinyDB('dbping.json')

table_down_now = db.table('DownNow')
table_log = db.table('Log')


### Sites to monitor

sites = conf['sites']['listsites'] # in credentials.xml


### Checks if there is a connection to the internet

def is_connected():
	global connection
	try:
		socket.create_connection(("www.google.com", 443))
		connection = 1

	except OSError:
		connection = 0
		pass


### Get status of sites to monitor

def get_status():

	global styleColor
	global styleMessage
	global humanErrorMess

	listStatus = []

	for site in sites:

		try:
			requests.head(site, timeout=12)

			x = requests.get(site, timeout=20)

			urlSite = x.url
			statusCode = x.status_code
			reasonMess = x.reason	

			print("\nURL: " + urlSite)

			if statusCode < 400:
				print("Status code: " + (f"{bcolors.OKGREEN}") + str(statusCode) + (f"{bcolors.ENDC}"))
			else:
				errorSuggest(statusCode)
				print("Status code: " + (f"{bcolors.FAIL}") + str(statusCode) + (f"{bcolors.ENDC}"))
				print("Problem: " + (f"{bcolors.FAIL}") + humanErrorMess + (f"{bcolors.ENDC}"))

			if reasonMess == "OK":
				print("Reason: " + (f"{bcolors.OKGREEN}") + reasonMess + (f"{bcolors.ENDC}"))
			else:
				print("Reason: " + (f"{bcolors.FAIL}") + reasonMess + (f"{bcolors.ENDC}"))		

			if x.ok == True:
				errorCode = "OK"

				styleColor = "green"
				styleMessage ="All systems GO"

				urlStrip = urlSite # Stripping http from displey on frontend
				urlStrip = urlStrip.replace("http://","")
				urlStrip = urlStrip.replace("https://","")
				urlStrip = urlStrip.replace("/","")

				listStatus.append('<tr><th class="first"><p class="calfont' + styleColor +'">' + str(x.status_code) + '</p></th><th class="second"><p class="calfont">' + (date) + " " + (month) + " | " + (klNu) +'</p></th><th class="third"><p class="calfont">' + (urlStrip) + '</p></th></tr>')

				if (site + "3") in sitesDown:
					sitesDown.remove(site + "3")
					
					msgToSend = ("Your site - " + site + "  - is now up and running again.")
					subjToSend = "Kring|Ping - Your site is UP"
					sendMail(site, msgToSend, subjToSend)

					logging(urlSite, statusCode, humanErrorMess, reasonMess, errorCode)

				elif (site + "2") in sitesDown:
					sitesDown.remove(site + "2") 

				elif (site + "1") in sitesDown:
					sitesDown.remove(site + "1")

				else:
					pass
			else:
				
				errorCode = "Warning"
				styleColor = "yellow"
				styleMessage = "Warnings found"

				if (site + "3") in sitesDown:

					errorCode = "Error"
					styleColor = "red"
					styleMessage = "Errors found"

				elif (site + "2") in sitesDown:

					errorCode = "Error"
					styleColor = "red"
					styleMessage = "Errors found"

				elif (site + "1") in sitesDown:

					errorCode = "Warning"
					styleColor = "yellow"
					styleMessage = "Warnings found"

				else:
					pass


				urlStrip = urlSite # Stripping http from displey on frontend
				urlStrip = urlStrip.replace("http://","")
				urlStrip = urlStrip.replace("https://","")
				urlStrip = urlStrip.replace("/","")

				listStatus.append('<tr><th class="first"><p class="calfont' + styleColor +'">' + str(x.status_code) + '</p></th><th class="second"><p class="calfont">' + (date) + " " + (month) + " | " + (klNu) +'</p></th><th class="third"><p class="calfont">' + (urlStrip) + '</p></th></tr>')

				
				if (site + "3") in sitesDown:
					print(">>> Site is down and message has been sent")

				elif (site + "2") in sitesDown:

					print("Added site to error list. Sending e-mail.")
					
					msgToSend = ("Your site - " + site + "  - is down. There seems to be a problem regarding: " + humanErrorMess + ".")
					subjToSend = "Kring|Ping - Your site is DOWN"
					sendMail(site, msgToSend, subjToSend)

					logging(urlSite, statusCode, humanErrorMess, reasonMess, errorCode)

					sitesDown.remove(site + "2")
					sitesDown.append(site + "3")

				elif (site + "1") in sitesDown:

					logging(urlSite, statusCode, humanErrorMess, reasonMess, errorCode)

					sitesDown.remove(site + "1")
					sitesDown.append(site + "2")

					print(">>> Warning 2")

				elif site not in sitesDown:

					logging(urlSite, statusCode, humanErrorMess, reasonMess, errorCode)

					sitesDown.append(site + "1")

					print(">>> Warning 1")

				else:
					pass


			print("\n-------------------")

			time.sleep(pauseTimeSite)

		except: # Catching error where nGinx server is down (or other web server)

			urlSite = site
			statusCode = "50X" # Hard coded error code.
			reasonMess = "Site Down"
			errorCode = "Error"
			humanErrorMess = "nGinx error"

			errorCode = "Warning"
			styleColor = "yellow"
			styleMessage = "Warnings found"

			if (site + "3") in sitesDown:

				errorCode = "Error"
				styleColor = "red"
				styleMessage = "Errors found"

			elif (site + "2") in sitesDown:

				errorCode = "Error"
				styleColor = "red"
				styleMessage = "Errors found"

			elif (site + "1") in sitesDown:

				errorCode = "Warning"
				styleColor = "yellow"
				styleMessage = "Warnings found"

			else:
				pass

			urlStrip = urlSite # Stripping http from displey on frontend
			urlStrip = urlStrip.replace("http://","")
			urlStrip = urlStrip.replace("https://","")
			urlStrip = urlStrip.replace("/","")

			listStatus.append('<tr><th class="first"><p class="calfont' + styleColor +'">' + statusCode + '</p></th><th class="second"><p class="calfont">' + (date) + " " + (month) + " | " + (klNu) +'</p></th><th class="third"><p class="calfont">' + (urlStrip) + '</p></th></tr>')

			print("\nURL: " + urlSite)
			print("Status code: " + (f"{bcolors.FAIL}") + str(statusCode) + (f"{bcolors.ENDC}"))
			print("Problem: " + (f"{bcolors.FAIL}") + humanErrorMess + (f"{bcolors.ENDC}"))

			if (site + "3") in sitesDown:
				print(">>> Site is down and message has been sent")

			elif (site + "2") in sitesDown:

				print("Added site to error list. Sending e-mail.")
				
				msgToSend = ("Your site - " + site + "  - is down. There seems to be a problem regarding: " + humanErrorMess + ".")
				subjToSend = "Kring|Ping - Your site is DOWN"
				sendMail(site, msgToSend, subjToSend)

				logging(urlSite, statusCode, humanErrorMess, reasonMess, errorCode)

				sitesDown.remove(site + "2")
				sitesDown.append(site + "3")

			elif (site + "1") in sitesDown:

				logging(urlSite, statusCode, humanErrorMess, reasonMess, errorCode)

				sitesDown.remove(site + "1")
				sitesDown.append(site + "2")

				print(">>> Warning 2")

			elif site not in sitesDown:

				logging(urlSite, statusCode, humanErrorMess, reasonMess, errorCode)

				sitesDown.append(site + "1")

				print(">>> Warning 1")

			else:
				pass

			print("\n-------------------")

			time.sleep(pauseTimeSite)

	print("\n---||| SITES CURRENTLY DOWN |||---")
	
	print(sitesDown)

	statusSites = ("".join(listStatus))

	if "red" in statusSites:
		styleColor = "red"
		styleMessage = "Errors found"
	
	elif "yellow" in statusSites:
		styleColor = "#d6b827"
		styleMessage = "Warnings found"

	else:
		styleColor = "green"
		styleMessage = "All systems GO"


	with open("status.php", "w") as f2:
			f2.write(statusSites)


### Based on own server - possible problems from error codes

def errorSuggest(statusCode):

	global humanErrorMess

	if statusCode == 200:
		humanErrorMess = "Everything OK"
	elif statusCode == 404:
		humanErrorMess = "URL not found"
	elif statusCode == 500:
		humanErrorMess = "MySQL or database error"
	elif statusCode == 502:
		humanErrorMess = "PHP error"
	else:
		humanErrorMess = "Unidentified error"


### Send warning SMS with Twilio // Not used at the moment

def sendSMS(site, msgToSend, subjToSend):

	account_sid = conf["twilio"]["account_sid"]
	auth_token = conf["twilio"]["auth_token"]
	client = Client(account_sid, auth_token)

	message = client.messages.create(
		to= conf["twilio"]["to_phone_number"],
		from_= conf["twilio"]["from_phone_number"],
		body=subjToSend + "\n" + msgToSend)

	print(">>> Successfully sent SMS")


### Send warning E-mail

def sendMail(site, msgToSend, subjToSend):
	try:
		msg = MIMEMultipart()
		message = msgToSend
		password = conf["email"]["password"]

		msg['From'] = "micke.kring@edu.stockholm.se"
		msg['To'] = "jag@mickekring.se"
		msg['Subject'] = subjToSend
		msg.attach(MIMEText(message, 'plain'))

		server = smtplib.SMTP('smtp-relay.sendinblue.com: 587')
		server.starttls()
		server.login(msg['From'], password)
		server.sendmail(msg['From'], msg['To'], msg.as_string())
		server.quit()

		print((f"{bcolors.OKGREEN}") + "\n>>> Successfully sent e-mail to %s:" % (msg['To']) + (f"{bcolors.ENDC}"))

	except:
		print((f"{bcolors.FAIL}") + "\n>>> Error sending e-mail." + (f"{bcolors.ENDC}"))


### Log incident to database

def logging(urlSite, statusCode, humanErrorMess, reasonMess, errorCode):
	try:
		table_log.insert({'DateTime': '{0}'.format(strftime('%Y-%m-%d %H:%M:%S')), 'Url': urlSite, 'StatusCode': str(statusCode), 'HumanErrorMessege': humanErrorMess, 'ServerError': reasonMess, 'StatusCode': errorCode})
		print((f"{bcolors.OKGREEN}") + "\n>>> Successfully logged incident." + (f"{bcolors.ENDC}"))

	except:
		print((f"{bcolors.FAIL}") + "\n>>> Failed logging incident." + (f"{bcolors.ENDC}"))


### Creates page downnow.php with number of sites down at the moment

def sites_down_now():
	sitesDownList = len(sitesDown)
	print("Sites down: " + str(sitesDownList))

	if sitesDownList > 0:
		styleColor = "red"
	else:
		styleColor = "green"

	with open("downnow.php", "w") as f1:
		f1.write('<h1 style="color: ' + styleColor + '">' + str(sitesDownList) + '</h1>')

def get_latest_error():
	try:
		get_total_db = len(table_log)
		get_latest = table_log.get(doc_id=get_total_db)

		latest_date = (get_latest['DateTime'])
		ls = (get_latest['Url'])
		ls = ls.replace("http://","")
		ls = ls.replace("https://","")
		ls = ls.replace("/","")

	except:
		ls = "No errors logged"
		latest_date = "No errors logged"

	with open("lastdown.php", "w") as f1:
		f1.write('<p class="boxp">' + latest_date + '<br />' + ls + '</p>')


### Creates page time.php with stamped date and time

def timeNow():
	global klNu
	global day
	global date
	global month

	klNu = (t.strftime("%H:%M"))
	year = (t.strftime("%Y"))
	month = (t.strftime("%B"))
	date = (t.strftime("%d"))
	day = (t.strftime("%A"))

	print(klNu)
	print(day)

	styleTime = '<style type="text/css">.div1-half-top {background-color: ' + styleColor + ';}</style>'

	with open("time.php", "w") as f1:
		f1.write(styleTime + '<h1 class="clock"><i class="far fa-clock" aria-hidden="true"></i> ' + klNu + '</h1><h4>' + day + ' | ' + date + ' ' + month + ' ' + year + '</h4>' + '<h1 class="available" style="color: ' + styleColor + '">' + styleMessage + '</h1>')


# File uploads to SFTP-server #

def fileupload():
	try:
		host = conf['sftp']['host']
		port = conf['sftp']['port']
		transport = paramiko.Transport((host, port))

		password = conf['sftp']['password']
		username = conf['sftp']['username']
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		sftp.chdir(remoteUrlPath)

		filepath1 = "time.php"
		localpath1 = localUrlPath + "time.php"

		filepath2 = "status.php"
		localpath2 = localUrlPath + "status.php"

		filepath3 = "downnow.php"
		localpath3 = localUrlPath + "downnow.php"

		filepath4 = "lastdown.php"
		localpath4 = localUrlPath + "lastdown.php"

		sftp.put(localpath1, filepath1)
		sftp.put(localpath2, filepath2)
		sftp.put(localpath3, filepath3)
		sftp.put(localpath4, filepath4)

		sftp.close()
		transport.close()

		print("\n>>> Files Successfully uploaded.")
	
	except:
		
		print("\n>>> Error. Files unable to upload.")
		
		pass


### Main loop

def Main():
	while True:
		
		global conDown
		
		os.system("clear")

		timeNow()
		
		is_connected()
		
		if connection == 1:

			if conDown == 1:
				sitesDown.clear()
				print("Reset of sites down list - Complete")
			else:
				pass

			get_status()

			conDown == 0

			time.sleep(pauseTime)

		else:
			conDown = 1
			print("Script not connected to the internet. Just passing by...")
			
			urlSite = "Internet Error"
			statusCode = 999
			humanErrorMess = "Internet connection down"
			reasonMess ="x"
			errorCode = "Error"
			
			if urlSite not in sitesDown:
				sitesDown.append(urlSite)

				logging(urlSite, statusCode, humanErrorMess, reasonMess, errorCode)
			else:
				pass

		sites_down_now()

		get_latest_error()

		timeNow()

		fileupload()

		time.sleep(pauseTime)

if __name__ == "__main__":
	Main()