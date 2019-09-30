import mongo_utils as mg
import pandas as pd

def get_scheduled_volunteers(day, week, server):

    collection = mg.config_collection(server)
    
    sess = []
    for result in collection.find({'day':day}):
        sess.append(result)
        
    sess_dict = sess[0]['sessions'][week]
    
    lst = []
    for vol_list in sess_dict.values():
        lst = lst + vol_list
        
    return pd.Series(lst).unique()

def get_scheduled_volunteer_frequencies(day, week, server):
    
    collection = mg.config_collection(server)
    
    sess = []
    for result in collection.find({'day':day}):
        sess.append(result)
        
    sess_dict = sess[0]['sessions'][week]
    freq = {}
    for session_id in sess_dict.keys():
        for vol in sess_dict[session_id]:
            if vol in freq.keys():
                freq[vol] += 1
            else:
                freq[vol] = 1
                
    return freq

def read_session_dates(dates):
    
    date_dict = {}
    day = 0
    for week in range(1, int((len(dates)/2))+1):
        
        date_dict[str(week)+'-2'] = dates[day]
        date_dict[str(week)+'-4'] = dates[day+1]
        
        day += 2
        
        
    return date_dict

def translate_session_code(session_code):
    
    dates = ['Tue Sept 3',
         'Thu Sept 5',
         'Tue Sept 10',
         'Thu Sept 12',
         'Tue Sept 17',
         'Thu Sept 19',
         'Tue Oct 15',
         'Thu Oct 17',
         'Tue Oct 22',
         'Thu Oct 24']
    
    date_dict = read_session_dates(dates)
    a,b,c,d = session_code.split('-')
    
    return date_dict[b+'-'+c]
    

def translate_volunteer_code(volunteer_id):
    vol_names = pd.read_excel('data/schedule data.xlsx', sheet_name='1-volunteers', usecols=[1,2], index_col=0, header=1)
    return vol_names.loc[volunteer_id][0]

def extract_session(day, week, session_id, sessions):
    
    sess = None
    for session in sessions[day][week]:
        
        if session.get_id() == session_id:
            sess = session
            break
            
    return sess
    
def report_volunteer_schedule(volunteer_id, server, sessions):
    
    coll = mg.config_collection(server)
    for vol in coll.find({'volunteer_id':volunteer_id}):
        schdl = vol['schedule']
        print('\n\nFull schedule for {}'.format(translate_volunteer_code(volunteer_id)))
        for day in schdl.keys():
               
            for week in schdl[day].keys():
                
                session_ids = schdl[day][week]
                if len(session_ids) > 0:
                    
                    print(week, day)
                    for session_id in session_ids:
                        
                        session = extract_session(day, week, session_id, sessions)
                        slot = session.get_volunteer_time_slot(volunteer_id)
                        
                        if slot is not None:
                            
                            print('\t'+translate_session_code(session_id)+': session '+session_id[-2:]+
                             ' '+slot)
                        
                else:
                    pass
                
def report_session_details(sessions, rpt):
    rpt.write('SESSION DETAILS')
    for day in sessions.keys():
        for week in sessions[day].keys():
            rpt.write('\n\n'+week+' '+day+'\n')
            
            for session in sessions[day][week]:
                session_name = translate_session_code(session.get_id())
                rpt.write('\t'+session_name+': '+session.get_id())
                
                slots = session.get_time_slots()
                
                for slot in slots.keys():
                    rpt.write('\t\t'+slot+': '+translate_volunteer_code(slots[slot]))
                    
                rpt.write('\n')
                
def report_volunteer_schedule_no_db(volunteers, sessions, rpt):
    
    rpt.write('INDIVIDUAL VOLUNTEER SCHEDULES')
    for volunteer_id in volunteers.keys():
        rpt.write('\n\n'+volunteer_id+': '+translate_volunteer_code(volunteer_id)+'\n')
        
        schedule = volunteers[volunteer_id].get_schedule()
        
        for day in schedule.keys():
            for week in schedule[day].keys():
                session_ids = schedule[day][week]
                
                if len(session_ids) > 0:
                    rpt.write(week+' '+day+'\n')                
                    for session_id in session_ids:
                        session = extract_session(day, week, session_id, sessions)
                        slot = session.get_volunteer_time_slot(volunteer_id)
                        
                        if slot is not None:
                            rpt.write('\t'+translate_session_code(session_id)+': session '+session_id[-2:]+
                             ' '+slot+'\n')
                        else:
                            rpt.write('\t'+translate_session_code(session_id)+': session '+session_id[-2:]+
                                  ' Warning: volunteer scheduled but not assigned time slot!'+'\n')
                        
                else:
                    pass
					
                rpt.write('\n')
        
            
