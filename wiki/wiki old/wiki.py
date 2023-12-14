import requests
import urllib.parse
import os
import json

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"

base = "https://en.uesp.net/wiki/"
path = "/storage/emulated/0/qpython/wiki/"


qlinks = ["Special:AllPages"]
donelinks = {"Special:AllPages": True}
redirects = {}

"""
a = open("/storage/emulated/0/qpython/qlinks.txt", "r")
qlinks = a.read().split("\n")
a.close()
a = open("/storage/emulated/0/qpython/donelinks.txt", "r")
donelinks = json.loads(a.read())
a.close()
a = open("/storage/emulated/0/qpython/redirects.txt", "r")
redirects = json.loads(a.read())
a.close()
"""

def gethtml(url):
    #print(url)
    return requests.get(url=base+url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}).text

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
        linkhere = qlinks[0]
        content = gethtml(linkhere)
        
        pagename = content.split('"wgPageName":"',1)[1].split('"',1)[0]
        fpagename = format(pagename)
        
        if pagename != linkhere:
            if donelinks.get(pagename):
                qlinks.pop(0)
                continue
            flinkhere = format(linkhere)
            redirects[urllib.parse.quote(flinkhere)] = urllib.parse.quote(fpagename)
            print(linkhere + " > " + pagename)
        else:
            print(pagename)
        
        parts = content.split('href="/wiki/')
        links = []
        fcontent = parts[0]
        for i in range(1, len(parts)):
            [link, parts[i]] = parts[i].split('"',1)
            links.append(link)
            flink = format(link)
            fcontent += 'href="./' + urllib.parse.quote(flink) + '.html"' + parts[i]
        
        f = open(path+fpagename+".html", "w", encoding="utf8")
        f.write(fcontent)
        f.close()
        
        for link in links:
            if not donelinks.get(link):
                donelinks[link] = True
                qlinks.append(link)
        qlinks.pop(0)

except Exception as e:
    a = open("/storage/emulated/0/qpython/qlinks.txt", "w")
    a.write("\n".join(qlinks))
    a.close()
    a = open("/storage/emulated/0/qpython/donelinks.txt", "w")
    a.write(str(donelinks))
    a.close()
    a = open("/storage/emulated/0/qpython/redirects.txt", "w")
    a.write(str(redirects))
    a.close()
    print(e)
    quit()


a = open("/storage/emulated/0/qpython/r.txt", "w")
a.write(str(redirects))
a.close()

print("Substituting redirects")
c = 0
d = 5

files = os.listdir(path)
for f in files:
    h = open(path + f, "+")
    content = h.read()
    parts = content.split('href="./')
    fcontent = parts.pop(0)
    
    for p in parts:
        [link, t] = p.split('.html"', 1)
        r = redirects.get(link)
        if r:
            fcontent += 'href="./' + r + '.html"' + t
        else:
            fcontent += p
    
    h.write(fcontent)
    h.close()
    
    c += 1
    if c/len(files)*100 > d:
        print(str(d) + "%")
        d += 5
    






