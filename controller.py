from session import Session
from volunteer import Volunteer
from student_group import StudentGroup
import pandas as pd
import random
import mongo_utils as mg
import reporting_utils as rp
import sys

def read_inputs():
    
    # Read input file
    volunteer_info = pd.read_excel('data/schedule data.xlsx', sheet_name='1-volunteers', header=[1], index_col=0)
    volunteer_info.drop(columns=['Name'], inplace=True)
    session_ids = pd.read_excel('data/schedule data.xlsx', sheet_name="2-sessions", header=[0,1], index_col=0)
    
    return volunteer_info, session_ids

def make_volunteer(volunteer_info):
    
    volunteer = Volunteer(volunteer_info[0]) 
    
    tues_av = {
        "week1":volunteer_info[1],
        "week2":volunteer_info[3],
        "week3":volunteer_info[5],
        "week4":volunteer_info[7],
        "week5":volunteer_info[9]
    }
    thur_av = {
        "week1":volunteer_info[2],
        "week2":volunteer_info[4],
        "week3":volunteer_info[6],
        "week4":volunteer_info[8],
        "week5":volunteer_info[10]
    }
    
    volunteer.set_availability('tuesday', tues_av)
    volunteer.set_availability('thursday', thur_av)
    
    return volunteer

def make_volunteers(volunteer_info):
    
    volunteers = {} # store for all volunteers
    
    # make volunteer and add them to the store
    for i in range(0, len(volunteer_info)):
        volunteer = make_volunteer(volunteer_info.iloc[i])
        volunteers[volunteer.get_id()] = volunteer
        
    return volunteers

def define_sessions(day, week, session_ids):
    
    sessions = []
    for session_id in session_ids[week][day]:
        if session_id != 'none':
            
            session = Session(week, day, session_id) # create session
            session.assign_student_group(StudentGroup(session_id[-4:])) # assign student group
            sessions.append(session)
            
    return sessions
    
def make_sessions(session_ids):
    
    sessions = {}
    
    weeks = ["week1", "week2", "week3", "week4", "week5"]
    days = ["tuesday", "thursday"]
    
    # initialize sessions
    for day in days:
        sessions[day] = {}
    
    for day in days:
        for week in weeks:
            sessions[day][week] = define_sessions(day, week, session_ids)
            
    return sessions, weeks, days

def get_available_volunteers(day, week, volunteers):
    
    available_vols = []
    for volunteer_id in volunteers.keys():
        if volunteers[volunteer_id].is_available(day=day, week=week):
            available_vols.append(volunteer_id)
            
    return available_vols

def get_volunteer_compatible_sessions(volunteer_ids, day, week, volunteers, sessions):

    vol_sess_lists = {}
    
    for volunteer_id in volunteer_ids:
        
        vol_sess_lists[volunteer_id] = [] # initialize volunteer compatible sessions
        
        for session in sessions[day][week]:
            # Check that the volunteer has not seen the student group in the session
            if session.get_student_group() not in volunteers[volunteer_id].get_groups_seen():
                vol_sess_lists[volunteer_id].append(session.get_id())
                
    return vol_sess_lists

def pick_most_flexible_volunteer(vol_sess_lists):
    
    vol_flex_scores = {}
    for volunteer_id in vol_sess_lists.keys():
        vol_flex_scores[volunteer_id] = len(vol_sess_lists[volunteer_id])
        
    max_score = max(vol_flex_scores.values())
    
    pick =''
    
    for volunteer_id in vol_flex_scores.keys():
        if vol_flex_scores[volunteer_id] == max_score:
            pick = volunteer_id
            break
        
    return pick

def pick_least_flexible_volunteer(vol_sess_lists):
    
    vol_flex_scores = {}
    for volunteer_id in vol_sess_lists.keys():
        vol_flex_scores[volunteer_id] = len(vol_sess_lists[volunteer_id])
        
    max_score = min(vol_flex_scores.values())
    
    pick =''
    
    
    for volunteer_id in vol_flex_scores.keys():
        if vol_flex_scores[volunteer_id] == max_score:
            pick = volunteer_id
            break
        
    return pick

def get_session_eligible_volunteers(sessions, volunteers):
    
    sess_vol_lists = {}
    
    for session in sessions:
    
        sess_vol_lists[session.get_id()] = []
    
        for volunteer_id in volunteers.keys():
            if session.get_student_group() not in volunteers[volunteer_id].get_groups_seen():
                sess_vol_lists[session.get_id()].append(volunteer_id)
            
    return sess_vol_lists


def get_session_ids(day, week, sessions):
    
    session_ids = []
    
    for session in sessions[day][week]:
        session_ids.append(session.get_id())
            
    return session_ids

def get_user_vol_schedule(d, w):
    
    source = 'data/schedule data.xlsx'
    slots = ['slotA','slotB','slotC','slotD']
    parser = {}
    parser['tuesday'] = {
                     'week1':{'cols':'C', 'h_row':2, 'nrows':22, 'sheet':'Rotations', 'slots':['slotA']},
                     'week2':{'cols':'D:G', 'h_row':2, 'nrows':22, 'sheet':'Rotations', 'slots':slots},
                     'week3':{'cols':'H:K', 'h_row':2, 'nrows':22, 'sheet':'Rotations', 'slots':slots},
                     'week4':{'cols':'M:P', 'h_row':2, 'nrows':22, 'sheet':'Rotations', 'slots':slots},
                     'week5':{'cols':'R:U', 'h_row':2, 'nrows':22, 'sheet':'Rotations', 'slots':slots}
                     }
    parser['thursday'] = {
                     'week1':{'cols':'C', 'h_row':25, 'nrows':22, 'sheet':'Rotations', 'slots':['slotA']},
                     'week2':{'cols':'D:G', 'h_row':25, 'nrows':22, 'sheet':'Rotations', 'slots':slots},
                     'week3':{'cols':'H:K', 'h_row':25, 'nrows':22, 'sheet':'Rotations', 'slots':slots},
                     'week4':{'cols':'M:P', 'h_row':25, 'nrows':22, 'sheet':'Rotations', 'slots':slots},
                     'week5':{'cols':'R:U', 'h_row':25, 'nrows':22, 'sheet':'Rotations', 'slots':slots}
                     }
    
    past_data = {}
    for day in parser.keys():
        past_data[day] = {}
    
        for week in parser[day].keys():
            past_data[day][week] = pd.read_excel(source, 
                       sheet_name=parser[day][week]['sheet'], 
                       header=parser[day][week]['h_row'],
                       usecols=parser[day][week]['cols'], 
                       nrows=parser[day][week]['nrows'],
                       names=parser[day][week]['slots'])
            
    return past_data[d][w]

def get_volunteer_code(vol_name):
    vol_names = pd.read_excel('data/schedule data.xlsx', 
                              sheet_name='1-volunteers', 
                              usecols=[1,2], index_col=0, header=1)
    volunteer_id = None
    
    for vol_id in vol_names.index:
        if vol_names.loc[vol_id][0] == vol_name:
            volunteer_id = vol_id
            break
            
    return volunteer_id
    
def get_user_specified_vol_list(day, week):
    
    user_vols = get_user_vol_schedule(day, week)
    
    vol_list = []
    
    if len(user_vols['slotA'].dropna(inplace=False)) > 0:
        for vol_name in user_vols['slotA'].dropna(inplace=False):
            vol_list.append(get_volunteer_code(vol_name))
            
    return vol_list
def pick_day_available_volunteers(day, week, volunteers):
    
    vol_list = get_available_volunteers(day, week, volunteers)
    vols = {}
    
             
    if len(vol_list) <= 18 and day=='thursday':
        for vol in vol_list:
            vols[vol] = volunteers[vol]
                
    elif len(vol_list) > 18 and day=='thursday':
        for vol in random.sample(vol_list, k=18):
            vols[vol] = volunteers[vol]
            
    elif len(vol_list) <= 19 and day=='tuesday':
        for vol in vol_list:
            vols[vol] = volunteers[vol]
                
    elif len(vol_list) > 19 and day=='tuesday':
        for vol in random.sample(vol_list, k=19):
            vols[vol] = volunteers[vol]
        
    return vols

def pick_day_available_volunteers_2(day, week, volunteers):
    
    vol_list = get_user_specified_vol_list(day, week)
    
    if vol_list == []:
        vol_list = get_available_volunteers(day, week, volunteers)        
    else:
        pass
        
    vols = {}    
    if len(vol_list) <= 18 and day=='thursday':
        for vol in vol_list:
            vols[vol] = volunteers[vol]
                
    elif len(vol_list) > 18 and day=='thursday':
        for vol in random.sample(vol_list, k=18):
            vols[vol] = volunteers[vol]
            
    elif len(vol_list) <= 19 and day=='tuesday':
        for vol in vol_list:
            vols[vol] = volunteers[vol]
                
    elif len(vol_list) > 19 and day=='tuesday':
        for vol in random.sample(vol_list, k=19):
            vols[vol] = volunteers[vol]
        
    return vols



def generate_schedule_strategy_1(volunteers, sessions):
    
    weeks = ["week1", "week2", "week3", "week4", "week5"]
    days = ["tuesday", "thursday"]

    for sch_day in days:
        for sch_week in weeks:
            daily_sessions = sessions[sch_day][sch_week]
        
            for i in range(0, len(daily_sessions)):
                session = daily_sessions[i]
                day = session.get_day()
                week = session.get_week()
            
                for i in range(0, session.max_n_volunteers):
                
                    sess_vol_lists = get_session_eligible_volunteers(sessions[day][week], volunteers)
    
                    volunteer_ids = sess_vol_lists[session.get_id()]
                    vol_sess_lists = get_volunteer_compatible_sessions(volunteer_ids, day, week, volunteers, sessions)
                
            
                    vol_selected = pick_most_flexible_volunteer(vol_sess_lists)
    
                    session.schedule_volunteer(volunteers[vol_selected])
        return volunteers, sessions

def generate_schedule_strategy_2(day, week, volunteers, sessions):
    
    daily_sessions = sessions[day][week]
    sess_vol_lists = get_session_eligible_volunteers(sessions[day][week], volunteers)
    
    for i in range(0, len(daily_sessions)):
        session = daily_sessions[i]
        day = session.get_day()
        week = session.get_week()
        
        volunteer_ids = sess_vol_lists[session.get_id()]
        scheduled_count = 0
        
        for volunteer_id in volunteer_ids:
            
            if len(volunteers[volunteer_id].get_schedule()[day][week]) < 4:
                session.schedule_volunteer(volunteers[volunteer_id])
                scheduled_count += 1
                
            if scheduled_count >= 4:
                break
                
def generate_schedule_strategy_3(day, week, volunteers, sessions, log):
    
    vol_ids = list(volunteers.keys())
    sess_ids = list(i.get_id() for i in sessions[day][week])
    
    session_dict = make_session_dict(sessions)
    max_combination_count = 1000
    scheduled_count = 0
    
    log.write('\n'+day+' '+week)
    for i in range(max_combination_count):
        combination = make_combinations(vol_ids, sess_ids, n_combinations=1)
        
        combination_valid = check_combination_validity(combination, volunteers, session_dict)
        
        
        if combination_valid:
            log.write('\n\t'+'combination ' +str(i)+' valid: '+str(combination_valid))
            schedule_combination(combination, volunteers, session_dict)
            #print(day, week, combination)
            scheduled_count += 1
            
        if scheduled_count >= 4:
            break 
            
    log.write('\n')
    
def make_combinations(lst1, lst2, n_combinations):

    tracker = {}
    if len(lst1) == len(lst2):

        
        for vol in lst1:
            tracker[vol] = []

        for i in range(n_combinations):
            rd_lst = random.sample(lst1, len(lst1))
    
            for vol in rd_lst:
                tracker[vol].append(lst2[rd_lst.index(vol)])
    
    return tracker

def make_session_dict(sessions):
    session_dict = {}
    for day in sessions.keys():
        for week in sessions[day].keys():
            for session in sessions[day][week]:
                session_dict[session.get_id()] = session
                
    return session_dict

def check_combination_validity(combination, volunteers, session_dict):
    
    check = True
    for vol_id in combination.keys():
        if not session_dict[combination[vol_id][0]].check_if_can_schedule(volunteers[vol_id]):
            check = False
            break
            
    return check

def schedule_combination(combination, volunteers, session_dict):
    
    for vol_id in combination.keys():
        session_dict[combination[vol_id][0]].schedule_volunteer(volunteers[vol_id])
                
def store_volunteer_schedules(server, volunteers):

    collection = mg.config_collection(server)

    # write generated volunteer schedules to database
    for volunteer in volunteers.values():
        doc = {}
        doc['volunteer_id'] = volunteer.get_id()
        doc['schedule'] = volunteer.get_schedule()
    
        collection.insert_one(doc)
            
def store_session_info(server, sesisons):

    collection = mg.config_collection(server)

    # write session information to database
    weeks = ["week1", "week2", "week3", "week4", "week5"]
    days = ["tuesday", "thursday"]

    for day in days:
        doc = {}
        doc['day'] = day
        doc['sessions'] = {}
        for week in weeks:
            doc['sessions'][week] = {}
        
            for session in sessions[day][week]:
                doc['sessions'][week][session.get_id()] = session.get_scheduled_volunteers()
        
        collection.insert_one(doc)
        
def store_rotations(server, sessions):
    
    collection = mg.config_collection(server)

    # write session information to database
    weeks = ["week1", "week2", "week3", "week4", "week5"]
    days = ["tuesday", "thursday"]

    for day in days:
        doc = {}
        doc['day'] = day
        doc['sessions'] = {}
        for week in weeks:
            doc['sessions'][week] = {}
        
            for session in sessions[day][week]:
                doc['sessions'][week][session.get_id()] = session.get_time_slots()
        
        collection.insert_one(doc)
        
def read_specifed_volunteers(day, week):
    
    specified_volunteers = {}
    
    vol_names = pd.read_excel(week+'_volunteers.xlsx', sheet_name=day, header=0)
    name_code_map = pd.read_excel('data/schedule data.xlsx', 
                                              sheet_name='1-volunteers', 
                                              usecols=[1,2], 
                                              index_col=1, 
                                              header=1)
    vol_ids = []
    for vol_name in vol_names[vol_names.columns[0]]:
        vol_id = name_code_map.loc[vol_name][0]
        vol_ids.append(vol_id)
        
    return vol_ids

def make_rotations(sessions):
    
    weeks = ["week1","week2", "week3", "week4", "week5"] 
    days = ["tuesday", "thursday"]
    
    for day in days:
        for week in weeks:
            time_dict = {'slotA':[], 'slotB':[], 'slotC':[], 'slotD':[]}
            for session in sessions[day][week]:
                time_dict = session.set_time_slots(time_dict)

if __name__ == "__main__":
    
    volunteer_info, session_ids = read_inputs()
    
    volunteers = make_volunteers(volunteer_info)
    sessions, weeks, days = make_sessions(session_ids)
    
    log = open('log.txt', 'w')

    for day in days:
        for week in weeks:
            vols = pick_day_available_volunteers_2(day, week, volunteers)
            generate_schedule_strategy_3(day, week, vols, sessions, log)
            
    log.close()
    make_rotations(sessions)
    
    rpt = open('GENERATED_SCHEDULE.txt', 'w')
    rp.report_session_details(sessions, rpt)
    rp.report_volunteer_schedule_no_db(volunteers, sessions, rpt)

    rpt.close()
    
    '''
    server = {"host":"localhost",
          "port":27017,
          "database":"scheduling_tool",
          "collection":""}
    
    server['collection'] = "volunteer_schedules"
    store_volunteer_schedules(server, volunteers)
    
    server['collection'] = "sessions"
    store_session_info(server, sessions)
    
    server['collection'] = "rotations"
    store_rotations(server, sessions)
    
    server['collection'] = "volunteer_schedules"
    for volunteer_id in volunteers.keys():  
        rp.report_volunteer_schedule(volunteer_id, server, sessions)
    ''' 
    
