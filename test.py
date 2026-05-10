f = open("grades.csv", "r")

ln = [x[0:x.rfind(".")+3] + "\n" for x in f.readlines()]

g = open("grades2.csv", "w")

g.writelines(ln)
