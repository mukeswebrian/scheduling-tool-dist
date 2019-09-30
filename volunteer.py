class Volunteer():
    
    def __init__(self, volunteer_id):
        
        self.volunteer_id = volunteer_id
        
        self.max_daily_sessions = 4
        
        self.availability = {}
        default_availability = {
                                 'week1': 1,
                                 'week2': 1,
                                 'week3': 1,
                                 'week4': 1,
                                 'week5': 1
                                }
        self.set_availability('tuesday', default_availability)
        self.set_availability('thursday', default_availability)
        
        self.conditions = []
        
        
        self.n_times_scheduled = 0
        
        tues_schedule = {
                                 'week1': [],
                                 'week2': [],
                                 'week3': [],
                                 'week4': [],
                                 'week5': []
                                }
        
        thurs_schedule = {
                                 'week1': [],
                                 'week2': [],
                                 'week3': [],
                                 'week4': [],
                                 'week5': []
                                }
        
        self.schedule = {'tuesday':tues_schedule, 'thursday':thurs_schedule}
        
        self.groups_seen = []
        
    def get_id (self):
        return self.volunteer_id
    
    def set_availability(self, day, availability):
        self.availability[day] = availability
        
    def get_availability(self, day):
        return self.availability[day]
    
    def set_conditions(self, conditions):
        self.conditions = conditions
        
    def get_conditions(self):
        return self.conditions
    
    def get_times_scheduled(self):
        return self.n_times_scheduled
    
    def get_groups_seen(self):
        return self.groups_seen
    
    def get_schedule(self):
        return self.schedule
    
    def update_schedule(self, session):
        debug = False
        
        # update schedule
        day = session.get_day()
        week = session.get_week()
        
        below_max_sessions = len(self.schedule[day][week]) < self.max_daily_sessions
        
        if below_max_sessions:
            self.schedule[day][week].append(session.get_id())
            
        else:
            if debug == True:
                print("Failed to schedule volunteer {} in session {} because the volunteer is over-booked on {} {}.".
                      format(self.get_id(), session.get_id(), week, day))
    
    def increament_scheduled_count(self):   
        # increament times scheduled
        self.n_times_scheduled += 1
    
    def update_groups_seen(self, student_group_id):
        
        debug = False
        
        # update list of groups seen
        if student_group_id in self.groups_seen:
            if debug == True:
                print("Error: volunteer {} has already seen student group {}".format( 
                  str(self.volunteer_id), 
                  str(student_group_id)))
                
            return False
        
        else:
            self.groups_seen.append(student_group_id)
            return True
        
    def check_groups_seen(self, student_group_id):
        
        if student_group_id in self.groups_seen:
            return False
        
        else:
            return True
        
    def is_available(self, day, week):  
       
        if self.get_availability(day)[week] == 1:
            return True
        else:
            return False
        
    def describe(self):
        print('\nvolunteer id: ', self.volunteer_id)
        print('\nmaximum daily sessions: ', self.max_daily_sessions)
        print('\nstudent groups seen: ', self.groups_seen)
        print('\nknown medical conditions: ', self.conditions)
        print('\ntotal number of times scheduled: ', self.n_times_scheduled)
        print('\nTuesday availability: ', self.availability['tuesday'])
        print('\nTuesday schedule: ', self.schedule['tuesday'])
        print('\nThursday availability: ', self.availability['thursday'])
        print('\nThursday schedule: ', self.schedule['thursday'])