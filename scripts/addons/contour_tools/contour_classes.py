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
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bpy_extras.view3d_utils import region_2d_to_vector_3d
from bpy_extras.view3d_utils import region_2d_to_location_3d
import blf
#from development.contour_tools import contour_utilities

class ContourControlPoint(object):
    
    def __init__(self, parent, x, y, color = (1,0,0,1), size = 2, mouse_radius=10):
        self.x = x
        self.y = y
        self.world_position = None #to be updated later
        self.color = color
        self.size = size
        self.mouse_rad = mouse_radius
        self.parent = parent
        
    def mouse_over(self,x,y):
        dist = (self.x -x)**2 + (self.y - y)**2
        #print(dist < 100)
        if dist < 100:
            return True
        else:
            return False
        
    def screen_from_world(self,context):
        point = location_3d_to_region_2d(context.region, context.space_data.region_3d,self.world_position)
        self.x = point[0]
        self.y = point[1]
        
    def screen_to_world(self,context):
        region = context.region  
        rv3d = context.space_data.region_3d
        if self.world_position:
            self.world_position = region_2d_to_location_3d(region, rv3d, (self.x, self.y),self.world_position)
        
class ContourCutLine(object): 
    
    def __init__(self, x, y, view_dir):
        self.head = ContourControlPoint(self,x,y, color = (1,0,0,1))
        self.tail = ContourControlPoint(self,x,y, color = (0,1,0,1))
        self.plane_tan = ContourControlPoint(self,x,y, color = (.8,.8,.8,1))
        self.view_dir = view_dir  #this is imporatnt...no reason contours cant bend
        self.target = None
        self.depth = None #perhaps we need a depth value? 
        self.updated = False
        self.plane_pt = None
        self.plane_no = None
        self.seed_face_index = None
        self.verts = []
        self.verts_simple = []
        self.eds_simple = []
        self.edges = []
        
    def draw(self,context, settings):
        '''
        setings are the addon preferences for contour tools
        '''
        
        debug = settings.debug
        #settings = context.user_preferences.addons['contour_tools'].preferences
        
        #this should be moved to only happen if the view changes :-/  I'ts only
        #a few hundred calcs even with a lot of lines. Waste not want not.
        if self.head.world_position:
            self.head.screen_from_world(context)
        if self.tail.world_position:
            self.tail.screen_from_world(context)
        if self.plane_tan.world_position:
            self.plane_tan.screen_from_world(context)
            
        
        #draw connecting line
        points = [(self.head.x,self.head.y),(self.tail.x,self.tail.y)]
        if settings.show_edges:
            contour_utilities.draw_polyline_from_points(context, points, (0,.2,1,1), settings.line_thick, "GL_LINE_STIPPLE")
        
        #draw the two handles
        contour_utilities.draw_points(context, points, self.head.color, settings.handle_size)
        
        #draw the current plane point and the handle to change plane orientation
        if self.plane_pt:
            point1 = location_3d_to_region_2d(context.region, context.space_data.region_3d, self.plane_pt)
            point2 = (self.plane_tan.x, self.plane_tan.y)
            if settings.show_edges:
                contour_utilities.draw_polyline_from_points(context, [point1,point2], (0,.2,1,1), settings.line_thick, "GL_LINE_STIPPLE")
            contour_utilities.draw_points(context, [point2], self.plane_tan.color, settings.handle_size)
            contour_utilities.draw_points(context, [point1], self.head.color, settings.handle_size)
        
        #draw the raw contour vertices
        if (self.verts and self.verts_simple == []) or (debug > 0 and settings.show_verts):
            contour_utilities.draw_3d_points(context, self.verts, (0,1,.2,1), settings.raw_vert_size)
        
        #draw the simplified contour vertices and edges (rings)    
        if self.verts_simple:
            points = self.verts_simple.copy()
            if 0 in self.eds[-1]:
                points.append(self.verts_simple[0])
            
            if settings.show_ring_edges:
                contour_utilities.draw_polyline_from_3dpoints(context, points, (0,1,.2,1), settings.line_thick,"GL_LINE_STIPPLE")
            contour_utilities.draw_3d_points(context, self.verts_simple, (0,.2,1,1), settings.vert_size)
            if debug:
                if settings.vert_inds:
                    for i, point in enumerate(self.verts):
                        loc = location_3d_to_region_2d(context.region, context.space_data.region_3d, point)
                        blf.position(0, loc[0], loc[1], 0)
                        blf.draw(0, str(i))
                    
                if settings.simple_vert_inds:    
                    for i, point in enumerate(self.verts_simple):
                        loc = location_3d_to_region_2d(context.region, context.space_data.region_3d, point)
                        blf.position(0, loc[0], loc[1], 0)
                        blf.draw(0, str(i))
        #draw contour points? later
    
    def hit_object(self,context, ob, update_normal = True, method = 'VIEW'):
        region = context.region  
        rv3d = context.space_data.region_3d
        
        pers_mx = rv3d.perspective_matrix  #we need the perspective matrix
        inv_persx_mx = pers_mx.inverted() #and we need to invert it...for some reason    
        pos = rv3d.view_location
        
        #midpoint of the  cutline and world direction of cutline
        screen_coord = (self.head.x + self.tail.x)/2, (self.head.y + self.tail.y)/2
        
        view_x = rv3d.view_rotation * Vector((1,0,0))
        view_y = rv3d.view_rotation * Vector((0,1,0))
        view_z = rv3d.view_rotation * Vector((0,0,1))
        cut_vec = (self.tail.x - self.head.x)*view_x + (self.tail.y - self.head.y)*view_y
        cut_vec.normalize()
        
        if update_normal:
            if method == 'VIEW':
                self.plane_no = cut_vec.cross(view_z).normalized()
        
        
                vec = region_2d_to_vector_3d(region, rv3d, screen_coord)
                loc = region_2d_to_location_3d(region, rv3d, screen_coord, vec)
        
                #raycast what I think is the ray onto the object
                #raycast needs to be in ob coordinates.
                a = loc + 3000*vec
                b = loc - 3000*vec
    
                mx = ob.matrix_world
                imx = mx.inverted()
                hit = ob.ray_cast(imx*a, imx*b)    
        
                if hit[2] != -1:
                    self.plane_pt = mx * hit[0]
                    self.seed_face_index = hit[2]
                    print(hit[2])
                    self.head.world_position = region_2d_to_location_3d(region, rv3d, (self.head.x, self.head.y), mx * hit[0])
                    self.tail.world_position = region_2d_to_location_3d(region, rv3d, (self.tail.x, self.tail.y), mx * hit[0])
                    self.plane_tan.world_position = self.plane_pt + (self.head.world_position - self.tail.world_position).length/4 * view_z
                    
                else:
                    self.plane_pt = None
                    self.seed_face_index = None
                    self.verts = []
                    self.verts_simple = []
            
        elif method == 'HANDLE':
            
            #the midpoint between the two vectors
            b = .5 * (self.head.world_position + self.tail.world_position)
            a = self.plane_tan.world_position
            
            z = a - b
            x = self.head.world_position - self.tail.world_position
            self.plane_no = z.cross(x).normalized()
            
            mx = ob.matrix_world
            imx = mx.inverted() 
            hit = ob.ray_cast(imx * (a + 5 * z), imx * (b - 5 * z))
            if hit[2] != -1:
                self.plane_pt = mx * hit[0]
                self.seed_face_index = hit[2]
                
                self.head.world_position = self.plane_pt + .5*x
                self.tail.world_position = self.plane_pt - .5*x
                
                print(self.plane_no)
            else:
                self.plane_pt = None
                self.seed_face_index = None
                self.verts = []
                self.verts_simple = []
                print('aim better')
            
    def handles_to_screen(self,context):
        
        region = context.region  
        rv3d = context.space_data.region_3d
        
        
        self.head.world_position = region_2d_to_location_3d(region, rv3d, (self.head.x, self.head.y),self.plane_pt)
        self.tail.world_position = region_2d_to_location_3d(region, rv3d, (self.tail.x, self.tail.y),self.plane_pt)
        
          
    def cut_object(self,context, ob, bme):
        
        mx = ob.matrix_world
        pt = self.plane_pt
        pno = self.plane_no
        if pt and pno:
            cross = contour_utilities.cross_section_seed(bme, mx, pt, pno, self.seed_face_index, debug = True)   
            if cross:
                self.verts = [mx*v for v in cross[0]]
                self.eds = cross[1]
        else:
            self.verts = []
            self.eds = []
            print('no hit! aim better')
        
    def simplify_cross(self,segments, shift = 0):
        if self.verts !=[] and self.eds != []:
            [self.verts_simple, self.eds_simple] = contour_utilities.space_evenly_on_path(self.verts, self.eds, segments, shift)
        
          
    def active_element(self,context,x,y):
        active_head = self.head.mouse_over(x, y)
        active_tail = self.tail.mouse_over(x, y)
        active_tan = self.plane_tan.mouse_over(x, y)
        
        mouse_loc = Vector((x,y,0))
        head_loc = Vector((self.head.x, self.head.y, 0))
        tail_loc = Vector((self.tail.x, self.tail.y, 0))
        intersect = intersect_point_line(mouse_loc, head_loc, tail_loc)
        
        dist = (intersect[0] - mouse_loc).length_squared
        bound = intersect[1]
        active_self = (dist < 100) and (bound < 1) and (bound > 0) #TODO:  make this a sensitivity setting
        
        if active_head and active_tail and active_self: #they are all clustered together
            #print('returning head but tail too')
            return self.head
        
        elif active_tail:
            #print('returning tail')
            return self.tail
        
        elif active_head:
            #print('returning head')
            return self.head
        
        elif active_tan:
            return self.plane_tan
        
        elif active_self:
            #print('returning line')
            return self
        
        else:
            #print('returning None')
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