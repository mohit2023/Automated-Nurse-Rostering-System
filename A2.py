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

def solve_CSP(N,days,m,a,e,nurse_count,curr_day):
    if(curr_day == days):
        return True

    last_day = curr_day-1
    
    morning_available_rest = nurse_count[last_day]['R'][0]+nurse_count[last_day]['R'][1]+nurse_count[last_day]['A'][1] 
    morning_available_non_rest = nurse_count[last_day]['A'][0]

    morning_pair = (0,m)
    while morning_pair[1]>=0:
        if(morning_pair[1]<=morning_available_rest and morning_pair[0]<=morning_available_non_rest):
            available_rest = nurse_count[last_day]['M'][1] + nurse_count[last_day]['E'][1] + (morning_available_rest-morning_pair[1])
            available_non_rest = N-m-available_rest
            evening_pair = (0,e)
            while evening_pair[1]>=0:
                if(evening_pair[1]<=available_rest and evening_pair[0]<=available_non_rest):
                    left_rest = available_rest - evening_pair[1]
                    left_non_rest = available_non_rest - evening_pair[0]
                    afternoon_pair = (0,a)
                    while afternoon_pair[1]>=0:
                        if(afternoon_pair[1]<=left_rest and afternoon_pair[0]<=left_non_rest):
                            rest_pair = (left_non_rest-afternoon_pair[0],left_rest-afternoon_pair[1])
                            curr_count = {'M':morning_pair,'E':evening_pair,'A':afternoon_pair,'R':rest_pair}
                            left_days = days-curr_day-1
                            r = N-m-e-a
                            non_rest_total = morning_pair[0]+evening_pair[0]+afternoon_pair[0]
                            if(non_rest_total<=r*left_days):
                                nurse_count[curr_day] = curr_count
                                result = solve_CSP(N,days,m,a,e,nurse_count,curr_day+1)
                                if(result):
                                    return True
                        afternoon_pair = (afternoon_pair[0]+1,afternoon_pair[1]-1)
                evening_pair = (evening_pair[0]+1,evening_pair[1]-1)
        morning_pair = (morning_pair[0]+1,morning_pair[1]-1)

    return False


def part1_CSP(N,D,m,a,e):
    if(D>1 and N-m-e<m):
        return {}
    elif(D>=7 and (N-m-a-e)*7<N):
        return {}
    if(D == 0):
        return {}

    nurse = [['M' if i<m else 'E' if i-m<e else 'A' if i-m-e<a else 'R'  for i in range(N)]]
    if(D == 1):
        return nurse
    days = min(D,7)
    if(days<7):
        week_rest = [True for i in range(0,N)]
        nurse_count = [{'M':(0,m),'E':(0,e),'A':(0,a),'R':(0,N-m-a-e)}]
    else:
        week_rest = [False if i<m+e+a else True for i in range(0,N)]
        nurse_count = [{'M':(m,0),'E':(e,0),'A':(a,0),'R':(N-m-a-e,0)}]
    for i in range(1,days):
        nurse_count.append([])
    flag = solve_CSP(N,days,m,a,e,nurse_count,1)
    if(not flag):
        return {}
    
    for i in range(1,len(nurse_count)):
        nurse_curr_day = ['R' for j in range(N)]
        morning_avaialble = []
        for j in range(N):
            if(nurse[i-1][j]=='A' or nurse[i-1][j]=='R'):
                morning_avaialble.append(j)
        count_rest = 0
        count_non_rest = 0
        for id in morning_avaialble:
            if(week_rest[id] and count_rest<nurse_count[i]['M'][1]):
                nurse_curr_day[id] = 'M'
                count_rest = count_rest+1
            elif(count_non_rest<nurse_count[i]['M'][0] and not week_rest[id]):
                nurse_curr_day[id] = 'M'
                count_non_rest = count_non_rest+1
        available = []
        for j in range(N):
            if(nurse_curr_day[j] != 'M'):
                available.append(j)

        count_rest = 0
        count_non_rest = 0
        for id in range(N):
            if(nurse_curr_day[id]!='M' and week_rest[id] and count_rest<nurse_count[i]['E'][1]):
                nurse_curr_day[id] = 'E'
                count_rest = count_rest+1
            elif(nurse_curr_day[id]!='M' and count_non_rest<nurse_count[i]['E'][0] and not week_rest[id]):
                nurse_curr_day[id] = 'E'
                count_non_rest = count_non_rest+1

        count_rest = 0
        count_non_rest = 0
        for id in range(N):
            if(nurse_curr_day[id]=='R' and week_rest[id] and count_rest<nurse_count[i]['A'][1]):
                nurse_curr_day[id] = 'A'
                count_rest = count_rest+1
            elif(nurse_curr_day[id]=='R' and count_non_rest<nurse_count[i]['A'][0] and not week_rest[id]):
                nurse_curr_day[id] = 'A'
                count_non_rest = count_non_rest+1
        
        for i in range(N):
            if(nurse_curr_day[i] == 'R'):
                week_rest[i] = True
        nurse.append(nurse_curr_day)

    done_days = 7
    while D>done_days:
        nurse_curr_day = generate_nonConflict_nurse(nurse[done_days-1],N,m,a,e)
        maping = generate_maping(nurse[done_days-7],nurse_curr_day,N)
        nurse.append(nurse_curr_day)
        done_days = done_days+1
        while(done_days<D and done_days%7!=0):
            nurse_curr_day = map_roster(nurse[done_days-7],maping,N)
            nurse.append(nurse_curr_day)
            done_days = done_days+1
    
    return nurse
        
def generate_nonConflict_nurse(nurse,N,m,a,e):
    result = ['R' for j in range(N)]
    count = 0
    for j in range(N):
        if(nurse[j]=='A' or nurse[j]=='R' and count<m):
            result[j] = 'M'
            count = count+1
    count_e = 0
    count_a = 0
    for j in range(N):
        if(result[j]=='R'):
            if(count_e<e):
                result[j] = 'E'
                count_e = count_e+1
            elif(count_a<a):
                result[j] = 'A'
                count_a = count_a+1
    return result

def generate_maping(roster1,roster2,N):
    result = {}
    i = 0
    j = 0
    while i<N and j<N:
        if(roster2[i] == 'M' and roster1[j] == 'M'):
            result[i]=j
        while i<N and roster2[i]!='M':
            i = i+1
        while j<N and roster1[j]!='M':
            j = j+1
    i = 0
    j = 0
    while i<N and j<N:
        if(roster2[i] == 'E' and roster1[j] == 'E'):
            result[i]=j
        while i<N and roster2[i]!='E':
            i = i+1
        while j<N and roster1[j]!='E':
            j = j+1
    i = 0
    j = 0
    while i<N and j<N:
        if(roster2[i] == 'A' and roster1[j] == 'A'):
            result[i]=j
        while i<N and roster2[i]!='A':
            i = i+1
        while j<N and roster1[j]!='A':
            j = j+1
    i = 0
    j = 0
    while i<N and j<N:
        if(roster2[i] == 'R' and roster1[j] == 'R'):
            result[i]=j
        while i<N and roster2[i]!='R':
            i = i+1
        while j<N and roster1[j]!='R':
            j = j+1

        
    for j in range(len(roster)):
        result[roster[1]] = roster[2]
    return result

def map_roster(roster,maping,N):
    result = ['R' for i in range(N)]
    for id in range(N):
        result[id] = roster[maping[id]]
    return result


    

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
        nurse_roster = part1_CSP(N,D,m,a,e)
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









