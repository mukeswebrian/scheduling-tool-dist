'''
Author: Brian Mukeswe
Date: September 30, 2019
Contact: mukeswebrian@yahoo.com

This class defines a teaching session into which a volunteer can be scheduled
'''
class Session():
    
    def __init__(self, week, day, session_id):
        
        self.week = week
        self.day = day
        self.session_id = session_id
        self.max_n_volunteers = 4
        
        self.student_group = None
        
        self.scheduled_volunteers = []
        self.time_slots = {}
        
    def get_id(self):
        return self.session_id
    
    def get_week(self):
        return self.week
    
    def get_day(self):
        return self.day
    
    def get_scheduled_volunteers(self):
        return self.scheduled_volunteers
        
    def assign_student_group(self, student_group):
        self.student_group = student_group.get_id()
        
    def get_student_group(self):
        return self.student_group
    
    def schedule_volunteer(self, volunteer):
        debug = False
        
        volunteer_not_seen = volunteer.check_groups_seen(self.get_student_group())
        volunteer_available = volunteer.is_available(self.get_day(), self.get_week())
        session_not_full = len(self.scheduled_volunteers) < self.max_n_volunteers
        
        if session_not_full and volunteer_not_seen and volunteer_available:
            
            self.scheduled_volunteers.append(volunteer.get_id())
            volunteer.update_schedule(self)
            volunteer.increament_scheduled_count()
            volunteer.update_groups_seen(self.get_student_group())
            
            
        elif not session_not_full:
            if debug == True:
                print("Failed to update session {} because the session already has {} volunteers".
                      format(self.get_id(), len(self.get_scheduled_volunteers())))
                
        elif not volunteer_not_seen:
            if debug == True:
                print("Failed to update session {} because volunteer {} has already seen group {}".
                      format(self.get_id(), volunteer.get_id(), self.get_student_group()))
                
        else:
            if debug == True:
                print("Failed to update session {} because volunteer {} is not available".
                      format(self.get_id(), volunteer.get_id()))
                
    def check_if_can_schedule(self, volunteer):
        
        volunteer_not_seen = volunteer.check_groups_seen(self.get_student_group())
        volunteer_available = volunteer.is_available(self.get_day(), self.get_week())
        session_not_full = len(self.scheduled_volunteers) < self.max_n_volunteers
        volunteer_not_fully_scheduled = len(volunteer.get_schedule()[self.get_day()][self.get_week()]) < volunteer.max_daily_sessions
        
        if volunteer_not_seen and volunteer_available and session_not_full and volunteer_not_fully_scheduled:
            return True
        else:
            return False
    
    def set_time_slots(self, time_dict):
        
        vols = self.get_scheduled_volunteers()
        non_sloted_vols = [i for i in vols]
    
        slots = list(time_dict.keys())
        
        for slot in slots: 
            for vol in non_sloted_vols:
                
                if vol not in time_dict[slot]:
                    time_dict[slot].append(vol)
                    self.time_slots[slot] = vol
                    non_sloted_vols.remove(vol)
               
                    break
                   
        return time_dict
    
    def get_volunteer_time_slot(self, volunteer_id):
        
        target = None
        if volunteer_id in self.time_slots.values():
       
            for slot in self.time_slots.keys():
                if self.time_slots[slot] == volunteer_id:
                    target = slot
                    
        return target
            
                
    def get_time_slots(self):
        return self.time_slots
                
    def describe(self):
        print('\nsession_id: ', self.session_id)
        print('\nweek: ', self.week)
        print('\nday: ', self.day)
        print('\nmaximum allowed volunteers: ', self.max_n_volunteers)
        print('\nassigned student group: ', self.get_student_group())
        print('\nscheduled volunteers: ', self.get_scheduled_volunteers())
        print('\ntime slots: ', self.get_time_slots())
