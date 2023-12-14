import os

path = "/storage/emulated/0/qpython/wiki/"
dest = "/storage/emulated/0/qpython/wikif/"

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

fs = [""]

while len(fs) > 0:
    f = fs.pop(0)
    fb = f.split("/")
    
    p = path + f
    d = dest + f
    if os.path.isfile(p):
        a = open(p, "r", encoding="utf8")
        content = a.read()
        a.close()
        
        links = content.split('href="/wiki/')
        content = links.pop(0)
        for link in links:
            [link, o] = link.split('"',1)
            link = link.split("#",1)[0]
            
            content += 'href="'
            
            t = link.split(":", 1)
            if len(t) == 1:
                if len(fb) > 1:
                    content += "."
                content += "./" + format(t[0])
            else:
                if len(fb) == 1:
                    content += "./" + t[0] + "/" + format(t[1])
                elif fb[0] == t[0]:
                    content += "./" + format(t[1])
                else:
                    content += "../" + t[0] + "/" + format(t[1])
            
            content += '.html"' + o
        
        a = open(d, "w", encoding="utf8")
        a.write(content)
        a.close()
        
        c += 1
        print(str(c) + " " + f)
        
    else:
        ls = os.listdir(p)
        for l in ls:
            fs.append(f + "/" + l)
        if not os.path.exists(d):
            os.mkdir(d)

"""
    n = ""
    if len(p) == 1:
        n = format(p[0])
    else:
        n = p[0] + "/" + format(p[1])
    
    content = ""
    if os.path.exists(path+n+".html"):
        f = open(path+n+".html", "r", encoding="utf8")
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
"""
