# Kring Ping Site checker
It's a Python script that checks whether your sites are up or down

## What's this?
This project is using the Python requests module to connect to your site (or sites) and check if your site(s) is up or down, and if down - logs this to a TinyDB database and e-mails you. It also updates a web page front end with basic info.<br />
I run the script on a Raspberry Pi, uploading the php-files the script generates to my web server.<br /><br />
__Disclaimer!__ I'm just a cowboy builder when it comes to coding. I'm not a coder, just a tinkerer. As long as it works...

![kringping](https://user-images.githubusercontent.com/10948066/206173987-1fcd03cc-7677-4dd5-87ce-94f4610a25ad.jpg)

## Flow
1. The script tries to connect to your site (or sites) if it's connected to the internet.
2. If site(s) is down - it logs the site with the error in the database and sends you an e-mail.
4. PHP page status.php is updated and sent via sftp to your server.
5. Repeat.
6. If site(s) that have been down is up again, script logs that to the databaase and sends you an e-mail.

## Requirements

### Python 3.x

__Modules__

pip3 install<br />
pyyaml, tinydb, email, smtplib, paramiko

__Web site and server__

You need a domain and a web server that the script can upload the frontend php-files to, via sftp.<br />

## Setup

1. Save the files main.py, config.xml and the folder named 'web', containing the file 'status.php' on the machine that will be running the script. 
2. Upload the files index.php and style.css to your web server.
3. Edit config.xml and add your info such as file paths, sftp- and e-mail account and more.
4. Run ping.py

# Changelog

### v 2.0.0 | Dec 7 2022
Rewritten version of the script.

### v 1.1.2 | May 26 2021
Bug fix - frontend showing latest errors displayed the last errored url on all three lines.

### v 1.1.1 | May 22 2021
Minor updates. 

### v 1.1 | May 17 2021
Updated mainping.py and moved server paths and sites to monitor to credentials.xml

### v 1.0 | May 16 2021
Initial upload. Everything works as the flow above describes.<br />
This README.md lacks a lot. :) 
