import grequests
import os


# Warning: This script got the wiki site blacklisted by my network after it detected a ddos attack from it. It is dangerously fast.

base = "https://en.uesp.net/wiki/"
path = "/Users/benap/Desktop/uesp/wiki/"

batch = []
done = {}
nextbatch = []
missing = []

if os.path.isfile(path + "batch.txt") and os.path.isfile(path + "done.txt"):
	f = open(path + "batch.txt")
	batch = f.read().split("\n")
	f.close()
	f = open(path + "done.txt")
	d = f.read().split("\n")
	f.close()
	for link in d:
		done[link] = True
	print("Fetching batch with " + str(len(batch)) + " pages and " + str(len(done)) + " pages already found.")
else:
	batch.append("Special:AllPages")
	done[batch[0]] = True


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


fetch = []
for page in batch:
	fetch.append(grequests.get(base + page))
responses = grequests.map(fetch)


for i in range(len(responses)):
	if responses[i] == None:
		missing.append(batch[i])
		continue

	name = responses[i].url[len(base):]
	f = open(path + format(name) + ".html", "w", encoding="utf8")
	f.write(responses[i].text)
	f.close()

	links = responses[i].text.split('href="/wiki/')
	links.pop(0)
	for link in links:
		link = link.split('"',1)[0].split("#",1)[0]
		if not done.get(link):
			nextbatch.append(link)
			done[link] = True


f = open(path + "done.txt", "w")
f.write("\n".join(list(done.keys())))
f.close()
f = open(path + "batch.txt", "w")
f.write("\n".join(nextbatch))
f.close()

if len(missing) == 0:
	print("Completed batch.")
else:
	print("Completed batch with " + str(len(missing)) + " missing responses:\n" + "\n".join(missing))

