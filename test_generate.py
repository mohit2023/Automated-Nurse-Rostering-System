import random
import csv


List = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]

Matrix=[]
for i in range(50):
	N=random.choice(List)
	D=random.choice(List)
	m=int(N*(random.random()))
	a=int((N-m)*(random.random()))
	e=int((N-m-a)*(random.random()))
	Matrix.append([N,D,m,a,e])

print(Matrix)
#header = ['N','D','m','a','e']
filename = 'input_a.csv'

with open(filename,'ab',) as file:
	writer = csv.writer(file)
	for i in range(50):
		writer.writerow(Matrix[i])



