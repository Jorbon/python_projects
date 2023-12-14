import sys

def k(state, x, y, c=1):
	a = (x+1, x+1, x+2, x+2, x-1, x-1, x-2, x-2)
	b = (y+2, y-2, y+1, y-1, y+2, y-2, y+1, y-1)
	vi = []
	for i in range(8):
		if a[i] >= 0 and a[i] < n and b[i] >= 0 and b[i] < n:
			if (state >> (a[i]*n + b[i])) & 1 == 0:
				vi.append(i)
	
	global ct, max_c
	ct += 1
	if c > max_c:
		max_c = c
	if ct > n*n*100:
		return False
	
	vi.sort(key=lambda i : a[i]*(n-1-a[i]) + b[i]*(n-1-b[i]))
	
	for idx in range(len(vi)):
		i = vi[idx]
		newstate = state | (1 << (a[i]*n + b[i]))
		if k(newstate, a[i], b[i], c+1) or (newstate == (1 << (n*n)) - 1):
			positions.append(a[i]*n + b[i])
			return True
	return False

n = 0
ct = 0
cc = 0
max_c = 0
positions = []

def solve_board(size:int, print_tour=False, starting_x=0, starting_y=0):
	global n, ct, max_c, positions
	n = size
	ct = 0
	cc = 0
	max_c = 0
	positions = []
	
	while True:
		cc += 1
		if k(1 << (starting_x*n + starting_y), starting_x, starting_y):
			break
		ct = 0
		starting_y += 1
		if starting_y > starting_x:
			starting_y = 0
			starting_x += 1
			if starting_x > n*0.5:
				print(f"{n}x{n}: Reasonable solution not found from any board space. Max progress: {max_c}/{n*n}")
				return
	
	print(f"{n}x{n}: Solution found in {ct} moves on attempt {cc} from position ({starting_x+1}, {starting_y+1})")
	
	if print_tour:
		positions.append(starting_x*n + starting_y)
		
		board = []
		for i in range(n*n):
			board.append("x")
		
		for i in range(len(positions)):
			board[positions[-i-1]] = i+1
		
		s = ""
		for i in range(len(board)):
			s += str(board[i])
			if i % n == n - 1:
				s += "\n"
			else:
				s += "\t"
		
		print(s)


sys.setrecursionlimit(3000)

for s in range(1, 47):
	solve_board(s)

for s in range(5, 21):
	solve_board(s, True)