'''
Author: Brian Mukeswe
Date: September 30, 2019
Contact: mukeswebrian@yahoo.com

This class defines a student group that can be assigned to a session
'''
class StudentGroup():
    
    def __init__(self, group_id):
        
        self.group_id = group_id
        
    def get_id(self):
        return self.group_id
