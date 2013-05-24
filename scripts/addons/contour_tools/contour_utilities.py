'''
Created on Apr 23, 2013

@author: Patrick Moore, patrick.moore.bu@gmail.com
some copy right?
some use agreement?
Open sourceness?
'''
import bpy
import bgl
import blf
import bmesh
import time
import math

from collections import deque

from bpy_extras import view3d_utils
from mathutils.geometry import intersect_line_plane, intersect_point_line
from bpy_extras.view3d_utils import location_3d_to_region_2d

def callback_register(self, context):
        if str(bpy.app.build_revision)[2:7] == "unkno" or eval(str(bpy.app.build_revision)[2:7]) >= 53207:
            self._handle = bpy.types.SpaceView3D.draw_handler_add(self.menu.draw, (self, context), 'WINDOW', 'POST_PIXEL')
        else:
            self._handle = context.region.callback_add(self.menu.draw, (self, context), 'POST_PIXEL')
        return None
            
def callback_cleanup(self, context):
    if str(bpy.app.build_revision)[2:7] == "unkno" or eval(str(bpy.app.build_revision)[2:7]) >= 53207:
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
    else:
        context.region.callback_remove(self._handle)
    return None

def draw_points(context, points, color, size):
    '''
    draw a bunch of dots
    args:
        points: a list of tuples representing x,y SCREEN coordinate eg [(10,30),(11,31),...]
        color: tuple (r,g,b,a)
        size: integer? maybe a float
    '''

    bgl.glColor4f(*color)
    bgl.glPointSize(size)
    bgl.glBegin(bgl.GL_POINTS)
    for coord in points:  
        bgl.glVertex2f(*coord)  
    
    bgl.glEnd()   
    return


def perp_vector_point_line(pt1, pt2, ptn):
    '''
    Vector bwettn pointn and line between point1
    and point2
    args:
        pt1, and pt1 are Vectors representing line segment
    
    return Vector
    
    pt1 ------------------- pt
            ^
            |
            |
            |<-----this vector
            |
            ptn
    '''
    pt_on_line = intersect_point_line(ptn, pt1, pt2)[0]
    alt_vect = pt_on_line - ptn
    
    return alt_vect


def rpd_cycle(verts, a, b, match_factor):
    '''
    http://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm
    
    searhces between two points for a point with perpendicular distance
    greater than the match factor
    '''

    max_perp_d = 0
    indx = a
    for i in range(a+1,b):
        perp_d = perp_vector_point_line(verts[a],verts[b],verts[i])
        if perp_d > max_perp_d:
            max_perp_d = perp_d
            indx = i
            
    if max_perp_d > match_factor:
        return i
    else:
        return None
        

def RPD_open_loop(verts, match_factor):
    '''
    a list of vertex locations in order
    match factor = distance to aim for between approximation and original
    '''
    
    #do some timing
    
    #count simplifaction iterations
    
    #
    new_verts_inds = [0,len(verts)-1]
    A = 0
    B = len(verts)-1
    new_v = rpd_cycle(verts, A, B, match_factor)
    if new_v:
        pairs = None #TODO: take care of this function
    
    
    
def RPD_closed_loop(verts,match_factor):
    '''
    a list of vertex locations in order
    match factor = distance to aim for between approximation and original
    '''
    
    #first we simply duplicated the last vert
    #move it by some small amount so that we get an
    #open loop
    
    
    #now we do RPD open loop
    


def draw_3d_points(context, points, color, size):
    '''
    draw a bunch of dots
    args:
        points: a list of tuples representing x,y SCREEN coordinate eg [(10,30),(11,31),...]
        color: tuple (r,g,b,a)
        size: integer? maybe a float
    '''
    points_2d = [location_3d_to_region_2d(context.region, context.space_data.region_3d, loc) for loc in points]

    bgl.glColor4f(*color)
    bgl.glPointSize(size)
    bgl.glBegin(bgl.GL_POINTS)
    for coord in points_2d:  
        bgl.glVertex2f(*coord)  
    
    bgl.glEnd()   
    return

def draw_polyline_from_points(context, points, color, thickness, LINE_TYPE):
    '''
    a simple way to draw a line
    args:
        points: a list of tuples representing x,y SCREEN coordinate eg [(10,30),(11,31),...]
        color: tuple (r,g,b,a)
        thickness: integer? maybe a float
        LINE_TYPE:  eg...bgl.GL_LINE_STIPPLE or 
    '''
    
    if LINE_TYPE == "GL_LINE_STIPPLE":  
        bgl.glLineStipple(4, 0x5555)  #play with this later
        bgl.glEnable(bgl.GL_LINE_STIPPLE)  
    
    bgl.glColor4f(*color)
    bgl.glLineWidth(thickness)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for coord in points:  
        bgl.glVertex2f(*coord)  
    
    bgl.glEnd()  
      
    if LINE_TYPE == "GL_LINE_STIPPLE":  
        bgl.glDisable(bgl.GL_LINE_STIPPLE)  
        bgl.glEnable(bgl.GL_BLEND)  # back to uninterupted lines  
      
    return


def draw_polyline_from_3dpoints(context, points_3d, color, thickness, LINE_TYPE):
    '''
    a simple way to draw a line
    slow...becuase it must convert to screen every time
    but allows you to pan and zoom around
    
    args:
        points_3d: a list of tuples representing x,y SCREEN coordinate eg [(10,30),(11,31),...]
        color: tuple (r,g,b,a)
        thickness: integer? maybe a float
        LINE_TYPE:  eg...bgl.GL_LINE_STIPPLE or 
    '''
    points = [location_3d_to_region_2d(context.region, context.space_data.region_3d, loc) for loc in points_3d]
    if LINE_TYPE == "GL_LINE_STIPPLE":  
        bgl.glLineStipple(4, 0x5555)  #play with this later
        bgl.glEnable(bgl.GL_LINE_STIPPLE)  
    
    bgl.glColor4f(*color)
    bgl.glLineWidth(thickness)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for coord in points:  
        bgl.glVertex2f(*coord)  
    
    bgl.glEnd()  
      
    if LINE_TYPE == "GL_LINE_STIPPLE":  
        bgl.glDisable(bgl.GL_LINE_STIPPLE)  
        bgl.glEnable(bgl.GL_BLEND)  # back to uninterupted lines  
      
    return
    
    


def cross_section(bme, mx, point, normal, debug = True):
    '''
    Takes a mesh and associated world matrix of the object and returns a cross secion in local
    space.
    
    Args:
        mesh: Blender BMesh
        mx:   World matrix (type Mathutils.Matrix)
        point: any point on the cut plane in world coords (type Mathutils.Vector)
        normal:  plane normal direction (type Mathutisl.Vector)
    '''
    
    times = []
    times.append(time.time())
    #bme = bmesh.new()
    #bme.from_mesh(me)
    #bme.normal_update()
    
    #if debug:
        #n = len(times)
        #times.append(time.time())
        #print('succesfully created bmesh in %f sec' % (times[n]-times[n-1]))
    verts =[]
    eds = []
    
    #convert point and normal into local coords
    #in the mesh into world space.This saves 2*(Nverts -1) matrix multiplications
    imx = mx.inverted()
    pt = imx * point
    no = imx.to_3x3() * normal  #local normal
    
    edge_mapping = {}  #perhaps we should use bmesh becaus it stores the great cycles..answer yup
    
    for ed in bme.edges:
        
        A = ed.verts[0].co
        B = ed.verts[1].co
        V = B - A
        
        proj = V.project(no).length
        
        #perp to normal = parallel to plane
        #only calc 2nd projection if necessary
        if proj == 0:
            
            #make sure not coplanar
            p_to_A = A - pt
            a_proj = p_to_A.project(no).length
            
            if a_proj == 0:
               
                edge_mapping[len(verts)] = ed.link_faces
                verts.append(1/2 * (A +B)) #put a midpoing since both are coplanar

        else:
            
            #this handles the one point on plane case
            v = intersect_line_plane(A,B,pt,no)
           
            if v:
                check = intersect_point_line(v,A,B)
                if check[1] >= 0 and check[1] <= 1:
                    
                                             
                    
                    #the vert coord index    =  the face indices it came from
                    edge_mapping[len(verts)] = [f.index for f in ed.link_faces]
                    verts.append(v)
    
    if debug:
        n = len(times)
        times.append(time.time())
        print('calced intersections %f sec' % (times[n]-times[n-1]))
       
    #iterate through smartly to create edge keys          
    for i in range(0,len(verts)):
        a_faces = set(edge_mapping[i])
        for m in range(i,len(verts)):
            if m != i:
                b_faces = set(edge_mapping[m])
                if a_faces & b_faces:
                    eds.append((i,m))
    
    if debug:
        n = len(times)
        times.append(time.time())
        print('calced connectivity %f sec' % (times[n]-times[n-1]))
        
    if len(verts):
        #new_me = bpy.data.meshes.new('Cross Section')
        #new_me.from_pydata(verts,eds,[])
        
    
        #if debug:
            #n = len(times)
            #times.append(time.time())
            #print('Total Time: %f sec' % (times[-1]-times[0]))
            
        return (verts, eds)
    else:
        return None
    

def cross_edge(A,B,pt,no):
    '''
    wrapper of intersect_line_plane that limits intersection
    to within the line segment.
    
    args:
        A - Vector endpoint of line segment
        B - Vector enpoint of line segment
        pt - pt on plane to intersect
        no - normal of plane to intersect
        
    return:
        list [Intersection Type, Intersection Point, Intersection Point2]
        eg... ['CROSS',Vector((0,1,0)), None]
        eg... ['POINT',Vector((0,1,0)), None]
        eg....['COPLANAR', Vector((0,1,0)),Vector((0,2,0))]
        eg....[None,None,None]
    '''
 
    ret_val = [None]*3 #list [intersect type, pt 1, pt 2]
    V = B - A #vect representation of the edge
    proj = V.project(no).length
    
    #perp to normal = parallel to plane
    #worst case is a coplanar issue where the whole face is coplanar..we will get there
    if proj == 0:
        
        #test coplanar
        #don't test both points.  We have already tested once for paralellism
        #simply proving one out of two points is/isn't in the plane will
        #prove/disprove coplanar
        p_to_A = A - pt
        #truly, we could precalc all these projections to save time but use mem.
        #because in the multiple edges coplanar case, we wil be testing
        #their verts over and over again that share edges.  So for a mesh with
        #a lot of n poles, precalcing the vert projections may save time!  
        #Hint to future self, look at  Nfaces vs Nedges vs Nverts
        #may prove to be a good predictor of which method to use.
        a_proj = p_to_A.project(no).length
        
        if a_proj == 0:
            print('special case co planar edge')
            ret_val = ['COPLANAR',A,B]
            
    else:
        
        #this handles the one point on plane case
        v = intersect_line_plane(A,B,pt,no)
       
        if v:
            check = intersect_point_line(v,A,B)
            if check[1] > 0 and check[1] < 1:  #this is the purest cross...no co-points
                #the vert coord index    =  the face indices it came from
                ret_val = ['CROSS',v,None]
                
            elif check[1] == 0 or check[1] == 1:
                print('special case coplanar point')
                #now add all edges that have that point into the already checked list
                #this takes care of poles
                ret_val = ['POINT',v,None]
    
    return ret_val
    

def face_cycle(face, pt, no, prev_eds, verts, connection):
    '''
    args:
        face - Blender BMFace
        pt - Vector, point on plane
        no - Vector, normal of plane
        
        
        These arguments will be modified
        prev_eds - MUTABLE list of previous edges already tested in the bmesh
        verts - MUTABLE list of Vectors representing vertex coords
        connection - MUTABLE dictionary of vert indices and face connections
        
    return:
        element - either a BMVert or a BMFace depending on what it finds.
    '''
    if len(face.edges) > 4:
        ngon = True
        print('oh shit an ngon')
    else:
        ngon = False
        
    for ed in face.edges:
        if ed.index not in prev_eds:
            prev_eds.append(ed.index)
            A = ed.verts[0].co
            B = ed.verts[1].co
            result = cross_edge(A, B, pt, no)
                
            if result[0] == 'CROSS':
                
                connection[len(verts)] = [f.index for f in ed.link_faces]
                verts.append(result[1])
                next_faces = [newf for newf in ed.link_faces if newf.index != face.index]
                if len(next_faces):
                    return next_faces[0]
                else:
                    #guess we got to a non manifold edge
                    print('found end of mesh!')
                    return None
                
            elif result[0] == 'POINT':
                if result[1] == A:
                    co_point = ed.verts[0]
                else:
                    co_point = ed.verts[1]
                    
                connection[len(verts)] = [f.index for f in co_point.link_faces]  #notice we take the face loop around the point!
                verts.append(result[1])  #store the "intersection"
                    
                return co_point
            
                
def vert_cycle(vert, pt, no, prev_eds, verts, connection):
    '''
    args:
        vert - Blender BMVert
        pt - Vector, point on plane
        no - Vector, normal of plane
        
        
        These arguments will be modified
        prev_eds - MUTABLE list of previous edges already tested in the bmesh
        verts - MUTABLE list of Vectors representing vertex coords
        connection - MUTABLE dictionary of vert indices and face connections
        
    return:
        element - either a BMVert or a BMFace depending on what it finds.
    '''                
    
    for f in vert.link_faces:
        for ed in f.edges:
            if ed.index not in prev_eds:
                prev_eds.append(ed.index)
                A = ed.verts[0].co
                B = ed.verts[1].co
                result = cross_edge(A, B, pt, no)
                
                if result[0] == 'CROSS':
                    connection[len(verts)] = [f.index for f in ed.link_faces]
                    verts.append(result[1])
                    next_faces = [newf for newf in ed.link_faces if newf.index != f.index]
                    if len(next_faces):
                        #return face to try face cycle
                        return next_faces[0]
                    else:
                        #guess we got to a non manifold edge
                        print('found end of mesh!')
                        return None
                    
                elif result[0] == 'COPLANAR':
                    cop_face = 0
                    for face in ed.link_faces:
                        if face.no.cross(no) == 0:
                            cop_face += 1
                            print('found a coplanar face')
    
                    if cop_face == 2:
                        #we have two coplanar faces with a coplanar edge
                        #this makes our cross section fail from a loop perspective
                        print("double coplanar face error, stopping here")
                        return None
                    
                    else:
                        #jump down line to the next vert
                        if ed.verts[0].index == vert.index:
                            element = ed.verts[1]
                            
                        else:
                            element = ed.verts[0]
                        
                        #add the new vert coord into the mix
                        connection[len(verts)] = [f.index for f in element.link_faces]
                        verts.append(element.co)
                        
                        #return the vert to repeat the vert cycle
                        return element

def space_evenly_on_path(verts, edges, segments):  #prev deved for Open Dental CAD
    '''
    Gives evenly spaced location along a string of verts
    Assumes that nverts > nsegments
    Assumes verts are ORDERED along path
    Assumes edges are ordered coherently
    Yes these are lazy assumptions, but the way I build my data
    guarantees these assumptions so deal with it.
    
    args:
        verts - list of vert locations type Mathutils.Vector
        eds - list of index pairs type tuple(integer) eg (3,5).
              should look like this though [(0,1),(1,2),(2,3),(3,4),(4,0)]     
        segments - number of segments to divide path into        
    return
        new_verts - list of new Vert Locations type list[Mathutils.Vector]
    '''
    
    if segments >= len(verts):
        print('more segments requested than original verts...I refuse to subdivide until my developer gets smarter')
        return verts, edges
     
    #determine if cyclic or not, first vert same as last vert
    if 0 in edges[-1]:
        cyclic = True
        #print('cyclic vert chain...oh well doesnt matter')
    else:
        cyclic = False
        
        
    #calc_length
    arch_len = 0
    cumulative_lengths = [0] #is this a stupid way to do this? If the 
    for i in range(0,len(verts)-2):
        v0 = verts[i]
        v1 = verts[i+1]
        V = v1-v0
        arch_len += V.length
        cumulative_lengths.append(arch_len)
        
    if cyclic:
        v0 = verts[i+1]
        v1 = verts[0]
        V = v1-v0
        arch_len += V.length
        cumulative_lengths.append(arch_len)
        
    #identify vert indicies of import
    #this will be the largest vert which lies at
    #no further than the desired fraction of the curve
    
    #initialze new vert array and seal the end points
    if cyclic:
        new_verts = [[None]]*(segments)
        new_verts[0] = verts[0]
            
    else:
        new_verts = [[None]]*(segments + 1)
        new_verts[0] = verts[0]
        new_verts[-1] = verts[-1]
    
    n = 0 #index to save some looping through the cumulative lengths list
    for i in range(0,segments-1):
        desired_length = (i+1)/segments * arch_len
        
        #find the original vert with the largets legnth
        #not greater than the desired length
        for j in range(n, len(verts)-1):
            if cumulative_lengths[j] > desired_length:
                n = j - 1
                break

        extra = desired_length - cumulative_lengths[j-1]
        new_verts[i+1] = verts[j-1] + extra * (verts[j]-verts[j-1]).normalized()
    
    eds = []
    
    for i in range(0,len(new_verts)-1):
        eds.append((i,i+1))
    if cyclic:
        #close the loop
        eds.append((i+1,0))

    print(cumulative_lengths)
    print(arch_len)
    print(eds)    
    return new_verts, eds
 
def list_shift(seq, n):
    n = n % len(seq)
    return seq[n:] + seq[:n]

def align_edge_loops(verts_1, verts_2, eds_1, eds_2):
    '''
    Modifies vert order and edge indices to  provide best
    bridge between edge_loop1 and edge_loop2
    
    args:
        verts_1: list of Vectors
        verts_2: list of Vectors
        
        eds_1: connectivity of the first loop, really just to test loop or line
        eds_2: connectivity of 2nd loops, really just to test for loop or line
        
    return:
        verts_2
    '''
    print('testing alignment')
    if 0 in eds_1[-1]:
        cyclic = True
        print('cyclic vert chain')
    else:
        cyclic = False
    
    if len(verts_1) != len(verts_2):
        print(len(verts_1))
        print(len(verts_2))
        print('non uniform loops, stopping until your developer gets smarter')
        return verts_2
    
    
    #turns out, sum of diagonals is > than semi perimeter
    #lets exploit this (only true if quad is pretty much flat)
    #if we have paths reversed...our indices will give us diagonals
    #instead of perimeter
    D1_O = verts_2[0] - verts_1[0]
    D2_O = verts_2[-1] - verts_1[-1]
    D1_R = verts_2[0] - verts_1[-1]
    D2_R = verts_2[-1] - verts_1[0]
            
    original_length = D1_O.length + D2_O.length
    reverse_length = D1_R.length + D2_R.length
    if reverse_length < original_length:
        verts_2.reverse()
        print('reversing')
        
    
    
    #iterate all verts and "handshake problem" them
    #into a dictionary?  That's not very effecient!
    edge_len_dict = {}
    for i in range(0,len(verts_1)):
        for n in range(0,len(verts_2)):
            edge = (i,n)
            vect = verts_2[n] - verts_1[i]
            edge_len_dict[edge] = vect.length
    
    shift_lengths = []
    #shift_cross = []
    for shift in range(0,len(verts_2)):
        tmp_len = 0
        #tmp_cross = 0
        for i in range(0, len(verts_2)):
            shift_mod = int(math.fmod(i+shift, len(verts_2)))
            tmp_len += edge_len_dict[(i,shift_mod)]
        shift_lengths.append(tmp_len)
           
    final_shift = shift_lengths.index(min(shift_lengths))
    if final_shift != 0:
        print("shifting verst by %i" % final_shift)
        verts_2 = list_shift(verts_2, final_shift)
    
    
            
    return verts_2
    

def cross_section_seed(bme, mx, point, normal, seed_index, debug = True):
    '''
    Takes a mesh and associated world matrix of the object and returns a cross secion in local
    space.
    
    Args:
        bme: Blender BMesh
        mx:   World matrix (type Mathutils.Matrix)
        point: any point on the cut plane in world coords (type Mathutils.Vector)
        normal:  plane normal direction (type Mathutisl.Vector)
        seed: face index, typically achieved by raycast
        exclude_edges: list of edge indices (usually already tested from previous iterations)
    '''
    
    times = []
    times.append(time.time())
    #bme = bmesh.new()
    #bme.from_mesh(me)
    #bme.normal_update()
    
    #if debug:
        #n = len(times)
        #times.append(time.time())
        #print('succesfully created bmesh in %f sec' % (times[n]-times[n-1]))
    verts =[]
    eds = []
    
    #convert point and normal into local coords
    #in the mesh into world space.This saves 2*(Nverts -1) matrix multiplications
    imx = mx.inverted()
    pt = imx * point
    no = imx.to_3x3() * normal  #local normal
    
    edge_mapping = {}  #perhaps we should use bmesh becaus it stores the great cycles..answer yup
    
    #first initial search around seeded face.
    #if none, we may go back to brute force
    #but prolly not :-)
    seed_edge = None
    seed_search = 0
    prev_eds = []
    seeds =[]
    
    if len(bme.faces[seed_index].edges) > 4:
        print('no NGon Support for initial seed yet! try again')
        return None
    
    for ed in bme.faces[seed_index].edges:
        seed_search += 1        
        prev_eds.append(ed.index)
        
        A = ed.verts[0].co
        B = ed.verts[1].co
        result = cross_edge(A, B, pt, no)
        if result[0] == 'CROSS':
            #add the point, add the mapping move forward
            edge_mapping[len(verts)] = [f.index for f in ed.link_faces]
            verts.append(result[1])
            seeds.append([face for face in ed.link_faces if face.index != seed_index][0])
            seed_edge = True
        
    if not seed_edge:
        print('failed to find a good face to start with, cancelling until your programmer gets smarter')
        return None    
        
    #we have found one edge that crosses, now, baring any terrible disconnections in the mesh,
    #we traverse through the link faces, wandering our way through....removing edges from our list

    total_tests = 0
    
    #by the way we append the verts in the first face...we find A then B then start at A... so there is a little  reverse in teh vert order at the middle.
    verts.reverse()
    for element in seeds: #this will go both ways if they dont meet up.
        element_tests = 0
        while element and total_tests < 10000:
            total_tests += 1
            element_tests += 1
            #first, we know that this face is not coplanar..that's good
            #if new_face.no.cross(no) == 0:
                #print('coplanar face, stopping calcs until your programmer gets smarter')
                #return None
            if type(element) == bmesh.types.BMFace:
                element = face_cycle(element, pt, no, prev_eds, verts, edge_mapping)
            
            elif type(element) == bmesh.types.BMVert:
                element = vert_cycle(element, pt, no, prev_eds, verts, edge_mapping)
                
        print('cpomplete %i tests in this seed search' % element_tests)
        print('%i vertices found so far' % len(verts))
        
 
    #The following tests for a closed loop
    #if the loop found itself on the first go round, the last test
    #will only get one try, and find no new crosses
    #trivially, mast make sure that the first seed we found wasn't
    #on a non manifold edge, which should never happen
    closed_loop = element_tests == 1 and len(seeds) == 2
    
    print('walked around cross section in %i tests' % total_tests)
    print('found this many vertices: %i' % len(verts))       
                
    if debug:
        n = len(times)
        times.append(time.time())
        print('calced intersections %f sec' % (times[n]-times[n-1]))
       
    #iterate through smartly to create edge keys
    #no longer have to do this...verts are created in order
    
    if closed_loop:        
        for i in range(0,len(verts)-1):
            eds.append((i,i+1))
        
        #the edge loop closure
        eds.append((i+1,0))
        
    else:
        #two more verts found than total tests
        #one vert per element test in the last loop
        
        
        #split the loop into the verts into the first seed and 2nd seed
        seed_1_verts = verts[:len(verts)-(element_tests)] #yikes maybe this index math is right
        seed_2_verts = verts[len(verts)-(element_tests):]
        seed_2_verts.reverse()
        
        seed_2_verts.extend(seed_1_verts)
        
        
        for i in range(0,len(seed_1_verts)-1):
            eds.append((i,i+1))
    
        verts = seed_2_verts
    if debug:
        n = len(times)
        times.append(time.time())
        print('calced connectivity %f sec' % (times[n]-times[n-1]))
        
    if len(verts):
        #new_me = bpy.data.meshes.new('Cross Section')
        #new_me.from_pydata(verts,eds,[])
        
    
        #if debug:
            #n = len(times)
            #times.append(time.time())
            #print('Total Time: %f sec' % (times[-1]-times[0]))
            
        return (verts, eds)
    else:
        return None