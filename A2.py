import json
import csv
import sys


def CSP(N,D,m,a,e):
    return {"N0_0": "R", "N1_0": "R", "N2_0": "A", "N0_1": "R", "N1_1": "M", "N2_1": "E"}

def part_2(csvreader):
    return {}

def part1_nonCSP(N,D,m,a,e):
    NO_SOLUTION = False
    if(D>1 and N-m-e<m):
        NO_SOLUTION = True
    elif(D>=7 and m+a+e>=N):
        NO_SOLUTION = True
    if(NO_SOLUTION):
        return {}
    
    

def part_1(csvreader):
    soln_list = []
    rows = []
    for row in csvreader:
        rows.append(row)
        N = int(row[0])
        D = int(row[1])
        m = int(row[2])
        a = int(row[3])
        e = int(row[4])
        soln_list.append(part1_nonCSP(N,D,m,a,e))

def main(name):
    file = open(name)
    csvreader = csv.reader(file)
    header = []
    header = next(csvreader)
    num = len(header)
    if(num == 5):
        part_1(csvreader)
    elif(num == 7):
        part_2(csvreader)
    else:
        print("INVALID INPUT FILE FORMAT\n")
    file.close()

if(len(sys.argv) == 2):
    main(sys.argv[1])
else:
    print("Program Takes Input FileName as Argument\n")


# with open("solution.json" , 'w') as file:
#    for d in soln_list:
#        json.dump(d,file)
#        file.write("\n")









