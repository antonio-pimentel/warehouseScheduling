import sys
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType

def main():
    # =====================================================
    #   READ INPUT
    # =====================================================
    lines = sys.stdin.readlines()
    n = int(lines[0])   # number of runners
    m = int(lines[1])   # number of products
    rInitPos = [int(a) for a in lines[2].split()]   # initial position runners
    movTime = [ [int(a) for a in lines[3+i].split()] for i in range(m) ]
    cbTime = [int(a) for a in lines[m+3].split()]   # conv belt time each prod
    o = int(lines[m+4])   # number of orders
    orders = [ [int(a) for a in lines[m+5+i][1:].split()] for i in range(o) ]
    orderSize = [int(lines[m+5+i][0]) for i in range(o)]

    print("n: ",n)
    print("m: ",m)
    print("rInitPos: ", rInitPos)
    print("movTime: ", movTime)
    print("cbTime: ", cbTime)
    print("o: ", o)
    print("orders: ", orders)
    print("orderSize: ", orderSize)

    # Count num products by type
    products = [0]*m
    for order in orders:
        for p in order:
            products[p-1] += 1

    print("products: ", products)

    # Maximum time
    maxTime = 10        # TODO calculate max time ?
    topId = 10000       # TODO

    # =====================================================
    #   CREATE VARIABLES
    # =====================================================
    # Runners position over time : rPos[timestep][runner][position]
    rPos = [ [[j+1 + i*m + t*m*n for j in range(m)] for i in range(n)] for t in range(maxTime) ]


    # Product's position overtime
    # - Product at Shelf at t
    # - Product at CB at t
    # - Product at PS at t

    # - Runner active ?     (to check if active > 50% of finish time ?)


    # =====================================================
    #   CONSTRAINTS
    # =====================================================
    solver = Glucose4()

    for r in range(n):
        # Set runners initial position
        solver.add_clause([rPos[0][r][rInitPos[r]-1]])
        # Runner can only be in one position at a time
        for t in range(maxTime):
            enc = CardEnc.equals(lits=rPos[t][r], bound=1, top_id=topId, encoding=EncType.pairwise)
            for clause in enc.clauses:
                solver.add_clause(clause)

    

    print("\n",solver.solve())
    sol = solver.get_model()
    print(sol)

    # =====================================================
    #   EXPLAIN MODEL
    # =====================================================
    # Print runners positions at each timestep
    for t in range(maxTime):
        print("t=", t+1, end="\t")
        for i in range(n):
            print("r{}:".format(i+1), end="")
            for j in range(m):
                if sol[j + i*m + t*m*n] > 0:
                    print((j+1 + i*m + t*m*n)%m if (j+1 + i*m + t*m*n)%m!=0 else m, end="\t")
        print()
    

if __name__ == '__main__':
   main()