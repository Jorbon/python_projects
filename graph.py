path = "C:/Users/benap/AppData/Roaming/.minecraft/screenshots/2021-04-18_00.42.39.png"

dest = "C:/Users/benap/AppData/Roaming/.minecraft/saves/graph/generated/minecraft/structures/graph.nbt"


import os
import gzip
from struct import pack, unpack, calcsize

# struct docs: https://docs.python.org/3/library/struct.html
# int = ord(byte)
# byte = bytes([int])

bytelist = b''
def nextb(n=1):
	global bytelist
	b = bytelist[:n]
	bytelist = bytelist[n:]
	return b
def next(fmt="b"):
	global bytelist
	return unpack(">"+fmt, nextb(calcsize(">"+fmt)))

# a very old version of my Tag class, missing a lot of features. It's fine for this though
class Tag:
	toId = {"end": 0, "byte": 1, "short": 2, "int": 3, "long": 4, "float": 5, "double": 6, "byte_array": 7, "string": 8, "list": 9, "compound": 10, "int_array": 11, "long_array": 12}
	toType = ["end", "byte", "short", "int", "long", "float", "double", "byte_array", "string", "list", "compound", "int_array", "long_array"]

	def __init__(self, id=0, value="", name="", listid=1):
		if type(id) == str:
			self.id = Tag.toId[id]
		else:
			self.id = id
		self.name = name
		self.value = value

		if self.id == 9:
			if type(listid) == str:
				self.listid = Tag.toId[listid]
			else:
				self.listid = listid
		else:
			self.listid = 0
	
	def getType(self):
		return Tag.toType[self.id]
	
	def pack(self):
		if (self.id == 0):
			return '\x00'
		
		def packpl(self):
			if self.id == 0:
				return b''
			m = ["", "b", "h", "i", "q", "f", "d"]
			if self.id <= 6:
				return pack(">" + m[self.id], self.value)
			if self.id == 7:
				return pack(">i" + str(len(self.value)) + "b", len(self.value), *self.value)
			if self.id == 8:
				return pack(">h", len(self.value)) + bytes(self.value, "utf-8")
			if self.id == 9:
				total = bytes([self.listid]) + pack(">i", len(self.value))
				if self.listid == 9:
					for item in self.value:
						total += packpl(item)		# if you've got a list of lists, you'd better put the nested lists in as full tags, cause i'm not keeping track of all the types for your chaotic n-dimensional list tag in a single tag object. Just make sure on these nested tags that id = 9 or "list" and listid can be whatever you want.
				else:
					for item in self.value:
						total += packpl(Tag(self.listid, item))
				return total
			if self.id == 10:
				total = b''
				for item in self.value:
					total += item.pack()
				return total + b'\x00'
			if self.id == 11:
				return pack(">i" + str(len(self.value)) + "i", len(self.value), *self.value)
			if self.id == 12:
				return pack(">i" + str(len(self.value)) + "q", len(self.value), *self.value)

		return bytes([self.id]) + pack(">H", len(self.name)) + bytes(self.name, "utf-8") + packpl(self)

	def save(self, dest):
		f = gzip.open(dest, "wb")
		f.write(self.pack())
		f.close()
	
	@staticmethod
	def load(path):
		f = gzip.open(path)
		tag = Tag.unpack(f.read())
		f.close()
		return tag
	
	@staticmethod
	def unpack(byte_list):
		global bytelist
		bytelist = byte_list
		out = Tag(next("b")[0])
		if out.id == 0:
			return out
		
		out.name = str(next(str(next("H")[0]) + "s")[0], "utf-8")
		
		def unpackpl(id):
			global bytelist
			m = ["", "b", "h", "i", "q", "f", "d"]
			if id == 0:
				return ("", 1)
			if id <= 6:
				return (next(m[id])[0], 1)
			if id == 7:
				return (list(next(str(next("i")[0]) + "b")), 1)
			if id == 8:
				return (str(nextb(next("h")[0]), "utf-8"), 1)
			if id == 9:
				listid = next("b")[0]
				length = next("i")[0]
				array = []
				if listid == 9:
					for i in range(length):
						t = unpackpl(listid)
						array.append(Tag(listid, t[0], "", t[1]))
				else:
					for i in range(length):
						t = unpackpl(listid)
						array.append(t[0])
				return (array, listid)
			if id == 10:
				array = []
				tag = Tag(1, 0)
				while True:
					tag = Tag.unpack(bytelist)
					if tag.id == 0:
						break
					array.append(tag)
				return (array, 1)
			if id == 11:
				return (list(next(str(next("i")[0]) + "i")), 1)
			if id == 12:
				return (list(next(str(next("i")[0]) + "q")), 1)
		
		out.value, out.listid = unpackpl(out.id)
		return out

	def toString(self):
		if self.id == 0:
			return ""

		def toStringpl(self):
			m = ["", "b", "s", "", "L", "f", ""]
			if self.id <= 6:
				return str(self.value) + m[self.id]
			if self.id == 7:
				return "[B;" + str(self.value)[1:]
			if self.id == 8:
				return '"' + self.value + '"'
			if self.id == 9:
				if len(self.value) == 0:
					return "[]"
				total = "["
				if self.listid == 9:
					for item in self.value:
						total += toStringpl(item) + ", "
				else:
					for item in self.value:
						total += toStringpl(Tag(self.listid, item)) + ", "
				return total[:-2] + "]"
			if self.id == 10:
				if len(self.value) == 0:
					return "{"+"}"
				total = "{"
				for item in self.value:
					total += item.toString() + ", "
				return total[:-2] + "}"
			if self.id == 11:
				return "[I;" + str(self.value)[1:]
			if self.id == 12:
				return "[L;" + str(self.value)[1:]
		
		return '"' + self.name + '": ' + toStringpl(self)


from PIL import Image

print("Loading image...")

img = Image.open(path).convert("RGB")
data = img.getdata()
counts = []
key = {}
c = 0

print("Scanning pixels...")

for px in data:

	if str(px) in key:
		index = key[str(px)]
		counts[index] = (counts[index][0], counts[index][1] + 1)
	else:
		key[str(px)] = len(counts)
		counts.append((px, 1))
	
	c += 1
	if c % 100000 == 0:
		print(str(100 * c / len(data))[:5] + "%" + " scanned (" + str(c) + "px), found " + str(len(counts)) + " unique colors...")

print("Sorting " + str(len(counts)) + " colors by frequency...")
counts.sort(key=lambda item: item[1], reverse=True)

"""
for i in range(len(counts)):
	counts[i] = (counts[i][0], counts[i][1], counts[i][1] / len(data))

mean = len(data) / len(counts)
meanpc = 1 / len(counts)


	# for logging color frequency data
f = open("C:/Users/benap/Desktop/temp.txt", "w")
for item in counts:
	f.write(str(item[1]) + ",")

"""


# structure file generator

print("Generating structure file...")

tag = Tag(10, [Tag(9, [256, 256, 256], "size", 3), Tag(9, [], "entities", 10), Tag(9, [], "blocks", 10), Tag(9, [], "palette", 10), Tag(3, 2580, "DataVersion")])



key = ["white_stained_glass_pane", "light_blue_stained_glass_pane", "blue_stained_glass_pane", "iron_bars", "blue_stained_glass", "magenta_stained_glass", "red_stained_glass", "black_stained_glass", "sandstone_wall", "stone_brick_wall", "nether_brick_wall", "polished_blackstone_wall", "netherite_block"]

for block in key:
	tag.value[3].value.append([Tag("string", "minecraft:" + block, "Name")])

ceiling = 2 ** (1 - len(key)) * counts[0][1]
index = 0
prev_shift_count = 1
c = 0

for i in range(len(counts)-1, -1, -1):
	tag.value[2].value.append([Tag("list", counts[i][0], "pos", "int"), Tag("int", index, "state")])

	if counts[i][1] > ceiling and counts[i][1] > prev_shift_count:
		while counts[i][1] > ceiling:
			index += 1
			ceiling *= 2
		prev_shift_count = counts[i][1]


	c += 1
	if c % 10000 == 0:
		print(str(100 * c / len(counts))[:5] + "%" + " done (" + str(c) + " blocks)...")

print("Saving...")
tag.save(dest)

print("Done!")

