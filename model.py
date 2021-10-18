import numpy as np
import copy
import random

TREE = 0
TENT = 1
EMPTY = -2
GRASS = 2 # GRASS > 1

def ingest_file(path):
    stream = open(path,'r')
    data = stream.readlines()
    stream.close()
    h_constraints = list(map(int,list(data[0].strip())))
    v_constraints = list(map(int,list(data[1].strip())))
    trees = []
    for i,line in enumerate(data[2:]):
        cursor = 0
        for c in line.strip().split(' '):
            size = 1
            if len(c) == 2:
                size = int(c[1])
            for l in range(size):
                if c[0] == 't':
                    trees.append((i,cursor+l))
            cursor += size
    return i + 1, trees, h_constraints, v_constraints

def constructor_from_grid(grid, h_constraints, v_constraints, trees, tents):
    g = Game(grid.shape[0],trees, h_constraints, v_constraints)
    g.grid = grid
    g.tents = tents
    g._init_grid()
    return g

class Game:


    def __init__(self, grid_size, trees, h_constraints, v_constraints, verbose=False):
        assert len(h_constraints) == len(v_constraints) == grid_size,\
                f"Incorrect constraints size ({grid_size},{len(h_constraints)},{len(v_constraints)})"
        self.grid = np.ones([grid_size,grid_size])*GRASS
        self.verbose = verbose
        self.grid_valid = True
        self.h_constraints = np.array(h_constraints)
        self.v_constraints = np.array(v_constraints)
        self.trees_satisfied = False
        self.trees = trees
        self.tents = []
        rows, cols = zip(*self.trees)
        self.grid[rows, cols] = TREE
        self._init_grid()


    def extract_conf(self):
        return self.grid.copy(),\
               self.h_constraints.copy().tolist(),\
               self.v_constraints.copy().tolist(),\
               [ind for ind in self.trees],\
               [ind for ind in self.tents]


    def _init_grid(self):
        if self.verbose:
            print("========= INIT GRID")
        self.tree_neighbors = []
        self.tent_neighbors = []
        self.calc_tree_neighbors()
        self.calc_tent_neighbors()


    def calc_tree_neighbors(self):
        array = self.trees
        grid_size = self.grid.shape[0]
        for tree_n, (tree_i, tree_j) in enumerate(array):
            # CONSTRUCT INDICES FOR NEIGHBORS
            neighbors = []
            if tree_i < grid_size - 1:
                neighbors.append((tree_i + 1, tree_j))
            if tree_i > 0:
                neighbors.append((tree_i - 1, tree_j))
            if tree_j < grid_size - 1:
                neighbors.append((tree_i, tree_j + 1))
            if tree_j > 0:
                neighbors.append((tree_i, tree_j - 1))
            self.tree_neighbors.append((tree_n, neighbors))


    def in_bounds(self, x, y):
        return x >= 0 and y >= 0 and\
               x < self.grid.shape[0] and y < self.grid.shape[0]

    def calc_tent_neighbors(self):
        self.tents = list(set(self.tents))
        array = self.tents
        self.tent_neighbors = []
        grid_size = self.grid.shape[0]
        for tree_n, (tree_i, tree_j) in enumerate(array):
            # CONSTRUCT INDICES FOR NEIGHBORS
            neighbors = []
            for n in list(range(4)) + list(range(5,9)):
                i,j = n//3 - 1, n%3 - 1
                ind = (tree_i + i, tree_j + j)
                if self.in_bounds(*ind):
                    neighbors.append(ind)
            self.tent_neighbors.append((tree_n, neighbors))


    def random_tent(self):
        if self.verbose:
            print("========= RANDOM TENT")
        for tree_n, neighbors in random.sample(self.tree_neighbors,len(self.tree_neighbors)):
            rows, cols = zip(*neighbors)
            empty_neighbors = np.array(neighbors)[
                np.argwhere(self.grid[rows,cols]<0).reshape(-1)
            ].tolist()
            tent_neighbors = np.array(neighbors)[
                np.argwhere(self.grid[rows,cols]==TENT).reshape(-1)
            ].tolist()
            if (len(empty_neighbors) > 0) & (len(tent_neighbors) == 0):
                rows, cols = zip(*random.sample(empty_neighbors,len(empty_neighbors))[:1])
                self.grid[rows, cols] = TENT
                self.tents.append(tuple(empty_neighbors[0]))
                self.calc_tent_neighbors()
                return


    def null_constraints(self):
        h_null = np.argwhere(self.h_constraints == 0)
        v_null = np.argwhere(self.v_constraints == 0)
        self.grid[v_null, :] = np.power(self.grid[v_null,:],2)
        self.grid[:, h_null] = np.power(self.grid[:, h_null],2)
        if self.verbose:
            print("========= NULL CONSTRAINTS")
            print(self)


    def tree_constraints(self):
        for tree_n, neighbors in self.tree_neighbors:
            rows, cols = zip(*neighbors)
            grass_neighbors = np.array(neighbors)[
                np.argwhere(self.grid[rows,cols]>1).reshape(-1)
            ].tolist()
            if len(grass_neighbors) > 0:
                rows, cols = zip(*grass_neighbors)
                self.grid[rows, cols] = EMPTY
        if self.verbose:
            print("========== TREE CONSTRAINTS")
            print(self)


    def check_tree_neighbors(self):
        self.trees_satisfied = True
        for tree_n, neighbors in self.tree_neighbors:
            rows, cols = zip(*neighbors)
            empty_neighbors = np.array(neighbors)[
                np.argwhere(self.grid[rows,cols]<0).reshape(-1)
            ].tolist()
            tent_neighbors = np.array(neighbors)[
                np.argwhere(self.grid[rows,cols]==TENT).reshape(-1)
            ].tolist()
            if len(tent_neighbors) == 0:
                self.trees_satisfied = False
            if (len(empty_neighbors) == 1) & (len(tent_neighbors) == 0):
                rows, cols = zip(*empty_neighbors)
                self.grid[rows, cols] = TENT
                self.tents.append(tuple(empty_neighbors[0]))
                self.calc_tent_neighbors()
        if self.verbose:
            print("========= CHECK TREE NEIGHBORS")
            print(self)

    def check_tent_neighbors(self):
        for tree_n, neighbors in self.tent_neighbors:
            rows, cols = zip(*neighbors)
            empty_neighbors = np.array(neighbors)[
                np.argwhere(self.grid[rows,cols]<0).reshape(-1)
            ].tolist()
            tent_neighbors = np.array(neighbors)[
                np.argwhere(self.grid[rows,cols]==TENT).reshape(-1)
            ].tolist()
            if len(tent_neighbors) > 0:
                self.grid_valid = False
            elif len(empty_neighbors) != 0:
                rows, cols = zip(*empty_neighbors)
                self.grid[rows, cols] = GRASS
        if self.verbose:
            print("========= CHECK TENT NEIGHBORS")
            print(self)

    def check_constraints(self):
        for i, constr in enumerate(self.h_constraints):
            # calculate relevant numbers
            squares = self.grid[:, i]
            tents = np.argwhere(squares == TENT)
            n_tents = tents.shape[0]
            empty = np.argwhere(squares < 0)
            n_empty = empty.shape[0]
            # logic
            if n_tents > constr:
                self.grid_valid = False
            if constr - n_tents == 0: # fill empty with grass
                self.grid[empty, i] = GRASS
            if constr - n_tents == n_empty:
                # fill empty with tents
                self.grid[empty, i] = TENT
                tent_indices = np.argwhere(self.grid==TENT)
                self.tents.extend(list(map(tuple,tent_indices.tolist())))
                self.calc_tent_neighbors()

        for i, constr in enumerate(self.v_constraints):
            # calculate relevant numbers
            squares = self.grid[i, :]
            tents = np.argwhere(squares == TENT)
            n_tents = tents.shape[0]
            empty = np.argwhere(squares < 0)
            n_empty = empty.shape[0]
            # logic
            if n_tents > constr:
                self.grid_valid = False
            if constr - n_tents == 0: # fill empty with grass
                self.grid[i, empty] = EMPTY
            if constr - n_tents == n_empty:
                # fill empty with tents
                self.grid[i, empty] = TENT
                tent_indices = np.argwhere(self.grid==TENT)
                self.tents.extend(list(map(tuple,tent_indices.tolist())))
                self.calc_tent_neighbors()
        if self.verbose:
            print("========= CHECK CONSTRAINTS")
            print(self)


    def __len__(self):
        return self.grid[self.grid < 0].shape[0]


    def is_solved(self):
        return (self.grid_valid) and (self.trees_satisfied)


    def heuristic(self):
        self.tree_constraints()
        self.null_constraints()
        iter = 0
        nb_empty = len(self)
        nb_empty_last = -1
        while nb_empty != nb_empty_last:
            nb_empty = nb_empty_last
            if self.verbose:
                print(f"======= ITER : {iter}, NUMBER OF EMPTY : {len(self)} ")
            self.check_tent_neighbors()
            self.check_tree_neighbors()
            self.check_constraints()
            nb_empty_last = len(self)
            iter+=1

    def __str__(self):
        grid_str = '  ' + ' '.join(map(str,self.h_constraints)) + '\n'
        for i in range(self.grid.shape[0]):
            grid_str += str(self.v_constraints[i]) + ' '
            for j in range(self.grid.shape[0]):
                if self.grid[i,j] == TENT:
                    grid_str += 'X '
                elif self.grid[i,j] == TREE:
                    grid_str += 'T '
                elif self.grid[i,j] < 0:
                    grid_str += '  '
                else:
                    grid_str += '_ '
            grid_str += '\n'
        return grid_str
