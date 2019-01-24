#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Typo3 Enumerator - Automatic Typo3 Enumeration Tool
# Copyright (c) 2014-2017 Jan Rude
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)
#-------------------------------------------------------------------------------

import re
import sys
from colorama import Fore
from lib.request import Request
from lib.output import Output

class Typo3_Installation:
	"""
	This class checks, if Typo3 is used on the domain with different approaches.
	If Typo3 is used, a link to the default login page is shown.
	"""
	@staticmethod
	def run(domain):
		check_on_root = Typo3_Installation.check_root(domain)
		if not check_on_root:
			default_files = Typo3_Installation.check_default_files(domain)
			if not default_files:
				typo = Typo3_Installation.check_404(domain)

	"""
	This method requests the root page
		and searches for a specific string in the response.
		Usually there are some TYPO3 notes in the HTML comments.

		If found, it searches for a Typo3 path reference
		in order to determine the Typo3 installation path.
	"""
	@staticmethod
	def check_root(domain):
		response = Request.get_request(domain.get_name(), '/')
		if response is None:
			return False
		if re.search('[Tt][Yy][Pp][Oo]3', response[0]):
			domain.set_typo3()
			headers = Request.interesting_headers(response[1], response[2])
			for key in headers:
				domain.set_interesting_headers(key, headers[key])

			try:
				path = re.search('(href|src|content)=(.{0,35})(typo3temp/|typo3conf/)', response[0])
				if not (path.groups()[1] == '"' or '"../' in path.groups()[1]):
					real_path = (path.groups()[1].split('"')[1])
					if 'http' in real_path:
						domain.set_name(real_path[0:len(real_path)-1])
					else:
						domain.set_name(domain.get_name() + real_path[0:len(real_path)-1])
					domain.set_path(real_path[0:len(real_path)-1])
			except:
				pass
			return True
		else:
			return False

	"""
	This method requests different files, which are generated on installation.
		Usually they are not deleted by admins 
		and can be used as an indicator of a TYPO3 installation.
	"""
	@staticmethod
	def check_default_files(domain):
		files = {'/typo3_src/README.md':'[Tt][Yy][Pp][Oo]3 [Cc][Mm][Ss]',
				'/typo3_src/README.txt':'[Tt][Yy][Pp][Oo]3 [Cc][Mm][Ss]',
				'/typo3_src/INSTALL.txt':'INSTALLING [Tt][Yy][Pp][Oo]3',
				'/typo3_src/INSTALL.md':'INSTALLING [Tt][Yy][Pp][Oo]3',
				'/typo3_src/LICENSE.txt':'[Tt][Yy][Pp][Oo]3'
			}

		for path, regex in files.items():
			try:
				response = Request.get_request(domain.get_name(), path)
				regex = re.compile(regex)
				searchInstallation = regex.search(response[0])
				installation = searchInstallation.groups()
				domain.set_typo3()
				return True
			except:
				pass
		return False

	"""
	This method requests a site which is not available.
		TYPO3 installations usually generate a default error page,
		which can be used as an indicator.
	"""
	@staticmethod
	def check_404(domain):
		domain_name = domain.get_name()
		response = Request.get_request((domain_name.split('/')[0] + '//' + domain_name.split('/')[2]), '/idontexist')
		try:
			regex = re.compile('[Tt][Yy][Pp][Oo]3 CMS')
			searchInstallation = regex.search(response[0])
			installation = searchInstallation.groups()
			domain.set_typo3()
			return True
		except:
			return False

	"""
	This method requests the default login page
		and searches for a specific string in the title or the response.
		If the access is forbidden (403), extension search is still possible.
	"""
	@staticmethod
	def search_login(domain):
		try:
			response = Request.get_request(domain.get_name(), '/typo3/index.php')
			regex = re.compile('<title>(.*)</title>', re.IGNORECASE)
			searchTitle = regex.search(response[0])
			title = searchTitle.groups()[0]

			login_text = Fore.GREEN + domain.get_name() + '/typo3/index.php' + Fore.RESET
			login_text += '\n | Accessible?'.ljust(30)  
			
			if ('TYPO3 Backend access denied: The IP address of your client' in response[0]) or (response[3] == 403):
				login_text += (Fore.YELLOW + ' Forbidden (IP Address Restriction)' + Fore.RESET)
			elif (('TYPO3 Login' in title) or ('TYPO3 CMS Login') in title):
				login_text += Fore.GREEN + ' Yes' + Fore.RESET
			else:
				login_text = Fore.RED + 'Could not be found' + Fore.RESET
			domain.set_login_found(login_text)
			return True
		except:
			return False