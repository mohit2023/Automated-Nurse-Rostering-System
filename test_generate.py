import random
import csv



# List = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]

# Matrix=[]
# for i in range(50):
# 	N=random.choice(List)
# 	D=random.choice(List)
# 	m=int(N*(random.random()))
# 	a=int((N-m)*(random.random()))
# 	e=int((N-m-a)*(random.random()))
# 	Matrix.append([N,D,m,a,e])

# #print(Matrix)
# header = ['N','D','m','a','e']
# filename = 'input_a.csv'

# with open(filename,'ab',) as file:
# 	writer = csv.writer(file)
# 	writer.writerow(header)
# 	for i in range(50):
# 		writer.writerow(Matrix[i])

Matrix = []
for N in range(21):
	for D in range(8):
		for m in range(0,N):
			for a in range(0,N-m):
				for e in range(0,N-m-a):
					Matrix.append([N,D,m,a,e])

header = ['N','D','m','a','e']
filename = 'testcase_a.csv'

with open(filename,'w') as file:
	writer = csv.writer(file)
	writer.writerow(header)
	for i in range(len(Matrix)):
		writer.writerow(Matrix[i])


# part 2 test cases 
Matrix = []
for N in range(10,11):
	for D in range(9,10):
		for m in range(N):
			for a in range(N-m):
				for e in range(N-m-a):
					for S in range(6,N-2):
						Matrix.append([N,D,m,a,e,S,100])

header = ['N','D','m','a','e','S','T']
filename = 'testcase_b.csv'

with open(filename,'w') as file:
	writer = csv.writer(file)
	writer.writerow(header)
	for i in range(len(Matrix)):
		writer.writerow(Matrix[i])


