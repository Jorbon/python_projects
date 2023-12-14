avg = {}
pointtable = [50, 100, 200, 300, 400, 500, 600, 1000, 2000]
dicetable = [1, 1, 3, 3, 3, 3, 3, 4, 5]

# strategy preferences
ranks = [8, 7, 9, 6, 5, 4, 3, 2, 1]
cutoff = [0, 300, 250, 400, 750, 2150, 5000]


def getStoredAvg(n, carry):
	if carry in avg:
		return avg[carry][n]
	return 0

def score(points, nextn, carry):
	return points + getStoredAvg(nextn, carry + points)

def getAvgScore(n, carry):
	if carry >= cutoff[n]:
		return 0

	sum = 0
	
	for d in range(6 ** n):
		sets = {}
		ds = d
		for i in range(n):
			ns = ds % 6 + 1
			ds = int(ds / 6)
			if ns in sets:
				sets[ns] += 1
			else:
				sets[ns] = 1

		spread = []
		num = list(sets.keys())
		count = list(sets.values())
		for i in range(len(sets)):
			spread.append((count[i], num[i]))
		spread = sorted(spread, key = lambda a : a[1] - a[0]*10)
		for i in range(len(sets)):
			(count[i], num[i]) = spread[i]
		
		
		if len(num) == 6 or (len(num) == 3 and count[0] == count[1] == count[2] == 2) or (len(num) == 2 and count[0] == 4 and count[1] == 2):
			sum += score(1500, 6, carry)
			continue
		if count[0] == 6:
			sum += score(3000, 6, carry)
			continue
		if len(num) == 2 and count[0] == count[1] == 3:
			sum += score(2500, 6, carry)
			continue

		pointunits = []
		pointtotal = 0
		pointdice = 0
		for i in range(len(num)):
			if count[i] == 5:
				pointunits.append(8)
				pointtotal += 2000
				pointdice += 5
			elif count[i] == 4:
				pointunits.append(7)
				pointtotal += 1000
				pointdice += 4
			elif count[i] == 3:
				if num[i] == 1:
					pointunits.append(1)
					pointunits.append(1)
					pointunits.append(1)
					pointtotal += 300
				else:
					pointunits.append(num[i])
					pointtotal += 100 * num[i]
				pointdice += 3
			elif count[i] == 2:
				if num[i] == 1:
					pointunits.append(1)
					pointunits.append(1)
					pointtotal += 200
					pointdice += 2
				elif num[i] == 5:
					pointunits.append(0)
					pointunits.append(0)
					pointtotal += 100
					pointdice += 2
			elif count[i] == 1:
				if num[i] == 1:
					pointunits.append(1)
					pointtotal += 100
					pointdice += 1
				elif num[i] == 5:
					pointunits.append(0)
					pointtotal += 50
					pointdice += 1
			else:
				print("count what? " + str(count[i]))
				return 0

		if pointdice == 0:
			sum -= carry
			continue

		if pointdice == n:
			sum += score(pointtotal, 6, carry)
			continue

		pointunits = sorted(pointunits, key = lambda a : ranks[a])

		# strategy
		if n - dicetable[pointunits[0]] <= 2:
			sum += score(pointtotal, n - pointdice, carry)
		else:
			sum += score(pointtable[pointunits[0]], n - dicetable[pointunits[0]], carry)
		

	
	return sum / (6 ** n)


f = open("C:\\Users\\benap\\Desktop\\f.csv", "w")

for carry in range(cutoff[6], -1, -50):
	entry = [0]
	out = str(carry)
	for n in range(1, 7):
		a = getAvgScore(n, carry)
		entry.append(a)
		out += ", " + str(round(a))
	avg[carry] = entry

	f.write(out + "\n")
	if carry % 500 == 0:
		print(carry)

f.close()
