import json
from z3 import *
f = open('time.json')
file = json.load(f)
s = Solver()
courses = []
profs = set()
batches = set()
rooms = []
for i in file["Classrooms"]:
    rooms.append(i[0])
for i in file["Courses"]:
    courses.append(i)
    batches.add(i[4])
    for pro in i[3]:
        profs.add(pro)
        
# print(rooms)
# print(profs)
# print(batches)

room_dic = {}
for i in file["Room Types"]:
    for j in file["Classrooms"]:
        if j[1] == i:
            if i in room_dic:
                room_dic[i].append(j[0])
            else:
                room_dic[i] = [j[0]]
                
# for i in room_dic:
#     print(i, room_dic[i])
    
course_dic = {}
for i in courses:
    course_dic[i[0]] = [i[2], [i[1], i[3], i[4]]]

days = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
def get_next(t):
    s = str(t)
    result = ""
    if len(s) == 4:
        if s[2] == '3':
            result += s[0]
            x = int(s[1]) + 1
            result += str(x)
            result += '00'
        else:
            result += s[0] + s[1] + '30'
    else:
        if s[1] == '3':
            x = int(s[0]) + 1
            result += str(x)
            result +=  '00'
        else:
            result += s[0] + "30"
    return result

t = 830
timeslots = []
while(t !=  1700):
    if t == 1230:
        t = 1400
    timeslots.append(t)
    t = int(get_next(t))
# print(timeslots)

# room_available = {{}}
available = {}
for day in days:
    available[day] = {}
    for ts in timeslots:
        available[day][ts] = {}
        for room in rooms:
            available[day][ts][room] = [True]
        for batch in batches:
            available[day][ts][batch] = True
        for prof in profs:
            available[day][ts][prof] = True
            
def ts_to_t(t):
    s = str(t)
    result = ""
    if(len(s) == 3):
        result += "0" + s[0] + ":" + s[1] + s[2]
    else:
        result += s[0] + s[1] + ":" + s[2] + s[3]
    
    return result
counter = 1
for day in days:
#     if(counter == 2):
#         break
#     counter += 1
    for course in course_dic:
#         classes = course_dic[course][0]
        prof = course_dic[course][1][1][0]
        batch = course_dic[course][1][2]
        room_type = course_dic[course][1][0]
        Professor, Batch, Room = Bools('Professor Batch Room')
        s.add(Professor, Batch, Room)
        if(s.check() == "sat"):
            check0 = 1
        if len(course_dic[course][0]) > 0:
            for ts in timeslots:
                check0 = 1
                t = ts
                assigned = False
                for room in room_dic[room_type]:
                    check1 = 1
                    for _ in range(int(2*course_dic[course][0][0])):
#                         print("(",prof,batch,course,room,t,")")
                        if (t == 1230) or (t == 1300) or (t== 1700) or(not available[day][t][batch]) or (not available[day][t][room][0]) or (not available[day][t][prof]):
#                             print("XX[",prof,batch,course,room,"]XX")
                            check1 = 0
                            break
                        t = int(get_next(t))
#                     if(not check1):
#                         break
                    if(check1 and check0):
                        t = ts
#                         print("VV(",prof,batch,course,room,t,")VV")
                        for _ in range(int(2*course_dic[course][0][0])):
                            available[day][t][batch] = False
                            available[day][t][prof] = False
                            available[day][t][room][0] = False
                            available[day][t][room].append(course)
                            assigned = True
                            course_dic[course][0] = course_dic[course][0][1:]
                            t = int(get_next(t))
                        break
                if(assigned):
                    break
for day in days:
    print("----------------------------------")
    print(day)
    print("----------------------------------")
    for ts in timeslots:
        print(ts_to_t(ts))
        for r in rooms:
            if not available[day][ts][r][0]:
                print(r, available[day][ts][r][1])
        print()