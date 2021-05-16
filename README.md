# Kring Ping Site checker
 Checks whether your sites are up or down

## What's this?
This project is using the Python requests module to connect to your site (or sites) to check if your site is up or down, and if down - logs this to a TinyDB database and e-mails you. It also updates a web page with info.

## Flow
1. The script tries to connect to your site (or sites).
2. If down - it logs the site(s) with a warning in the database and tries two more times.
3. If still down - it logs the site with an error in the database and e-mails you.
4. Web pages are updated and sent via sftp to your server.
5. Repeat.
