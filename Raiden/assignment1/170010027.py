import json
import csv
from z3 import *
with open('newinp1.json', 'r') as f:
	inp = json.load(f)

def get_next(str_):
    '''
    Input: Current time

    Output: Current Time + 30 minutes

    Eg: \n
    Input: "12:00"
    
    Ouput: "12:30"
    '''
    result_str = ""
    hr = str_[:str_.find(':')]
    min = str_[str_.find(':')+1:]

    if int(min) == 30:
        result_str = str(int(hr)+1) + ":" + "00"
    else:
        result_str = hr + ":" + "30"
    return result_str



def get_time_slots():
    '''
    This function returns all the 30 minutes time slots possible in the Institute Timings
    Output Format:\n

    [
        [8:30, 9:30, 10:30, 11:30, 12:30],
        [2:00, 2:30, 3:00, 3:30, 4:00]
    ]
    '''
    time_slots = []
    for slot in inp["Institute time"]:
        cons_time_slots = []
        start_time = slot[0]
        cons_time_slots.append(slot[0])
        while get_next(start_time) != slot[1]:
            cons_time_slots.append(get_next(start_time))
            start_time = get_next(start_time)
        cons_time_slots.append(slot[1])
        time_slots.append(cons_time_slots)
    return time_slots

def slot_generator(x):
    '''
    Input: Size of lecture, eg: 1 = 1hr, 2 = 2hr, 1.5 = 1.5hr

    Output: This function returns a list of all the possible time slots for each course
    
    Example:\n
    Input: 1\n
    Output:\n
    [
        [8:30, 9:30], [9:30, 10:30], [10:30, 11:30], [11:30-12:30]
        [2:00, 3:00], [3:00, 4:00], [4:00, 5:00]
    ]
    '''
    slot_list = []
    for slot_list_ in get_time_slots():
        for i in range(len(slot_list_) - 2*x):
            slot_list.append([slot_list_[i], slot_list_[i+2*x]])
    return slot_list

def make_room_dict():
    '''
    This function returns a dictionary of room-types mapped to classrooms available

    Example\n
    Output\n
    {
        small = [T1, T2, T3]
        big = [LH1, LH2]
    }
    '''
    result_dict = {}
    for Room in inp["Room Types"]:
        for pair_ in inp["Classrooms"]:
            if pair_[1] in result_dict:
                result_dict[pair_[1]].append(pair_[0])
            else:
                result_dict[pair_[1]] = [pair_[0]]
    return result_dict


def make_string_course():
    '''Returns a list of propositions
    
    Format:\n
    CourseName_Room*Slot(Instructors)Batch/Dat@startTime-EndTime
    
    Example:

    CS207_LH1*0(Amaldev Manuel+)2/Monday@15:00-16:00
    '''

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    result_str = ""
    result_list = []
    for elm in inp["Courses"]:
        # For every course
        for day in days:
            # For every day
            for i in range(len(elm[2])):
                # For every lecture in a week
                for slot in slot_generator(int(elm[2][i])):
                    # For every slot, we can make for every lecture of the subject in a week
                    required_room_available = make_room_dict()[elm[1]]
                    for room in required_room_available:
                        # For every room in required room available
                        result_str += elm[0]
                        result_str += "_"+ room
                        result_str+="*"+str(i)
                        result_str+="("
                        for prof in elm[3]:
                            result_str+=prof+"+"
                        result_str+=")"
                        result_str+=str(elm[4])
                        result_str+="/"+day
                        result_str+="@"
                        result_str+=slot[0]+"-"+slot[1]
                        result_list.append(result_str)
                        result_str= ""
    return result_list

propositions = make_string_course()
s = Solver()

days = ["Monday","Tuesday","Wednesday","Thursday","Friday"]

for course in inp["Courses"]:
    # For all the courses
    Not_list = []
    c_list = []

    for itr in range(len(course[2])):
        # for all the lectures of the courses
        for i in range(len(propositions)):
            # For i in len(propositions)
            if course[0] in propositions[i] and '*' + str(itr) in propositions[i]:
                # Course in propositions[i] and *i length ka slot in proposition
                for j in range(len(propositions)):
                    # For j in len(propositions)
                    if i != j:
                        if course[0] in propositions[i] and "*" + str(itr) in propositions[j]:
                            Not_list.append(Not(Bool(propositions[j])))
                c_list.append(And(Bool(propositions[i]), And(Not_list)))
            Not_list = []
        s.add(Or(c_list))
        c_list = []

batch_list = set()
prof_list = set()

for course in inp["Courses"]:
    batch_list.add(course[4])
    for prof in course[3]:
        prof_list.add(prof)

# Batch List = List of all Batches
# Prof List = List of all professors

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
tt = []
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
            tt.append([day, strt_time, end_time, room ,Course, Instructors,Batch])
            
    for i in days:
        for j in tt:
            if i == j[0]:
                with open('time_table.csv', 'a') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(j)

else :
	print("No")