'''
Created on Apr 23, 2013

@author: Patrick
'''


bl_info = {
    "name": "Contour Tools",
    "description": "A series of tools for contours and retopology",
    "author": "Patrick Moore",
    "version": (0, 0, 1),
    "blender": (2, 6, 6),
    "location": "None Yet :/ ",
    "warning": '',  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"}

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'contour_tools'))    

'''    
if "bpy" in locals():
    import imp
    imp.reload(contour_classes)
    imp.reload(contour_utilities)

    print("Reloaded multifiles")
    
else:
    from . import contour_classes,  contour_utilities
    
    print("Imported multifiles")
'''
import bpy
import bmesh
import math
from mathutils import Vector
import contour_utilities
from contour_classes import ContourCutLine
from mathutils.geometry import intersect_line_plane, intersect_point_line
from bpy.props import EnumProperty, StringProperty,BoolProperty, IntProperty
from bpy.types import Operator, AddonPreferences

methods = (('0','WALKING','0'),('1','BRUTE','1'))


class ContourToolsAddonPreferences(AddonPreferences):
    bl_idname = __name__
    
    simple_vert_inds = BoolProperty(
            name="Simple Inds",
            default=False,
            )
    
    vert_inds = BoolProperty(
            name="Vert Inds",
            description = "Display indices of the raw contour verts",
            default=False,
            )
    
    show_verts = BoolProperty(
            name="Show Raw Verts",
            description = "Display the raw contour verts",
            default=False,
            )
    
    show_edges = BoolProperty(
            name="Show Span Edges",
            description = "Display the extracted mesh edges.  Usually only turned off for debugging",
            default=True,
            )
    
    show_ring_edges = BoolProperty(
            name="Show Ring Edges",
            description = "Display the extracted mesh edges.  Usually only turned off for debugging",
            default=True,
            )
    
    debug = IntProperty(
            name="Debug Level",
            default=1,
            min = 0,
            max = 4,
            )
    
    vert_size = IntProperty(
            name="Vertex Size",
            default=3,
            min = 1,
            max = 10,
            )
    
    raw_vert_size = IntProperty(
            name="Raw Vertex Size",
            default=1,
            min = 1,
            max = 10,
            )
    
    handle_size = IntProperty(
            name="Handle Vertex Size",
            default=5,
            min = 1,
            max = 10,
            )
    
 
    line_thick = IntProperty(
            name="Line Thickness",
            default=1,
            min = 1,
            max = 10,
            )
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Contour Tools Beta Preferences and Settings")
        layout.prop(self, "debug")
        layout.prop(self, "show_verts")
        layout.prop(self, "show_edges")
        layout.prop(self, "show_ring_edges")
        layout.prop(self, "vert_inds")
        layout.prop(self, "simple_vert_inds")
        layout.prop(self, "vert_size")
        layout.prop(self, "raw_vert_size")
        layout.prop(self, "handle_size")
        layout.prop(self, "line_thick")
        

def retopo_draw_callback(self,context):
    
    settings = context.user_preferences.addons['contour_tools'].preferences
    if self.cut_lines:
        for c_cut in self.cut_lines:
            c_cut.draw(context, settings)
            
    
    if self.follow_lines != [] and settings.show_edges:
        for follow in self.follow_lines:
            contour_utilities.draw_polyline_from_3dpoints(context, follow, (0,1,.2,1), settings.line_thick,"GL_LINE_STIPPLE")
        #event value press
            #asses proximity for hovering
            #if no proximity:
                #add new cutline 
                #w/ head at mouse position
                #view direction
                #v3d = context.space_data
                #region = v3d.region_3d        
                #view = region.view_rotation * Vector((0,0,1)) 
                #self.cutlines.append(ContourCutLine(mouse.x, mouse.y, view)
                #cutline.tail as drag target
            
            #if we are hoving over something of interest
                #drag target = hover object    
            
            #self.drag = True  #toggle the drag
    
        #event value release
            #confirm location of drag target
            #self.drag_target.x = event.mouse_x
            #self.drag_target.y = event.mouse_y
            #self.drag = False
    
#Operator
class CGCOOKIE_OT_retopo_contour(bpy.types.Operator):
    '''Slice an object and retopo along slices'''
    bl_idname = "cgcookie.retop_contour"
    bl_label = "Contour Retopologize"    
    
    @classmethod
    def poll(cls,context):
        if context.mode not in {'EDIT_MESH','OBJECT'}:
            return False
        
        if context.active_object:
            if context.mode == 'EDIT_MESH':
                if len(context.selected_objects) > 1:
                    return True
                else:
                    return False
            else:
                return context.object.type == 'MESH'
        else:
            return False
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            
            back_to_edit = False
            if context.mode == 'EDIT_MESH':
                bpy.ops.object.mode_set(mode='OBJECT')
                back_to_edit = True
                bm = self.tmp_bme
                
            else:
                bm = self.dest_bme
                
            #the world_matris of the orignal form
            orig_mx = self.original_form.matrix_world
            orig_ims = orig_mx.inverted()
            
            #the world matrix of the destination (retopo) mesh
            reto_mx = self.desination_ob.matrix_world
            reto_imx = reto_mx.inverted()
            
            #make list of bmverts...these should go smoothly into            
            bmverts = []
            for vert in self.verts:
                bmverts.append(bm.verts.new(tuple(reto_imx * (orig_mx * vert))))
            
            # Initialize the index values of this sequence...stupi they aren't going in there!)
            self.dest_bme.verts.index_update()

            #this is tricky, I'm hoping that because my vert list is
            #actually composed of BMVerts that this will add in mesh data
            #smoothly with no problems.
            bmfaces = []
            for face in self.faces:

                #actual BMVerts not indices I think?
                new_face = tuple([bmverts[i] for i in face])
                bmfaces.append(bm.faces.new(new_face))
            
            if not back_to_edit:
                # Finish up, write the bmesh back to the mesh
                bm.to_mesh(self.dest_me)
            
                #thies means we created a new object
                context.scene.objects.link(self.desination_ob)
            
            else:
                #disabled unti the BMesh API supports the dest keyword argument
                #bmesh.ops.duplicate(bm, geom = bm.verts[:] + bm.edges[:] + bm.faces[:],dest = self.dest_bme)
                
                # Finish up, write the bmesh back to the mesh
                bm.to_mesh(self.dest_me)
                
                context.scene.objects.link(self.retopo_ob)
                self.retopo_ob.update_tag()
                
                bpy.ops.object.select_all(action='DESELECT')
                self.retopo_ob.select = True
                context.scene.objects.active = self.desination_ob
                self.desination_ob.select = True
                bpy.ops.object.join()
                self.original_form.select = True
                
                    
            self.desination_ob.update_tag()
            context.scene.update()
            if back_to_edit:
                bpy.ops.object.mode_set(mode = 'EDIT')
            
            context.area.header_text_set()
            contour_utilities.callback_cleanup(self,context)
            bm.free()
            self.dest_bme.free()
            self.bme.free()
            
            return{'FINISHED'}
            
        if event.type == 'MOUSEMOVE':
            
            if self.drag and self.drag_target:
            
                if hasattr(self.drag_target,"head"): #then it's a  line, we need to move both?
                    delta = Vector((event.mouse_region_x,event.mouse_region_y)) - Vector((self.initial_location_mouse))
                    self.drag_target.head.x = self.initial_location_head[0] + delta[0]
                    self.drag_target.head.y = self.initial_location_head[1] + delta[1]
                    self.drag_target.tail.x = self.initial_location_tail[0] + delta[0]
                    self.drag_target.tail.y = self.initial_location_tail[1] + delta[1]
                    self.drag_target.plane_tan.x = self.initial_location_tan[0] + delta[0]
                    self.drag_target.plane_tan.y = self.initial_location_tan[1] + delta[1]
                    self.drag_target.head.screen_to_world(context)
                    self.drag_target.tail.screen_to_world(context)
                    self.drag_target.plane_tan.screen_to_world(context)
                else:
                    self.drag_target.x = event.mouse_region_x
                    self.drag_target.y = event.mouse_region_y
                    self.drag_target.screen_to_world(context)
                return {'RUNNING_MODAL'}
                
            #else detect proximity to items around
            else:
                #identify hover target for highlighting
                if self.cut_lines:
                    new_target = False
                    for c_cut in self.cut_lines:
                        h_target = c_cut.active_element(context,event.mouse_region_x,event.mouse_region_y)
                        if h_target:
                            new_target = True
                            self.hover_target = h_target
                    
                    if not new_target:
                        self.hover_target = None
                                
                    return {'RUNNING_MODAL'}
                return {'RUNNING_MODAL'}
        
        #even right click or escape
        if event.type in ('RIGHTMOUSE', 'ESC'):
            
            if event.type == 'RIGHTMOUSE' and event.value == 'PRESS' and self.hover_target:
                if hasattr(self.hover_target, "head"):
                    self.cut_lines.remove(self.hover_target)
                    self.hover_target = None
                    
                else:
                    self.cut_lines.remove(self.hover_target.parent)
                    self.hover_target = None
                    
                self.push_mesh_data(context)    
                return {'RUNNING_MODAL'}
            
            elif event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
                return {'RUNNING_MODAL'}        
                
                
            else:
                #clean up callbacks to prevent crash
                context.area.header_text_set()
                contour_utilities.callback_cleanup(self,context)
                self.bme.free()
                return {'CANCELLED'}  
        
        if event.type in {'MIDDLEMOUSE'}:
            for cut_line in self.cut_lines:
                if cut_line.head.world_position:
                    cut_line.head.screen_from_world(context)
                    cut_line.tail.screen_from_world(context)
            return {'PASS_THROUGH'}
        
        if event.type in {'WHEELDOWNMOUSE','WHEELUPMOUSE','NUMPAD_PLUS','NUMPAD_MINUS'}:
            
            if (event.type == 'WHEELUPMOUSE' and event.ctrl) or (event.type == 'NUMPAD_PLUS' and event.value == 'PRESS'):
                if len(self.cut_lines):
                    max_segments =  min([len(cut.verts) for cut in self.cut_lines])
                else:
                    max_segments = 10
                    
                if self.segments >= max_segments:
                    self.segments = max_segments
                    return {'RUNNING_MODAL'}
                else:
                    self.segments += 1
                message = "Segments: %i" % self.segments
                context.area.header_text_set(text = message)
                
                for cut_line in self.cut_lines:
                    if not cut_line.verts:
                        cut_line.hit_object(context, self.original_form)
                        cut_line.cut_object(context, self.original_form, self.bme)
                        cut_line.simplify_cross(self.segments)
                    cut_line.simplify_cross(self.segments)
                
                self.push_mesh_data(context,re_order = False)
                return {'RUNNING_MODAL'}
            
            elif (event.type == 'WHEELDOWNMOUSE' and event.ctrl) or (event.type == 'NUMPAD_MINUS' and event.value == 'PRESS'):
            
                if self.segments < 4:
                    self.segments = 3
                else:
                    self.segments -= 1
        
                message = "Segments: %i" % self.segments
                context.area.header_text_set(text = message)
                
                for cut_line in self.cut_lines:
                    if not cut_line.verts:
                        cut_line.hit_object(context, self.original_form)
                        cut_line.cut_object(context, self.original_form, self.bme)
                        cut_line.simplify_cross(self.segments)
                    cut_line.simplify_cross(self.segments)
            
                self.push_mesh_data(context,re_order = False)
                return {'RUNNING_MODAL'}
            
            
            else:
                for cut_line in self.cut_lines:
                    if cut_line.head.world_position:
                        cut_line.head.screen_from_world(context)
                        cut_line.tail.screen_from_world(context)
                return{'PASS_THROUGH'}  
        
        #event click
        elif event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE':
                if self.drag and self.drag_target:
                    if hasattr(self.drag_target,"head"): #then it's a  line
                        delta =Vector((event.mouse_region_x,event.mouse_region_y)) -  Vector((self.initial_location_mouse)) 
                        self.drag_target.head.x = self.initial_location_head[0] + delta[0]
                        self.drag_target.head.y = self.initial_location_head[1] + delta[1]
                        self.drag_target.tail.x = self.initial_location_tail[0] + delta[0]
                        self.drag_target.tail.y = self.initial_location_tail[1] + delta[1]
                        self.drag_target.plane_tan.x = self.initial_location_tan[0] + delta[0]
                        self.drag_target.plane_tan.y = self.initial_location_tan[1] + delta[1]
                        
                        self.drag_target.head.screen_to_world(context)
                        self.drag_target.tail.screen_to_world(context)
                        self.drag_target.plane_tan.screen_to_world(context)
                        
                        if self.drag_target.head.world_position:
                            self.drag_target.hit_object(context, self.original_form, update_normal = False, method = 'HANDLE')
                        else:
                            self.drag_target.hit_object(context, self.original_form, update_normal = True, method = 'VIEW')
                            
                        self.drag_target.cut_object(context, self.original_form, self.bme)
                        
                        #now we have a new cut, make sure our max segments aren't overwhelmed
                        if len(self.cut_lines):
                            max_segments =  min([len(cut.verts) for cut in self.cut_lines])
                        else:
                            max_segments = 10
                            
                        if self.segments >= max_segments:
                            self.segments = max_segments
                        
                        self.drag_target.simplify_cross(self.segments)
                        self.push_mesh_data(context)
                    else:
                        self.drag_target.x = event.mouse_region_x
                        self.drag_target.y = event.mouse_region_y
                        if self.drag_target == self.drag_target.parent.plane_tan:
                            print('changing handle')
                            self.drag_target.screen_to_world(context)
                            self.drag_target.parent.hit_object(context, self.original_form, update_normal = False, method = 'HANDLE')
                        else:
                            self.drag_target.parent.hit_object(context, self.original_form, update_normal = True, method = 'VIEW')
                            
                        self.drag_target.parent.cut_object(context, self.original_form, self.bme)
                        self.drag_target.parent.simplify_cross(self.segments)
                        if self.new:
                            self.new = False
                    self.push_mesh_data(context)
                
                #clear the drag and hover
                self.drag = False
                self.hover_target = None
    
                return {'RUNNING_MODAL'}
        
            if event.value == 'PRESS':
                self.drag = True
                self.drag_target = self.hover_target #presume them ose cant move w/o making it through modal?
                if hasattr(self.drag_target,"head"):
                    self.initial_location_head = (self.drag_target.head.x, self.drag_target.head.y)
                    self.initial_location_tail = (self.drag_target.tail.x, self.drag_target.tail.y)
                    self.initial_location_tan = (self.drag_target.plane_tan.x, self.drag_target.plane_tan.y)
                    self.initial_location_mouse = (event.mouse_region_x,event.mouse_region_y)
                
                if not self.drag_target:
                    v3d = context.space_data
                    region = v3d.region_3d 
                    view = region.view_rotation * Vector((0,0,1))
                    self.cut_lines.append(ContourCutLine(event.mouse_region_x, event.mouse_region_y, view))
                    self.drag_target = self.cut_lines[-1].tail
                    self.new = True
            
                    return {'RUNNING_MODAL'}
                return {'RUNNING_MODAL'}
            return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}
        #ret_val = retopo_modal(self, context, event)
        #print('modal ret val')
        #print(ret_val)
        #return ret_val
    
    def push_mesh_data(self,context, re_order = True):
        
        if len(self.cut_lines) < 2:
            print('waiting on other cut lines')
            return
        
        imx = self.original_form.matrix_world.inverted()
        
        total_verts = []
        total_edges = []
        total_faces = []
        
        valid_cuts = [c_line for c_line in self.cut_lines if c_line.verts != [] and c_line.verts_simple != []]
        self.cut_lines = valid_cuts
        if len(valid_cuts) < 2:
            return
        


        #####order the cuts####
        
        #first dictionary their current indices
        planes = [(cut.plane_pt, cut.plane_no) for cut in valid_cuts]
        
        valid_pairs = []
        #test validity of all pairs
        #a pair is valid if the line segment corosses
        #none of the other planes reasonable close to
        #the plane origin.  This will fail in hairpin turns
        #but that case should be relatively uncommon
        
        for i in range(0,len(valid_cuts)):
            for m in range(i,len(valid_cuts)):
                if m != i:
                    pair = (i,m)
                    valid_pairs.append(pair)
                    A = valid_cuts[i].plane_pt
                    B = valid_cuts[m].plane_pt
                    C = .5 * (A + B)
                    ray1 = A - valid_cuts[i].plane_tan.world_position
                    ray2 = B - valid_cuts[m].plane_tan.world_position
                    ray = ray1.lerp(ray2,.5).normalized()
                    
                    hit = self.original_form.ray_cast(imx * (C + 100 * ray), imx * (C - 100 * ray))
                    
                    for j, plane in enumerate(planes):
                        if j != i and j != m:
                            pt = plane[0]
                            no = plane[1]
                            v = intersect_line_plane(A,B,pt,no)
                            if v:
                                check = intersect_point_line(v,A,B)
                                pair_length = (B - A).length/2
                                inval_length = (v - pt).length
                                if (check[1] >= 0 and check[1] <= 1 and inval_length < pair_length) or hit[2] == -1:
                                    print('invalid pair %s' % str(pair))
                                    
                                    if pair in valid_pairs:
                                        valid_pairs.remove(pair)
                                    
        print(valid_pairs)
        
        if re_order and len(valid_pairs) > 0:
            #sort the pairs
            new_order = []
            new_order.append(valid_pairs[-1][0])
            new_order.append(valid_pairs[-1][1])
            valid_pairs.pop()
            
            tests = 0
            max_tests = len(valid_pairs) + 2
            while len(valid_pairs) and tests < max_tests:
                tests += 1
                for pair in valid_pairs:
                    end = set(pair) & {new_order[-1]}
                    beg = set(pair) & {new_order[0]}
                    if end or beg:
                        valid_pairs.remove(pair)
                        if end:
                            new_order.append(list(set(pair) - end)[0])
                        else:
                            new_order.insert(0, list(set(pair)-beg)[0])
                            
                        break
            print('the new order is')            
            print(new_order)     
            cuts_copy = valid_cuts.copy()
            valid_cuts = []
            for i, n in enumerate(new_order):
                valid_cuts.append(cuts_copy[n])
            
            del cuts_copy
            self.valid_cuts = valid_cuts  
        #now
        n_rings = len(self.valid_cuts)
        n_lines = len(self.valid_cuts[0].verts_simple)
        #align verts
        for i in range(0,n_rings-1):
            vs_1 = self.valid_cuts[i].verts_simple
            vs_2 = self.valid_cuts[i+1].verts_simple
            es_1 = self.valid_cuts[i].eds_simple
            es_2 = self.valid_cuts[i+1].eds_simple
            
            self.valid_cuts[i+1].verts_simple = contour_utilities.align_edge_loops(vs_1, vs_2, es_1, es_2)
        
                
        #work out the connectivity edges
        for i, cut_line in enumerate(self.valid_cuts):
            for v in cut_line.verts_simple:
                total_verts.append(imx * v)
            for ed in cut_line.eds_simple:
                total_edges.append((ed[0]+i*n_lines,ed[1]+i*n_lines))
            
            if i < n_rings - 1:
                #make connections between loops
                for j in range(0,n_lines):
                    total_edges.append((i*n_lines + j, (i+1)*n_lines + j))
        
        cyclic = 0 in valid_cuts[0].eds_simple[-1]
        #work out the connectivity faces:
        for j in range(0,len(valid_cuts) - 1):
            for i in range(0,n_lines-1):
                ind0 = j * n_lines + i
                ind1 = j * n_lines + (i + 1)
                ind2 = (j + 1) * n_lines + (i + 1)
                ind3 = (j + 1) * n_lines + i
                total_faces.append((ind0,ind1,ind2,ind3))
            
            if cyclic:
                ind0 = (j + 1) * n_lines - 1
                ind1 = j * n_lines + int(math.fmod((j+1)*n_lines, n_lines))
                ind2 = ind0 + 1
                ind3 = ind0 + n_lines
                total_faces.append((ind0,ind1,ind2,ind3))
                print('part implemented')
        print(len(total_verts))       
        print(total_faces)
        self.follow_lines = []
        for i in range(0,len(self.valid_cuts[0].verts_simple)):
            tmp_line = []
            for cut_line in self.valid_cuts:
                tmp_line.append(cut_line.verts_simple[i])
            self.follow_lines.append(tmp_line)


        self.verts = total_verts
        self.faces = total_faces
        self.edges = total_edges
        '''
        ideasman42_> bmesh.ops.duplicate
        <ideasman42_> this has a destination argument
        <ideasman42_> you can duplicate into another mesh
        <ideasman42_> but this api isnt well tested :S
        <ideasman42_> bmesh.ops.duplicate(bm_from, dest=bm_to, geom=bm_to.verts[:] + bm_to.edges[:] + bm_to.faces[:])
        <ideasman42_> Patrick_Moore, try that
        <ideasman42_> might be good to have a simple function for this though
        <ideasman42_> bm.join(other)
        '''
  
    def invoke(self, context, event):
        #if edit mode
        if context.mode == 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()
            
            '''
            self.desination_ob = context.object
            self.dest_me = context.object.to_mesh(scene=context.scene, apply_modifiers=True, settings='PREVIEW')
            self.dest_bme = bmesh.new()
            
            #we will build this bmesh then add it to the existing one
            self.tmp_bme = bmesh.new()
            
            self.dest_bme.from_mesh(self.dest_me)
            '''
            
            ########################################################
            #### This is temporary code until bmesh.ops improves ###
            ########################################################
            
            #new object to build to then join
            self.desination_ob = context.object
            #new blank mesh
            self.dest_me = bpy.data.meshes.new("tmp_recontour")
            self.retopo_ob = bpy.data.objects.new('tmp',self.dest_me) #this is an empty currently
            self.retopo_ob.matrix_world = self.desination_ob.matrix_world
            
            #we will build this bmesh then to_mesh it into
            #self.dest_me....then join retopo ob to dest ob
            #and be frustrated.
            self.tmp_bme = bmesh.new()
            self.dest_bme = bmesh.new()
            bpy.ops.object.editmode_toggle()
            
            #the selected object will be the original form
            self.original_form = [ob for ob in context.selected_objects if ob.name != context.object.name][0]
            
            
        else:
            
            #the active object will be the target
            self.original_form  = context.object
            
            #no temp mesh needed
            self.tmp_bme = None
            
            #new blank mesh
            self.dest_me = bpy.data.meshes.new(self.original_form.name + "_recontour")
            #new object to hold it
            self.desination_ob = bpy.data.objects.new('ReContour_ob',self.dest_me) #this is an empty currently
            #bmesh to operate on
            self.dest_bme = self.bme = bmesh.new()
            self.dest_bme.from_mesh(self.dest_me)
            
        
        #get the info about the original form 
        me = self.original_form.to_mesh(scene=context.scene, apply_modifiers=True, settings='PREVIEW')
        self.bme = bmesh.new()
        self.bme.from_mesh(me)
        
        #default segments (spans)
        self.segments = 10
        message = "Segments: %i" % self.segments
        context.area.header_text_set(text = message)
            
            
        #here is where we will cache verts edges and faces
        #unti lthe user confirms and we output a real mesh.
        self.verts = []
        self.edges = []
        self.faces = []
            
       
        #These are all variables/values used in the user interaction
        #and drawing
        
        
        #is the user moving and existing entity or a new one.
        self.new = False 
        #is the mouse clicked and held down
        self.drag = False
        
        #what is the user dragging..a cutline, a handle etc
        self.drag_target = None
        #what is the mouse over top of currently
        self.hover_target = None
        
        #at the begniinging of a drag, we want to keep track
        #of where things started out
        self.initial_location_head = None
        self.initial_location_tail = None
        self.initial_location_mouse = None
        
        #cut_linse are actual instances of the
        #ContourCutLine calss which controls the extraction of
        #the contours.
        self.cut_lines = []
        #the validity of a cut is determined by the inferred connectivity to
        #other cut_lines, we make a subset here.  CutLines are cheap so we duplicate
        #instead of referencing indices for now.
        self.valid_cuts = []
        
        #this iw a collection of verts used for open GL drawing the spans
        self.follow_lines = []
        
        #add in the draw callback and modal method
        self._handle = bpy.types.SpaceView3D.draw_handler_add(retopo_draw_callback, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}
    
    def execute(self,context):
        for line in self.cut_lines:
            print(line.view_dir)

#resgistration
def register():
    bpy.utils.register_class(ContourToolsAddonPreferences)
    bpy.utils.register_class(CGCOOKIE_OT_retopo_contour)
    

#unregistration
def unregister():
    bpy.utils.unregister_class(CGCOOKIE_OT_retopo_contour)
    bpy.utils.unregister_class(ContourToolsAddonPreferences)