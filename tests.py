'''
Author: Brian Mukeswe
Date: September 30, 2019
Contact: mukeswebrian@yahoo.com

Test cases to verify the fucntionality of the volunteer and session classes
'''
from unittest import TestCase
from student_group import StudentGroup
from volunteer import Volunteer
from session import Session

class testStudentGroup(TestCase):
    
    def test_group_id(self):
        group = StudentGroup('A')
        self.assertEqual(group.get_id(), 'A', "correct group id is assigned and retrieved")

class testVolunteer(TestCase):
    
    def test_volunteer_id(self):
        vol = Volunteer(volunteer_id='v001')
        self.assertEqual(vol.get_id(), 'v001', "Correct volunteer id is assigned and retrieved")
        
    def test_availability(self):
        
        sample_availability = {
                        'week1': 1,
                        'week2': 0,
                        'week3': 1,
                        'week4': 0,
                        'week5': 0
                        }
        vol = Volunteer(volunteer_id='v001')
        vol.set_availability('tuesday', sample_availability)
        self.assertEqual(vol.get_availability('tuesday'), sample_availability, "availability is set and retrieved correctly")
        
    def test_simple_scheduling(self):
        
        vol = Volunteer(volunteer_id='v001')
        
        group = StudentGroup('A')
        sess = Session(week='week2', day='thursday', session_id='s001')
        sess.assign_student_group(group)
        
        sess.schedule_volunteer(vol)
        
        self.assertEqual(vol.get_groups_seen(), ['A'], 'volunteer has correctly updated list of groups seen')
        self.assertEqual(vol.get_schedule()['thursday']['week2'], ['s001'], 'volunteer schedule updated correctly')
        self.assertEqual(vol.get_times_scheduled(), 1, 'correctly counted times scheduled')
        self.assertEqual(vol.get_schedule()['tuesday']['week2'], [], 'Tuesday not updated')
        
    def test_shceduling_previously_seen_volunteer(self):
        
        vol = Volunteer(volunteer_id='v001')
        
        group = StudentGroup('A')
        
        sess1 = Session(week='week2', day='thursday', session_id='s001')
        sess1.assign_student_group(group)
        sess2 = Session(week='week3', day='tuesday', session_id='s002')
        sess2.assign_student_group(group)
        
        sess1.schedule_volunteer(vol)
        sess2.schedule_volunteer(vol)
        
        self.assertEqual(vol.get_groups_seen(), ['A'], 'volunteer has correctly updated list of groups seen')
        self.assertEqual(vol.get_schedule()['thursday']['week2'], ['s001'], 'first schedule update successful')
        self.assertEqual(vol.get_schedule()['tuesday']['week3'], [], 'second schedule update not successful')
        
    def test_over_scheduling_session(self):
        
        vols = []
        
        # create five volunteers
        for i in range(1, 6):    
            vols.append(Volunteer(volunteer_id='v00'+str(i)))
            
        # create a session
        group = StudentGroup('A')
        sess = Session(week='week2', day='thursday', session_id='s001')
        sess.assign_student_group(group)
        
        # assign all volunteers to the session
        for vol in vols:
            sess.schedule_volunteer(vol)
            
        self.assertEqual(len(sess.get_scheduled_volunteers()), 4, "only four volunteers scheduled")
        
    def test_over_scheduling_volunteer(self):
        
        vol = Volunteer(volunteer_id='v001')
        
        # create 5 sessions on the same day, each session with a different student group
        sessions = []
        for i in range(1, 6):
            
            group = StudentGroup('A'+str(i))
            sess = Session(week='week2', day='thursday', session_id='s00'+str(i))
            sess.assign_student_group(group)
            
            sessions.append(sess)
        
        # schedule the volunteer for all sessions  
        for session in sessions:
            session.schedule_volunteer(vol)
            
        
        self.assertEqual(len(vol.get_schedule()['thursday']['week2']), 4, "only four of the five sessions are scheduled")
        
    def test_scheduling_unalvailable_volunteer(self):
        
        vol = Volunteer(volunteer_id='v001')
        vol.availability['tuesday']['week2'] = 0 # set as not available
        
        # create a session
        group = StudentGroup('A')
        sess = Session(week='week2', day='tuesday', session_id='s001')
        sess.assign_student_group(group)
        
        #schedule volunteer
        sess.schedule_volunteer(vol)
        
        self.assertEqual(vol.schedule['tuesday']['week2'], [], "volunteer is not scheduled for the session")
        self.assertEqual(sess.get_scheduled_volunteers(), [], "volunteer is not added to list of scheduled volunteers")
        

        
