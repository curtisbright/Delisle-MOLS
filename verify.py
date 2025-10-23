#!/usr/bin/env python3

import fileinput
import sys
import json
import time

# Pass -v for verbose mode
verbose = "-v" in sys.argv
if verbose: sys.argv.remove("-v")

# Read relations from the first command-line argument
if len(sys.argv) <= 1:
    print("Provide the form of the two relations as the first command-line argument, e.g., python3 verify.py [[1,3,3],[1,3,3],[1,3,3],[1,3,3]]")
    print("Provide the list of solutions to verify on the standard input")
    quit()

data = json.loads(sys.argv[1])

n = 10

# Convert the list l of positive literals from solution into a pair of Latin squares
def to_mols(l):
    LA = [[-1 for j in range(n)] for i in range(n)]
    LB = [[-1 for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if 4*n*(i*n+j)+2*n+k+1 in l:
                    LA[i][j] = k
                if 4*n*(i*n+j)+3*n+k+1 in l:
                    LB[i][j] = k

    return(LA, LB)

# Print Latin square A to file f
def print_square_latin(A,f=None):
    for i in range(n):
        st = ""
        for j in range(n):
            st += str(A[i][j])+" "
        print(st[:-1], file=f)
    print(file=f)

# Take relation data and produce the equivalence classes of rows/columns/symbols
def to_classes(R):
    return [range(R[0]), range(R[0],R[0]+R[1]), range(R[0]+R[1],R[0]+R[1]+R[2]), range(R[0]+R[1]+R[2],n)]

# Row and column class data
row_classes = to_classes(data[0])
col_classes = to_classes(data[1])
sym1_classes = to_classes(data[2])
sym2_classes = to_classes(data[3])

# Extract columns in relation 1 in class c (0 to 3)
def extract_r1(R, c):
    return list(range(n*c,n*c+R[0]+R[1]))

# Extract columns in relation 2 in class c (0 to 3)
def extract_r2(R, c):
    return list(range(n*c,n*c+R[0])) + list(range(n*c+R[0]+R[1],n*c+R[0]+R[1]+R[2]))

R1 = extract_r1(data[0],0) + extract_r1(data[1],1) + extract_r1(data[2],2) + extract_r1(data[3],3)
R2 = extract_r2(data[0],0) + extract_r2(data[1],1) + extract_r2(data[2],2) + extract_r2(data[3],3)

# Functions implementing Delisle's equivalence classes (defined in Section 2.2 of Delisle's thesis)
def br1(r): return 1 if r in R1 else 0
def br2(r): return 1 if r in R2 else 0
def bc1(c): return 1 if c+n in R1 else 0
def bc2(c): return 1 if c+n in R2 else 0
def rc_class(r,c): return 2*((br1(r)+bc1(c))% 2) + (br2(r)+bc2(c))%2
def bs1(s): return 1 if s+2*n in R1 else 0
def bs2(s): return 1 if s+2*n in R2 else 0
def bt1(t): return 1 if t+3*n in R1 else 0
def bt2(t): return 1 if t+3*n in R2 else 0
def st_class(s,t): return 2*((bs1(s)+bt1(t))% 2) + (bs2(s)+bt2(t))%2

count = 0
start_time = time.time()

# Read list of solutions from the standard input
for line in fileinput.input(files='-'):
    l = list(map(int, line.split()[3:-1]))

    # Read incidence matrix
    IM = [[0 for j in range(40)] for i in range(n*n)]
    for i in range(n):
        for j in range(n):
            IM[j+i*n][i] = 1
            IM[j+i*n][10+j] = 1
    for lit in l:
        row = (lit-1)//40
        col = (lit-1)%40
        IM[row][col] = 1

    # Read MOLS
    A, B = to_mols(l)

    if verbose:
        print("List of positive literals in solution: " + str(l))
        print_square_latin(A)
        print_square_latin(B)

    # Check squares A and B are Latin
    for i in range(n):
        assert(sorted([A[i][j] for j in range(n)])==list(range(n)))
        assert(sorted([B[i][j] for j in range(n)])==list(range(n)))

    for j in range(n):
        assert(sorted([A[i][j] for i in range(n)])==list(range(n)))
        assert(sorted([B[i][j] for i in range(n)])==list(range(n)))

    # Check symmetry breaking
    for c in range(4):
        assert(sorted([A[i][0] for i in row_classes[c]])==[A[i][0] for i in row_classes[c]]) # Symmetry breaking on rows
        assert(sorted([A[0][i] for i in col_classes[c]])==[A[0][i] for i in col_classes[c]]) # Symmetry breaking on cols
        # Symmetry breaking on symbols in A
        S = []
        for s in sym1_classes[c]:
            for i in range(n):
                if A[i][0] == s: S.append(A[i][0])
        assert(sorted(S)==S)
        # Symmetry breaking on symbols in B
        T = []
        for t in sym2_classes[c]:
            for i in range(n):
                if B[i][0] == t: T.append(B[i][0])
        assert(sorted(T)==T)

    assert(A[1][0] < A[0][1] or (A[1][0] == A[0][1] and B[1][0] < B[0][1])) # Symmetry breaking via transpose
    i = 0
    while(A[i][0] == B[i][0]): i += 1
    assert(A[i][0] < B[i][0]) # Symmetry breaking via swapping A and B

    # Check orthogonality
    assert(sorted([[A[i][j], B[i][j]] for i in range(n) for j in range(n)])==[[x,y] for x in range(n) for y in range(n)])

    # Check the relation constraints using Delisle's classes
    for r in range(n):
        for c in range(n):
            assert(rc_class(r,c) == st_class(A[r][c],B[r][c]))

    # Check the relation constraints using sums
    for i in range(n*n):
        assert(sum([IM[i][j] for j in R1]) % 2 == 0)
        assert(sum([IM[i][j] for j in R2]) % 2 == 0)

    count += 1

end_time = time.time()

print(f"{count} solutions verified in {round(end_time-start_time,2)} seconds")
