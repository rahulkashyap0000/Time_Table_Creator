import json
import csv
from z3 import *
with open('newinp1.json', 'r') as f:
	inp = json.load(f)

# This function return time after 30 minutes of the given time
def get_next(str_):
	result_str = ""
	hr = str_[:str_.find(':')]
	min = str_[str_.find(':')+1:]
	if int(min) == 30:
		result_str = str(int(hr)+1) +":"+"00"
	else :
		result_str = hr + ":" + "30"
	return result_str

# This function return 30 min time slots possible in Institute Timings
def get_time_slots():
	time_slots = []
	for slot in inp["Institute time"]:
		cons_time_slots = []
		start_time = slot[0]
		cons_time_slots.append(slot[0])
		while get_next(start_time)!=slot[1] :
			cons_time_slots.append(get_next(start_time))
			start_time = get_next(start_time)
		cons_time_slots.append(slot[1])
		time_slots.append(cons_time_slots)
	return time_slots


# This function makes a dictionary whose keys are room type and values are room name
def make_room_dict():
	result_dict = {}
	for Room in inp["Room Types"]:
		for pair_ in inp["Classrooms"]:
			if pair_[1] == Room:
				if pair_[1] in result_dict:
					result_dict[pair_[1]].append(pair_[0])
				else :
					result_dict[pair_[1]] = [pair_[0]]
	return result_dict
# This function generates possible time slots for each course
def slot_generator(x):
	slot_list = []
	for slot_list_ in get_time_slots():
		for i in range(len(slot_list_) - 2*x):
			slot_list.append([slot_list_[i], slot_list_[i+2*x]])
	return slot_list

def make_string_course_insrt():
	'''This function returns a list of propositions'''
	days = ['Monday','Tuesday','Wednesday','Thursday','Friday']
	result_list = []
	result_str = ""
	for elm in inp["Courses"]:
		for day in days:
			for i in range(len(elm[2])):
				for slot in slot_generator(int(elm[2][i])):
					for room in make_room_dict()[elm[1]]:
						result_str += elm[0]
						result_str += "_" + room
						result_str += "*" + str(i)
						result_str += "("
						for prof in elm[3]:
							result_str += prof + "+"
						result_str += ")"
						result_str += str(elm[4])
						result_str += "/" + day
						result_str += "@"
						result_str += slot[0] +"-"+ slot[1]
						result_list.append(result_str)
						result_str = ""
	return result_list

# This function check whether time x is less than time y
def lesser(x,y):
	hr1 = int(x[:x.find(":")])
	min1 = int(x[x.find(":")+1:])
	hr2 = int(y[:y.find(":")])
	min2 = int(y[y.find(":")+1:])
	time1 = hr1*100 + min1
	time2 = hr2*100 + min2
	if time1 < time2:
		return True
	return False

# This function check whether time x is greater than time y
def greater(x,y):
	hr1 = int(x[:x.find(":")])
	min1 = int(x[x.find(":")+1:])
	hr2 = int(y[:y.find(":")])
	min2 = int(y[y.find(":")+1:])
	time1 = hr1*100 + min1
	time2 = hr2*100 + min2
	if time1 > time2:
		return True
	return False

propositions = make_string_course_insrt()
''' The propostion look like this CourseName_Room*Slot(Instructors)Batch/Day@startTime-EndTime   CS207_LH1*0(Amaldev Manuel+)2/Monday@15:00-16:00'''

s = Solver()
#print(propositions[1921])
#s.add(Bool(propositions[0]))
#for proposition in propositions:
#	if "NO101" in proposition:
#		print(proposition)(

days = ['Monday','Tuesday','Wednesday','Thursday','Friday']


# Because we have encode the lecture slots in the propositions we only have to put the contraint that only one lecture for a particular course and slot will be there in a week
for course in inp["Courses"]:
	Not_list = []
	c_list = []
	for itr in range(len(course[2])):
		for i in range(len(propositions)):
			if course[0] in propositions[i] and "*" + str(itr) in propositions[i]:
				for j in range(len(propositions)):
					if i != j:
						if course[0] in propositions[j] and "*" + str(itr) in propositions[j]:
						#print(j)
							Not_list.append(Not(Bool(propositions[j])))
				c_list.append(And(Bool(propositions[i]),And(Not_list)))
			Not_list = []
		s.add(Or(c_list))
		c_list = []

batch_list = set()
prof_list = set()
for course in inp["Courses"]:
	#print(course[4])
	batch_list.add(course[4])
	for prof in course[3]:
		prof_list.add(prof)

#print(batch_list)
#print(prof_list)

# All the professors teaching the course should be free in that slot
dummy_propositions = propositions
for prof in list(prof_list):
	for day in days:
		const_list = []
		for proposition in dummy_propositions:
			if prof in proposition and day in proposition:
				const_list.append(proposition)
				for other_proposition in dummy_propositions:
					if proposition != other_proposition:
						if prof in other_proposition and day in other_proposition:
							strt_time = proposition[proposition.find("@")+1:proposition.find("-")]
							end_time = proposition[proposition.find("-")+1:]
							strt_time_new = other_proposition[other_proposition.find("@")+1:other_proposition.find("-")]
							end_time_new = other_proposition[other_proposition.find("-")+1:]
							if ((not(lesser(strt_time_new,strt_time)) and not(greater(end_time_new,end_time)))or (lesser(strt_time_new,strt_time)) and greater(end_time_new,end_time) or (not(greater(strt_time,strt_time_new)) and greater(end_time,strt_time_new) and lesser(end_time,end_time_new)) or (not(greater(strt_time,strt_time_new)) and greater(end_time,strt_time_new) and lesser(end_time,end_time_new))): 
								const_list.append(other_proposition)
				or_list=[]
				and_list = []
				for elm in const_list:
					and_list.append(Bool(elm))
					for other_elm in const_list:
						if elm != other_elm:
							and_list.append(Not(Bool(other_elm)))
					or_list.append(Implies(and_list[0],And(and_list[1:])))
					and_list = []
				s.add(And(or_list))
				const_list = []
				dummy_propositions.remove(proposition)

# Only one lecture should be there in a time slot for a room
dummy_propositions = propositions
for room_tupple in inp["Classrooms"]:
	for day in days:
		const_list = []
		for proposition in dummy_propositions:
			if room_tupple[0] in proposition and day in proposition:
				const_list.append(proposition)
				for other_proposition in dummy_propositions:
					if proposition != other_proposition:
						if room_tupple[0] in other_proposition and day in other_proposition:
							strt_time = proposition[proposition.find("@")+1:proposition.find("-")]
							end_time = proposition[proposition.find("-")+1:]
							strt_time_new = other_proposition[other_proposition.find("@")+1:other_proposition.find("-")]
							end_time_new = other_proposition[other_proposition.find("-")+1:]
							if ((not(lesser(strt_time_new,strt_time)) and not(greater(end_time_new,end_time)))or (lesser(strt_time_new,strt_time)) and greater(end_time_new,end_time) or (not(greater(strt_time,strt_time_new)) and greater(end_time,strt_time_new) and lesser(end_time,end_time_new)) or (not(greater(strt_time,strt_time_new)) and greater(end_time,strt_time_new) and lesser(end_time,end_time_new))): 
								const_list.append(other_proposition)
				or_list=[]
				and_list = []
				for elm in const_list:
					and_list.append(Bool(elm))
					for other_elm in const_list:
						if elm != other_elm:
							and_list.append(Not(Bool(other_elm)))
					or_list.append(Implies(and_list[0],And(and_list[1:])))
					and_list = []
				s.add(And(or_list))
				const_list = []
				dummy_propositions.remove(proposition)


# A batch should have only one lecture in a particular time slot 
dummy_propositions = propositions
for batch in list(batch_list):
	for day in days:
		const_list = []
		for proposition in dummy_propositions:
			if ")"+str(batch) +"/" in proposition and day in proposition:
				const_list.append(proposition)
				for other_proposition in dummy_propositions:
					if proposition != other_proposition:
						if ")" + str(batch) + "/"  in other_proposition and day in other_proposition:
							strt_time = proposition[proposition.find("@")+1:proposition.find("-")]
							end_time = proposition[proposition.find("-")+1:]
							strt_time_new = other_proposition[other_proposition.find("@")+1:other_proposition.find("-")]
							end_time_new = other_proposition[other_proposition.find("-")+1:]
							if ((not(lesser(strt_time_new,strt_time)) and not(greater(end_time_new,end_time)))or (lesser(strt_time_new,strt_time)) and greater(end_time_new,end_time) or (not(greater(strt_time,strt_time_new)) and greater(end_time,strt_time_new) and lesser(end_time,end_time_new)) or (not(greater(strt_time,strt_time_new)) and greater(end_time,strt_time_new) and lesser(end_time,end_time_new))): 
								const_list.append(other_proposition)
				or_list=[]
				and_list = []
				for elm in const_list:
					and_list.append(Bool(elm))
					for other_elm in const_list:
						if elm != other_elm:
							and_list.append(Not(Bool(other_elm)))
					or_list.append(Implies(and_list[0],And(and_list[1:])))
					and_list = []
				s.add(And(or_list))
				const_list = []
				dummy_propositions.remove(proposition)



with open('time_table.csv', 'wb') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Day', 'Start_time', 'End_time', 'Room' , 'Course', 'Instructors' ,'Batch'])

time_table = {}
if s.check() == sat:
	m = s.model()
	for proposition in m:
		if m[proposition]:
			
			#print(proposition)
			proposition = str(proposition)
			day = proposition[proposition.find('/')+1:proposition.find('@')]
			room = proposition[proposition.find('_')+1:proposition.find('*')]
			strt_time = proposition[proposition.find("@")+1:proposition.find("-")]
			end_time = proposition[proposition.find("-")+1:]
			Course = proposition[:proposition.find('_')] 
			Instructors = proposition[proposition.find('(')+1 : proposition.find('+)')]
			Batch =   proposition[proposition.find(')')+1: proposition.find('/')]
			if day not in time_table:
				time_table[day] = {}
			if room not in time_table[day]:
				time_table[day][room] = {}
			if strt_time not in time_table[day][room]:
				time_table[day][room][strt_time] = {}
			if end_time not in time_table[day][room]:
				time_table[day][room][end_time] = {}

			# if start_tine not in time_table[day]:
				# time_table[day] = {}
			time_table[day][room][strt_time] = Course
			time_table[day][room][end_time] = Course
			with open('time_table.csv', 'a') as csv_file:
				writer = csv.writer(csv_file)
				writer.writerow([day, strt_time, end_time, room ,Course, Instructors,Batch])
			

else :
	print("No")