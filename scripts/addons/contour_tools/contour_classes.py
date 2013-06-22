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
        self.shift = 0
        
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
                
                return self.plane_pt
            
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
                
            else:
                self.plane_pt = None
                self.seed_face_index = None
                self.verts = []
                self.verts_simple = []
                print('aim better')
                
            return self.plane_pt
            
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
        
    def simplify_cross(self,segments):
        if self.verts !=[] and self.eds != []:
            [self.verts_simple, self.eds_simple] = contour_utilities.space_evenly_on_path(self.verts, self.eds, segments, self.shift)
        
    def analyze_relationship(self, other,debug = False):
        '''
        runs a series of quantitative assemsents of the spatial relationship
        to another cut line to assist in anticipating the the optimized
        connectivity data
        
        assume the other cutline has already been solidified and the only variation
        which can happen is on this line
        '''
        #requirements
        # both loops must have a verts simple
        
        
        #caclulate the center of mass of each loop using existing
        #verts simple since they are evenly spaced it will be a
        #good example
        COM_other = contour_utilities.get_com(other.verts_simple)
        COM_self = contour_utilities.get_com(self.verts_simple)
        
        #the vector pointing from the COM of the other cutline
        #to this cutline.  This will be our convention for
        #positive direciton
        delta_com_vect = COM_self - COM_other  
        #delta_com_vect.normalize()
        
        #the plane normals
        self_no = self.plane_no.copy()
        other_no = other.plane_no.copy()
        
        #if for some reason they aren't normalized...fix that
        self_no.normalize()
        other_no.normalize()
        
        #make sure the other normal is aligned with
        #the line from other to self for convention
        if other_no.dot(delta_com_vect) < 0:
            other_no = -1 * other_no
            
        #and now finally make the self normal is aligned too    
        if self_no.dot(other_no) < 0:
            self_no = -1 * self_no
        
        #how parallel are the loops?
        parallelism = self_no.dot(other_no)
        if debug > 1:
            print('loop paralellism = %f' % parallelism)
        
        #this may be important.
        avg_no = self_no.lerp(other_no, 0.5)
        
        #are the loops aimed at one another?
        #compare the delta COM vector to each normal
        self_aimed_other = self_no.dot(delta_com_vect.normalized())
        other_aimed_self = other_no.dot(delta_com_vect.normalized())
        
        aiming_difference = self_aimed_other - other_aimed_self
        if debug > 1:
            print('aiming difference = %f' % aiming_difference)
        #do we expect divergence or convergence?
        #remember other -> self is positive so enlarging
        #while traveling in this direction is divergence
        radi_self = contour_utilities.approx_radius(self.verts_simple, COM_self)
        radi_other = contour_utilities.approx_radius(other.verts_simple, COM_other)
        
        #if divergent or convergent....we will want to maximize
        #the opposite phenomenon with respect to the individual
        #connectors and teh delta COM line
        divergent = (radi_self - radi_other) > 0
        divergence = (radi_self - radi_other)**2 / ((radi_self - radi_other)**2 + delta_com_vect.length**2)
        divergence = math.pow(divergence, 0.5)
        if debug > 1:
            print('the loops are divergent: ' + str(divergent) + ' with a divergence of: ' + str(divergence))
        
        return [COM_self, delta_com_vect, divergent, divergence]
        
    def connectivity_analysis(self,other):
        
        bulk_props = self.analyze_relationship(other)
        COM_self = bulk_props[0]
        
        delta_com_vect = bulk_props[1]
        delta_com_vect.normalize()
        
        divergent = bulk_props[2]
        divergence = bulk_props[3]
        
        ideal_to_com = 0
        for i, v in enumerate(self.verts_simple):
            connector = v - other.verts_simple[i]
            connector.normalize()
            align = connector.dot(delta_com_vect)
            #this shouldnt happen but it appears to be...shrug
            if align < 0:
                print('damn reverse!')
                align *= -1    
            ideal_to_com += align
        
        ideal_to_com = 1/len(self.verts_simple) * ideal_to_com
        print(ideal_to_com)
        return ideal_to_com
    
    
    def align_to_other(self,other, auto_align = True):
        
        '''
        Modifies vert order of self to  provide best
        bridge between self verts and other loop
        
        '''
        verts_1 = other.verts_simple
        verts_2 = self.verts_simple
        
        eds_1 = other.eds_simple
        eds_2 = self.eds_simple
        
        
        print('testing alignment')
        if 0 in eds_1[-1]:
            cyclic = True
            print('cyclic vert chain')
        else:
            cyclic = False
        
        if len(verts_1) != len(self.verts_simple):
            print(len(verts_1))
            print(len(self.verts_simple))
            print('non uniform loops, stopping until your developer gets smarter')
            return
        
        
        #turns out, sum of diagonals is > than semi perimeter
        #lets exploit this (only true if quad is pretty much flat)
        #if we have paths reversed...our indices will give us diagonals
        #instead of perimeter
        #D1_O = verts_2[0] - verts_1[0]
        #D2_O = verts_2[-1] - verts_1[-1]
        #D1_R = verts_2[0] - verts_1[-1]
        #D2_R = verts_2[-1] - verts_1[0]
                
        #original_length = D1_O.length + D2_O.length
        #reverse_length = D1_R.length + D2_R.length
        #if reverse_length < original_length:
            #verts_2.reverse()
            #print('reversing')
            
        if cyclic:
            #another test to verify loop direction is to take
            #something reminiscint of the curl
            #since the loops in our case are guaranteed planar
            #(they come from cross sections) we can find a direction
            #from which to take the curl pretty easily.  Apologies to
            #any real mathemeticians reading this becuase I just
            #bastardized all these math terms.
            V1_0 = verts_1[1] - verts_1[0]
            V1_1 = verts_1[2] - verts_1[1]
            
            V2_0 = self.verts_simple[1] - self.verts_simple[0]
            V2_1 = self.verts_simple[2] - self.verts_simple[1]
            
            no_1 = V1_0.cross(V1_1)
            no_1.normalize()
            no_2 = V2_0.cross(V2_1)
            no_2.normalize()
            
            #we have no idea which way we will get
            #so just pick the directions which are
            #pointed in the general same direction
            if no_1.dot(no_2) < 0:
                no_2 = -1 * no_2
            
            #average the two directions    
            ideal_direction = no_1.lerp(no_1,.5)
        
            curl_1 = contour_utilities.discrete_curl(verts_1, ideal_direction)
            curl_2 = contour_utilities.discrete_curl(self.verts_simple, ideal_direction)
            
            if curl_1 * curl_2 < 0:
                print('reversing loop 2')
                print('curl1: %f and curl2: %f' % (curl_1,curl_2))
                self.verts_simple.reverse()
                print('reversing the base loops too...risky? I live dangerously')
                self.verts.reverse()
                self.shift *= -1
                
        
        else:
            #if the segement is not cyclic
            #all we have to do is compare the endpoints
            Vtotal_1 = verts_1[-1] - verts_1[0]
            Vtotal_2 = self.verts_simple[-1] - self.verts_simple[0]
    
            if Vtotal_1.dot(Vtotal_2) < 0:
                print('reversing path 2')
                self.verts_simple.reverse()
                self.verts.reverse()
                
        #iterate all verts and "handshake problem" them
        #into a dictionary?  That's not very effecient!
        edge_len_dict = {}
        for i in range(0,len(verts_1)):
            for n in range(0,len(self.verts_simple)):
                edge = (i,n)
                vect = self.verts_simple[n] - verts_1[i]
                edge_len_dict[edge] = vect.length
        
        shift_lengths = []
        #shift_cross = []
        for shift in range(0,len(self.verts_simple)):
            tmp_len = 0
            #tmp_cross = 0
            for i in range(0, len(self.verts_simple)):
                shift_mod = int(math.fmod(i+shift, len(self.verts_simple)))
                tmp_len += edge_len_dict[(i,shift_mod)]
            shift_lengths.append(tmp_len)
               
        final_shift = shift_lengths.index(min(shift_lengths))
        if final_shift != 0:
            print("shifting verts by %i segments" % final_shift)
            self.verts_simple = contour_utilities.list_shift(self.verts_simple, final_shift)
        
        self.connectivity_analysis(other)
        
        if auto_align and cyclic:
            alignment_quality = self.connectivity_analysis(other)
            pct_change = 1
            left_bound = -1
            right_bound = 1
            iterations = 0
            while pct_change > 0.001 and iterations < 50:
                print('###########################################')
                iterations += 1
                width = right_bound - left_bound
                
                self.shift = 0.5 * (left_bound + right_bound)
                self.simplify_cross(len(self.eds_simple))
                alignment_quality = self.connectivity_analysis(other)
                
                self.shift = left_bound
                self.simplify_cross(len(self.eds_simple))
                alignment_quality_left = self.connectivity_analysis(other)
                
                self.shift = right_bound
                self.simplify_cross(len(self.eds_simple))
                alignment_quality_right = self.connectivity_analysis(other)
                
                if alignment_quality_left < alignment_quality and alignment_quality_right < alignment_quality:
                    print('midde')
                    left_bound += width*1/4
                    right_bound -= width*1/4
                    pct_change = (right_bound - left_bound)/2
                    
                elif alignment_quality_left > alignment_quality and alignment_quality_right > alignment_quality:
                    print('edges')
                    if alignment_quality_right > alignment_quality_left:
                        left_bound = right_bound - 0.5 * width
                    else:
                        right_bound = left_bound + 0.5 * width
                    
                    pct_change = (right_bound - left_bound)/2
                    
                elif alignment_quality_left < alignment_quality and alignment_quality_right > alignment_quality:
                    print('move to the right')
                    #right becomes the new middle
                    right_bound += width * 1/4
                    left_bound += width * 3/4
                    pct_change = pct_change = (right_bound - left_bound)/2
                    alignment_quality = alignment_quality_right
            
                elif alignment_quality_left > alignment_quality and alignment_quality_right < alignment_quality:
                    print('move to the left')
                    #right becomes the new middle
                    right_bound -= width * 3/4
                    left_bound -= width * 1/4
                    pct_change = pct_change = (right_bound - left_bound)/2
                    
                print('pct change iteration %i was %f' % (iterations, pct_change))
                print(alignment_quality)
                print(alignment_quality_left)
                print(alignment_quality_right)
            print('converged or didnt in %i iterations' % iterations)
              
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