import grequests
import os

#requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"

base = "https://stardewvalleywiki.com/"
path = "/Users/benap/Desktop/sv/wiki/"


batch = ["Stardew_Valley_Wiki"]
done = {"Stardew_Valley_Wiki": True}
nextbatch = []
b = 0
c = 0

while len(batch) > 0:
	b += 1
	print("fetching batch " + str(b) + " with " + str(len(batch)) + " files...")

	fetch = []
	for page in batch:
		fetch.append(grequests.get(base + page))

	responses = grequests.map(fetch)

	for r in responses:
		if r == None:
			c += 1
			continue

		name = r.url[len(base):]

		f = open(path + name + ".html", "w", encoding="utf8")
		f.write(r.text)
		f.close()

		links = r.text.split('href="/')
		links.pop(0)
		for link in links:
			link = link.split('"',1)[0].split("#",1)[0]
			
			if link[0:23] == "/stardewvalleywiki.com/":
				link = link[23:]
			
			if ":" in link or "/" in link or link[0:9] == "mediawiki":
				continue

			if not done.get(link):
				nextbatch.append(link)
				done[link] = True
		
		print(name)

	batch = nextbatch
	nextbatch = []

print("Completed with " + str(c) + " missing responses.")

