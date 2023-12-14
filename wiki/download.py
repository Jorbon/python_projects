import requests
import os
from time import sleep

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"

base = "https://en.uesp.net/wiki/"
path = "/Users/benap/Desktop/uesp/wiki/"

#ds = ["", "Morrowind", "Tribunal", "Bloodmoon", "Morrowind_Mod", "Tamriel_Data", "Tamriel_Rebuilt", "Project_Tamriel", "Morrowind_Rebirth", "Oblivion", "Shivering", "Oblivion_Mod", "Better_Cities", "Daggerfall", "Daggerfall_Mod", "Arena", "Arena_Mod", "Mod", "Battlespire", "Redguard", "Stormhold", "Dawnstar", "Shadowkey", "Legends", "Blades", "DFU_Mod", "MediaWiki", "Pinball", "SkyrimVSE", "Merchandise", "OBMobile", "Call_to_Arms", "Books", "Skyrim", "Skyrim_Mod", "Beyond_Skyrim", "Online", "Online_Mod", "Lore", "UESPWiki", "Special", "General", "UESPWiki", "File", "User", "Category", "Help", "Template", "Talk", "Bloodmoon_talk", "User_talk", "UESPWiki_talk", "Help_talk", "Lore_talk", "Mod_talk", "OBMobile_talk", "Shadowkey_talk", "SkyrimVSE_talk", "General_talk", "Online_talk", "Books_talk", "Oblivion_Mod_talk", "Blades_talk", "Legends_talk", "Oblivion_talk", "Shivering_talk", "Morrowind_talk", "Tribunal_talk", "Redguard_talk", "Battlespire_talk", "Daggerfall_talk", "Arena_talk", "Morrowind_Mod_talk", "Stormhold_talk", "Dawnstar_talk", "Tamriel_Rebuilt_talk", "Daggerfall_Mod_talk", "Morrowind_Rebirth_talk"]

#doms = {}

s = 0
l = [1, 1, 1, 1, 1, 1, 1, 10, 20, 30, 60]


qlinks = []
dlinks = {}

if os.path.isfile(path + "qlinks.txt") and os.path.isfile(path + "dlinks.txt"):
	f = open(path + "qlinks.txt")
	qlinks = f.read().split("\n")
	f.close()
	f = open(path + "dlinks.txt")
	d = f.read().split("\n")
	for link in d:
		dlinks[link] = True
	print("Loaded progress with " + str(len(qlinks)) + " queued links and " + str(len(dlinks)) + " links already found.")
else:
	qlinks.append("Special:AllPages")
	dlinks[qlinks[0]] = True

"""
for d in ds:
	doms[d] = True
	if not os.path.exists(path + d):
	  os.mkdir(path + d)
"""



def gethtml(url):
	s = 0
	while True:
		try:
			response = requests.get(url=base+url, timeout=(3,60), headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'})
			break
		except Exception:
			t = 300
			if s < len(l):
				t = l[s]
			s += 1
			print("retry " + str(s) + " (" + str(t) + "s)")
			sleep(t)
	return response.text

def format(txt):
	txt = ";".join(txt.split(":"))
	txt = "-".join(txt.split("/"))
	txt = "^".join(txt.split("\\"))
	txt = "'".join(txt.split('"'))
	txt = "@".join(txt.split("*"))
	txt = "&".join(txt.split("?"))
	txt = "[".join(txt.split("<"))
	txt = "]".join(txt.split(">"))
	return txt


try:
	while len(qlinks) > 0:
		page = qlinks.pop(0)
		
		p = page.split(":", 1)
		n = ""
		if len(p) == 1:
			n = format(p[0])
		else:
			n = p[0] + "/" + format(p[1])
		
		content = ""
		flag = " "
		if os.path.exists(path+n+".html"):
			f = open(path+n+".html", "r", encoding="utf8")
			content = f.read()
			f.close()
			flag = "f"
		else:
			content = gethtml(page)
			if not os.path.isdir(path + p[0]):
				os.mkdir(path + p[0])
			f = open(path+n+".html", "w", encoding="utf8")
			f.write(content)
			f.close()
		
		print(flag + " " + str(len(dlinks)-len(qlinks)) + " / " + str(len(dlinks)) + "  " + page)
		
		links = content.split('href="/wiki/')
		links.pop(0)
		for link in links:
			link = link.split('"',1)[0].split("#",1)[0]
			
			d = link.split(":", 1)
			if len(d) == 1:
				d = ""
			else:
				d = d[0]
			
			#if doms.get(d) and not dlinks.get(link):
			if not dlinks.get(link):
				qlinks.append(link)
				dlinks[link] = True

except KeyboardInterrupt:
	f = open(path + "dlinks.txt", "w")
	f.write("\n".join(list(dlinks.keys())))
	f.close()
	f = open(path + "qlinks.txt", "w")
	f.write("\n".join(qlinks))
	f.close()
	print("Saved progress for " + str(len(qlinks)) + " queued links and " + str(len(dlinks)) + " links already found.")


