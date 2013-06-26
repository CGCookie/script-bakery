'''
Created on Apr 23, 2013

@author: Patrick
'''


bl_info = {
    "name": "Contour Retopology Tool",
    "description": "A tool to retopology forms quickly with contour strokes.",
    "author": "Patrick Moore",
    "version": (0, 0, 1),
    "blender": (2, 6, 8),
    "location": "View 3D > Tool Shelf",
    "warning": 'Beta',  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "https://github.com/CGCookie/script-bakery/issues?labels=Contour+Retopology&milestone=1&page=1&state=open",
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
from contour_classes import ContourCutLine, ExistingVertList
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
    edge_thick = IntProperty(
            name="Edge Thickness",
            default=1,
            min=1,
            max=10,
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
    
    stroke_thick = IntProperty(
            name="Stroke",
            description = "width lines drawn by user",
            default=1,
            min = 1,
            max = 10,
            )
    
    auto_align = BoolProperty(
            name="Iteratively Align verts",
            description = "Attempt to automatically align vertices in adjoining edgeloops. Improves outcome, but slows performance",
            default=False,
            )
    
    use_x_ray = BoolProperty(
            name="X-Ray",
            description = 'Enable X-Ray on Retopo-mesh upon creation',
            default=False,
            )
    
    def draw(self, context):
        layout = self.layout

        # User Settings
        row = layout.row()        
        row.prop(self, "show_edges", text="Show Edge Loops")
        row.prop(self, "line_thick", text ="Edge Thickness")
        
        row = layout.row(align=True)
        row.prop(self, "show_ring_edges", text="Show Edge Rings")
        row.prop(self, "vert_size")

        row = layout.row(align=True)
        row.prop(self, "handle_size", text="Handle Size")
        row.prop(self, "stroke_thick", text="Stroke Thickness")
        
        layout.prop(self, "auto_align")
        layout.prop(self, "use_x_ray", "Enable X-Ray at Mesh Creation")

        layout.separator()
        
        # Debug Settings
        layout.label(text="Debug Settings")
        
        layout.prop(self, "debug")
        layout.prop(self, "vert_inds", text="Show Vertex Indices")
        layout.prop(self, "simple_vert_inds", text="Show Simple Indices")

        row = layout.row()
        row.prop(self, "show_verts", text="Show Raw Vertices") 
        row.prop(self, "raw_vert_size")

        
class CGCOOKIE_OT_retopo_contour_panel(bpy.types.Panel)  :
    '''Retopologize Forms with Contour Strokes'''
    bl_label = "Contour Retopolgy"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        col = layout.column()

        col.operator("cgcookie.retop_contour", text="Draw Contours")    



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
    '''Retopologize Forms with Contour Strokes'''
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
            
            
            if context.mode == 'EDIT_MESH':
                back_to_edit = True
            else:
                back_to_edit = False
                
            bm = self.dest_bme
                
            #the world_matrix of the orignal form
            orig_mx = self.original_form.matrix_world
            orig_ims = orig_mx.inverted()
            
            #the world matrix of the destination (retopo) mesh
            reto_mx = self.destination_ob.matrix_world
            reto_imx = reto_mx.inverted()
            
            #make list of bmverts     
            bmverts = []
            bridge = False
            a = 0
            if self.sel_verts and self.sel_edges and len(self.sel_verts):
                bridge =True
                a = len(self.sel_verts)
            for i, vert in enumerate(self.verts):
                new_vert = bm.verts.new(tuple(reto_imx * (orig_mx * vert)))
                bmverts.append(new_vert)
                if bridge and i < a:
                    new_vert.select = True
            
            # Initialize the index values of this sequence
            self.dest_bme.verts.index_update()

            #this is tricky, I'm hoping that because my vert list is
            #actually composed of BMVerts that this will add in mesh data
            #smoothly with no problems.
            bmfaces = []
            for face in self.faces:

                #actual BMVerts not indices I think?
                new_face = tuple([bmverts[i] for i in face])
                bmfaces.append(bm.faces.new(new_face))
            
            
            # Finish up, write the modified bmesh back to the mesh
            
            #if editmode...we have to do it this way
            if context.mode == 'EDIT_MESH':
                bmesh.update_edit_mesh(self.dest_me, tessface=False, destructive=True)
            
            #if object mode....we do it like this
            else:
                #write the data into the object
                bm.to_mesh(self.dest_me)
            
                #remember we created a new object
                #moving this to the invoke?
                context.scene.objects.link(self.destination_ob)
                
                self.destination_ob.select = True
                context.scene.objects.active = self.destination_ob
                
                if context.space_data.local_view:
                    mx_copy = context.space_data.region_3d.view_matrix.copy()
                    view_loc = context.space_data.region_3d.view_location.copy()
                    view_rot = context.space_data.region_3d.view_rotation.copy()
                    view_dist = context.space_data.region_3d.view_distance
                    bpy.ops.view3d.localview()
                    bpy.ops.view3d.localview()
                    #context.space_data.region_3d.view_matrix = mx_copy
                    context.space_data.region_3d.view_location = view_loc
                    context.space_data.region_3d.view_rotation = view_rot
                    context.space_data.region_3d.view_distance = view_dist
                    context.space_data.region_3d.update()
                    
            self.destination_ob.update_tag()
            context.scene.update()
            
            context.area.header_text_set()
            contour_utilities.callback_cleanup(self,context)
            bm.free()
            self.dest_bme.free()
            self.bme.free()
            if self.tmp_ob:
                context.scene.objects.unlink(self.tmp_ob)
                me = self.tmp_ob.data
                self.tmp_ob.user_clear()
                bpy.data.objects.remove(self.tmp_ob)
                bpy.data.meshes.remove(me)
            if back_to_edit:
                #not sure why this is necessary?
                #TODO:  make this bmesh data manipulation instead of bpy.ops
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle()
                if self.sel_verts and len(self.sel_verts):
                    bpy.ops.mesh.bridge_edge_loops(type='SINGLE', use_merge=False, merge_factor=0.5, number_cuts=0, interpolation='PATH', smoothness=1, profile_shape_factor=0, profile_shape='SMOOTH')
                    bpy.ops.mesh.select_all(action='DESELECT')
            return{'FINISHED'}
            
        elif event.type == 'MOUSEMOVE':
            
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
        
        #escape
        elif event.type== 'ESC':
            #TODO:  Delete the destination ob in case we dont need it
            #need to carefully implement this so people dont delete their wok
            
            
            #clean up callbacks to prevent crash
            context.area.header_text_set()
            contour_utilities.callback_cleanup(self,context)
            self.bme.free()
            if self.tmp_ob:
                context.scene.objects.unlink(self.tmp_ob)
                me = self.tmp_ob.data
                self.tmp_ob.user_clear()
                bpy.data.objects.remove(self.tmp_ob)
                bpy.data.meshes.remove(me)
            return {'CANCELLED'}  
        
        elif event.type in {'MIDDLEMOUSE'}:
            for cut_line in self.cut_lines:
                if cut_line.head.world_position:
                    cut_line.head.screen_from_world(context)
                    cut_line.tail.screen_from_world(context)
            return {'PASS_THROUGH'}
        
        
        elif event.type == 'RIGHTMOUSE' and event.value == 'PRESS' and self.hover_target:
            if hasattr(self.hover_target, "head"):
                self.cut_lines.remove(self.hover_target)
                self.hover_target = None
                    
            else:
                self.cut_lines.remove(self.hover_target.parent)
                self.hover_target = None
            
            auto_align = context.user_preferences.addons['contour_tools'].preferences.auto_align        
            self.push_mesh_data(context, a_align = auto_align)    
            return {'RUNNING_MODAL'}
            
    
        #########temporary testing#############
        if event.type in {'LEFT_ARROW','RIGHT_ARROW'}:
            if self.hover_target and hasattr(self.hover_target, 'head'):
                if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
                    self.hover_target.shift -= .05
                    if self.hover_target.shift < -1:
                        self.hover_target.shift = -1   
                
                if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
                    self.hover_target.shift += .05
                    if self.hover_target.shift > 1:
                        self.hover_target.shift = 1
            
                self.hover_target.simplify_cross(self.segments)
                self.push_mesh_data(context, a_align = False)
        #######################################
        
        
        if event.type in {'WHEELDOWNMOUSE','WHEELUPMOUSE','NUMPAD_PLUS','NUMPAD_MINUS'}:
            
            if (event.type == 'WHEELUPMOUSE' and event.ctrl) or (event.type == 'NUMPAD_PLUS' and event.value == 'PRESS'):
                if len(self.cut_lines):
                    max_segments =  min([len(cut.verts) for cut in self.cut_lines])
                else:
                    max_segments = 10
                    
                if self.segments >= max_segments and not self.sel_verts:
                    self.segments = max_segments
                    return {'RUNNING_MODAL'}
                elif not self.sel_verts:
                    self.segments += 1
                    
                else:
                    self.segments = len(self.sel_edges)
                    
                message = "Segments: %i" % self.segments
                context.area.header_text_set(text = message)
                
                for cut_line in self.cut_lines:
                    if not cut_line.verts:
                        print('recutting this line because it has no freaking verts?')
                        hit = cut_line.hit_object(context, self.original_form)
                        if hit:
                            cut_line.cut_object(context, self.original_form, self.bme)
                            cut_line.simplify_cross(self.segments)
                        else:
                            self.cut_lines.remove(cut_line)

                    else:
                        cut_line.simplify_cross(self.segments)
                auto_align = context.user_preferences.addons['contour_tools'].preferences.auto_align
                self.push_mesh_data(context,re_order = False, a_align = auto_align)
                return {'RUNNING_MODAL'}
            
            elif (event.type == 'WHEELDOWNMOUSE' and event.ctrl) or (event.type == 'NUMPAD_MINUS' and event.value == 'PRESS'):
            
                if self.segments < 4:
                    self.segments = 3
                elif not self.sel_verts:
                    self.segments -= 1
                else:
                    self.segments = len(self.sel_edges)
        
                message = "Segments: %i" % self.segments
                context.area.header_text_set(text = message)
                
                for cut_line in self.cut_lines:
                    if not cut_line.verts:
                        hit = cut_line.hit_object(context, self.original_form)
                        if hit:
                            cut_line.cut_object(context, self.original_form, self.bme)
                            cut_line.simplify_cross(self.segments)
                        else:
                            self.cut_lines.remove(cut_line)
                        
                    else:
                        cut_line.simplify_cross(self.segments)
            
                auto_align = context.user_preferences.addons['contour_tools'].preferences.auto_align
                self.push_mesh_data(context,re_order = False, a_align = auto_align)
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
                        
                        #we already know we are dragging a line
                        #if the handle doesn't have a world position, it means it's
                        #a newly created line and the head and tail haven't been
                        #projected into 3d space and only exist in screen space
                        if self.drag_target.head.world_position:
                            hit = self.drag_target.hit_object(context, self.original_form, update_normal = False, method = 'HANDLE')
                        else:
                            hit = self.drag_target.hit_object(context, self.original_form, update_normal = True, method = 'VIEW')
                        
                        #if it hit
                        if hit:    
                            self.drag_target.cut_object(context, self.original_form, self.bme)
                        
                            #now we have a new cut, make sure our max segments aren't overwhelmed
                            if len(self.cut_lines):
                                max_segments =  min([len(cut.verts) for cut in self.cut_lines])
                            else:
                                max_segments = 10
                            
                            if self.segments >= max_segments:
                                self.segments = max_segments
                        
                            self.drag_target.simplify_cross(self.segments)
                            auto_align = context.user_preferences.addons['contour_tools'].preferences.auto_align
                            self.push_mesh_data(context, a_align = auto_align)
                            
                        else:
                            self.cut_lines.remove(self.drag_target)
                            self.drag_target = None
                    else:
                        self.drag_target.x = event.mouse_region_x
                        self.drag_target.y = event.mouse_region_y
                        if self.drag_target == self.drag_target.parent.plane_tan:
                            print('changing handle')
                            self.drag_target.screen_to_world(context)
                            hit = self.drag_target.parent.hit_object(context, self.original_form, update_normal = False, method = 'HANDLE')
                        else:
                            print('reshooting and re_cutting')
                            hit = self.drag_target.parent.hit_object(context, self.original_form, update_normal = True, method = 'VIEW')
                        
                        if hit:    
                            self.drag_target.parent.cut_object(context, self.original_form, self.bme)
                            self.drag_target.parent.simplify_cross(self.segments)
                            if self.new:
                                self.new = False
                                
                        else:
                            self.cut_lines.remove(self.drag_target.parent)
                            self.drag_target = None
                            if self.new:
                                self.new = False
                    auto_align = context.user_preferences.addons['contour_tools'].preferences.auto_align        
                    self.push_mesh_data(context, a_align = auto_align)
                
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
    
    def push_mesh_data(self,context, re_order = True, debug = False, a_align = False):
        
        total_verts = []
        total_edges = []
        total_faces = []
        
        
        if len(self.cut_lines) < 2:
            print('waiting on other cut lines')
            return
        
        imx = self.original_form.matrix_world.inverted()
        

        
        valid_cuts = [c_line for c_line in self.cut_lines if c_line.verts != [] and c_line.verts_simple != []]
        self.cut_lines = valid_cuts
        if len(valid_cuts) < 2:
            return
        


        #####order the cuts####
        
        #first make a list of the cut Center of Mass and normals
        #in the same order as valid cuts
        planes = [(contour_utilities.get_com(cut.verts_simple), cut.plane_no) for cut in valid_cuts]
        
        valid_pairs = []
        #test validity of all pairs
        #a pair is valid if the line segment crosses
        #none of the other planes reasonably close to
        #the plane origin.  This will fail in hairpin turns
        #but that case should be relatively uncommon
        
        for i in range(0,len(valid_cuts)):
            for m in range(i,len(valid_cuts)):
                if m != i:
                    pair = (i,m)
                    
                    #does this seem premature to append here?
                    valid_pairs.append(pair)
                    A = planes[i][0]  #the COM of the cut loop
                    B = planes[m][0] #the COM of the other cut loop
                    C = .5 * (A + B)  #the midpoint of the line between them?
                    
                    #we know the plane_pt is ON the mesh
                    #vs the COM of the loop which is inside the mesh (potentially)
                    #TODO: make this way beeeter
                    ray1 = A - valid_cuts[i].plane_pt  #valid_cuts[i].plane_tan.world_position
                    ray2 = B - valid_cuts[m].plane_pt  #plane_tan.world_position
                    ray = ray1.lerp(ray2,.5).normalized()
                    
                    #TODO: make 100 here actually be the approx radius of the two cuts :-)
                    hit = self.original_form.ray_cast(imx * (C + 100 * ray), imx * (C - 100 * ray))
                    
                    #what the hell is this?
                    
                    #iterate through all the other planes other than the two in the current pair
                    for j, plane in enumerate(planes):
                        if j != i and j != m:
                            pt = plane[0]
                            no = plane[1]
                            
                            #intersect the line between the two loops
                            #with the other planes...most likely it will intersect
                            v = intersect_line_plane(A,B,pt,no)
                            if v:
                                #if the distance between the intersection is less than
                                #than 1/2 the distance between the current pair
                                #than this pair is invalide because there is a loo
                                #in between
                                check = intersect_point_line(v,A,B)
                                pair_length = (B - A).length/2
                                inval_length = (v - pt).length
                                if (check[1] >= 0 and check[1] <= 1 and inval_length < pair_length) or hit[2] == -1:
                                    print('invalid pair %s' % str(pair))
                                    
                                    if pair in valid_pairs:
                                        valid_pairs.remove(pair)
        print('found valid pairs')
        if debug:                            
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
            if debug:
                print('the new order is')            
                print(new_order)     
            cuts_copy = valid_cuts.copy()
            valid_cuts = []
            for i, n in enumerate(new_order):
                valid_cuts.append(cuts_copy[n])
            
            #guaranteed editmode for this to happen
            #this makes sure we bridge the correct end
            #when we are done
            if self.sel_edges and len(self.sel_edges) and self.sel_verts and len(self.sel_verts) and self.existing_cut:
                mx = self.destination_ob.matrix_world
                
                #bridge_vert_vecs = [mx * v.co for v in self.sel_verts]
                bridge_loop_location = contour_utilities.get_com(self.existing_cut.verts_simple)
                
                loop_0_loc = contour_utilities.get_com(valid_cuts[0].verts_simple)
                loop_1_loc = contour_utilities.get_com(valid_cuts[-1].verts_simple)
                
                dist_0 = bridge_loop_location - loop_0_loc
                dist_1 = bridge_loop_location - loop_1_loc
                
                if dist_1.length < dist_0.length:
                    valid_cuts.reverse()
                    
                    
            del cuts_copy
            self.valid_cuts = valid_cuts  
        #now
        n_rings = len(self.valid_cuts)
        n_lines = len(self.valid_cuts[0].verts_simple)
        #align verts
        if self.existing_cut:
            self.valid_cuts[0].align_to_other(self.existing_cut, auto_align = a_align)
        
        for i in range(0,n_rings-1):
            vs_1 = self.valid_cuts[i].verts_simple
            vs_2 = self.valid_cuts[i+1].verts_simple
            es_1 = self.valid_cuts[i].eds_simple
            es_2 = self.valid_cuts[i+1].eds_simple
            
            self.valid_cuts[i+1].align_to_other(self.valid_cuts[i], auto_align = a_align)
                
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
                
        #print(len(total_verts))       
        #print(total_faces)
        self.follow_lines = []
        for i in range(0,len(self.valid_cuts[0].verts_simple)):
            tmp_line = []
            if self.existing_cut:
                tmp_line.append(self.existing_cut.verts_simple[i])
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
        settings = context.user_preferences.addons['contour_tools'].preferences
        
        if context.mode == 'EDIT_MESH':
            
            
            '''
            self.destination_ob = context.object
            self.dest_me = context.object.to_mesh(scene=context.scene, apply_modifiers=True, settings='PREVIEW')
            self.dest_bme = bmesh.new()
            
            #we will build this bmesh then add it to the existing one
            self.tmp_bme = bmesh.new()
            
            self.dest_bme.from_mesh(self.dest_me)
            '''
            
            ########################################################
            #### This is temporary code until bmesh.ops improves ###
            ########################################################
            
            #the active object will be the retopo object
            #whose geometry we will be augmenting
            self.destination_ob = context.object

            
            #get the destination mesh data
            self.dest_me = self.destination_ob.data
            
            #we will build this bmesh using from editmesh
            self.dest_bme = bmesh.from_edit_mesh(self.dest_me)
            
            #the selected object will be the original form
            self.original_form = [ob for ob in context.selected_objects if ob.name != context.object.name][0]
            
            #note, we will have to use bmesh.update_edit_mesh
            self.sel_edges = [ed for ed in self.dest_bme.edges if ed.select]  #we will have to bridge these :-)
            if self.sel_edges and len(self.sel_edges):
                self.sel_verts = [vert for vert in self.dest_bme.verts if vert.select]
                self.segments = len(self.sel_edges)
                self.existing_cut = ExistingVertList(self.sel_verts, self.sel_edges,self.destination_ob.matrix_world)
            else:
                self.sel_verts = None
                self.segments = 10
            
        else:
            #make the irrelevant variables None
            self.sel_edges = None
            self.sel_verts = None
            self.existing_cut = None
            
            #the active object will be the target
            self.original_form  = context.object
            
            #no temp mesh needed
            self.tmp_bme = None
            
            #new blank mesh
            self.dest_me = bpy.data.meshes.new(self.original_form.name + "_recontour")
            #new object to hold it
            self.destination_ob = bpy.data.objects.new(self.original_form.name + "_recontour",self.dest_me) #this is an empty currently
            self.destination_ob.matrix_world = self.original_form.matrix_world
            self.destination_ob.update_tag()
            
            #bmesh to operate on
            self.dest_bme = bmesh.new()
            self.dest_bme.from_mesh(self.dest_me)
            
            #default segments (spans)
            self.segments = 10
        
        #get the info about the original form
        #and convert it to a bmesh for fast connectivity info
        me = self.original_form.to_mesh(scene=context.scene, apply_modifiers=True, settings='PREVIEW')
        self.bme = bmesh.new()
        self.bme.from_mesh(me)
        
        if settings.use_x_ray:
            self.orig_x_ray = self.destination_ob.show_x_ray
            self.destination_ob.show_x_ray = True
        
        #check for ngons, and if there are any...triangulate just the ngons
        ngons = []
        for f in self.bme.faces:
            if len(f.verts) > 4:
                ngons.append(f)
        if len(ngons):
            print('Ngons detected, this is a real hassle just so you know')
            print('Ngons detected, this will probably double operator initial startup time')
            new_geom = bmesh.ops.triangulate(self.bme, faces = ngons, use_beauty = True)
            new_faces = new_geom['faces']
            new_me = bpy.data.meshes.new('tmp_recontour_mesh')
            self.bme.to_mesh(new_me)
            new_me.update()
            self.tmp_ob = bpy.data.objects.new('ContourTMP', new_me)
            context.scene.objects.link(self.tmp_ob)
            self.tmp_ob.matrix_world = self.original_form.matrix_world
            self.original_form = self.tmp_ob
        else:
            self.tmp_ob = None
            

        message = "Segments: %i" % self.segments
        context.area.header_text_set(text = message)
            
        #temporary variable for testing
        self.ring_shift = 0
            
        #here is where we will cache verts edges and faces
        #unti lthe user confirms and we output a real mesh.
        self.verts = []
        self.edges = []
        self.faces = []
            
       
        #These are all variables/values used in the user interaction
        #and drawing
        
        
        #is the user moving an existing entity or a new one.
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
    bpy.utils.register_class(CGCOOKIE_OT_retopo_contour_panel)
    bpy.utils.register_class(CGCOOKIE_OT_retopo_contour)
    

#unregistration
def unregister():
    bpy.utils.unregister_class(CGCOOKIE_OT_retopo_contour)
    bpy.utils.unregister_class(CGCOOKIE_OT_retopo_contour_panel)
    bpy.utils.unregister_class(ContourToolsAddonPreferences)