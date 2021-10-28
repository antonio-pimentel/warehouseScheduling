'''
    Warehouse Packaging Scheduling
    1st Project - ALC 2021/2022
    António Pimentel, 86385
'''

import sys
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

def main():
    def solve(maxTime, toPrint):
        # region  CREATE VARIABLES --------------------------------------------

        # Runners position over time : rPos[timestep][runner][position]
        rPos = [ [[j+1 + i*m + t*m*n for j in range(m)] for i in range(n)] for t in range(maxTime) ]
        maxId = m + (n-1)*m + (maxTime-1)*m*n

        # Product placed on Coveyor Belt at timestep t : productCB[t][productType][x]
        productCB = [ [[ j for j in range(1, products[i]+1)] for i in range(m)] for t in range(maxTime) ]
        for t in range(maxTime):
            for i in range(m):
                for j in range(products[i]):
                    productCB[t][i][j] += maxId
                maxId += products[i]

        # Product arrives at Packing Station at timestep t : productPS[t][productType][x]
        productPS = [ [[ j for j in range(1, products[i]+1)] for i in range(m)] for t in range(maxTime) ]
        for t in range(maxTime):
            for i in range(m):
                for j in range(products[i]):
                    productPS[t][i][j] += maxId
                maxId += products[i]

        # Runner is active at t : rActive[timestep][runner]
        rActive = [ [maxId + 1+i + t*n for i in range(n)] for t in range(maxTime) ]
        maxId += n + (maxTime-1)*n

        topId = maxId+1
        #endregion

        solver = Glucose4()
        vpool = IDPool(occupied=[[1, topId]])

        # region  CONSTRAINTS -------------------------------------------------
        # Runners position
        for r in range(n):
            # Set runners initial position
            solver.add_clause([rPos[0][r][rInitPos[r]-1]])
            # Runner can only be in one position at a time
            for t in range(maxTime):
                enc = CardEnc.atmost(lits=rPos[t][r], bound=1, encoding=EncType.pairwise)
                for clause in enc.clauses:
                    solver.add_clause(clause)

        # Runners movement
        for r in range(n):                # runner
            for t in range(1,maxTime):    # time
                for i in range(m):        # destination    
                    prevPosConst = [-1*rPos[t][r][i]]
                    for j in range(m):    # origin
                        if (t-movTime[j][i] >= 0):
                            prevPosConst += [rPos[t-movTime[j][i]][r][j]]          
                            for ti in range(t-movTime[j][i]+1, t):
                                for pi in range(m):
                                    # runner cant be anywhere while moving between positions
                                    solver.add_clause([-1*rPos[t][r][i], -1*rPos[t-movTime[j][i]][r][j], -1*rPos[ti][r][pi]])    
                    # for runner to be in x@t has to have been on x@t-1 or y@t-3 or ... 
                    solver.add_clause(prevPosConst)

        # Runners cant stop while active
        # If a runner is at a position a corresponding product has to placed on the CB
        for t in range(1,maxTime-1):
            for r in range(n):
                for i in range(m):
                    solver.add_clause([-1*rPos[t][r][i]] +[productCB[t+1][i][j] for j in range(products[i])])

        # If runner is at position then it's active 
        for t in range(maxTime):
            for r in range(n):
                for x in range(m):
                    solver.add_clause([-1*rPos[t][r][x], rActive[t][r]])

        for t in range(1, maxTime):
            for r in range(n):
                # If active @t -> active @t-1 
                solver.add_clause([ -1*rActive[t][r], rActive[t-1][r] ])
                # If runner innactive @t and not anywhere @t-1 -> runner innactive @t-1    
                solver.add_clause([rActive[t][r],-1*rActive[t-1][r]]+[rPos[t-1][r][x] for x in range(m)])

        # Every runner is inactive @maxTime
        for r in range(n):
            solver.add_clause([-1*rActive[maxTime-1][r]])

        # If a runner is active @t then all other runner were active @ 50% of t
        for t in range(maxTime):
            for r1 in range(n):
                for r2 in range(n):
                    if (r1 != r2):
                        solver.add_clause([-1*rActive[t][r1], rActive[t//2+t%2][r2]])

        # Runners should't be at the same position at the same time
        for t in range(1,maxTime-1):
            for i in range(m):
                enc = CardEnc.atmost(lits=[rPos[t][r][i] for r in range(n)], bound=1, vpool=vpool, encoding=EncType.seqcounter)
                for clause in enc.clauses:
                    solver.add_clause(clause)

        # No products at CB at t0 and t1
        [[solver.add_clause([-1 * productCB[0][i][j]]) for j in range(products[i])] for i in range(m)]
        [[solver.add_clause([-1 * productCB[1][i][j]]) for j in range(products[i])] for i in range(m)]

        # Max 1 product of each type at CB at each timestep
        for t in range(maxTime):
            for i in range(m):
                enc = CardEnc.atmost(lits=[productCB[t][i][j] for j in range(products[i])], bound=1, vpool=vpool, encoding=EncType.seqcounter)
                for clause in enc.clauses:
                    solver.add_clause(clause)

        # A runner has to be at the products position for it to placed on the CB
        # productCB[t][productType][x] -> ( rPos[t-1][runnerX][productType] V runnerY V ... )
        for t in range(1,maxTime):
            for i in range(m):
                for j in range(products[i]):
                    solver.add_clause([-1*productCB[t][i][j]] + [rPos[t-1][rx][i] for rx in range(n)])

        # If at CB at t will be on PS at t + Cij
        # productCB[t][i][j] -> productPS [t + cbTime[i]] [i][j]
        for t in range(maxTime):
            for i in range(m):
                for j in range(products[i]):
                    if (t+cbTime[i] < maxTime):
                        solver.add_clause([-1*productCB[t][i][j], productPS[t+cbTime[i]][i][j]])
                    else:
                        solver.add_clause([-1*productCB[t][i][j]])

        # Max 1 product arrives at PS at each timestep    
        for t in range(maxTime):
            enc = CardEnc.atmost(lits=[productPS[t][i][j] for i in range(m) for j in range(products[i])], bound=1, vpool=vpool, encoding=EncType.seqcounter)
            for clause in enc.clauses:
                solver.add_clause(clause)

        # Every product arrives at CB at some timestep
        for i in range(m):
            for j in range(products[i]):
                enc = CardEnc.equals(lits=[productCB[t][i][j] for t in range(maxTime)], bound=1, vpool=vpool, encoding=EncType.seqcounter)
                for clause in enc.clauses:
                    solver.add_clause(clause)

        # Every product arrives at PS at some timestep
        for i in range(m):
            for j in range(products[i]):
                enc = CardEnc.equals(lits=[productPS[t][i][j] for t in range(maxTime)], bound=1, vpool=vpool, encoding=EncType.seqcounter)
                for clause in enc.clauses:
                    solver.add_clause(clause)

        #endregion

        # region  SOLVE -------------------------------------------------------

        solver.solve()
        sol = solver.get_model()
        if (not sol):
            return False
        else:
            if (not toPrint):
                return True
            
            # print optimal timespan
            print(maxTime-2)

            # print runners
            for r in range(n):
                l = []
                for t in range(1, maxTime):
                    for x in range(m):
                        if (sol[rPos[t][r][x]-1] > 0):
                            l.append(x+1)
                print(len(l), end="")
                [print(" ", i, end="") for i in l]
                print()

            # print Coveyor Belt times of each Order
            aux = [[] for i in range(m)]
            for t in range(maxTime):
                for i in range(m):
                    for j in range(products[i]):
                        if (sol[productCB[t][i][j]-1] > 0):
                            aux[i].append(t-1)
            for order in orders:
                print(len(order), end="")
                for p in order:
                    print(" {}:{}".format(p, aux[p-1].pop(0)), end="")
                print()
            
            return True
        #endregion


    # region READ INPUT -------------------------------------------------------
    lines = sys.stdin.readlines()
    n = int(lines[0])   # number of runners
    m = int(lines[1])   # number of products
    rInitPos = [int(a) for a in lines[2].split()]   # initial position runners
    movTime = [ [int(a) for a in lines[3+i].split()] for i in range(m) ]
    cbTime = [int(a) for a in lines[m+3].split()]   # conv belt time each prod
    o = int(lines[m+4])   # number of orders
    orders = [ [int(a) for a in lines[m+5+i][1:].split()] for i in range(o) ]
    orderSize = [int(lines[m+5+i][0]) for i in range(o)]

    # Count num products by type
    products = [0]*m
    for order in orders:
        for p in order:
            products[p-1] += 1

    #endregion

    # region MAX TIME ---------------------------------------------------------
    # calculate max time upper bound
    maxTime = 0
    # max time to go from other initial positions to 1st runners pos
    for r in range(1,n):
        if (movTime[rInitPos[r]-1][rInitPos[0]-1] > maxTime):
            maxTime = movTime[rInitPos[r]-1][rInitPos[0]-1]
    # time to go to every position at place prods seq
    currentPos = rInitPos[0]-1
    for i in range(m):
        if (products[i] > 0):
            maxTime += movTime[currentPos][i] + products[i]
            currentPos = i
    maxTime += max(cbTime)
    #endregion

    # region OPTIMAL SOLUTION SEARCH ------------------------------------------
    timespan = maxTime
    while(solve(timespan,0)):
        timespan -= 1

    if (timespan == maxTime):
        print("UNSAT", end="")
    else:
        solve(timespan+1, 1)

    #endregion


if __name__ == '__main__':
   main()
