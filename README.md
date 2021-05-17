# Kring Ping Site checker
It's a Python script that checks whether your sites are up or down

## What's this?
This project is using the Python requests module to connect to your site (or sites) to check if your site is up or down, and if down - logs this to a TinyDB database and e-mails you. It also updates a web page with info.<br />
I run this on a Raspberry Pi, uploading the php-files the script generates to my web server.<br /><br />
__Disclaimer!__ I'm just a cowboy builder when it comes to coding. I'm not a coder, just a tinkerer. As long as it works...

## Flow
1. The script tries to connect to your site (or sites) if it's connected to the internet.
2. If site(s) is down - script logs the site(s) with a warning in the database and tries two more times.
3. If site(s) still down - it logs the site with an error in the database and sends you an e-mail.
4. Web pages are updated and sent via sftp to your server.
5. Repeat.
6. If site(s) that have been down is up again, script logs that to the databaase and sends you an e-mail.

## Requirements

### Python 3.x

__Modules__

pip3 install paramiko <br />
pip3 install pyyaml<br />
pip3 install tinydb<br />

# Changelog

### v 1.1 | May 17 2021
Updated mainping.py and moved server paths and sites to monitor to credentials.xml

### v 1.0 | May 16 2021
Initial upload. Everything works as the flow above describes.<br />
This README.md lacks a lot. :) 
