#====================

file = open("student.txt","r",encoding="utf-8")
print(file.name)
print(file.mode)
print(file.closed)
print(file.encoding)
print(file.read())
file.close()
file = open("student.txt","r",encoding="utf-8")
print(type(file))
content = file.read()
print(content)
file.close()
# 問他有沒有關掉“”管線
file.closed

# 這樣寫file離開個區域直接關，節約資源
with open("student.txt","r",encoding = "utf-8") as file:
    content = file.read()

print(file.closed)
# csv.reader(csvfile, /, dialect='excel', **fmtparams)

import csv

with open("考試分數_3年6班.csv", "r", encoding = "utf-8") as file:
    reader = csv.reader(file)
    print(type(reader))
    for row in reader:
        print(row)

# class csv.DictReader(f, fieldnames=None, restkey=None, restval=None, dialect='excel', *args, **kwds) 
import csv

with open("考試分數_3年6班.csv", "r", encoding = "utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row)

