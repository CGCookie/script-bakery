'''
Created on Apr 23, 2013

@author: Patrick
'''

####class definitions####

import bpy
import math
from mathutils import Vector
from mathutils.geometry import intersect_point_line
import contour_utilities

class ContourControlPoint(object):
    
    def __init__(self, x, y, color = (1,0,0,1), size = 2, mouse_radius=10):
        self.x = x
        self.y = y
        self.world_position = Vector((0,0,0)) #to be updated later
        self.color = color
        self.size = size
        self.mouse_rad = mouse_radius
        
    def mouse_over(self,x,y):
        dist = (self.x -x)**2 + (self.y - y)**2
        print(dist < 100)
        if dist < 100:
            return True
        else:
            return False

    
class ContourCutLine(object): 
    
    def __init__(self, x, y, view_dir):
        self.head = ContourControlPoint(x,y, color = (1,0,0,1))
        self.tail = ContourControlPoint(x,y, color = (0,1,0,1))
        self.view_dir = view_dir  #this is imporatnt...no reason contours cant bend
        self.target = None
        self.depth = None #perhaps we need a depth value? 
        
    def draw(self,context):
        
        #draw connecting line
        points = [(self.head.x,self.head.y),(self.tail.x,self.tail.y)]
        contour_utilities.draw_polyline_from_points(context, points, (0,.5,1,1), 1, "GL_LINE_STIPPLE")
        #draw head #draw tail
        contour_utilities.draw_points(context, points, (1,0,.2,1), 5)
        #draw contour points? later
    
    def active_element(self,context,x,y):
        active_head = self.head.mouse_over(x, y)
        active_tail = self.tail.mouse_over(x, y)
        
        mouse_loc = Vector((x,y,0))
        head_loc = Vector((self.head.x, self.head.y, 0))
        tail_loc = Vector((self.tail.x, self.tail.y, 0))
        intersect = intersect_point_line(mouse_loc, head_loc, tail_loc)
        
        dist = (intersect[0] - mouse_loc).length_squared
        bound = intersect[1]
        active_self = (dist < 100) and (bound < 1) and (bound > 0) #TODO:  make this a sensitivity setting
        
        if active_head and active_tail and active_self: #they are all clustered together
            print('returning head but tail too')
            return self.head
        
        elif active_tail:
            print('returning tail')
            return self.tail
        
        elif active_head:
            print('returning head')
            return self.head
        
        elif active_self:
            print('returning line')
            return self
        
        else:
            print('returning None')
            return None
#cut line, a user interactive 2d line which represents a plane in 3d splace
    #head (type conrol point)
    #tail (type control points)
    #target mesh
    #view_direction (crossed with line to make plane normal for slicing)
    
    #draw method
    
    #new control point project method
    
    #mouse hover line calc
    
    
#retopo object, surface
    #colelction of cut lines
    #collection of countours to loft
    
    #n rings (crosses borrowed from looptools)
    #n follows (borrowed from looptools and or bsurfaces)
    
    #method contours from cutlines
    
    #method bridge contours