import sys
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType

def main():
    # Read Input
    lines = sys.stdin.readlines()
    n = int(lines[0])   # number of runners
    m = int(lines[1])   # number of products
    pos = [int(a) for a in lines[2].split()]   # initial position runners
    movTime = [ [int(a) for a in lines[3+i].split()] for i in range(m) ]
    cbTime = [int(a) for a in lines[m+3].split()]   # conv belt time each prod
    o = int(lines[m+4])   # number of orders
    orders = [ [int(a) for a in lines[m+5+i][1:].split()] for i in range(o) ]

    print("n: ",n, "\nm: ",m)
    print("pos: ", pos)
    print("movTime: ", movTime)
    print("cbTime: ", cbTime)
    print("o: ", o)
    print("orders: ", orders)

    


if __name__ == '__main__':
   main()