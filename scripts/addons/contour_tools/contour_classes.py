'''
Created on Apr 23, 2013

@author: Patrick
'''

####class definitions####

import bpy
import math
from mathutils import Vector, Quaternion
from mathutils.geometry import intersect_point_line, intersect_line_plane
import contour_utilities
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bpy_extras.view3d_utils import region_2d_to_vector_3d
from bpy_extras.view3d_utils import region_2d_to_location_3d
import blf
#from development.contour_tools import contour_utilities

class ContourControlPoint(object):
    
    def __init__(self, parent, x, y, color = (1,0,0,1), size = 2, mouse_radius=10):
        self.desc = 'CONTROL_POINT'
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

class ExistingVertList(object):
    def __init__(self, verts, edges, mx):
        self.desc = 'EXISTING_VERT_LIST'
        
        edge_keys = [[ed.verts[0].index, ed.verts[1].index] for ed in edges]
        remaining_keys = [i for i in range(1,len(edge_keys))]
        
        vert_inds_unsorted = [vert.index for vert in verts]
        vert_inds_sorted = [edge_keys[0][0], edge_keys[0][1]]
        
        iterations = 0
        max_iters = math.factorial(len(remaining_keys))
        while len(remaining_keys) > 0 and iterations < max_iters:
            print(remaining_keys)
            iterations += 1
            for key_index in remaining_keys:
                l = len(vert_inds_sorted) -1
                key_set = set(edge_keys[key_index])
                last_v = {vert_inds_sorted[l]}
                if  key_set & last_v:
                    vert_inds_sorted.append(int(list(key_set - last_v)[0]))
                    remaining_keys.remove(key_index)
                    break
        
        if vert_inds_sorted[0] == vert_inds_sorted[-1]:
            cyclic = True
            vert_inds_sorted.pop()
        else:
            cyclic = False
            
        self.eds_simple = [[i,i+1] for i in range(0,len(vert_inds_sorted)-1)]
        if cyclic:
            self.eds_simple.append([len(vert_inds_sorted)-1,0])
            
        self.verts_simple = []
        for i in vert_inds_sorted:
            v = verts[vert_inds_unsorted.index(i)]
            self.verts_simple.append(mx * v.co)
        
            
class ContourCutLine(object): 
    
    def __init__(self, x, y, line_width = 3,
                 line_color = (0,0,1,1), 
                 handle_color = (1,0,0,1),
                 geom_color = (0,1,0,1),
                 vert_color = (0,.2,1,1)):
        
        self.desc = "CUT_LINE"
        self.head = ContourControlPoint(self,x,y, color = handle_color)
        self.tail = ContourControlPoint(self,x,y, color = handle_color)
        #self.plane_tan = ContourControlPoint(self,x,y, color = (.8,.8,.8,1))
        #self.view_dir = view_dir
        self.target = None
 
        self.updated = False
        self.plane_pt = None  #this will be a point on an object surface...calced after ray_casting
        self.plane_com = None  #this will be a point in the object interior, calced after cutting a contour
        self.plane_no = None
        
        #these points will define two orthogonal vectors
        #which lie tangent to the plane...which we can use
        #to draw a little widget on the COM
        self.plane_x = None
        self.plane_y = None
        self.plane_z = None
        
        self.vec_x = None
        self.vec_y = None
        #self.vec_z is the plane normal
        
        self.seed_face_index = None
        
        #high res coss section
        #@ resolution of original mesh
        self.verts = []
        self.verts_screen = []
        self.edges = []
        #low res derived contour
        self.verts_simple = []
        self.eds_simple = []
        
        #screen cache for fast selection
        self.verts_simple_screen = []
        
        #variable used to shift loop beginning on high res loop
        self.shift = 0
        
        #visual stuff
        self.line_width = line_width
        self.line_color = line_color
        self.geom_color = geom_color
        self.vert_color = vert_color
        
    def update_screen_coords(self,context):
        self.verts_screen = [location_3d_to_region_2d(context.region, context.space_data.region_3d, loc) for loc in self.verts]
        self.verts_simple_screen = [location_3d_to_region_2d(context.region, context.space_data.region_3d, loc) for loc in self.verts_simple]
        
          
    def draw(self,context, settings, three_dimensional = True, interacting = False):
        '''
        setings are the addon preferences for contour tools
        '''
        
        debug = settings.debug
        #settings = context.user_preferences.addons['contour_tools'].preferences
        
        #this should be moved to only happen if the view changes :-/  I'ts only
        #a few hundred calcs even with a lot of lines. Waste not want not.
        if self.head and self.head.world_position:
            self.head.screen_from_world(context)
        if self.tail and self.tail.world_position:
            self.tail.screen_from_world(context)
        #if self.plane_tan.world_position:
            #self.plane_tan.screen_from_world(context)
            
        if debug > 1:
            if self.plane_com:
                com_2d = location_3d_to_region_2d(context.region, context.space_data.region_3d, self.plane_com)
                
                contour_utilities.draw_3d_points(context, [self.plane_com], (0,1,0,1), 4)
                if self.vec_x:
                    pt_x = location_3d_to_region_2d(context.region, context.space_data.region_3d, self.plane_com + self.vec_x)
                    screen_vec_x = pt_x - com_2d
                    screen_pt_x = com_2d + 40 * screen_vec_x.normalized()
                    contour_utilities.draw_points(context, [pt_x], (1,1,0,1), 6)
                    
                if self.vec_y:
                    pt_y = location_3d_to_region_2d(context.region, context.space_data.region_3d, self.plane_com + self.vec_y)
                    screen_vec_y = pt_y - com_2d
                    screen_pt_y = com_2d + 40 * screen_vec_y.normalized()
                    contour_utilities.draw_points(context, [pt_y], (0,1,1,1), 6)

                if self.plane_no:
                    pt_z = location_3d_to_region_2d(context.region, context.space_data.region_3d, self.plane_com + self.plane_no)
                    screen_vec_z = pt_z - com_2d
                    screen_pt_z = com_2d + 40 * screen_vec_z.normalized()
                    contour_utilities.draw_points(context, [pt_z], (1,0,1,1), 6)
                    
        
        #draw connecting line
        if self.head:
            points = [(self.head.x,self.head.y),(self.tail.x,self.tail.y)]
            
            contour_utilities.draw_polyline_from_points(context, points, (0,.2,1,1), settings.stroke_thick, "GL_LINE_STIPPLE")
        
            #draw the two handles
            contour_utilities.draw_points(context, points, self.head.color, settings.handle_size)
        
        #draw the current plane point and the handle to change plane orientation
        #if self.plane_pt and settings.draw_widget:
            #point1 = location_3d_to_region_2d(context.region, context.space_data.region_3d, self.plane_pt)
            #point2 = (self.plane_tan.x, self.plane_tan.y)

            #contour_utilities.draw_polyline_from_points(context, [point1,point2], (0,.2,1,1), settings.stroke_thick, "GL_LINE_STIPPLE")
            #contour_utilities.draw_points(context, [point2], self.plane_tan.color, settings.handle_size)
            #contour_utilities.draw_points(context, [point1], self.head.color, settings.handle_size)
        
        #draw the raw contour vertices
        if (self.verts and self.verts_simple == []) or (debug > 0 and settings.show_verts):
            
            if three_dimensional:
                
                contour_utilities.draw_3d_points(context, self.verts, self.vert_color, settings.raw_vert_size)
            else:    
                contour_utilities.draw_points(context, self.verts_screen, self.vert_color, settings.raw_vert_size)
        
        #draw the simplified contour vertices and edges (rings)    
        if self.verts !=[] and self.eds != []:
            if three_dimensional:
                points = self.verts_simple.copy()
            else:
                points = self.verts_simple_screen.copy()
               
            if 0 in self.eds[-1]:
                points.append(points[0])
            #draw the ring
            #draw the points over it
            if settings.show_ring_edges:
                if three_dimensional:
                    contour_utilities.draw_polyline_from_3dpoints(context, points, self.geom_color, settings.line_thick,"GL_LINE_STIPPLE")
                    if not interacting:
                        contour_utilities.draw_3d_points(context, points, self.vert_color, settings.vert_size)
                else:
                    contour_utilities.draw_polyline_from_points(context, points, self.geom_color, settings.line_thick,"GL_LINE_STIPPLE")
                    if not interacting:
                        contour_utilities.draw_points(context,points, self.vert_color, settings.vert_size)
                
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
    
    def hit_object(self, context, ob, method = 'VIEW'):
        settings = context.user_preferences.addons['contour_tools'].preferences
        region = context.region  
        rv3d = context.space_data.region_3d
        
        pers_mx = rv3d.perspective_matrix  #we need the perspective matrix
        
        #the world direction vectors associated with
        #the view rotations
        view_x = rv3d.view_rotation * Vector((1,0,0))
        view_y = rv3d.view_rotation * Vector((0,1,0))
        view_z = rv3d.view_rotation * Vector((0,0,1))
        
        
        #this only happens on the first time.
        #after which everything is handled by
        #the widget
        if method == 'VIEW':
            #midpoint of the  cutline and world direction of cutline
            screen_coord = (self.head.x + self.tail.x)/2, (self.head.y + self.tail.y)/2
            cut_vec = (self.tail.x - self.head.x)*view_x + (self.tail.y - self.head.y)*view_y
            cut_vec.normalize()
            self.plane_no = cut_vec.cross(view_z).normalized()
            
            #we need to populate the 3 axis vectors
            self.vec_x = -1 * cut_vec.normalized()
            self.vec_y = self.plane_no.cross(self.vec_x)
            

    
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
                self.head.world_position = region_2d_to_location_3d(region, rv3d, (self.head.x, self.head.y), mx * hit[0])
                self.tail.world_position = region_2d_to_location_3d(region, rv3d, (self.tail.x, self.tail.y), mx * hit[0])
                
                self.plane_pt = mx * hit[0]
                self.seed_face_index = hit[2]

                if settings.use_perspective:
                    
                    cut_vec = self.head.world_position - self.tail.world_position
                    cut_vec.normalize()
                    self.plane_no = cut_vec.cross(vec).normalized()
                    self.vec_x = -1 * cut_vec.normalized()
                    self.vec_y = self.plane_no.cross(self.vec_x)
                    

                    
                self.plane_x = self.plane_pt + self.vec_x
                self.plane_y = self.plane_pt + self.vec_y
                self.plane_z = self.plane_pt + self.plane_no
                    
                                #we need to populate the 3 axis vectors
            
            

                #self.plane_tan.world_position = self.plane_pt + self.vec_y
                
                
                
            else:
                self.plane_pt = None
                self.seed_face_index = None
                self.verts = []
                self.verts_simple = []
            
            return self.plane_pt
        
        elif method in {'3_AXIS_COM','3_AXIS_POINT'}:
            mx = ob.matrix_world
            imx = mx.inverted()
            y = self.vec_y
            x = self.vec_x
                  
            if method == '3_AXIS_COM':
                
                if not self.plane_com:
                    print('failed no COM')
                    return
                pt = self.plane_com


                
            else:
                if not self.plane_pt:
                    print('failed no COM')
                    return
                pt = self.plane_pt
                
            hits = [ob.ray_cast(imx * pt, imx * (pt + 5 * y)),
                    ob.ray_cast(imx * pt, imx * (pt + 5 * x)),
                    ob.ray_cast(imx * pt, imx * (pt - 5 * y)),
                    ob.ray_cast(imx * pt, imx * (pt - 5 * x))]
            

            dists = []
            inds = []
            for i, hit in enumerate(hits):
                if hit[2] != -1:
                    R = pt - hit[0]
                    dists.append(R.length)
                    inds.append(i)
            
            #make sure we had some hits!
            if any(dists):
                #pick the best one as the closest one to the pt       
                best_hit = hits[inds[dists.index(min(dists))]]       
                self.plane_pt = mx * best_hit[0]
                self.seed_face_index = best_hit[2]
                
                
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
        indx = self.seed_face_index
        if pt and pno:
            cross = contour_utilities.cross_section_seed(bme, mx, pt, pno, indx, debug = True)   
            if cross:
                self.verts = [mx*v for v in cross[0]]
                self.eds = cross[1]
                
        else:
            self.verts = []
            self.eds = []
        
    def simplify_cross(self,segments):
        if self.verts !=[] and self.eds != []:
            [self.verts_simple, self.eds_simple] = contour_utilities.space_evenly_on_path(self.verts, self.eds, segments, self.shift)
            
    def update_com(self):
        if self.verts_simple != []:
            self.plane_com = contour_utilities.get_com(self.verts_simple)
        else:
            self.plane_com = None
                
    def derive_3_axis_control(self, method = 'FROM_VECS', n=0):
        '''
        args
        
        method: text enum in {'VIEW','FROM_VECS','FROM_VERT'}
        '''
        
        if len(self.verts_simple) and self.plane_com:

            
            #y vector
            y_vector = self.verts_simple[n] - self.plane_com
            y_vector.normalize()
            self.vec_y = y_vector
            
            #x vector
            x_vector = y_vector.cross(self.plane_no)
            x_vector.normalize()
            self.vec_x = x_vector
            
            
            #now the 4 points are in world space
            #we could use a vector...but transforming
            #to screen can be tricky with vectors as
            #opposed to locations.
            self.plane_x = self.plane_com + x_vector
            self.plane_y = self.plane_com + y_vector
            self.plane_z = self.plane_com + self.plane_no
            
            
            
        
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
        
        
        COM_self = contour_utilities.get_com(self.verts_simple)
        COM_other = contour_utilities.get_com(other.verts_simple)
        delta_com_vect = COM_self - COM_other  #final - initial :: self - other
        delta_com_vect.normalize()
        

        
        ideal_to_com = 0
        for i, v in enumerate(self.verts_simple):
            connector = v - other.verts_simple[i]  #continue convention of final - initial :: self - other
            connector.normalize()
            align = connector.dot(delta_com_vect)
            #this shouldnt happen but it appears to be...shrug
            if align < 0:
                print('damn reverse!')
                print(align)
                align *= -1    
            ideal_to_com += align
        
        ideal_to_com = 1/len(self.verts_simple) * ideal_to_com
        
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
            #print(len(verts_1))
            #print(len(self.verts_simple))
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
        if auto_align:
            self.shift = 0
            self.simplify_cross(len(self.eds_simple))
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
            print('pre-shift alignment % f' % self.connectivity_analysis(other))
            print("shifting verts by %i segments" % final_shift)
            self.verts_simple = contour_utilities.list_shift(self.verts_simple, final_shift)
            print('post-shift alignment % f' % self.connectivity_analysis(other))
        
        if auto_align and cyclic:
            alignment_quality = self.connectivity_analysis(other)
            #pct_change = 1
            left_bound = -1
            right_bound = 1
            iterations = 0
            while iterations < 20:
                
                iterations += 1
                width = right_bound - left_bound
                
                self.shift = 0.5 * (left_bound + right_bound)
                self.simplify_cross(len(self.eds_simple)) #TODO not sure this needs to happen here
                self.verts_simple = contour_utilities.list_shift(self.verts_simple, final_shift)
                alignment_quality = self.connectivity_analysis(other)
                
                self.shift = left_bound
                self.simplify_cross(len(self.eds_simple))
                self.verts_simple = contour_utilities.list_shift(self.verts_simple, final_shift)
                alignment_quality_left = self.connectivity_analysis(other)
                
                self.shift = right_bound
                self.simplify_cross(len(self.eds_simple))
                self.verts_simple = contour_utilities.list_shift(self.verts_simple, final_shift)
                alignment_quality_right = self.connectivity_analysis(other)
                
                if alignment_quality_left < alignment_quality and alignment_quality_right < alignment_quality:
                    
                    left_bound += width*1/8
                    right_bound -= width*1/8
                    
                    
                elif alignment_quality_left > alignment_quality and alignment_quality_right > alignment_quality:
                    
                    if alignment_quality_right > alignment_quality_left:
                        left_bound = right_bound - 0.75 * width
                    else:
                        right_bound = left_bound + 0.75* width
                    
                elif alignment_quality_left < alignment_quality and alignment_quality_right > alignment_quality:
                    #print('move to the right')
                    #right becomes the new middle
                    left_bound += width * 1/4
            
                elif alignment_quality_left > alignment_quality and alignment_quality_right < alignment_quality:
                    #print('move to the left')
                    #right becomes the new middle
                    right_bound -= width * 1/4
                    
                    
                #print('pct change iteration %i was %f' % (iterations, pct_change))
                print(alignment_quality)
                #print(alignment_quality_left)
                #print(alignment_quality_right)
            print('converged or didnt in %i iterations' % iterations)
            print('final alignment quality is %f' % alignment_quality)
              
    def active_element(self,context,x,y):
        settings = context.user_preferences.addons['contour_tools'].preferences
        
        if self.head:
            active_head = self.head.mouse_over(x, y)
            active_tail = self.tail.mouse_over(x, y)
        else:
            active_head = False
            active_tail = False
        #active_tan = self.plane_tan.mouse_over(x, y)
        
        

        if len(self.verts_simple):
            mouse_loc = Vector((x,y))
            #Check by testing distance to all edges
            active_self = False
            for ed in self.eds_simple:
                
                a = self.verts_simple_screen[ed[0]]
                b = self.verts_simple_screen[ed[1]]
                intersect = intersect_point_line(mouse_loc, a, b)
        
                dist = (intersect[0] - mouse_loc).length_squared
                bound = intersect[1]
                if (dist < 100) and (bound < 1) and (bound > 0):
                    active_self = True
                    break
            '''
            region = context.region  
            rv3d = context.space_data.region_3d
            vec = region_2d_to_vector_3d(region, rv3d, (x,y))
            loc = region_2d_to_location_3d(region, rv3d, (x,y), vec)
            
            line_a = loc
            line_b = loc + vec
            #ray to plane
            hit = intersect_line_plane(line_a, line_b, self.plane_pt, self.plane_no)
            if hit:
                mouse_in_loop = contour_utilities.point_inside_loop_almost3D(hit, self.verts_simple, self.plane_no, p_pt = self.plane_pt, threshold = .01, debug = False)
                if mouse_in_loop:
                    self.geom_color = (.8,0,.8,0.5)
                    self.line_width = 2.5 * settings.line_thick
                else:
                    self.geom_color = (0,1,0,0.5)
                    self.line_width = settings.line_thick
                
            
        mouse_loc = Vector((x,y,0))
        head_loc = Vector((self.head.x, self.head.y, 0))
        tail_loc = Vector((self.tail.x, self.tail.y, 0))
        intersect = intersect_point_line(mouse_loc, head_loc, tail_loc)
        
        dist = (intersect[0] - mouse_loc).length_squared
        bound = intersect[1]
        active_self = (dist < 100) and (bound < 1) and (bound > 0) #TODO:  make this a sensitivity setting
        '''
        if active_head and active_tail and active_self: #they are all clustered together
            #print('returning head but tail too')
            return self.head
        
        elif active_tail:
            #print('returning tail')
            return self.tail
        
        elif active_head:
            #print('returning head')
            return self.head
        
        #elif active_tan:
            #return self.plane_tan
        
        elif active_self:
            #print('returning line')
            return self
        
        else:
            #print('returning None')
            return None



class CutLineManipulatorWidget(object):
    def __init__(self,context, settings, cut_line,x,y):
        
        self.desc = 'WIDGET'
        self.cut_line = cut_line
        self.x = x
        self.y = y
        
        #this will get set later by interaction
        self.transform = False
        self.transform_mode = None
        
        
        self.color = (settings.widget_color[0], settings.widget_color[1],settings.widget_color[2],1)
        self.color2 = (settings.widget_color2[0], settings.widget_color2[1],settings.widget_color2[2],1)
        self.color3 = (settings.widget_color3[0], settings.widget_color3[1],settings.widget_color3[2],1)
        
        self.radius = settings.widget_radius
        self.inner_radius = settings.widget_radius_inner
        self.line_width = settings.widget_thickness
        self.arrow_size = settings.arrow_size
        
        self.arc_radius = .5 * (self.radius + self.inner_radius)
        self.screen_no = None
        self.angle = 0
        
        #intitial conditions for "undo"
        if self.cut_line.plane_com:
            self.initial_com = self.cut_line.plane_com.copy()
        else:
            self.initial_com = None
            
        if self.cut_line.plane_pt:
            self.initial_plane_pt = self.cut_line.plane_pt.copy()
        else:
            self.initial_plane_pt = None
        
        self.vec_x = self.cut_line.vec_x.copy()
        self.vec_y = self.cut_line.vec_y.copy()
        self.initial_plane_no = self.cut_line.plane_no.copy()
        self.initial_seed = self.cut_line.seed_face_index
        
        self.wedge_1 = []
        self.wedge_2 = []
        self.wedge_3 = []
        self.wedge_4 = []
        
        self.arrow_1 = []
        self.arrow_2 = []
        
        self.arc_arrow_1 = []
        self.arc_arrow_2 = []
        

        
    def user_interaction(self, context, mouse_x,mouse_y):
        '''
        analyse mouse coords x,y
        return [type, transform]
        '''
        
        mouse_vec = Vector((mouse_x,mouse_y))
        self_vec = Vector((self.x,self.y))
        loc_vec = mouse_vec - self_vec
        
        
        region = context.region  
        rv3d = context.space_data.region_3d
        world_mouse = region_2d_to_location_3d(region, rv3d, (mouse_x, mouse_y), self.initial_com)
        world_widget = region_2d_to_location_3d(region, rv3d, (self.x, self.y), self.initial_com)
        
        if not self.transform:
            
            #this represents a switch...since by definition we were not transforming to begin with
            if loc_vec.length > self.inner_radius:
                self.transform = True
                
                #identify which quadrant we are in
                screen_angle = math.atan2(loc_vec[1], loc_vec[0])
                loc_angle = screen_angle - self.angle
                loc_angle = math.fmod(loc_angle + 4 * math.pi, 2 * math.pi)  #correct for any negatives
                
                if loc_angle >= 1/4 * math.pi and loc_angle < 3/4 * math.pi:
                    #we are in the  left quadrant...which is perpendicular
                    self.transform_mode = 'NORMAL_TRANSLATE'
                    
                elif loc_angle >= 3/4 * math.pi and loc_angle < 5/4 * math.pi:
                    self.transform_mode = 'EDGE_PARALLEL'
                
                elif loc_angle >= 5/4 * math.pi and loc_angle < 7/4 * math.pi:
                    self.transform_mode = 'NORMAL_TRANSLATE'
                
                else:
                    self.transform_mode = 'EDGE_PERPENDICULAR'
                    

                print(loc_angle)
                print(self.transform_mode)
                
            return {'DO_NOTHING'}  #this tells it whether to recalc things
            
        else:
            #we were transforming but went back in the circle
            if loc_vec.length < self.inner_radius:
                self.transform = False
                self.transform_mode = None
                
                #reset our initial values
                self.cut_line.plane_com = self.initial_com
                self.cut_line.plane_no = self.initial_plane_no
                self.cut_line.plane_pt = self.initial_plane_pt
                self.cut_line.vec_x = self.vec_x
                self.cut_line.vec_y = self.vec_y
                self.cut_line.seed_face_index = self.initial_seed
                
                
                return {'RECUT'}
                
            
            else:
                
                if self.transform_mode == 'NORMAL_TRANSLATE':
                    print('translating')
                    #the pixel distance used to scale the translation
                    screen_dist = loc_vec.length - self.inner_radius
                    
                    world_vec = world_mouse - world_widget
                    translate = screen_dist/loc_vec.length * world_vec.dot(self.initial_plane_no) * self.initial_plane_no
                    
                    self.cut_line.plane_com = self.initial_com + translate
                    
                    return {'REHIT','RECUT'}
                
                elif self.transform_mode in {'EDGE_PERPENDICULAR', 'EDGE_PARALLEL'}:
                    
                    #establish the transform axes
                    '''
                    screen_com = location_3d_to_region_2d(context.region, context.space_data.region_3d,self.cut_line.plane_com)
                    vertical_screen_vec = Vector((math.cos(self.angle + .5 * math.pi), math.sin(self.angle + .5 * math.pi)))
                    screen_y = screen_com + vertical_screen_vec
                    world_pre_y = region_2d_to_location_3d(region, rv3d, (screen_y[0], screen_y[1]),self.cut_line.plane_com)
                    world_y = world_pre_y - self.cut_line.plane_com
                    world_y_correct = world_y.dot(self.initial_plane_no)
                    world_y = world_y - world_y_correct * self.initial_plane_no
                    world_y.normalize()
                    
                    world_x = self.initial_plane_no.cross(world_y)
                    world_x.normalize()
                    '''
                    
                    axis_1  = rv3d.view_rotation * Vector((0,0,1))
                    axis_1.normalize()
                    
                    axis_2 = self.initial_plane_no.cross(axis_1)
                    axis_2.normalize()
                    
                    #self.cut_line.vec_x = world_x
                    #self.cut_line.vec_y = world_y
                    
                    #self.cut_line.plane_x = self.cut_line.plane_com + 2 * world_x
                    #self.cut_line.plane_y = self.cut_line.plane_com + 2 * world_y
                    #self.cut_line.plane_z = self.cut_line.plane_com + 2 * self.initial_plane_no
                    
                    #identify which quadrant we are in
                    screen_angle = math.atan2(loc_vec[1], loc_vec[0])
                    
                    if self.transform_mode == 'EDGE_PARALLEL':

                        rot_angle = screen_angle - self.angle #+ .5 * math.pi  #Mystery
                        rot_angle = math.fmod(rot_angle + 4 * math.pi, 2 * math.pi)  #correct for any negatives
                        print('rotating by %f' % rot_angle)
                        sin = math.sin(rot_angle/2)
                        cos = math.cos(rot_angle/2)
                        #quat = Quaternion((cos, sin*world_x[0], sin*world_x[1], sin*world_x[2]))
                        quat = Quaternion((cos, sin*axis_1[0], sin*axis_1[1], sin*axis_1[2]))    
                        #rotate around x axis...update y
                        #world_y = new_no.cross(world_x)
                        #new_com = self.initial_com
                        #new_tan = new_com + world_x
                        
                        
                        #self.cut_line.plane_x = self.cut_line.plane_com + 2 * world_x
                        #self.cut_line.plane_y = self.cut_line.plane_com + 2 * world_y
                        #self.cut_line.plane_z = self.cut_line.plane_com + 2 * new_no
                    #self.cut_line.plane_no = new_normal
                    
                    else:
                        rot_angle = screen_angle - self.angle + math.pi #+ .5 * math.pi  #Mystery
                        rot_angle = math.fmod(rot_angle + 4 * math.pi, 2 * math.pi)  #correct for any negatives
                        print('rotating by %f' % rot_angle)
                        sin = math.sin(rot_angle/2)
                        cos = math.cos(rot_angle/2)
                        #quat = Quaternion((cos, sin*world_y[0], sin*world_y[1], sin*world_y[2]))
                        quat = Quaternion((cos, sin*axis_2[0], sin*axis_2[1], sin*axis_2[2])) 
                        
                        #new_no = self.initial_plane_no.copy() #its not rotated yet
                        #new_no.rotate(quat)
    
                        #rotate around x axis...update y
                        #world_x = world_y.cross(new_no)
                        #new_com = self.initial_com
                        #new_tan = new_com + world_x
                        
                        
                        #self.cut_line.plane_x = self.cut_line.plane_com + 2 * world_x
                        #self.cut_line.plane_y = self.cut_line.plane_com + 2 * world_y
                        #self.cut_line.plane_z = self.cut_line.plane_com + 2 * new_no
                    
               
                    new_no = self.initial_plane_no.copy() #its not rotated yet
                    new_no.rotate(quat)

                    new_x = self.vec_x.copy() #its not rotated yet
                    new_x.rotate(quat)
                   
                    new_y = self.vec_y.copy()
                    new_y.rotate(quat)
                    
                    self.cut_line.vec_x = new_x
                    self.cut_line.vec_y = new_y
                    self.cut_line.plane_no = new_no    
                    return {'RECUT'}
        
        #
        #Tranfsorm mode = NORMAL_TANSLATE
            #get the distance from mouse to self.x,y - inner radius
            
            #get the world distance by projecting both the original x,y- inner radius
            #and the mouse_x,mouse_y to the depth of the COPM
            
            #if "precision divide by 1/10?
            
            #add the translation vector to the
        
        #Transform mode = EDGE_PARALLEL
        
        #Transfrom mode = EDGE_PEREPENDICULAR
        

    def derive_screen(self,context):
        region = context.region  
        rv3d = context.space_data.region_3d
        view_z = rv3d.view_rotation * Vector((0,0,1))
        if view_z.dot(self.initial_plane_no) > -.95 and view_z.dot(self.initial_plane_no) < .95:
            point_0 = location_3d_to_region_2d(context.region, context.space_data.region_3d,self.cut_line.plane_com)
            point_1 = location_3d_to_region_2d(context.region, context.space_data.region_3d,self.cut_line.plane_com + self.initial_plane_no.normalized())
            self.screen_no = point_1 - point_0
            if self.screen_no.dot(Vector((0,1))) < 0:
                self.screen_no = point_0 - point_1
            self.screen_no.normalize()
            
            self.angle = math.atan2(self.screen_no[1],self.screen_no[0]) - 1/2 * math.pi
        else:
            self.screen_no = None
        
        
        up = self.angle + 1/2 * math.pi
        down = self.angle + 3/2 * math.pi
        left = self.angle + math.pi
        right =  self.angle
        
        deg_45 = .25 * math.pi
        
        self.wedge_1 = contour_utilities.pi_slice(self.x,self.y,self.inner_radius,self.radius,up - deg_45,up + deg_45, 10 ,t_fan = False)
        self.wedge_2 = contour_utilities.pi_slice(self.x,self.y,self.inner_radius,self.radius,left - deg_45,left + deg_45, 10 ,t_fan = False)
        self.wedge_3 = contour_utilities.pi_slice(self.x,self.y,self.inner_radius,self.radius,down - deg_45,down + deg_45, 10 ,t_fan = False)
        self.wedge_4 = contour_utilities.pi_slice(self.x,self.y,self.inner_radius,self.radius,right - deg_45,right + deg_45, 10 ,t_fan = False)
        self.wedge_1.append(self.wedge_1[0])
        self.wedge_2.append(self.wedge_2[0])
        self.wedge_3.append(self.wedge_3[0])
        self.wedge_4.append(self.wedge_4[0])
        
        
        self.arc_arrow_1 = contour_utilities.arc_arrow(self.x, self.y, self.arc_radius, left - deg_45+.2, left + deg_45-.2, 10, self.arrow_size, 2*deg_45, ccw = True)
        self.arc_arrow_2 = contour_utilities.arc_arrow(self.x, self.y, self.arc_radius, right - deg_45+.2, right + deg_45-.2, 10, self.arrow_size,2*deg_45, ccw = True)
        self.inner_circle = contour_utilities.simple_curce(self.x, self.y, self.inner_radius, 20)
        self.inner_circle.append(self.inner_circle[0])
        
    def draw(self, context):
        

        if not self.transform:
            #draw wedges
            contour_utilities.draw_polyline_from_points(context, self.wedge_1, self.color, self.line_width, "GL_LINES")
            contour_utilities.draw_polyline_from_points(context, self.wedge_2, self.color, self.line_width, "GL_LINES")
            contour_utilities.draw_polyline_from_points(context, self.wedge_3, self.color, self.line_width, "GL_LINES")
            contour_utilities.draw_polyline_from_points(context, self.wedge_4, self.color, self.line_width, "GL_LINES")
            
            
            #check to make sure normal isn't
            #too paralell to view
                #draw arrow up (no)
            
                #draw arrow down (no)
                
            #draw arc 1
            l = len(self.arc_arrow_1)
            contour_utilities.draw_polyline_from_points(context, self.arc_arrow_1[:l-1], self.color2, self.line_width, "GL_LINES")
            #draw a line perpendicular to arc
            point_1 = Vector((self.x,self.y)) + 2/3 * (self.inner_radius + self.radius) * Vector((math.cos(self.angle +  math.pi), math.sin(self.angle +  math.pi)))
            point_2 = Vector((self.x,self.y)) + 1/3 * (self.inner_radius + self.radius) * Vector((math.cos(self.angle +  math.pi), math.sin(self.angle +  math.pi)))
            contour_utilities.draw_polyline_from_points(context, [point_1, point_2], self.color3, self.line_width, "GL_LINES")
            
            #drawa arc 2
            contour_utilities.draw_polyline_from_points(context, self.arc_arrow_2[:l-1], self.color2, self.line_width, "GL_LINES")
            
            
            #draw an up and down arrow
            point_1 = Vector((self.x,self.y)) + 2/3 * (self.inner_radius + self.radius) * Vector((math.cos(self.angle + .5*math.pi), math.sin(self.angle + .5*math.pi)))
            point_2 = Vector((self.x,self.y)) + 1/3 * (self.inner_radius + self.radius) * Vector((math.cos(self.angle + .5*math.pi), math.sin(self.angle + .5*math.pi)))
            contour_utilities.draw_polyline_from_points(context, [point_1, point_2], self.color, self.line_width, "GL_LINES")
            
            point_1 = Vector((self.x,self.y)) + 2/3 * (self.inner_radius + self.radius) * Vector((math.cos(self.angle +  3/2 * math.pi), math.sin(self.angle +  3/2 * math.pi)))
            point_2 = Vector((self.x,self.y)) + 1/3 * (self.inner_radius + self.radius) * Vector((math.cos(self.angle +  3/2 * math.pi), math.sin(self.angle +  3/2 * math.pi)))
            contour_utilities.draw_polyline_from_points(context, [point_1, point_2], self.color, self.line_width, "GL_LINES")
        else:
            


            #draw a small inner circle
            contour_utilities.draw_polyline_from_points(context, self.inner_circle, self.color, self.line_width, "GL_LINES")
            
            
            if self.transform_mode == "NORMAL_TRANSLATE":
                #draw a ling from the center of mass to the mouse
                points = [self.initial_com, self.cut_line.plane_com]
                contour_utilities.draw_3d_points(context, points, self.cut_line.vert_color, 2)
                contour_utilities.draw_polyline_from_3dpoints(context, points, self.cut_line.geom_color ,2 , "GL_STIPPLE")
                
            else:
                rv3d = context.space_data.region_3d
                view_x = rv3d.view_rotation * Vector((1,0,0))
                p1 = self.cut_line.plane_com
                p2 = p1 + view_x
                p3 = p1 + self.cut_line.plane_no
                
                
                p1_2d =  location_3d_to_region_2d(context.region, context.space_data.region_3d, p1)
                p2_2d =  location_3d_to_region_2d(context.region, context.space_data.region_3d, p2)
                p3_2d =  location_3d_to_region_2d(context.region, context.space_data.region_3d, p3)
                
                vec_2d_scale = p1_2d - p2_2d
                screen_scale = self.radius / vec_2d_scale.length
                
                vec_2d = p1_2d - p3_2d
                
                p4_2d = p1_2d + screen_scale * vec_2d
                
                contour_utilities.draw_points(context, [p1_2d, p4_2d], self.cut_line.vert_color, 2)
                contour_utilities.draw_polyline_from_points(context, [p1_2d, p4_2d], self.cut_line.geom_color ,2 , "GL_STIPPLE")
                
            
            #If self.transform_mode != 
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