import requests
import os
from time import sleep

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"

base = "https://en.uesp.net/wiki/"
path = "/storage/emulated/0/qpython/wiki/"


qlinks = ["Special:AllPages"]
dlinks = {"Special:AllPages": True}
s = 0
l = [10, 20, 30, 60]

def gethtml(url):
    s = 0
    while True:
        try:
            content = requests.get(url=base+url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}).text
            break
        except Exception:
            t = 900
            if s < len(l):
                t = l[s]
            sleep(t)
            s += 1
            print("no load, retry " + str(s))
    return content

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

files = os.listdir(path)
c = 0
c1 = 0
c2 = 0
d = 10
found = {}
for f in files:
    h = open(path + f, "r")
    content = h.read()
    h.close()
    
    links = content.split('href="/wiki/')
    links.pop(0)
    for link in links:
        link = link.split('"',1)[0]
        if not dlinks.get(link) and not os.path.exists(path+format(link)+".html"):
            qlinks.append(link)
            dlinks[link] = True
            c2 += 1
        c1 += 1
    
    c += 1
    if c > d:
        print(str(d) + " / " + str(len(files)) + " files scanned (" + str(round(d/len(files)*100, 1)) + "%), " + str(c2) + " / " + str(c1) + " links queued (" + str(round(c2/c1*100, 1)) + "%)")
        d += 10


while len(qlinks) > 0:
    page = qlinks.pop(0)
    content = gethtml(page)
    
    f = open(path+format(page)+".html", "w", encoding="utf8")
    f.write(content)
    f.close()
    
    print(page)
    
    links = content.split('href="/wiki/')
    links.pop(0)
    for link in links:
        link = link.split('"',1)[0]
        if not dlinks.get(link):
            qlinks.append(link)
            dlinks[link] = True

