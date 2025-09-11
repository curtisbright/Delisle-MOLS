#!/usr/bin/env python3

import fileinput
import sys
import os
import time
from pynauty import *

# Pass -v for verbose mode
verbose = "-v" in sys.argv
if verbose: sys.argv.remove("-v")

# Pass a directory name as the first command-line argument to save copies of MOLS up to equivalence in the given directory
write_mols = (len(sys.argv) > 1)

if write_mols:
    dirname = sys.argv[1]
    os.makedirs(dirname, exist_ok=True)

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

# Convert the pair of Latin squares (X, Y) into a graph
def reduce_to_graph(X, Y):
    n = len(X)  # Assuming X and Y are n x n Latin squares
    g = Graph(4 + 4 * n + n * n)  # Total vertices: columns + symbols + rows

    # Initialize the adjacency list
    for i in range(4 + 4 * n + n * n):
        g.adjacency_dict[i] = []

    # Define the vertex groups
    column_vertices = range(4)  # Type 1: 4 column vertices
    symbol_vertices = range(4, 4 + 4 * n)  # Type 2: 4*n symbol vertices
    row_vertices = range(4 + 4 * n, 4 + 4 * n + n * n)  # Type 3: n*n row vertices

    # Set the vertex coloring based on types
    g.set_vertex_coloring([
        set(column_vertices),  # Type 1: Columns
        set(symbol_vertices),   # Type 2: Symbols
        set(row_vertices)       # Type 3: Rows
    ])

    # Add edges between Type 1 (Columns) and Type 2 (Symbols)
    for column_index in range(4):
        column_vertex = column_index
        for i in range(n):
            for j in range(n):
                if column_index == 0:
                    symbol = i  # Row index symbol
                elif column_index == 1:
                    symbol = j  # Column index symbol
                elif column_index == 2:
                    symbol = X[i][j]  # Symbol from X
                else:
                    symbol = Y[i][j]  # Symbol from Y

                # Map this symbol to a Type 2 vertex
                symbol_vertex = 4 + column_index * n + symbol
                if symbol_vertex not in g.adjacency_dict[column_vertex]:
                    g.adjacency_dict[column_vertex].append(symbol_vertex)
                if column_vertex not in g.adjacency_dict[symbol_vertex]:
                    g.adjacency_dict[symbol_vertex].append(column_vertex)

    # Add edges between Type 2 (Symbols) and Type 3 (Rows)
    for row in range(n):
        for col in range(n):
            # Type 3 vertex [row, col, X[row][col], Y[row][col]] in the orthogonal array
            type3_vertex = 4 + 4 * n + row * n + col  
            g.adjacency_dict[type3_vertex].append(4 + 0*n + row)
            g.adjacency_dict[type3_vertex].append(4 + 1*n + col)
            g.adjacency_dict[type3_vertex].append(4 + 2*n + X[row][col])
            g.adjacency_dict[type3_vertex].append(4 + 3*n + Y[row][col])

            g.adjacency_dict[4 + 0*n + row].append(type3_vertex)
            g.adjacency_dict[4 + 1*n + col].append(type3_vertex)
            g.adjacency_dict[4 + 2*n + X[row][col]].append(type3_vertex)
            g.adjacency_dict[4 + 3*n + Y[row][col]].append(type3_vertex)

    return g

certificates = dict()
c = 0
start_time = time.time()

for line in fileinput.input(files='-'):
    l = list(map(int, line.split()[3:-1]))

    A,B=to_mols(l)

    if verbose:
        print("List of positive literals in solution: " + str(l))
        print_square_latin(A)
        print_square_latin(B)

    g = reduce_to_graph(A, B)
    cert = certificate(g)

    c += 1

    if cert not in certificates:
        certificates[cert] = c
        print(f"graph {c} is new... {len(certificates)}/{c} distinct graphs")
        if write_mols:
            f = open(os.path.join(dirname, f"{c}.sol"), 'w')
            print_square_latin(A,f)
            print_square_latin(B,f)
            f.close()
    elif verbose:
        print(f"graph {c} is a duplicate of graph {certificates[cert]}... {len(certificates)}/{c} distinct graphs")
    if verbose: print("")

end_time = time.time()

print(f"Checked {c} graphs in {round(end_time-start_time,2)} seconds")
