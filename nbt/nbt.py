import os
import gzip
from struct import pack, unpack, calcsize

# struct docs: https://docs.python.org/3/library/struct.html
# int = ord(byte)
# byte = bytes([int])		2.7: chr(int)


class tag:
	toId = {"end": 0, "byte": 1, "short": 2, "int": 3, "long": 4, "float": 5, "double": 6, "byte_array": 7, "string": 8, "list": 9, "compound": 10, "int_array": 11, "long_array": 12}
	toType = ["end", "byte", "short", "int", "long", "float", "double", "byte_array", "string", "list", "compound", "int_array", "long_array"]
	bytelist = ''		# used for importing nbt bytestrings
	stringthing = ""	# used for importing snbt strings

	@staticmethod
	def next(fmt="b"):	# get some data from bytelist according to the format code
		n = calcsize(">"+fmt)
		b = tag.bytelist[:n]
		tag.bytelist = tag.bytelist[n:]
		return unpack(">"+fmt, b)
	@staticmethod
	def nexts():		# get the next whatever thing from stringthing, like a syntax character, string, or tag type
		def nextsb(n=1):	# get the next n chars from the front of stringthing
			if len(tag.stringthing) < n:
				raise Exception("Error reading SNBT data: file ended unexpectedly")
			s = tag.stringthing[:n]
			tag.stringthing = tag.stringthing[n:]
			return s

		char = nextsb()
		while char.isspace():
			char = nextsb()
		
		value = ""
		if char == '"' or char == "'":
			quote = char
			while True:
				char = nextsb()
				if char == quote and (len(value) == 0 or value[-1] != "\\"):
					break
				value += char
			return ("string", value)
		
		if char.isdigit():
			decimal = False
			while char.isdigit() or char == ".":
				value += char
				if char == ".":
					decimal = True
				char = nextsb()

			if char == "b" or char == "B":
				return ("byte", int(value))
			if char == "s" or char == "S":
				return ("short", int(value))
			if char == "l" or char == "L":
				return ("long", int(value))
			if char == "f" or char == "F":
				return ("float", float(value))
			if char == "d" or char == "D":
				return ("double", float(value))
			tag.stringthing = char + tag.stringthing
			
			if decimal:
				return ("double", float(value))
			else:
				return ("int", int(value))
		
		if char.isalpha():
			while char.isalnum():
				value += char
				char = nextsb()
			tag.stringthing = char + tag.stringthing
			
			return ("string", value)
		
		if char == "[":
			char = nextsb(2)
			if char == "B;" or char == "b;":
				return ("[B;", "[B;")
			if char == "I;" or char == "i;":
				return ("[I;", "[I;")
			if char == "L;" or char == "l;":
				return ("[L;", "[L;")
			tag.stringthing = char + tag.stringthing
			return ("[", "[")

		if char == "]" or char == "{" or char == "}" or char == ":" or char == ",":
			return (char, char)
		
		return ("char", char)

	def __init__(self, id=0, value="", name="", listid=1):
		if type(id) == str:
			self.id = tag.toId[id]
		else:
			self.id = id
		self.name = name
		self.value = value

		if self.id == 9:
			if type(listid) == str:
				self.listid = tag.toId[listid]
			else:
				self.listid = listid
		else:
			self.listid = 0
	
	def gettype(self):
		return tag.toType[self.id]
	
	def getlisttype(self):
		return tag.toType[self.listid]

	def pack(self):
		if (self.id == 0):
			return '\x00'
		
		def packPL(self):
			if self.id == 0:
				return ''
			m = ["", "b", "h", "i", "q", "f", "d"]
			maxes = [0, 256, 65536, 4294967296, 18446744073709551616]
			if self.id <= 6:
				value = self.value
				if self.id <= 4:	# truncate if out of range
					value = (value + maxes[self.id] / 2) % maxes[self.id] - maxes[self.id] / 2
				return pack(">" + m[self.id], value)
			if self.id == 7:
				value = self.value
				for i in range(len(value)):
					if value[i] >= 128:	# truncate if out of range
						value[i] = (value[i] + 128) % 256 - 128
				return pack(">i" + str(len(value)) + "b", len(value), *value)
			if self.id == 8:
				return pack(">h", len(self.value)) + self.value
			if self.id == 9:
				total = chr(self.listid) + pack(">i", len(self.value))
				if self.listid == 9:
					for item in self.value:
						total += packPL(item)		# if you've got a list of lists, you'd better put the nested lists in as full tags, cause i'm not keeping track of all the types for your chaotic n-dimensional list tag in a single tag object. Just make sure on these nested tags that id = 9 or "list" and listid can be whatever you want.
				else:
					for item in self.value:
						total += packPL(tag(self.listid, item))
				return total
			if self.id == 10:
				total = ""
				for item in self.value:
					total += item.pack()
				return total + '\x00'
			if self.id == 11:
				value = self.value
				for i in range(len(value)):
					value[i] = (value[i] + 2147483648) % 4294967296 - 2147483648	# truncate if out of range
				return pack(">i" + str(len(value)) + "i", len(value), *value)
			if self.id == 12:
				value = self.value
				for i in range(len(value)):
					value[i] = (value[i] + 9223372036854775808) % 18446744073709551616 - 9223372036854775808	# truncate if out of range
				return pack(">i" + str(len(self.value)) + "q", len(self.value), *self.value)

		return chr(self.id) + pack(">H", len(self.name)) + self.name + packPL(self)

	def save(self, path, compress=True):
		if compress:
			f = gzip.open(path, "wb")
		else:
			f = open(path, "wb")
		f.write(self.pack())
		f.close()
	
	@staticmethod
	def load(path, compressed=True):
		if compressed:
			f = gzip.open(path)
		else:
			f = open(path, "rb")
		t = tag.unpack(f.read())
		f.close()
		return t
	
	@staticmethod
	def unpack(byte_list):
		tag.bytelist = byte_list
		out = tag(tag.next("b")[0])
		if out.id == 0:
			return out
		
		out.name = tag.next(str(tag.next("H")[0]) + "s")[0]
		
		def unpackPL(id):
			m = ["", "b", "h", "i", "q", "f", "d"]
			if id == 0:
				return ("", 1)
			if id <= 6:
				return (tag.next(m[id])[0], 1)
			if id == 7:
				return (list(tag.next(str(tag.next("i")[0]) + "b")), 1)
			if id == 8:
				return (tag.next(str(tag.next("h")[0]) + "s")[0], 1)
			if id == 9:
				listid = tag.next("b")[0]
				length = tag.next("i")[0]
				array = []
				if listid == 9:
					for i in range(length):
						t = unpackPL(listid)
						array.append(tag(listid, t[0], "", t[1]))
				else:
					for i in range(length):
						t = unpackPL(listid)
						array.append(t[0])
				return (array, listid)
			if id == 10:
				array = []
				t = tag(1, 0)
				while True:
					t = tag.unpack(tag.bytelist)
					if t.id == 0:
						break
					array.append(t)
				return (array, 1)
			if id == 11:
				return (list(tag.next(str(tag.next("i")[0]) + "i")), 1)
			if id == 12:
				return (list(tag.next(str(tag.next("i")[0]) + "q")), 1)
		
		out.value, out.listid = unpackPL(out.id)
		return out
	
	def toString(self, dblquote=False):
		if self.id == 0:
			return ""

		if dblquote:
			quote = "'"
		else:
			quote = '"'

		def toStringPL(self, quote):
			m = ["", "b", "s", "", "L", "f", ""]
			if self.id <= 6:
				return str(self.value) + m[self.id]
			if self.id == 7:
				return "[B;" + str(self.value)[1:]
			if self.id == 8:
				return quote + self.value.replace(quote, "\\" + quote) + quote
			if self.id == 9:
				total = "["
				if len(self.value) == 0:
					return total + "]"
				
				if self.listid == 9:
					for item in self.value:
						total += toStringPL(item, quote) + ", "
				else:
					for item in self.value:
						total += toStringPL(tag(self.listid, item), quote) + ", "
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
		
		if self.id == 10 and len(self.name) == 0:
			return toStringPL(self, quote)
		else:
			return quote + self.name + quote + ": " + toStringPL(self, quote)
	
	def json(self):
		s = self.toString()
		tab = 0
		
		i = 0
		while i < len(s):
			if s[i] == '"':
				while True:
					i += 1 + (s[i] == "\\")
					if s[i] == '"':
						break
			elif s[i] == "'":
				while True:
					i += 1 + (s[i] == "\\")
					if s[i] == "'":
						break
			elif s[i] == "{" or s[i] == "[":
				if s[i+1] == "}" or s[i+1] == "]":
					i += 1
				else:
					if s[i] == "[" and s[i+2] == ";" and (s[i+1] == "B" or s[i+1] == "I" or s[i+1] == "L" or s[i+1] == "b" or s[i+1] == "i" or s[i+1] == "l"):
						i += 2
					tab += 1
					s = s[:i+1] + "\n" + tab*"\t" + s[i+1:]
					i += 1+tab
			elif s[i] == "}" or s[i] == "]":
				tab -= 1
				s = s[:i] + "\n" + tab*"\t" + s[i:]
				i += 1+tab
			elif s[i:i+2] == ", ":
				s = s[:i+1] + "\n" + tab*"\t" + s[i+2:]
				i += tab
			elif s[i] == ",":
				s = s[:i+1] + "\n" + tab*"\t" + s[i+1:]
				i += 1+tab
			i += 1
		
		return s

	def savesnbt(self, path, fmt=True):
		f = open(path, "w")
		if fmt:
			f.write(self.json())
		else:
			f.write(self.toString())
		f.close()

	@staticmethod
	def loadsnbt(path):
		f = open(path, "r")
		t = tag.fromString(f.read())
		f.close()
		return t
	
	@staticmethod
	def fromString(string_thing, n=None):
		tag.stringthing = string_thing
		if n == None:
			n = tag.nexts()
		
		def fromStringPL(n=None):
			if n == None:
				n = tag.nexts()
			
			id = 0
			if n[0] in tag.toId:
				id = tag.toId[n[0]]
			if id >= 1 and id <= 6:
				return (id, n[1], 1)
			
			if n[0] == "[B;":
				value = []
				while True:
					n = tag.nexts()
					if n[0] == "]":
						break
					if n[0] == "byte" or n[0] == "int":
						value.append(n[1])
					else:
						raise Exception("SNBT Parsing Error: invalid item in byte array")

					n = tag.nexts()
					if n[0] == "]":
						break
					if n[0] != ",":
						raise Exception("SNBT Parsing Error: invalid item in byte array")
				
				return (7, value, 1)
			if n[0] == "string":
				return (8, n[1], 1)
			if n[0] == "[":
				value = []
				listid = 0
				while True:
					n = tag.nexts()
					if n[0] == "]":
						break
					
					itemid, itemvalue, itemlistid = fromStringPL(n)
					if listid == 0:
						listid = itemid
					elif listid != itemid:
						raise Exception("SNBT Parsing Error: inconsistent list type")
					
					if itemid == 9:
						value.append(tag(9, itemvalue, "", itemlistid))
					else:
						value.append(itemvalue)

					n = tag.nexts()
					if n[0] == "]":
						break
					if n[0] != ",":
						raise Exception("SNBT Parsing Error: invalid list")
				
				return (9, value, listid)
			if n[0] == "{":
				value = []
				while True:
					n = tag.nexts()
					if n[0] == "}":
						break

					value.append(tag.fromString(tag.stringthing, n))

					n = tag.nexts()
					if n[0] == "}":
						break
					if n[0] != ",":
						raise Exception("SNBT Parsing Error: invalid compound list")
				
				return (10, value, 1)
			if n[0] == "[I;":
				value = []
				while True:
					n = tag.nexts()
					if n[0] == "]":
						break
					if n[0] == "int":
						value.append(n[1])
					else:
						raise Exception("SNBT Parsing Error: invalid item in int array")

					n = tag.nexts()
					if n[0] == "]":
						break
					if n[0] != ",":
						raise Exception("SNBT Parsing Error: invalid item in int array")
				
				return (11, value, 1)
			if n[0] == "[L;":
				value = []
				while True:
					n = tag.nexts()
					if n[0] == "]":
						break
					if n[0] == "long" or n[0] == "int":
						value.append(n[1])
					else:
						raise Exception("SNBT Parsing Error: invalid item in long array")

					n = tag.nexts()
					if n[0] == "]":
						break
					if n[0] != ",":
						raise Exception("SNBT Parsing Error: invalid item in long array")
				
				return (12, value, 1)

			raise Exception("SNBT Parsing Error: invalid character '" + n[1] + "'")
		

		if n[0] == "string":
			name = n[1]
			
			if tag.nexts()[0] != ":":
				raise Exception("SNBT Parsing Error: missing ':'")
			n = tag.nexts()
		else:
			name = ""
		
		id, value, listid = fromStringPL(n)
		return tag(id, value, name, listid)



class structure:
	def __init__(self, size=[1,1,1], entities=[], blocks=[], palette=[], DataVersion=2580):
		self.size = size
		self.entities = entities
		self.blocks = blocks
		self.palette = palette
		self.DataVersion = DataVersion
	
	@staticmethod
	def load(path):
		pass

	def save(path):
		



class mapdata:
	def __init__():
		pass



