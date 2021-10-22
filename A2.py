import json
import csv
import sys

def CSP(N,D,m,a,e):
    return {"N0_0": "R", "N1_0": "R", "N2_0": "A", "N0_1": "R", "N1_1": "M", "N2_1": "E"}

def dump(soln_list):
    with open("solution.json" , 'w') as file:
        # for d in soln_list:
        #     json.dump(d,file)
        #     file.write("\n")
        json.dump(soln_list,file)

def part_2(csvreader):
    return {}

def part1_nonCSP(N,D,m,a,e):
    NO_SOLUTION = False
    if(D>1 and N-m-e<m):
        NO_SOLUTION = True
    elif(D>=7 and (N-m-a-e)*7<N):
        NO_SOLUTION = True
    if(NO_SOLUTION):
        return {}
    
    nurse = []
    curr_week_rest = []
    for d in range(D):
        if(d%7 == 0):
            if(d+7 > D):
                curr_week_rest = [True for i in range(0,N)]
            else:
                curr_week_rest = [False for i in range(0,N)]
        if(d == 0):
            curr_day = ['M' if i<m else 'A' if i-m<a else 'E' if i-m-a<e else 'R'  for i in range(N)]
        else:
            curr_day = ['M' for i in range(N)]
            morning_available = []
            for i in range(N):
                if(nurse[d-1][i]=='R' or nurse[d-1][i]=='A'):
                    morning_available.append(i)
            morning_available_sort = []
            for x in morning_available:
                if(curr_week_rest[x]):
                    morning_available_sort.append(x)
            for x in morning_available:
                if(not curr_week_rest[x]):
                    morning_available_sort.append(x)
            # for i in range(0,m):
            #     curr_day[morning_available_sort[i]] = 'M'

            available = []
            for j in range(m,len(morning_available_sort)):
                available.append(morning_available_sort[j])
            for i in range(N):
                if(nurse[d-1][i]=='M' or nurse[d-1][i]=='E'):
                    available.append(i)
            available_sort = []
            for x in available:
                if(curr_week_rest[x]):
                    available_sort.append(x)
            for x in available:
                if(not curr_week_rest[x]):
                    available_sort.append(x)
            for i in range(m,N):
                if(i-m<a):
                    curr_day[available_sort[i-m]] = 'A'
                elif(i-m-a<e):
                    curr_day[available_sort[i-m]] = 'E'
                else:
                    curr_day[available_sort[i-m]] = 'R'
        for i in range(N):
            if(curr_day[i] == 'R'):
                curr_week_rest[i] = True
        nurse.append(curr_day)
    return nurse        

    

def part_1(csvreader):
    soln_list = []
    rows = []
    for row in csvreader:
        # print(row)
        if(len(row) != 5):
            print("INVALID INPUT FILE FORMAT\n")
            break
        rows.append(row)
        N = int(row[0])
        D = int(row[1])
        m = int(row[2])
        a = int(row[3])
        e = int(row[4])
        nurse_roster = part1_nonCSP(N,D,m,a,e)
        result = {}
        # print(result)
        # print(nurse_roster)
        for day in range(len(nurse_roster)):
            for id in range(len(nurse_roster[day])):
                key = "N"+str(id)+"_"+str(day)
                # print(key)
                result[key] = nurse_roster[day][id]
        soln_list.append(result)
    print(soln_list)
    return soln_list


def main(name):
    file = open(name)
    csvreader = csv.reader(file)
    header = []
    header = next(csvreader)
    num = len(header)
    if(num == 5):
        soln_list = part_1(csvreader)
        dump(soln_list)
    elif(num == 7):
        part_2(csvreader)
    else:
        print("INVALID INPUT FILE FORMAT\n")
    file.close()

if(len(sys.argv) == 2):
    main(sys.argv[1])
else:
    print("Program Takes Input FileName as Argument\n")









