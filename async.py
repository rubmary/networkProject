import time
from multiprocessing import Pool

def f(x, y):
	print("starting " + str(x) + "...")
	time.sleep(3)
	print("finishing " + str(x) + "!")
	return x*y

def f_aux(args):
	x = args[0]
	y = args[1]
	return f(x, y)

if __name__ == '__main__':
    p = Pool(5)
    results = p.map(f_aux, [[1, 2], [2, 3], [3, 4]])
    for e in results:
    	print(e)