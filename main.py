
__version__ = "2.0.2"

from urllib.request import urlopen
import sys
import time
import yaml
from tinydb import TinyDB, Query
import datetime
import os
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import email
import email.mime.application
import smtplib
import paramiko


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
conf = yaml.load(open('config.yml'), Loader=yaml.FullLoader)

# Error messages
nginx_error = "urllib.error.URLError"
php_error = "urllib.error.HTTPError"

# Loads sites to ceck
sites = conf['sites']['listsites']

# Move to config
seconds_to_sleep_between_runs = conf['config']['time_between_checks']

# Database settings
db = TinyDB('db.json')
table_down_time = db.table('DownTime')
table_total_time = db.table('TotalTime')
table_log = db.table('Log')
ask = Query()

sites_down_now = []

# HTML
new_row = '<div class="row">'
end_div = '</div>'
new_col = '<div class="col">'
start_rows = [1, 4, 7, 10, 13, 16, 19, 22]
end_rows = [3, 6, 9, 12, 15, 18, 21, 24]



# Check if site is reported down in global list
# sites_down_now

def is_site_down(site):

	is_down = 0

	for site_down in sites_down_now:
	
		if site in site_down['Url']:		
			is_down = 1
	
		else:
			pass

	return is_down


# If site is back up, store time down in database and sending mail

def site_back_up(time_now, site_url, site, html_status, up_or_down, error_code):

	print()

	for site_down in sites_down_now:

		if site in site_down['Url']:

			print(f"Site {site} is up and running again")

			up_or_down = "up"
				
			went_down_site_date = site_down['Date']
			error_code = site_down['Error']

			print(f"Down {went_down_site_date}")
			print(f"Up {time_now}")

			went_down_site_date = datetime.datetime.strptime(went_down_site_date, "%Y-%m-%d %H:%M:%S.%f")
			time_now = datetime.datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S.%f")
			time_down = time_now - went_down_site_date

			print(f"Total time down {time_down}\n")

			sites_down_now.remove(site_down)

			log_site_down_time(time_now, site_url, site, error_code, went_down_site_date, time_down)
			email_messages(site, up_or_down, error_code)
			
		else:
			pass



# Main function checking if site is up or down

def test_sites():

	status_html = []

	count_sites = 0
	last_site = len(sites)


	for site in sites:

		count_sites += 1

		if count_sites in start_rows:
			status_html.append(new_row)
		else:
			pass

		time_now = str(datetime.datetime.now())

		print()

		site_url = site
		site = site.replace("https://", "")
		print(f"URL: {site}\n")
		print(f"Tid: {time_now}")

		is_down = is_site_down(site)
		print(f"Is site in list of down sites: {is_down}")
	

		try:

			start_time = time.time()

			response = requests.get(site_url)

			end_time = time.time()

			response_time = end_time - start_time
			print(f"Svarstid: {response_time} sek")
			
			html_status = response.status_code

			
			if html_status == 200:
				print(f"{bcolors.OKGREEN}Status {html_status} | All systems go{bcolors.ENDC}")
				up_or_down = "up"
				error_code = "Up and running"

				if is_down == 1:
					site_back_up(time_now, site_url, site, html_status, up_or_down, error_code)

				else:
					pass

			elif html_status == 500 and is_down == 0:
				print(f"{bcolors.FAIL}Status {html_status} | MySQL error{bcolors.ENDC}")
				up_or_down = "down"
				error_code = "Database error"
				email_messages(site, up_or_down, error_code)
				sites_down_now.append({'Url': site, 'Date': str(time_now), 'Error': error_code})

			elif html_status == 500 and is_down == 1:
				print(f"{bcolors.FAIL}Status {html_status} | MySQL error{bcolors.ENDC}")
				up_or_down = "down"
				error_code = "Database error"

			elif html_status == 502 and is_down == 0:
				print(f"{bcolors.FAIL}Status {html_status} | PHP error{bcolors.ENDC}")
				up_or_down = "down"
				error_code = "PHP error"
				email_messages(site, up_or_down, error_code)
				sites_down_now.append({'Url': site, 'Date': str(time_now), 'Error': error_code})
			
			elif html_status == 502 and is_down == 1:
				print(f"{bcolors.FAIL}Status {html_status} | PHP error{bcolors.ENDC}")
				up_or_down = "down"
				error_code = "PHP error"

			elif is_down == 0:
				print(f"{bcolors.FAIL}Status {html_status} | Unknown Error{bcolors.ENDC}")
				up_or_down = "down"
				error_code = "Unknown error"
				email_messages(site, up_or_down, error_code)
				sites_down_now.append({'Url': site, 'Date': str(time_now), 'Error': error_code})


			response_length = len(response.text)
			print(f"Längd på status: {response_length}")

			response_headers = response.headers['content-type']
			print(f"Headers: {response_headers}")

			print(f"Status: {up_or_down}")

			# Log to DB
			log_site_to_database(time_now, site_url, site, response_time, html_status, up_or_down, error_code)
			html_col_status = create_html_status(time_now, site_url, site, response_time, html_status, up_or_down, error_code, count_sites)
			status_html.append(html_col_status)


		except:

			if is_down == 0:

				up_or_down = "down"
				response_time = 0
				html_status = "50X"
				error_code = "Web server error"
				sites_down_now.append({'Url': site, 'Date': str(time_now), 'Error': error_code})

				print(f"{bcolors.FAIL}Status {html_status} | nGinx Error{bcolors.ENDC}")
				print(f"{bcolors.FAIL}Error: {sys.exc_info()[0]}{bcolors.ENDC}")

				print(f"Status: {up_or_down}")

				email_messages(site, up_or_down, error_code)

				log_site_to_database(time_now, site_url, site, response_time, html_status, up_or_down, error_code)
				html_col_status = create_html_status(time_now, site_url, site, response_time, html_status, up_or_down, error_code, count_sites)
				status_html.append(html_col_status)

			elif is_down == 1:

				up_or_down = "down"
				response_time = 0
				html_status = "50X"
				error_code = "Web server error"

				print(f"{bcolors.FAIL}Status {html_status} | nGinx Error{bcolors.ENDC}")
				print(f"{bcolors.FAIL}Error: {sys.exc_info()[0]}{bcolors.ENDC}")

				print(f"Status: {up_or_down}")

				html_col_status = create_html_status(time_now, site_url, site, response_time, html_status, up_or_down, error_code, count_sites)
				status_html.append(html_col_status)


		if count_sites in end_rows or count_sites == last_site:
			status_html.append(end_div)
		else:
			pass

	status_php = ("".join(status_html))

	with open("web/status.php", "w") as f1:
		f1.write(status_php)

	print()
	#print(status_php)
	print("\n---   ---   ---   ---   ---   ---")



def email_messages(site, up_or_down, error_code):

	if up_or_down == "down":

		message_to_send = f"Just nu ligger {site} nere. Problemet verkar röra {error_code}."
		print(message_to_send)
		subject_to_send = f"{site} är nere!"
		print(subject_to_send)

		send_email(message_to_send, subject_to_send)

	else:

		message_to_send = f"Nu är {site} uppe igen, efter ett problem med {error_code}."
		subject_to_send = f"{site} är uppe igen!"

		send_email(message_to_send, subject_to_send)



### Send E-mail

def send_email(message_to_send, subject_to_send):
	
	try:
		msg = MIMEMultipart()
		message = message_to_send
		password = conf["email"]["password"]
		msg['From'] = conf["email"]["username"]
		msg['To'] = conf["email"]["mailto"]
		msg['Subject'] = subject_to_send
		msg.attach(MIMEText(message, 'plain'))

		server = smtplib.SMTP(conf["email"]["server"])
		server.starttls()
		server.login(msg['From'], password)
		server.sendmail(msg['From'], msg['To'], msg.as_string())
		server.quit()

		print(f"{bcolors.OKGREEN} \n>>> Successfully sent e-mail{bcolors.ENDC}")

	except:
		print(f"{bcolors.FAIL} \n>>> Error sending e-mail{bcolors.ENDC}")



### Log incident to database

def log_site_to_database(time_now, site_url, site, response_time, html_status, up_or_down, error_code):
	try:
		table_log.insert({'DateTime': time_now, 'SiteName': site
			, 'Url': site_url, 'StatusCode': str(html_status), 'ResponseTime': response_time
			, 'UpOrDown': up_or_down, 'ErrorCode': error_code})
		print((f"{bcolors.OKGREEN}") + "\n>>> Successfully logged status" + (f"{bcolors.ENDC}"))

	except:
		print((f"{bcolors.FAIL}") + "\n>>> Failed logging status" + (f"{bcolors.ENDC}"))



### N/A

def log_site_down_time(time_now, site_url, site, error_code, went_down_site_date, time_down):
	try:
		table_down_time.insert({'DateTime': str(time_now), 'SiteName': site
			, 'Url': site_url, 'ErrorCode': error_code
			, 'DownDate': str(went_down_site_date), 'TotalTimeDown': str(time_down)})
		print((f"{bcolors.OKGREEN}") + ">>> Successfully logged UP status" + (f"{bcolors.ENDC}\n"))

	except:
		print((f"{bcolors.FAIL}") + ">>> Failed logging UP status" + (f"{bcolors.ENDC}\n"))

	print("Placeholder")



def keep_time_of_script_total_time_run(total_time_loop_run):

	print()

	# Check to see if there is a database entry, if not
	# creates a first entry

	if table_total_time.get(doc_id = 1):

		latest_total_seconds =  table_total_time.get(doc_id = 1)
		latest_total_seconds = latest_total_seconds['Seconds']
		print(f"Second from dadabase {latest_total_seconds}")

		total_time_loop_run = round(total_time_loop_run, 0)
		total_time_loop_run = int(total_time_loop_run)
		print(f"Seconds to add: {total_time_loop_run}")

		total_time_run = latest_total_seconds + total_time_loop_run
		print(f"Total seconds script has run: {total_time_run}")

		table_total_time.update({'Seconds': total_time_run})
	
	else:
		table_total_time.insert({'Seconds': 1})

	print()



def create_html_status(time_now, site_url, site, response_time, html_status, up_or_down, error_code, count_sites):

	time_now = datetime.datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S.%f")

	year = time_now.year
	month = time_now.month
	day = time_now.day
	hour = time_now.hour
	minute = time_now.minute
	second = time_now.second

	if int(month) < 10:
		month = str(month)
		month = str("0" + month)

	if int(day) < 10:
		day = str(day)
		day = str("0" + day)

	if int(hour) < 10:
		hour = str(hour)
		hour = str("0" + hour)

	if int(minute) < 10:
		minute = str(minute)
		minute = str("0" + minute)

	if int(second) < 10:
		second = str(second)
		second = str("0" + second)

	if up_or_down == "up":
		circle = '<i class="fa-solid fa-circle-up"></i>'
		status_p = "mstatus_green"
	else:
		circle = '<i class="fa-solid fa-circle-down"></i>'
		status_p = "mstatus_red"

	time_up = create_stat_uptime(site_url)

	time_now_readable = (f'<i class="fa-regular fa-calendar"></i> {year}-{month}-{day} <i class="fa-regular fa-clock"></i> {hour}:{minute}:{second}')
	
	avg_req_time = average_request_get_time(site_url)

	status_title = circle + '<br /><h2>' + site + '</h2>'
	
	meta = '<p class="mdate">' + str(time_now_readable) + '</p><p><i class="fa-solid fa-download"></i> <strong>Request:</strong> ' + str(round(response_time * 1000, 2)) + ' ms<br /><i class="fa-solid fa-download"></i> <strong>Request:</strong> ' + str(round(avg_req_time * 1000, 2)) + ' ms (average)</p><p class="' + status_p + '"><i class="fa-solid fa-chart-column"></i> <strong>Status:</strong> ' + str(error_code) + '</p>'
	
	progress = '<div class="progress"><div class="progress-bar" role="progressbar" style="width: ' + str(time_up) + '%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100">Uptime: ' + str(time_up) + ' %</div></div>'

	status_html_col = new_col + status_title + meta + progress + end_div

	return status_html_col



def average_request_get_time(site_url):

	get_site_from_db = table_log.search(ask.Url == site_url)

	avg_list = []

	for x in get_site_from_db:

		rtime = (x['ResponseTime'])
		
		if isinstance(rtime, float): 
			avg_list.append(x['ResponseTime'])
		else:
			pass

	average_request_time = sum(avg_list) / len(avg_list)

	return average_request_time



def create_stat_uptime(site_url):

	get_site_from_db = table_down_time.search(ask.Url == site_url)

	down_time_seconds_list = []

	for x in get_site_from_db:

		dtime = (x['TotalTimeDown'])
		dtime = datetime.datetime.strptime(dtime, "%H:%M:%S.%f")

		dtime_hour = dtime.hour
		if dtime_hour > 0:
			down_time_seconds_list.append(dtime_hour * 3600)

		dtime_minute = dtime.minute
		if dtime_minute > 0:
			down_time_seconds_list.append(dtime_minute * 60)
		
		dtime_second = dtime.second
		if dtime_second > 0:
			down_time_seconds_list.append(dtime_second)

		new = dtime.time()


	site_time_seconds = (sum(down_time_seconds_list))
	latest_total_seconds =  table_total_time.get(doc_id = 1)

	try:
		latest_total_seconds = latest_total_seconds['Seconds']

	except:
		latest_total_seconds = 1

	print(f"Second from dadabase {latest_total_seconds}")

	time_down_percent = (site_time_seconds / latest_total_seconds) * 100
	time_up_percent = round(100 - time_down_percent, 2)

	return time_up_percent



def upload_files():
	
	try:
		host = conf['sftp']['host']
		port = conf['sftp']['port']
		transport = paramiko.Transport((host, port))

		password = conf['sftp']['password']
		username = conf['sftp']['username']
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		sftp.chdir(conf['config']['remoteurlpath'])

		filepath1 = "status.php"
		localpath1 = conf['config']['localurlpath'] + "web/status.php"

		sftp.put(localpath1, filepath1)

		sftp.close()
		transport.close()

		print("\n>>> Files Successfully uploaded.")
	
	except:
		
		print("\n>>> Error. Files unable to upload.")
		
		pass



# Runs a first check to see if script can access the internet
# and returns 1 or 0. If 1, the rest of the script runs.

def check_connection_to_internet():

	try:
		response = requests.get('https://google.com')
		return 1

	except:
		return 0



def Main():

	while True:

		internet_access = check_connection_to_internet()

		if internet_access == 1:

			start_time_loop_run = time.time()

			# Clear screen - for windows, use 'cls' instead of 'clear'
			os.system("clear")

			print("\n/// --- /// --- /// --- ///\n")

			# Times how long a main loop run takes, and saved to DB
			# for stats.

			test_sites()

			print(sites_down_now)

			upload_files()

			time.sleep(seconds_to_sleep_between_runs)

			end_time_loop_run = time.time()
			total_time_loop_run = end_time_loop_run - start_time_loop_run

			keep_time_of_script_total_time_run(total_time_loop_run)

		else:

			time.sleep(seconds_to_sleep_between_runs)



if __name__ == "__main__":
	Main()





