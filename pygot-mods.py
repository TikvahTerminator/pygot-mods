############################
##Written by Data Cohen 2020
############################
import ftplib
import argparse
import json
import base64
import sys
import requests
import bs4
import urllib
import tld
import os

parser = argparse.ArgumentParser(description='Update Spigot Server via FTP')

#####
##Globals
#####

Password = ""
Username = ""
Host = ""
modurls = []
modlocations = []
modfolder = 0
autodel = False

#############
##Downloaders
#############

def gitDL(url):
	global modlocations
	baseurl = tld.get_tld(url, as_object=True).fld
	page = requests.get(url)
	s = bs4.BeautifulSoup(page.content,'html.parser')
	tag = s.find_all('a',class_='d-flex flex-items-center min-width-0')
	for t in tag:
		g = urllib.request.urlopen('https://' + baseurl+t['href'])
		with open("mods/"+t['href'].split("/")[-1].rstrip(), 'b+w') as f:
			f.write(g.read())
			modlocations.append("mods/"+t['href'].split("/")[-1].rstrip())
			f.close()

def stdDL(url):
	filename = url.split("/")[-1]
	g = urllib.request.urlopen(url)
	with open("mods/"+filename.rstrip(), 'b+w') as f:
		f.write(g.read())
		modlocations.append("mods/"+filename.rstrip())
		f.close()

def lpDL(url):
	bu = tld.get_tld(url, as_object=True)
	baseurl = bu.fld
	page = requests.get(url)
	s = bs4.BeautifulSoup(page.content,'html.parser')
	tag = s.find_all('a')
	for t in tag:
		try:
			if t['href'].split("-")[-2] == 'Bukkit' and t['href'].split("-")[-1][-4:].lower() == '.jar' :
				req = urllib.request.Request(url+t['href'], headers={'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"})
				g = urllib.request.urlopen(req)
				with open('mods/'+t['href'].split("/")[-1].rstrip(), 'b+w') as f:
					f.write(g.read())
					modlocations.append('mods/'+t['href'].split("/")[-1].rstrip())
					f.close()
				break
		except KeyError:
			pass
		except IndexError:
			pass

def bukkitDL(url):
	st = url.split("/")[-1]
	idurl ='https://servermods.forgesvc.net/servermods/projects'
	headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'}
	parameters = {'search':st}
	page = requests.get(idurl, headers=headers, params=parameters)
	resp = page.json()
	id = 0
	for r in resp:
		if r['slug'] == st:
			id = r['id']
	modsurl='https://servermods.forgesvc.net/servermods/files'
	parameters = {'projectIds':str(id)}
	page = requests.get(modsurl, headers=headers, params=parameters)
	resp = page.json()
	DLLink=resp[-1]['downloadUrl']
	try:
		req = urllib.request.Request(DLLink, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"})
		g = urllib.request.urlopen(req)
		with open('mods/'+DLLink.split("/")[-1].rstrip(), 'b+w') as f:
			f.write(g.read())
			modlocations.append('mods/'+DLLink.split("/")[-1].rstrip())
			f.close()
	except KeyError:
		pass
	except IndexError:
		pass
#############################################################################################

#########
##Parsers
#########


def parseMod(url):
	domain = tld.get_tld(url, as_object=True).domain
	domain = domain.lower()
	if domain == 'github':
		return 'GIT'
	elif domain == 'lucko':
		return 'LP'
	elif domain == 'bukkit':
		return 'BUK'
	else:
		return 'DD'

def openCreds(credfile):
	global Password
	global Username
	global Host
	with open(credfile,'r',encoding='utf-8') as f:
		parsed = json.load(f)
		Password = base64.b64decode(parsed['pw'].encode('ascii')).decode('ascii')
		Username = parsed['user']
		Host = parsed['host']
		f.close()
	print("credfile: " + str(credfile) +" has been loaded")

def setCreds(filepath,pw,us,ho):
		with open(filepath,'w',encoding = 'utf-8') as f:
			dict = {'user':str(us), 'pw':base64.b64encode(pw.encode('ascii')).decode('ascii'), 'host':ho}
			f.write(json.dumps(dict))
			f.close()
		print("credfile: " + str(filepath) +" has been updated")

def openMods(modfile):
	global modurls
	with open(modfile,'r',encoding = 'utf-8') as f:
		for line in f:
			modurls.append(line.rstrip())
		f.close()
	print(str(len(modurls)-1) + " mods loaded")
	
###############
##FTP Functions
###############

def delMods(srv):
	if srv.pwd() == '/plugins':
		filelist = srv.nlst()
		jars = []
		for file in filelist:
			if file[-4:].lower() == '.jar':
				jars.append(file)
		for file in jars:
			if autodel == False:
				choice = input("Would you like to delete: " + file+"\t")
				if choice.lower() == "y" or choice.lower() == "yes":
					srv.delete(file)
					print(file + "has been deleted")
				else:
					pass
			else:
				srv.delete(file)
				print(file + "has been deleted")

def uplMods(srv):
	if srv.pwd() == '/plugins':
		for mod in modlocations:
			file = open(mod,'rb')
			filename = mod.split("/")[-1]
			srv.storbinary('STOR '+filename,file)
			file.close()
			print("Uploaded: " + filename)

def updateMods():
	server = ftplib.FTP_TLS(Host)
	server.login(Username,Password)
	server.prot_p()
	server.cwd('plugins')
	delMods(server)
	uplMods(server)
	server.quit()

##################
##Helper Functions
##################

def cleanupMods():
	print("Cleaning up /mods folder")
	for mod in modlocations:
		os.remove(mod)
	if modfolder == 0:
		os.rmdir("mods")
	else:
		pass
	

def dlMods():
	if os.path.exists("mods") == False:
		os.mkdir("mods")
		modfolder = 0
	else:
		modfolder = 1
	for mod in modurls:
		print(mod)
		type = parseMod(mod)
		if type == 'GIT':
			gitDL(mod)
		elif type == 'LP':
			lpDL(mod)
		elif type == 'BUK':
			bukkitDL(mod)
		elif type == 'DD':
			stdDL(mod)
			
#################
###Main Functions
#################


def banner():
	print("  _____        _____       _          __  __           _     ")
	print(" |  __ \      / ____|     | |        |  \/  |         | |    ")
	print(" | |__) |   _| |  __  ___ | |_ ______| \  / | ___   __| |___ ")
	print(" |  ___/ | | | | |_ |/ _ \| __|______| |\/| |/ _ \ / _` / __|")
	print(" | |   | |_| | |__| | (_) | |_       | |  | | (_) | (_| \__ \ ")
	print(" |_|    \__, |\_____|\___/ \__|      |_|  |_|\___/ \__,_|___/")
	print("         __/ |                                               ")
	print("        |___/                                                ")
	print("")
	print("")
	print("Data Cohen - 2020")
	print("")

def main():
	global autodir
	banner()
	if sys.version_info[0] < 3:
		print("This program was written for Python 3.6+. Please update!")
		sys.exit(1)
	elif sys.version_info[1] < 6:
		print("This program was written for Python 3.6+. Please update!")
		sys.exit(1)
	parser.add_argument('--create_cred', action='store_true', help='Create a JSON formatted Credentials file')
	parser.add_argument('--credfile', nargs=1, help='Path to JSON formatted Credentials file')
	parser.add_argument('--modsfile', nargs=1, help='Path to line separated mods file')
	parser.add_argument('--autorm', action='store_true', help='PyGot-Mods will remove ALL .jar files from your /plugins directory')
	args = parser.parse_args()
	autodel = args.autorm
	if args.create_cred == True:
		hn = str(input("Hostname?:\t"))
		print("")
		us = str(input("Username?\t"))
		print("")
		psw = str(input("Password?\t"))
		print("")
		fp = str(input("Output Path?\t"))
		print("")
		setCreds(fp,psw,us,hn)
		sys.exit(0)
	else:
		try:
			openCreds(args.credfile[0])
		except TypeError:
			print("TypeError: Your cred path is empty...")
			sys.exit(1)
		try:
			openMods(args.modsfile[0])
		except TypeError:
			print("TypeError: Your ModsFile is empty....")
			sys.exit(1)
		dlMods()
		updateMods()
		cleanupMods()
		print("Update completed!")
	
if __name__ == "__main__":
	main()