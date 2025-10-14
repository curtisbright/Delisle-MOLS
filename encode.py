#!/usr/bin/env python3
import sys
import json

# Counter for # of variables used in SAT instance
total_vars = 0
# List to hold clauses of SAT instance
clauses = []

# Generate a clause containing the literals in the set B, a row 
def generate_clause(X):
	clause = ""
	for x in X:
		clause += str(x) + " "
	clauses.append(clause + "0")

# Generate a clause specifying (x1 & ... & xn) -> (y1 | ... | yk)
# where X = {x1, ..., xn} and Y = {y1, ..., yk}
def generate_implication_clause(X, Y):
	if 'F' in X or 'T' in Y:
		return
	X = X - {'T'}
	Y = Y - {'F'}
	clause = ""
	for x in X:
		clause += str(-x) + " "
	for y in Y:
		clause += str(y) + " "
	clauses.append(clause + "0")

# Generate clauses encoding that <= s variables and >= l variables in X are assigned true
# using Sinz's sequential counter encoding
def generate_adder_clauses(X, l, s):
	global total_vars

	n = len(X)
	k = s+1

	S = [[0 for j in range(k+1)] for i in range(n+1)]

	for i in range(n+1):
		S[i][0] = 'T' # Vacuously at least 0 of {X_0, ..., X_(i-1)} are true

	for j in range(1, k+1):
		S[0][j] = 'F' # Never true that at least j>=1 of {} are true

	for j in range(1, l+1):
		S[n][j] = 'T' # Constrain that >= l of {X_0, ..., X_(n-1)} are true

	for i in range(1, n+1):
		S[i][k] = 'F' # Constrain that < k of {X_0, ..., X_(n-1)} are true

	# Define new auxiliary variables (and updates the global variable total_vars)
	for i in range(n+1):
		for j in range(k+1):
			if S[i][j] == 0:
				total_vars += 1
				S[i][j] = total_vars

	# Generate clauses encoding cardinality constraint
	for i in range(1, n+1):
		for j in range(1, k+1):
			generate_implication_clause({S[i-1][j]}, {S[i][j]})
			generate_implication_clause({X[i-1], S[i-1][j-1]}, {S[i][j]})
			if j <= l:
				generate_implication_clause({S[i][j]}, {S[i-1][j], X[i-1]})
				generate_implication_clause({S[i][j]}, {S[i-1][j-1]})

# Generate clauses encoding exactly one variable in X is assigned true
def generate_exactly_one_clauses(X):
	generate_adder_clauses(X, 1, 1)

# Read relations from the first command-line argument
if len(sys.argv) <= 1:
	print("Provide the form of the two relations as the first command-line argument, e.g., python3 encoder.py [[1,3,3],[1,3,3],[1,3,3],[1,3,3]]")
	quit()

data = json.loads(sys.argv[1])

PARALLEL_CLASSES = len(data) 
ROW = 100 
N = 10
COLUMN = N*PARALLEL_CLASSES

# A stores the adjacency matrix variables
A = [[0 for j in range(COLUMN)] for i in range(ROW)]
for i in range(ROW):
	for j in range(COLUMN):
		total_vars += 1
		A[i][j] = total_vars

# Variables for the Latin squares A, B, and Z
LA = [[[0 for k in range(10)] for j in range(10)] for i in range(10)]
LB = [[[0 for k in range(10)] for j in range(10)] for i in range(10)]
LZ = [[[0 for k in range(10)] for j in range(10)] for i in range(10)]

for i in range(10):
	for j in range(10):
		for k in range(10):
			LA[i][j][k] = A[i*10+j][20+k]
			LB[i][j][k] = A[i*10+j][30+k]
			total_vars += 1
			LZ[i][j][k] = total_vars

# Latin square constraints
for i in range(10):
	for j in range(10):
		generate_exactly_one_clauses([LA[i][j][k] for k in range(10)])
		generate_exactly_one_clauses([LA[i][k][j] for k in range(10)])
		generate_exactly_one_clauses([LA[k][i][j] for k in range(10)])
		generate_exactly_one_clauses([LB[i][j][k] for k in range(10)])
		generate_exactly_one_clauses([LB[i][k][j] for k in range(10)])
		generate_exactly_one_clauses([LB[k][i][j] for k in range(10)])
		generate_exactly_one_clauses([LZ[i][j][k] for k in range(10)])
		generate_exactly_one_clauses([LZ[i][k][j] for k in range(10)])
		generate_exactly_one_clauses([LZ[k][i][j] for k in range(10)])

# Orthogonality constraints
for i in range(10):
	for j in range(10):
		for k in range(10):
			for l in range(10):
				generate_implication_clause({LB[i][j][k], LA[i][j][l]}, {LZ[i][k][l]})
				generate_implication_clause({LB[i][j][k], LZ[i][k][l]}, {LA[i][j][l]})
				generate_implication_clause({LA[i][j][l], LZ[i][k][l]}, {LB[i][j][k]})

# Fix the first and second parallel classes
ROW_LIST = [(i*N,(i+1)*N) for i in range(N)]
for interval in ROW_LIST:
	for row in range(interval[0], interval[-1]):
		# First parallel class
		for col in range(N):
			if col == ROW_LIST.index(interval):
				generate_clause([A[row][col]])
			else:
				generate_clause([-A[row][col]])

		# Second parallel class
		for col1 in range(N,2*N):
			if col1 == (N+row%N):
				generate_clause([A[row][col1]])
			else:
				generate_clause([-A[row][col1]])

# Take relation data and produce the equivalence classes of rows/columns/symbols
def to_classes(R):
	return [range(R[0]), range(R[0],R[0]+R[1]), range(R[0]+R[1],R[0]+R[1]+R[2]), range(R[0]+R[1]+R[2],N)]

# Row and column class data
row_classes = to_classes(data[0])
col_classes = to_classes(data[1])
sym1_classes = to_classes(data[2])
sym2_classes = to_classes(data[3])

# Symmetry breaking for 2-MOLS(10) following the method in Delisle's thesis

# Symmetry breaking on rows (first Latin square)
for c in range(4):
	for i in row_classes[c][:-1]:
		for s in range(N):
			for s2 in range(s):
				generate_implication_clause({LA[i][0][s]}, {-LA[i+1][0][s2]})

# Symmetry breaking on cols (first Latin square)
for c in range(0 if data[0] == data[1] else 1, 4):
	for j in col_classes[c][:-1]:
		for s in range(N):
			for s2 in range(s):
				generate_implication_clause({LA[0][j][s]}, {-LA[0][j+1][s2]})

# Symmetry breaking on symbols (first Latin square)
for c in range(4):
	for j in range(N):
		for j2 in range(j):
			for s in sym1_classes[c][:-1]:
				generate_implication_clause({LA[j][0][s]}, {-LA[j2][0][s+1]})

# Symmetry breaking on symbols (second Latin square)
for c in range(4):
	for j in range(N):
		for j2 in range(j):
			for s in sym2_classes[c][:-1]:
				generate_implication_clause({LB[j][0][s]}, {-LB[j2][0][s+1]})

# Symmetry breaking using the transpose equivalence
if data[0] == data[1]:
	# Ensure (1,0) symbol pair is <= the (0,1) symbol pair
	for sp in range(N):
		for s in range(sp):
			generate_implication_clause({LA[1][0][sp]}, {-LA[0][1][s]})
		for tp in range(N):
			for t in range(tp):
				generate_implication_clause({LA[1][0][sp], LA[0][1][sp], LB[1][0][tp]}, {-LB[0][1][t]})

# Symmetry breaking using the swapping equivalence applies in all cases except case 2
if data[2] == data[3]:
	# Ensure LA[1][0] <= LB[1][0]
	for tp in range(N):
		for t in range(tp):
			generate_implication_clause({LA[1][0][tp]}, {-LB[1][0][t]})

	# If LA[1][0] == LB[1][0] then LA[2][0] <= LB[2][0]
	for t in range(N):
		for up in range(N):
			for u in range(up):
				generate_implication_clause({LA[1][0][t], LB[1][0][t], LA[2][0][up]}, {-LB[2][0][u]})

# Extract columns in relation 1 in class c (0 to 3)
def extract_r1(R, c):
	return list(range(N*c,N*c+R[0]+R[1]))

# Extract columns in relation 2 in class c (0 to 3)
def extract_r2(R, c):
	return list(range(N*c,N*c+R[0])) + list(range(N*c+R[0]+R[1],N*c+R[0]+R[1]+R[2]))

R1 = extract_r1(data[0],0) + extract_r1(data[1],1) + extract_r1(data[2],2) + extract_r1(data[3],3)
R2 = extract_r2(data[0],0) + extract_r2(data[1],1) + extract_r2(data[2],2) + extract_r2(data[3],3)

# Functions implementing Delisle's equivalence classes (defined in Section 2.2 of Delisle's thesis)
def br1(r): return 1 if r in R1 else 0
def br2(r): return 1 if r in R2 else 0
def bc1(c): return 1 if c+N in R1 else 0
def bc2(c): return 1 if c+N in R2 else 0
def rc_class(r,c): return 2*((br1(r)+bc1(c))% 2) + (br2(r)+bc2(c))%2
def bs1(s): return 1 if s+2*N in R1 else 0
def bs2(s): return 1 if s+2*N in R2 else 0
def bt1(t): return 1 if t+3*N in R1 else 0
def bt2(t): return 1 if t+3*N in R2 else 0
def st_class(s,t): return 2*((bs1(s)+bt1(t))% 2) + (bs2(s)+bt2(t))%2

# Relation constraints using Delisle's classes
for r in range(N):
	for c in range(N):
		for s in range(N):
			for t in range(N):
				if rc_class(r,c) != st_class(s,t):
					generate_clause({-LA[r][c][s], -LB[r][c][t]})

# Output SAT instance in DIMACS format
print("p cnf {0} {1}".format(total_vars, len(clauses)))
for clause in clauses:
	print(clause)
