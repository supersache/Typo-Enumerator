import socket
import urllib2
import os, sys
import re
from colorama import Fore
try:
	import socks
except:
	print "The module 'SocksiPy' is not installed.\nPlease install it with: sudo apt-get install python-socksipy"
	sys.exit(-2)

def start_daemon():
	os.system('service tor start')
	os.system('service privoxy start')
	print '[' + Fore.GREEN + ' ok ' + Fore.RESET + '] Starting privoxy daemon...done.'
	
# Using Privoxy and TOR for all connections
def connect(port):
	print "\nChecking connection..."
	socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, "127.0.0.1", port, True)
	socket.socket = socks.socksocket
	try:
		url = urllib2.Request('https://check.torproject.org/')
		torcheck = urllib2.urlopen(url)
		response = torcheck.read()
		torcheck.close()
	except:
		print Fore.RED + "Failed to connect through Privoxy and/or TOR!" + Fore.RESET
		print "Please make sure your configuration is right!\n"
		sys.exit(-2)
	try:
		regex = re.compile('Congratulations. This browser is configured to use Tor.')
		searchVersion = regex.search(response)
		version = searchVersion.groups()
		print Fore.GREEN + "Connection to TOR established" + Fore.RESET
		regex = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
		searchIP = regex.search(response)
		IP = searchIP.groups()[0]
		print "Your IP is: ", IP
	except Exception, e:
		print e
		print "It seems like TOR is not used.\nAborting...\n"
		sys.exit(-2)

def stop():
	print "\n"
	os.system('service tor stop')
	os.system('service privoxy stop')
	print '[' + Fore.GREEN + ' ok ' + Fore.RESET + '] Stopping privoxy daemon...done.'