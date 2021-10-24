import json
import csv
import sys
import time

TIME_LIMIT = 0
BEGIN_TIME = 0


GlobalSolutionList_softCSP = []

def time_elapsed():
    # print(BEGIN_TIME)
    current = time.perf_counter()
    return current - BEGIN_TIME

def within_timeLimit():
    elapsed = time_elapsed()
    if(elapsed >= TIME_LIMIT-1):
        return False
    return True

def dump(soln_list, filename):
    #print(soln_list)
    #print("\n")
    with open(filename , 'w') as file:
        for d in soln_list:
            json.dump(d,file)
            file.write("\n")
        #json.dump(soln_list,file)

 

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
    
    #print("Part1 solution count:")
    #print(nurse_count)
    
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
        if((nurse[j]=='A' or nurse[j]=='R') and count<m):
            result[j] = 'M'
            count = count+1
    # print(result)
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
    # print(N,m,a,e)
    # print(nurse,result)
    return result

def generate_maping(roster1,roster2,N):
    # print(roster1,roster2)
    result = {}
    i = 0
    j = 0
    while i<N and j<N:
        if(roster2[i] == 'M' and roster1[j] == 'M'):
            result[i]=j
            i=i+1
            j=j+1
        while i<N and roster2[i]!='M':
            i = i+1
        while j<N and roster1[j]!='M':
            j = j+1
    i = 0
    j = 0
    while i<N and j<N:
        if(roster2[i] == 'E' and roster1[j] == 'E'):
            result[i]=j
            i=i+1
            j=j+1
        while i<N and roster2[i]!='E':
            i = i+1
        while j<N and roster1[j]!='E':
            j = j+1
    i = 0
    j = 0
    while i<N and j<N:
        if(roster2[i] == 'A' and roster1[j] == 'A'):
            result[i]=j
            i=i+1
            j=j+1
        while i<N and roster2[i]!='A':
            i = i+1
        while j<N and roster1[j]!='A':
            j = j+1
    i = 0
    j = 0
    while i<N and j<N:
        if(roster2[i] == 'R' and roster1[j] == 'R'):
            result[i]=j
            i=i+1
            j=j+1
        while i<N and roster2[i]!='R':
            i = i+1
        while j<N and roster1[j]!='R':
            j = j+1

    return result

def map_roster(roster,maping,N):
    # print(maping)
    result = ['R' for i in range(N)]
    for id in range(N):
        # print(id)
        result[id] = roster[maping[id]]
    return result

def verify_roster(nurse_roster,N,D,m,a,e):
    if(nurse_roster == {}):
        return True

    for roster in nurse_roster:
        count_m = sum([1 if shift=='M' else 0 for shift in roster])
        count_e = sum([1 if shift=='E' else 0 for shift in roster])
        count_a = sum([1 if shift=='A' else 0 for shift in roster])
        if(m!=count_m or a!=count_a or e!=count_e):
            return False
    
    for i in range(1,D):
        for j in range(N):
            if(nurse_roster[i][j] == 'M'):
                if(nurse_roster[i-1][j] =='M' or nurse_roster[i-1][j] =='E'):
                    return False

    day = 0
    while day+7<=D:
        week_start = day
        week_end = day+7
        rest = [False for i in range(N)]
        for d in range(week_start,week_end):
            for id in range(N):
                if(nurse_roster[d][id] == 'R'):
                    rest[id] = True
        for id in range(N):
            if(not rest[id]):
                return False
        day = day+7
    
    return True
    

def part_1(csvreader):
    soln_list = []
    rows = []
    Matrix = []
    
    for row in csvreader:
        #print(row)
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
        if(not verify_roster(nurse_roster,N,D,m,a,e)):
            print("Error in result\n")
            print(row)
            print(nurse_roster)
        result = {}
        flag_1 = True
        if (nurse_roster=={}):
            if(D>1 and N-m-e<m):
                flag_1 = False
            elif(D>=7 and (N-m-a-e)*7<N):
                flag_1 = False
            if(D == 0):
                flag_1 = False
            if (flag_1==True):
                Matrix.append(row)
                print(row)
        #print(nurse_roster)

        for day in range(len(nurse_roster)):
            for id in range(len(nurse_roster[day])):
                key = "N"+str(id)+"_"+str(day)
                result[key] = nurse_roster[day][id]
        soln_list.append(result)
    #print(soln_list)
    header1 = ['N','D','m','a','e']
    filename1 = 'input_a111.csv'

    with open(filename1,'ab',) as file1:
        writer1 = csv.writer(file1)
        writer1.writerow(header)
        for i in range(len(Matrix)):
            writer.writerow(Matrix[i])
    return soln_list

def next_permutaion(base):
    if(base[2]!=0):
        base[2] = base[2]-1
        base[3] = base[3]+1
    else:
        if(base[1]!=0):
            base[1]=base[1]-1
            base[2]=base[2]+base[3]+1
            base[3]=0
        else:
            if(base[0]!=0):
                base[0]=base[0]-1
                base[1]=base[1]+base[2]+base[3]+1
                base[2]=0
                base[3]=0
            else:
                base = [-1,-1,-1,-1]
    return base

def permutation_constraint(base,c0,c1,c2,c3):
    if(base[0]>c0 or base[1]>c1 or base[2]>c2 or base[3]>c3):
        return False
    return True

def convertToJson(nurse_roster):
    result = {}
    for day in range(len(nurse_roster)):
        for id in range(len(nurse_roster[day])):
            key = "N"+str(id)+"_"+str(day)
            result[key] = nurse_roster[day][id]
    return result

def updateSolutionList_softCSP(nurse_roster,N,D,m,a,e,S):
    last_index = len(GlobalSolutionList_softCSP)-1
    print("Found a sol for: ", last_index)
    # print(nurse_count)
    # nurse_roster = create_roster_soft_CSP(nurse_count,N,D,m,a,e,S)
    print(nurse_roster)
    if(not verify_roster(nurse_roster,N,D,m,a,e)):
            print("Error in result\n")
            print(nurse_roster)
            return
    curr_weight = calculate_weight(nurse_roster,N,S,D)
    print("with weight: ", curr_weight)
    print("\n")
    past_weight = calculate_weight(GlobalSolutionList_softCSP[last_index],N,S,D)
    if(curr_weight > past_weight):
        result = convertToJson(nurse_roster)
        GlobalSolutionList_softCSP[last_index] = result
        # print("dump called from update\n")
        dump(GlobalSolutionList_softCSP,"solution2.json")
    

def solve_CSP_soft(N,D,m,a,e,S,nurse_count,curr_day):
    # print(curr_day, nurse_count)
    if(curr_day == D):
        # print("A sol found")
        # print(nurse_count)
        nurse_roster = create_roster_soft_CSP(nurse_count,N,D,m,a,e,S)
        updateSolutionList_softCSP(nurse_roster,N,D,m,a,e,S)
        return True

    if not within_timeLimit():
        return False

    flag = False
    ld = curr_day-1
    if(curr_day == 0):
        if(curr_day+7>D):
            m_s_r = S
            m_s_nr = 0
            m_ns_r = N-S
            m_ns_nr = 0
            m_f = [m,0,0,0]
            while m_f[0]>=0:
                if(permutation_constraint(m_f,m_s_r,m_s_nr,m_ns_r,m_ns_nr)):
                    e_s_r = S-m_f[0]
                    e_s_nr = 0
                    e_ns_r = N-S-m_f[2]
                    e_ns_nr = 0
                    e_f = [e,0,0,0]
                    while e_f[0]>=0:
                        if(permutation_constraint(e_f,e_s_r,e_s_nr,e_ns_r,e_ns_nr)):
                            a_r = N-m_f[0]-m_f[2]-e_f[0]-e_f[2]
                            a_ns_nr = 0
                            a_s_nr = 0
                            a_f = [0,a,0,0]
                            while a_f[0]>=0:
                                if(permutation_constraint(a_f,0,a_r,a_ns_nr,a_s_nr)):
                                    r_f = [0,a_r-a_f[1],a_ns_nr-a_f[2],a_s_nr-a_f[3]]
                                    curr_count = {'M':m_f,'E':e_f,'A':a_f,'R':r_f}
                                    non_rest_total = m_f[1]+m_f[3]+e_f[1]+e_f[3]+a_f[2]+a_f[3]
                                    left_week_days = 6-curr_day%7
                                    if(non_rest_total<=left_week_days*(N-m-e-a)):
                                        nurse_count[curr_day]=curr_count
                                        flag = flag or solve_CSP_soft(N,D,m,a,e,S,nurse_count,curr_day+1)
                                a_f = next_permutaion(a_f)
                        e_f = next_permutaion(e_f)
                m_f = next_permutaion(m_f)
            return flag
        else:
            m_s_r = 0
            m_s_nr = S
            m_ns_r = 0
            m_ns_nr = N-S
            m_f = [m,0,0,0]
            while m_f[0]>=0:
                if(permutation_constraint(m_f,m_s_r,m_s_nr,m_ns_r,m_ns_nr)):
                    e_s_r = 0
                    e_s_nr = S-m_f[1]
                    e_ns_r = 0
                    e_ns_nr = N-S-m_f[3]
                    e_f = [e,0,0,0]
                    while e_f[0]>=0:
                        if(permutation_constraint(e_f,e_s_r,e_s_nr,e_ns_r,e_ns_nr)):
                            a_r = 0
                            a_ns_nr = N-S-m_f[3]-e_f[3]
                            a_s_nr = S-m_f[1]-e_f[1]
                            a_f = [0,a,0,0]
                            while a_f[0]>=0:
                                if(permutation_constraint(a_f,0,a_r,a_ns_nr,a_s_nr)):
                                    r_f = [0,a_r-a_f[1],a_ns_nr-a_f[2],a_s_nr-a_f[3]]
                                    curr_count = {'M':m_f,'E':e_f,'A':a_f,'R':r_f}
                                    non_rest_total = m_f[1]+m_f[3]+e_f[1]+e_f[3]+a_f[2]+a_f[3]
                                    left_week_days = 6-curr_day%7
                                    if(non_rest_total<=left_week_days*(N-m-e-a)):
                                        nurse_count[curr_day]=curr_count
                                        flag = flag or solve_CSP_soft(N,D,m,a,e,S,nurse_count,curr_day+1)
                                a_f = next_permutaion(a_f)
                        e_f = next_permutaion(e_f)
                m_f = next_permutaion(m_f)
            return flag
    elif(curr_day%7 == 0):
        prev = nurse_count[ld]
        if(curr_day+7>D):
            m_s_r = S-prev['M'][0]-prev['M'][1]-prev['E'][0]-prev['E'][1]
            m_s_nr = 0
            m_ns_r = N-S-prev['M'][2]-prev['M'][3]-prev['E'][2]-prev['E'][3]
            m_ns_nr = 0
            m_f = [m,0,0,0]
            while m_f[0]>=0:
                if(permutation_constraint(m_f,m_s_r,m_s_nr,m_ns_r,m_ns_nr)):
                    e_s_r = S-m_f[0]
                    e_s_nr = 0
                    e_ns_r = N-S-m_f[2]
                    e_ns_nr = 0
                    e_f = [e,0,0,0]
                    while e_f[0]>=0:
                        if(permutation_constraint(e_f,e_s_r,e_s_nr,e_ns_r,e_ns_nr)):
                            a_r = N-m_f[0]-m_f[2]-e_f[0]-e_f[2]
                            a_ns_nr = 0
                            a_s_nr = 0
                            a_f = [0,a,0,0]
                            while a_f[0]>=0:
                                if(permutation_constraint(a_f,0,a_r,a_ns_nr,a_s_nr)):
                                    r_f = [0,a_r-a_f[1],a_ns_nr-a_f[2],a_s_nr-a_f[3]]
                                    curr_count = {'M':m_f,'E':e_f,'A':a_f,'R':r_f}
                                    non_rest_total = m_f[1]+m_f[3]+e_f[1]+e_f[3]+a_f[2]+a_f[3]
                                    left_week_days = 6-curr_day%7
                                    if(non_rest_total<=left_week_days*(N-m-e-a)):
                                        nurse_count[curr_day]=curr_count
                                        flag = flag or solve_CSP_soft(N,D,m,a,e,S,nurse_count,curr_day+1)
                                a_f = next_permutaion(a_f)
                        e_f = next_permutaion(e_f)
                m_f = next_permutaion(m_f)
            return flag
        else:
            m_s_r = 0
            m_s_nr = S-prev['M'][0]-prev['M'][1]-prev['E'][0]-prev['E'][1]
            m_ns_r = 0
            m_ns_nr = N-S-prev['M'][2]-prev['M'][3]-prev['E'][2]-prev['E'][3]
            m_f = [m,0,0,0]
            while m_f[0]>=0:
                if(permutation_constraint(m_f,m_s_r,m_s_nr,m_ns_r,m_ns_nr)):
                    e_s_r = 0
                    e_s_nr = S-m_f[1]
                    e_ns_r = 0
                    e_ns_nr = N-S-m_f[3]
                    e_f = [e,0,0,0]
                    while e_f[0]>=0:
                        if(permutation_constraint(e_f,e_s_r,e_s_nr,e_ns_r,e_ns_nr)):
                            a_r = 0
                            a_ns_nr = N-S-m_f[3]-e_f[3]
                            a_s_nr = S-m_f[1]-e_f[1]
                            a_f = [0,a,0,0]
                            while a_f[0]>=0:
                                if(permutation_constraint(a_f,0,a_r,a_ns_nr,a_s_nr)):
                                    r_f = [0,a_r-a_f[1],a_ns_nr-a_f[2],a_s_nr-a_f[3]]
                                    curr_count = {'M':m_f,'E':e_f,'A':a_f,'R':r_f}
                                    non_rest_total = m_f[1]+m_f[3]+e_f[1]+e_f[3]+a_f[2]+a_f[3]
                                    left_week_days = 6-curr_day%7
                                    if(non_rest_total<=left_week_days*(N-m-e-a)):
                                        nurse_count[curr_day]=curr_count
                                        flag = flag or solve_CSP_soft(N,D,m,a,e,S,nurse_count,curr_day+1)
                                a_f = next_permutaion(a_f)
                        e_f = next_permutaion(e_f)
                m_f = next_permutaion(m_f)
            return flag
    else:
        prev = nurse_count[ld]
        m_s_r = S-prev['M'][0]-prev['M'][1]-prev['E'][0]-prev['E'][1]-prev['A'][3]
        m_s_nr = prev['A'][3]
        m_ns_r = N-S-prev['M'][2]-prev['M'][3]-prev['E'][2]-prev['E'][3]-prev['A'][2]
        m_ns_nr = prev['A'][2]
        m_f = [m,0,0,0]
        while m_f[0]>=0:
            if(permutation_constraint(m_f,m_s_r,m_s_nr,m_ns_r,m_ns_nr)):
                e_s_r = m_s_r+prev['M'][0]+prev['E'][0]-m_f[0]
                e_s_nr = m_s_nr+prev['M'][1]+prev['E'][1]-m_f[1]
                e_ns_r = m_ns_r+prev['M'][2]+prev['E'][2]-m_f[2]
                e_ns_nr = m_ns_nr+prev['M'][3]+prev['E'][3]-m_f[3]
                e_f = [e,0,0,0]
                while e_f[0]>=0:
                    if(permutation_constraint(e_f,e_s_r,e_s_nr,e_ns_r,e_ns_nr)):
                        a_r = prev['M'][0]+prev['M'][2]+prev['E'][0]+prev['E'][2]+prev['A'][1]+N-m-e-a-m_f[0]-m_f[2]-e_f[0]-e_f[2]
                        a_ns_nr = prev['M'][3]+prev['E'][3]+prev['A'][2]-m_f[3]-e_f[3]
                        a_s_nr = N-m-e-a_r-a_ns_nr
                        a_f = [0,a,0,0]
                        while a_f[0]>=0:
                            if(permutation_constraint(a_f,0,a_r,a_ns_nr,a_s_nr)):
                                r_f = [0,a_r-a_f[1],a_ns_nr-a_f[2],a_s_nr-a_f[3]]
                                curr_count = {'M':m_f,'E':e_f,'A':a_f,'R':r_f}
                                non_rest_total = m_f[1]+m_f[3]+e_f[1]+e_f[3]+a_f[2]+a_f[3]
                                left_week_days = 6-curr_day%7
                                if(non_rest_total<=left_week_days*(N-m-e-a)):
                                    nurse_count[curr_day]=curr_count
                                    flag = flag or solve_CSP_soft(N,D,m,a,e,S,nurse_count,curr_day+1)
                            a_f = next_permutaion(a_f)
                    e_f = next_permutaion(e_f)
            m_f = next_permutaion(m_f)
        return flag

    return False

def create_roster_soft_CSP(nurse_count,N,D,m,a,e,S):
    nurse_roster = []
    prev_day_roster = ['A' for i in range(N)]
    week_rest = [False for i in range(N)]
    for d in range(D):
        if(d%7==0):
            if(d+7>D):
                week_rest = [True for i in range(N)]
            else:
                week_rest = [False for i in range(N)]

        nurse_curr_day = ['R' for j in range(N)]
        morning_available = []
        for j in range(N):
            if(prev_day_roster[j]=='A' or prev_day_roster[j]=='R'):
                morning_available.append(j)

        count = [0,0,0,0]
        for id in morning_available:
            if(week_rest[id] and id<S and count[0]<nurse_count[d]['M'][0]):
                nurse_curr_day[id] = 'M'
                count[0] = count[0]+1
            elif(count[1]<nurse_count[d]['M'][1] and id<S and not week_rest[id]):
                nurse_curr_day[id] = 'M'
                count[1] = count[1]+1
            elif(count[2]<nurse_count[d]['M'][2] and id>=S and week_rest[id]):
                nurse_curr_day[id]='M'
                count[2] = count[2]+1
            elif(count[3]<nurse_count[d]['M'][3] and id>=S and not week_rest[id]):
                nurse_curr_day[id] = 'M'
                count[3] = count[3]+1
        
        
        available = []
        for j in range(N):
            if(nurse_curr_day[j] == 'R'):
                available.append(j)
        count = [0,0,0,0]
        for id in available:
            if(week_rest[id] and id<S and count[0]<nurse_count[d]['E'][0]):
                nurse_curr_day[id] = 'E'
                count[0] = count[0]+1
            elif(count[1]<nurse_count[d]['E'][1] and id<S and not week_rest[id]):
                nurse_curr_day[id] = 'E'
                count[1] = count[1]+1
            elif(count[2]<nurse_count[d]['E'][2] and id>=S and week_rest[id]):
                nurse_curr_day[id]='E'
                count[2] = count[2]+1
            elif(count[3]<nurse_count[d]['E'][3] and id>=S and not week_rest[id]):
                nurse_curr_day[id] = 'E'
                count[3] = count[3]+1

        available = []
        for j in range(N):
            if(nurse_curr_day[j] == 'R'):
                available.append(j)
        count = [0,0,0,0]
        for id in available:
            if(week_rest[id] and id<S and count[0]<nurse_count[d]['A'][0]):
                nurse_curr_day[id] = 'A'
                count[0] = count[0]+1
            elif(count[1]<nurse_count[d]['A'][1] and week_rest[id]):
                nurse_curr_day[id] = 'A'
                count[1] = count[1]+1
            elif(count[2]<nurse_count[d]['A'][2] and id>=S and not week_rest[id]):
                nurse_curr_day[id]='A'
                count[2] = count[2]+1
            elif(count[3]<nurse_count[d]['A'][3] and id<S and not week_rest[id]):
                nurse_curr_day[id] = 'A'
                count[3] = count[3]+1

        prev_day_roster = nurse_curr_day
        for id in range(N):
            if(nurse_curr_day[id]=='R'):
                week_rest[id] = True
        nurse_roster.append(nurse_curr_day)
    
    return nurse_roster
        


def part2_CSP(N,D,m,a,e,S):
    if(D>1 and N-m-e<m):
        return
    elif(D>=7 and (N-m-a-e)*7<N):
        return
    if(D == 0):
        return

    nurse = [['M' if i<m else 'E' if i-m<e else 'A' if i-m-e<a else 'R'  for i in range(N)]]
    if(D == 1):
        updateSolutionList_softCSP(nurse,N,D,m,a,e,S)
        return

    nurse_count = []
    for i in range(D):
        nurse_count.append([])
    flag = solve_CSP_soft(N,D,m,a,e,S,nurse_count,0)
    if(not flag):
        return
    
    # print(nurse_count)
    # nurse_roster = create_roster_soft_CSP(nurse_count,N,D,m,a,e,S)
    # return nurse_roster

def calculate_weight(nurse_roster,N,S,D):
    if(nurse_roster == {} or nurse_roster == []):
        return 0
    result = N*D
    for d in range(D):
        for id in range(S):
            if(nurse_roster[d][id]=='M' or nurse_roster[d][id]=='E'):
                result = result+1
    return result

def part_2(csvreader):
    global BEGIN_TIME
    global TIME_LIMIT
    rows = []
    for row in csvreader:
        GlobalSolutionList_softCSP.append({})
        # print(row)
        if(len(row) != 7):
            print("INVALID INPUT FILE FORMAT\n")
            break
        rows.append(row)
        N = int(row[0])
        D = int(row[1])
        m = int(row[2])
        a = int(row[3])
        e = int(row[4])
        S = int(row[5])
        T = int(row[6])
        TIME_LIMIT = T
        BEGIN_TIME = time.perf_counter()
        part2_CSP(N,D,m,a,e,S)
        print("For row: ", row)
        dump(GlobalSolutionList_softCSP,"solution2.json")



def main(name):
    

    file = open(name)
    csvreader = csv.reader(file)
    header = []
    header = next(csvreader)
    num = len(header)
    if(num == 5):
        soln_list = part_1(csvreader)
        dump(soln_list,"solution.json")
    elif(num == 7):
        part_2(csvreader)
        dump(GlobalSolutionList_softCSP,"solution2.json")
    else:
        print("INVALID INPUT FILE FORMAT\n")
    file.close()



if(len(sys.argv) == 2):
    main(sys.argv[1])
else:
    print("Program Takes Input FileName as Argument\n")








































































# import json
# import csv
# import sys
# import time

# start_time = time.time()


# def CSP(N,D,m,a,e):
#     return {"N0_0": "R", "N1_0": "R", "N2_0": "A", "N0_1": "R", "N1_1": "M", "N2_1": "E"}

# def dump(soln_list):
#     with open("solution.json" , 'w') as file:
#         # for d in soln_list:
#         #     json.dump(d,file)
#         #     file.write("\n")
#         json.dump(soln_list,file)

# def part_2(csvreader):
#     return {}

 

# def solve_CSP(N,days,m,a,e,nurse_count,curr_day):
#     if(curr_day == days):
#         return True

#     last_day = curr_day-1
    
#     morning_available_rest = nurse_count[last_day]['R'][0]+nurse_count[last_day]['R'][1]+nurse_count[last_day]['A'][1] 
#     morning_available_non_rest = nurse_count[last_day]['A'][0]

#     morning_pair = (0,m)
#     while morning_pair[1]>=0:
#         if(morning_pair[1]<=morning_available_rest and morning_pair[0]<=morning_available_non_rest):
#             available_rest = nurse_count[last_day]['M'][1] + nurse_count[last_day]['E'][1] + (morning_available_rest-morning_pair[1])
#             available_non_rest = N-m-available_rest
#             evening_pair = (0,e)
#             while evening_pair[1]>=0:
#                 if(evening_pair[1]<=available_rest and evening_pair[0]<=available_non_rest):
#                     left_rest = available_rest - evening_pair[1]
#                     left_non_rest = available_non_rest - evening_pair[0]
#                     afternoon_pair = (0,a)
#                     while afternoon_pair[1]>=0:
#                         if(afternoon_pair[1]<=left_rest and afternoon_pair[0]<=left_non_rest):
#                             rest_pair = (left_non_rest-afternoon_pair[0],left_rest-afternoon_pair[1])
#                             curr_count = {'M':morning_pair,'E':evening_pair,'A':afternoon_pair,'R':rest_pair}
#                             left_days = days-curr_day-1
#                             r = N-m-e-a
#                             non_rest_total = morning_pair[0]+evening_pair[0]+afternoon_pair[0]
#                             if(non_rest_total<=r*left_days):
#                                 nurse_count[curr_day] = curr_count
#                                 result = solve_CSP(N,days,m,a,e,nurse_count,curr_day+1)
#                                 if(result):
#                                     return True
#                         afternoon_pair = (afternoon_pair[0]+1,afternoon_pair[1]-1)
#                 evening_pair = (evening_pair[0]+1,evening_pair[1]-1)
#         morning_pair = (morning_pair[0]+1,morning_pair[1]-1)

#     return False


# def part1_CSP(N,D,m,a,e):
#     if(D>1 and N-m-e<m):
#         return {}
#     elif(D>=7 and (N-m-a-e)*7<N):
#         return {}
#     if(D == 0):
#         return {}

#     nurse = [['M' if i<m else 'E' if i-m<e else 'A' if i-m-e<a else 'R'  for i in range(N)]]
#     if(D == 1):
#         return nurse
#     days = min(D,7)
#     if(days<7):
#         week_rest = [True for i in range(0,N)]
#         nurse_count = [{'M':(0,m),'E':(0,e),'A':(0,a),'R':(0,N-m-a-e)}]
#     else:
#         week_rest = [False if i<m+e+a else True for i in range(0,N)]
#         nurse_count = [{'M':(m,0),'E':(e,0),'A':(a,0),'R':(N-m-a-e,0)}]
#     for i in range(1,days):
#         nurse_count.append([])
#     flag = solve_CSP(N,days,m,a,e,nurse_count,1)
#     if(not flag):
#         return {}
    
#     for i in range(1,len(nurse_count)):
#         nurse_curr_day = ['R' for j in range(N)]
#         morning_avaialble = []
#         for j in range(N):
#             if(nurse[i-1][j]=='A' or nurse[i-1][j]=='R'):
#                 morning_avaialble.append(j)
#         count_rest = 0
#         count_non_rest = 0
#         for id in morning_avaialble:
#             if(week_rest[id] and count_rest<nurse_count[i]['M'][1]):
#                 nurse_curr_day[id] = 'M'
#                 count_rest = count_rest+1
#             elif(count_non_rest<nurse_count[i]['M'][0] and not week_rest[id]):
#                 nurse_curr_day[id] = 'M'
#                 count_non_rest = count_non_rest+1
#         available = []
#         for j in range(N):
#             if(nurse_curr_day[j] != 'M'):
#                 available.append(j)

#         count_rest = 0
#         count_non_rest = 0
#         for id in range(N):
#             if(nurse_curr_day[id]!='M' and week_rest[id] and count_rest<nurse_count[i]['E'][1]):
#                 nurse_curr_day[id] = 'E'
#                 count_rest = count_rest+1
#             elif(nurse_curr_day[id]!='M' and count_non_rest<nurse_count[i]['E'][0] and not week_rest[id]):
#                 nurse_curr_day[id] = 'E'
#                 count_non_rest = count_non_rest+1

#         count_rest = 0
#         count_non_rest = 0
#         for id in range(N):
#             if(nurse_curr_day[id]=='R' and week_rest[id] and count_rest<nurse_count[i]['A'][1]):
#                 nurse_curr_day[id] = 'A'
#                 count_rest = count_rest+1
#             elif(nurse_curr_day[id]=='R' and count_non_rest<nurse_count[i]['A'][0] and not week_rest[id]):
#                 nurse_curr_day[id] = 'A'
#                 count_non_rest = count_non_rest+1
        
#         for i in range(N):
#             if(nurse_curr_day[i] == 'R'):
#                 week_rest[i] = True
#         nurse.append(nurse_curr_day)

#     done_days = 7
#     while D>done_days:
#         nurse_curr_day = generate_nonConflict_nurse(nurse[done_days-1],N,m,a,e)
#         maping = generate_maping(nurse[done_days-7],nurse_curr_day,N)
#         nurse.append(nurse_curr_day)
#         done_days = done_days+1
#         while(done_days<D and done_days%7!=0):
#             nurse_curr_day = map_roster(nurse[done_days-7],maping,N)
#             nurse.append(nurse_curr_day)
#             done_days = done_days+1
    
#     print(nurse)
#     return nurse
        
# def generate_nonConflict_nurse(nurse,N,m,a,e):
#     result = ['R' for j in range(N)]
#     count = 0
#     for j in range(N):
#         if(nurse[j]=='A' or nurse[j]=='R' and count<m):
#             result[j] = 'M'
#             count = count+1
#     count_e = 0
#     count_a = 0
#     for j in range(N):
#         if(result[j]=='R'):
#             if(count_e<e):
#                 result[j] = 'E'
#                 count_e = count_e+1
#             elif(count_a<a):
#                 result[j] = 'A'
#                 count_a = count_a+1
#     return result

# def generate_maping(roster1,roster2,N):
#     result = {}
#     i = 0
#     j = 0
#     while i<N and j<N:
#         if(roster2[i] == 'M' and roster1[j] == 'M'):
#             result[i]=j
#             i=i+1
#             j=j+1
#         while i<N and roster2[i]!='M':
#             i = i+1
#         while j<N and roster1[j]!='M':
#             j = j+1
#     i = 0
#     j = 0
#     while i<N and j<N:
#         if(roster2[i] == 'E' and roster1[j] == 'E'):
#             result[i]=j
#             i=i+1
#             j=j+1
#         while i<N and roster2[i]!='E':
#             i = i+1
#         while j<N and roster1[j]!='E':
#             j = j+1
#     i = 0
#     j = 0
#     while i<N and j<N:
#         if(roster2[i] == 'A' and roster1[j] == 'A'):
#             result[i]=j
#             i=i+1
#             j=j+1
#         while i<N and roster2[i]!='A':
#             i = i+1
#         while j<N and roster1[j]!='A':
#             j = j+1
#     i = 0
#     j = 0
#     while i<N and j<N:
#         if(roster2[i] == 'R' and roster1[j] == 'R'):
#             result[i]=j
#             i=i+1
#             j=j+1
#         while i<N and roster2[i]!='R':
#             i = i+1
#         while j<N and roster1[j]!='R':
#             j = j+1

#     return result

# def map_roster(roster,maping,N):
#     result = ['R' for i in range(N)]
#     for id in range(N):
#         result[id] = roster[maping[id]]
#     return result

# def verify_roster(nurse_roster,N,D,m,a,e):
#     if(nurse_roster == {}):
#         return True

#     for roster in nurse_roster:
#         count_m = sum([1 if shift=='M' else 0 for shift in roster])
#         count_e = sum([1 if shift=='E' else 0 for shift in roster])
#         count_a = sum([1 if shift=='A' else 0 for shift in roster])
#         if(m!=count_m or a!=count_a or e!=count_e):
#             return False
    
#     for i in range(1,D):
#         for j in range(N):
#             if(nurse_roster[i][j] == 'M'):
#                 if(nurse_roster[i-1][j] =='M' or nurse_roster[i-1][j] =='E'):
#                     return False

#     day = 0
#     while day+7<=D:
#         week_start = day
#         week_end = day+7
#         rest = [False for i in range(N)]
#         for d in range(week_start,week_end):
#             for id in range(N):
#                 if(nurse_roster[d][id] == 'R'):
#                     rest[id] = True
#         for id in range(N):
#             if(not rest[id]):
#                 return False
#         day = day+7
    
#     return True
    

# def part_1(csvreader):
#     soln_list = []
#     rows = []
#     for row in csvreader:
#         # print(row)
#         if(len(row) != 5):
#             print("INVALID INPUT FILE FORMAT\n")
#             break
#         rows.append(row)
#         N = int(row[0])
#         D = int(row[1])
#         m = int(row[2])
#         a = int(row[3])
#         e = int(row[4])
#         nurse_roster = part1_CSP(N,D,m,a,e)
#         if(not verify_roster(nurse_roster,N,D,m,a,e)):
#             print("Error in result\n")
#             print(row)
#             print(nurse_roster)
#         result = {}
#         # print(result)
#         # print(nurse_roster)
#         for day in range(len(nurse_roster)):
#             for id in range(len(nurse_roster[day])):
#                 key = "N"+str(id)+"_"+str(day)
#                 # print(key)
#                 result[key] = nurse_roster[day][id]
#         soln_list.append(result)
#     print(soln_list)
#     return soln_list


# def main(name):
#     file = open(name)
#     csvreader = csv.reader(file)
#     header = []
#     header = next(csvreader)
#     num = len(header)
#     if(num == 5):
#         soln_list = part_1(csvreader)
#         dump(soln_list)
#     elif(num == 7):
#         part_2(csvreader)
#     else:
#         print("INVALID INPUT FILE FORMAT\n")
#     file.close()

# if(len(sys.argv) == 2):
#     main(sys.argv[1])
# else:
#     print("Program Takes Input FileName as Argument\n")



# end_time = time.time()

# print(end_time-start_time)






















































# import json
# import csv
# import sys
# import time

# start_time = time.time()

# def CSP(N,D,m,a,e):
#     return {"N0_0": "R", "N1_0": "R", "N2_0": "A", "N0_1": "R", "N1_1": "M", "N2_1": "E"}

# def dump(soln_list):
#     with open("solution.json" , 'w') as file:
#         # for d in soln_list:
#         #     json.dump(d,file)
#         #     file.write("\n")
#         json.dump(soln_list,file)

# def part_2(csvreader):
#     return {}

 

# def solve_CSP(N,days,m,a,e,nurse_count,curr_day):
#     print("hi1")
#     if(curr_day == days):
#         return True

#     last_day = curr_day-1
    
#     morning_available_rest = nurse_count[last_day]['R'][0]+nurse_count[last_day]['R'][1]+nurse_count[last_day]['A'][1] 
#     morning_available_non_rest = nurse_count[last_day]['A'][0]

#     morning_pair = (0,m)
#     while morning_pair[1]>=0:
#         if(morning_pair[1]<=morning_available_rest and morning_pair[0]<=morning_available_non_rest):
#             available_rest = nurse_count[last_day]['M'][1] + nurse_count[last_day]['E'][1] + (morning_available_rest-morning_pair[1])
#             available_non_rest = N-m-available_rest
#             evening_pair = (0,e)
#             while evening_pair[1]>=0:
#                 if(evening_pair[1]<=available_rest and evening_pair[0]<=available_non_rest):
#                     left_rest = available_rest - evening_pair[1]
#                     left_non_rest = available_non_rest - evening_pair[0]
#                     afternoon_pair = (0,a)
#                     while afternoon_pair[1]>=0:
#                         if(afternoon_pair[1]<=left_rest and afternoon_pair[0]<=left_non_rest):
#                             rest_pair = (left_non_rest-afternoon_pair[0],left_rest-afternoon_pair[1])
#                             curr_count = {'M':morning_pair,'E':evening_pair,'A':afternoon_pair,'R':rest_pair}
#                             left_days = days-curr_day-1
#                             r = N-m-e-a
#                             non_rest_total = morning_pair[0]+evening_pair[0]+afternoon_pair[0]
#                             if(non_rest_total<=r*left_days):
#                                 nurse_count[curr_day] = curr_count
#                                 result = solve_CSP(N,days,m,a,e,nurse_count,curr_day+1)
#                                 if(result):
#                                     return True
#                         afternoon_pair = (afternoon_pair[0]+1,afternoon_pair[1]-1)
#                 evening_pair = (evening_pair[0]+1,evening_pair[1]-1)
#         morning_pair = (morning_pair[0]+1,morning_pair[1]-1)

#     return False


# def part1_CSP(N,D,m,a,e):
#     if(D>1 and N-m-e<m):
#         return {}
#     elif(D>=7 and (N-m-a-e)*7<N):
#         return {}
#     if(D == 0):
#         return {}

#     nurse = [['M' if i<m else 'E' if i-m<e else 'A' if i-m-e<a else 'R'  for i in range(N)]]
#     if(D == 1):
#         return nurse
#     days = min(D,7)
#     if(days<7):
#         week_rest = [True for i in range(0,N)]
#         nurse_count = [{'M':(0,m),'E':(0,e),'A':(0,a),'R':(0,N-m-a-e)}]
#     else:
#         week_rest = [False if i<m+e+a else True for i in range(0,N)]
#         nurse_count = [{'M':(m,0),'E':(e,0),'A':(a,0),'R':(N-m-a-e,0)}]
#     for i in range(1,days):
#         nurse_count.append([])
#     flag = solve_CSP(N,days,m,a,e,nurse_count,1)
#     if(not flag):
#         return {}
    
#     for i in range(1,len(nurse_count)):
#         nurse_curr_day = ['R' for j in range(N)]
#         morning_avaialble = []
#         for j in range(N):
#             if(nurse[i-1][j]=='A' or nurse[i-1][j]=='R'):
#                 morning_avaialble.append(j)
#         count_rest = 0
#         count_non_rest = 0
#         for id in morning_avaialble:
#             if(week_rest[id] and count_rest<nurse_count[i]['M'][1]):
#                 nurse_curr_day[id] = 'M'
#                 count_rest = count_rest+1
#             elif(count_non_rest<nurse_count[i]['M'][0] and not week_rest[id]):
#                 nurse_curr_day[id] = 'M'
#                 count_non_rest = count_non_rest+1
#         available = []
#         for j in range(N):
#             if(nurse_curr_day[j] != 'M'):
#                 available.append(j)

#         count_rest = 0
#         count_non_rest = 0
#         for id in range(N):
#             if(nurse_curr_day[id]!='M' and week_rest[id] and count_rest<nurse_count[i]['E'][1]):
#                 nurse_curr_day[id] = 'E'
#                 count_rest = count_rest+1
#             elif(nurse_curr_day[id]!='M' and count_non_rest<nurse_count[i]['E'][0] and not week_rest[id]):
#                 nurse_curr_day[id] = 'E'
#                 count_non_rest = count_non_rest+1

#         count_rest = 0
#         count_non_rest = 0
#         for id in range(N):
#             if(nurse_curr_day[id]=='R' and week_rest[id] and count_rest<nurse_count[i]['A'][1]):
#                 nurse_curr_day[id] = 'A'
#                 count_rest = count_rest+1
#             elif(nurse_curr_day[id]=='R' and count_non_rest<nurse_count[i]['A'][0] and not week_rest[id]):
#                 nurse_curr_day[id] = 'A'
#                 count_non_rest = count_non_rest+1
        
#         for i in range(N):
#             if(nurse_curr_day[i] == 'R'):
#                 week_rest[i] = True
#         nurse.append(nurse_curr_day)

#     done_days = 7
#     while D>done_days:
#         nurse_curr_day = generate_nonConflict_nurse(nurse[done_days-1],N,m,a,e)
#         maping = generate_maping(nurse[done_days-7],nurse_curr_day,N)
#         nurse.append(nurse_curr_day)
#         done_days = done_days+1
#         while(done_days<D and done_days%7!=0):
#             nurse_curr_day = map_roster(nurse[done_days-7],maping,N)
#             nurse.append(nurse_curr_day)
#             done_days = done_days+1
    
#     return nurse
        
# def generate_nonConflict_nurse(nurse,N,m,a,e):
#     result = ['R' for j in range(N)]
#     count = 0
#     for j in range(N):
#         if(nurse[j]=='A' or nurse[j]=='R' and count<m):
#             result[j] = 'M'
#             count = count+1
#     count_e = 0
#     count_a = 0
#     for j in range(N):
#         if(result[j]=='R'):
#             if(count_e<e):
#                 result[j] = 'E'
#                 count_e = count_e+1
#             elif(count_a<a):
#                 result[j] = 'A'
#                 count_a = count_a+1
#     return result

# def generate_maping(roster1,roster2,N):
#     result = {}
#     i = 0
#     j = 0
#     while i<N and j<N:
#         if(roster2[i] == 'M' and roster1[j] == 'M'):
#             result[i]=j
#         while i<N and roster2[i]!='M':
#             i = i+1
#         while j<N and roster1[j]!='M':
#             j = j+1
#     i = 0
#     j = 0
#     while i<N and j<N:
#         if(roster2[i] == 'E' and roster1[j] == 'E'):
#             result[i]=j
#         while i<N and roster2[i]!='E':
#             i = i+1
#         while j<N and roster1[j]!='E':
#             j = j+1
#     i = 0
#     j = 0
#     while i<N and j<N:
#         if(roster2[i] == 'A' and roster1[j] == 'A'):
#             result[i]=j
#         while i<N and roster2[i]!='A':
#             i = i+1
#         while j<N and roster1[j]!='A':
#             j = j+1
#     i = 0
#     j = 0
#     while i<N and j<N:
#         print('196')
#         if(roster2[i] == 'R' and roster1[j] == 'R'):
#             result[i]=j
#         while i<N and roster2[i]!='R':
#             i = i+1
#         while j<N and roster1[j]!='R':
#             j = j+1

        
#     for j in range(len(roster)):
#         result[roster[1]] = roster[2]
#     return result

# def map_roster(roster,maping,N):
#     result = ['R' for i in range(N)]
#     for id in range(N):
#         result[id] = roster[maping[id]]
#     return result

# def verify_roster(nurse_roster,N,D,m,a,e):
#     if(nurse_roster == {}):
#         return True

#     for roster in nurse_roster:
#         count_m = sum([1 if shift=='M' else 0 for shift in roster])
#         count_e = sum([1 if shift=='E' else 0 for shift in roster])
#         count_a = sum([1 if shift=='A' else 0 for shift in roster])
#         if(m!=count_m or a!=count_a or e!=count_e):
#             return False
    
#     for i in range(1,D):
#         for j in range(N):
#             if(nurse_roster[i][j] == 'M'):
#                 if(nurse_roster[i-1][j] =='M' or nurse_roster[i-1][j] =='E'):
#                     return False

#     day = 0
#     while day+7<=D:
#         week_start = day
#         week_end = day+7
#         rest = [False for i in range(N)]
#         for d in range(week_start,week_end):
#             for id in range(N):
#                 if(nurse_roster[d][id] == 'R'):
#                     rest[id] = True
#         for id in range(N):
#             if(not rest[id]):
#                 return False
#         day = day+7
    
#     return True
    

# def part_1(csvreader):
#     soln_list = []
#     rows = []
#     for row in csvreader:
#         # print(row)
#         if(len(row) != 5):
#             print("INVALID INPUT FILE FORMAT\n")
#             break
#         rows.append(row)
#         N = int(row[0])
#         D = int(row[1])
#         m = int(row[2])
#         a = int(row[3])
#         e = int(row[4])
#         nurse_roster = part1_CSP(N,D,m,a,e)
#         if(not verify_roster(nurse_roster,N,D,m,a,e)):
#             print("Error in result\n")
#             print(row)
#             print(nurse_roster)
#         result = {}
#         # print(result)
#         # print(nurse_roster)
#         for day in range(len(nurse_roster)):
#             for id in range(len(nurse_roster[day])):
#                 key = "N"+str(id)+"_"+str(day)
#                 # print(key)
#                 result[key] = nurse_roster[day][id]
#         soln_list.append(result)
#     print(soln_list)
#     return soln_list


# def main(name):
#     file = open(name)
#     csvreader = csv.reader(file)
#     header = []
#     header = next(csvreader)
#     num = len(header)
#     if(num == 5):
#         print('hi')
#         soln_list = part_1(csvreader)
#         dump(soln_list)
#     elif(num == 7):
#         part_2(csvreader)
#     else:
#         print("INVALID INPUT FILE FORMAT\n")
#     file.close()

# if(len(sys.argv) == 2):
#     main(sys.argv[1])
# else:
#     print("Program Takes Input FileName as Argument\n")


# end_time = time.time()


# print(end_time-start_time)



