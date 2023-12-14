symbols = " H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og".split(" ")
masses = [0, 1.008, 4.0026, 6.94, 9.0122, 10.81, 12.011, 14.007, 15.999, 18.998, 20.18, 22.99, 24.305, 26.982, 28.805, 30.974, 32.06, 35.45, 39.948, 39.098, 40.078, 44.956, 47.867, 50.942, 51.996, 54.938, 55.845, 58.933, 58.693, 63.546, 65.38, 69.723, 72.63, 74.922, 78.971, 79.904, 83.798, 85.468, 87.62, 88.906, 91.224, 92.906, 95.95, 98, 101.07, 102.91, 106.42, 107.87, 112.41, 114.82, 118.71, 121.76, 127.60, 126.90, 131.29, 132.91, 137.33, 138.91, 140.12, 140.91, 144.24, 145, 150.36, 151.96, 157.25, 158.93, 162.50, 164.93, 167.26, 168.93, 173.05, 174.97, 178.49, 180.95, 183.84, 186.21, 190.23, 192.22, 195.08, 196.97, 200.59, 204.38, 207.2, 208.98, 209, 210, 222, 223, 226, 227, 232.04, 231.04, 238.03, 237, 244, 243, 247, 247, 251, 252, 257, 258, 259, 266, 267, 268, 269, 270, 277, 278, 281, 282, 285, 286, 289, 290, 293, 294, 294]

massmap = {}
for i in range(len(symbols)):
	massmap[symbols[i]] = masses[i]


def getMass(form):
	mass = 0
	gmult, form = getFrontNum(form)
	while len(form) > 0:
		if form[0] == "(":
			[p1, p2] = form[1:].split(")", 1)
			mult, form = getFrontNum(p2)
			mass += getMass(p1) * mult
		elif ord(form[0]) >= 65 and ord(form[0]) <= 90:
			l = 1
			if len(form) >= 2 and ord(form[1]) >= 97 and ord(form[1]) <= 122:
				l = 2
			mult, temp = getFrontNum(form[l:])

			try:
				mass += massmap[form[:l]] * mult
			except:
				#print("\"" + form[:l] + "\" isn't an element")
				pass
			
			form = temp
		else:
			form = form[1:]
	return mass * gmult


def getFrontNum(s):
	if len(s) == 0 or ord(s[0]) < 48 or ord(s[0]) > 57:
		return (1, s)
	out = 0
	while True:
		out = out * 10 + ord(s[0]) - 48
		s = s[1:]
		if len(s) == 0 or ord(s[0]) < 48 or ord(s[0]) > 57:
			return (out, s)


n = ""
mode = "m"
while True:
	n = input()
	if n == "q":
		print("ok bye")
		break
	elif n == "m":
		mode = n
		print("Molar mass mode")
		continue
	elif n == "s":
		mode = n
		print("Stoichiometry mode")
		continue
	
	if len(n) > 0:
		if mode == "m":
			print(str(round(getMass(n), 4)) + "g")
		elif mode == "s":
			p = n.split(" ", 2)
			if len(p) == 3:
				if p[0][-1] == "g":
					p[0] = p[0][:-1]
				print(str(round(float(p[0]) * getMass(p[2]) / getMass(p[1]), 4)) + "g")
			else:
				print("bad input")




