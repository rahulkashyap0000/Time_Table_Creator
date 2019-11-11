import json
f = open('newinp1.json')
file = json.load(f) 
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
room_dic = {}
for i in file["Room Types"]:
    for j in file["Classrooms"]:
        if j[1] == i:
            if i in room_dic:
                room_dic[i].append(j[0])
            else:
                room_dic[i] = [j[0]]


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
print(timeslots)

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

for day in days:
    for course in course_dic:
        classes = course_dic[course][0]
        prof = course_dic[course][1][1][0]
        batch = course_dic[course][1][2]
        if len(classes) > 0:
            for ts in timeslots:
                check0 = 1
                check1 = 1
                check2 = 1
                t = ts
                for _ in range(int(2*classes[0])):
                    if (t >= 1230) or (not available[day][t][prof]):
                        check0 = 0
                        break
                    t = int(get_next(t))
                t = ts
                for _ in range(int(2*classes[0])):
                    if (t >= 1230) or (not available[day][t][batch]):
                        check1 = 0
                        break
                    t = int(get_next(t))
                t = ts
                room_type = course_dic[course][1][0]
                for i in room_dic[room_type]:
                    t = ts
                    for _ in range(int(2*classes[0])):
                        if(t >= 1230) or (not available[day][t][i][0]):
                            check2 = 0
                            break
                        t = int(get_next(t))
                        
                    if(check0 and check1 and check2):
                        t = ts
                        for _ in range(int(2*classes[0])):
                            available[day][t][batch] = False
                            available[day][t][prof] = False
                            available[day][t][i][0] = False
                            available[day][t][i].append(course)
                            course_dic[course][0] = classes[1:]
                            t = int(get_next(t))
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