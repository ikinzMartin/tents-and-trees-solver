from model import Game, ingest_file
from solver import solve
import sys

if __name__ == '__main__':

    params = ingest_file(sys.argv[1])
    g = Game(*params)
    print(g)
    s = solve(g)
    print(s)
    s.check_tent_neighbors()
