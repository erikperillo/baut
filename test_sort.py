from random import randint

def randList(n):
    return [randint(-100,100) for i in range(n)]

n = 8

xvals = randList(n)
yvals = {"alfa":randList(n), "beta":randList(n), "omega":randList(n)}

print "xvals:",xvals
print "yvals:",yvals

for key in yvals:
    yvals[key] = [y for (x,y) in sorted(zip(xvals,yvals[key]))]

print "xvals:",sorted(xvals)
print "yvals:",yvals
