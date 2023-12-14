import requests
import os
from time import sleep

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"

base = "https://en.uesp.net/wiki/"
path = "/storage/emulated/0/qpython/wiki/"

ds = ["", "Morrowind", "Tribunal", "Bloodmoon", "Morrowind_Mod", "Tamriel_Data", "Tamriel_Rebuilt", "Project_Tamriel", "Morrowind_Rebirth"]
# "Special", "General", "UESPWiki", 
qlinks = ["Special:AllPages"]

doms = {}
dlinks = {}
dlinks[qlinks[0]] = True

s = 0
l = [1, 1, 1, 1, 1, 1, 1, 10, 20, 30, 60]

for d in ds:
    doms[d] = True
    if not os.path.exists(path + d):
      os.mkdir(path + d)

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


c = 0

while len(qlinks) > 0:
    page = qlinks.pop(0)
    
    p = page.split(":", 1)
    n = ""
    if len(p) == 1:
        n = format(p[0])
    else:
        n = p[0] + "/" + format(p[1])
    
    content = ""
    if os.path.exists(path+n+".html"):
        f = open(path+n+".html", "r")
        content = f.read()
        f.close()
        print("f " + str(c) + " / " + str(c+len(qlinks)) + "  " + page)
    else:
        content = gethtml(page)
        f = open(path+n+".html", "w", encoding="utf8")
        f.write(content)
        f.close()
        print("  " + str(c) + " / " + str(c+len(qlinks)) + "  " + page)
    
    links = content.split('href="/wiki/')
    links.pop(0)
    for link in links:
        link = link.split('"',1)[0].split("#",1)[0]
        
        d = link.split(":", 1)
        if len(d) == 1:
            d = ""
        else:
            d = d[0]
        
        if doms.get(d) and not dlinks.get(link):
            qlinks.append(link)
            dlinks[link] = True
    c += 1

