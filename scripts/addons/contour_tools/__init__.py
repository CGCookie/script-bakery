'''
Copyright (C) 2013 CG Cookie
http://cgcookie.com
hello@cgcookie.com

Created by Patrick Moore

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Contour Retopology Tool",
    "description": "A tool to retopologize forms quickly with contour strokes.",
    "author": "Patrick Moore",
    "version": (0, 0, 1),
    "blender": (2, 6, 8),
    "location": "View 3D > Tool Shelf",
    "warning": 'Beta',  # used for warning icon and text in addons panel
    "wiki_url": "http://cgcookie.com/blender/docs/contour-retopology/",
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
import blf
import math
import sys
import time
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
import contour_utilities
from contour_classes import ContourCutLine, ExistingVertList, CutLineManipulatorWidget, PolySkecthLine
from mathutils.geometry import intersect_line_plane, intersect_point_line
from bpy.props import EnumProperty, StringProperty,BoolProperty, IntProperty, FloatVectorProperty, FloatProperty
from bpy.types import Operator, AddonPreferences


#a place to store stokes for later
global contour_cache 
contour_cache = {}

contour_undo_cache = []

#store any temporary triangulated objects
#store the bmesh to prevent recalcing bmesh
#each time :-)
global contour_mesh_cache
contour_mesh_cache = {}

def object_validation(ob):
    
    valid = [ob.name, len(ob.data.vertices), len(ob.data.edges), len(ob.data.polygons)]
    
    return valid


def write_mesh_cache(orig_ob,tmp_ob, bme):
    
    #TODO try taking this out
    global contour_mesh_cache
    
    if 'valid' in contour_mesh_cache and contour_mesh_cache['valid']:
        del contour_mesh_cache['valid']
        
    valid = object_validation(orig_ob) #TODO, maybe this should be polygons
    
    contour_mesh_cache['valid'] = valid
    
    if 'bme' in contour_mesh_cache and contour_mesh_cache['bme']:
        bme_old = contour_mesh_cache['bme']
        bme_old.free()
        del contour_mesh_cache['bme']
    
    contour_mesh_cache['bme'] = bme
    
    if 'tmp' in contour_mesh_cache and contour_mesh_cache['tmp']:
        old_obj = contour_mesh_cache['tmp']
        
        #context.scene.objects.unlink(self.tmp_ob)
        me = old_obj.data
        old_obj.user_clear()
        bpy.data.objects.remove(old_obj)
        bpy.data.meshes.remove(me)
                
        del contour_mesh_cache['tmp']
        
    contour_mesh_cache['tmp'] = tmp_ob
    
def clear_mesh_cache():
    if 'valid' in contour_mesh_cache and contour_mesh_cache['valid']:
        del contour_mesh_cache['valid']
        
    if 'bme' in contour_mesh_cache and contour_mesh_cache['bme']:
        bme_old = contour_mesh_cache['bme']
        bme_old.free()
        del contour_mesh_cache['bme']
    
    if 'tmp' in contour_mesh_cache and contour_mesh_cache['tmp']:
        old_obj = contour_mesh_cache['tmp']
        bpy.data.objects.remove(old_obj.name)
        del contour_mesh_cache['tmp']
        

        
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
    
    show_cut_indices = BoolProperty(
            name="Show Cut Indices",
            description = "Display the order the operator stores cuts.  Usually only turned on for debugging",
            default=False,
            )
        
    
    show_ring_edges = BoolProperty(
            name="Show Ring Edges",
            description = "Display the extracted mesh edges.  Usually only turned off for debugging",
            default=True,
            )
    
    draw_widget = BoolProperty(
            name="Draw Widget",
            description = "Turn off to help make mockups or clean-up visualization ",
            default=True,
            )
    
    debug = IntProperty(
            name="Debug Level",
            default=1,
            min = 0,
            max = 4,
            )

    show_debug = BoolProperty(
            name="Show Debug Settings",
            description = "Show the debug settings, useful for troubleshooting",
            default=False,
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
    
    stroke_rgb = FloatVectorProperty(name="Stroke Color", description="Color of Strokes", min=0, max=1, default=(0,0.2,1), subtype="COLOR")
    handle_rgb = FloatVectorProperty(name="Handle Color", description="Color of Stroke Handles", min=0, max=1, default=(0.6,0,0), subtype="COLOR")
    vert_rgb = FloatVectorProperty(name="Vertex Color", description="Color of Verts", min=0, max=1, default=(0,0.2,1), subtype="COLOR")
    geom_rgb = FloatVectorProperty(name="Geometry Color", description="Color For Edges", min=0, max=1, default=(0,1, .2), subtype="COLOR")
    actv_rgb = FloatVectorProperty(name="Active Color", description="Active Cut Line", min=0, max=1, default=(0.6,.2,.8), subtype="COLOR")
    
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
            name="Stroke Thickness",
            description = "Width of stroke lines drawn by user",
            default=1,
            min = 1,
            max = 10,
            )
    
    auto_align = BoolProperty(
            name="Automatically Align Vertices",
            description = "Attempt to automatically align vertices in adjoining edgeloops. Improves outcome, but slows performance",
            default=True,
            )
    
    live_update = BoolProperty(
            name="Live Update",
            description = "Will live update the mesh preview when transforming cut lines.  Looks good, but can get slow on large meshes",
            default=True,
            )
    
    use_x_ray = BoolProperty(
            name="X-Ray",
            description = 'Enable X-Ray on Retopo-mesh upon creation',
            default=False,
            )
    
    use_perspective = BoolProperty(
            name="Use Perspective",
            description = 'Will cause non parallel cuts from same view',
            default=True,
            )
    
    #TODO  Theme this out nicely :-) 
    widget_color = FloatVectorProperty(name="Widget Color", description="Choose Widget color", min=0, max=1, default=(0,0,1), subtype="COLOR")
    widget_color2 = FloatVectorProperty(name="Widget Color", description="Choose Widget color", min=0, max=1, default=(1,0,0), subtype="COLOR")
    widget_color3 = FloatVectorProperty(name="Widget Color", description="Choose Widget color", min=0, max=1, default=(0,1,0), subtype="COLOR")
    widget_color4 = FloatVectorProperty(name="Widget Color", description="Choose Widget color", min=0, max=1, default=(0,0.2,.8), subtype="COLOR")
    widget_color5 = FloatVectorProperty(name="Widget Color", description="Choose Widget color", min=0, max=1, default=(.9,.1,0), subtype="COLOR")
    
    
    widget_radius = IntProperty(
            name="Widget Radius",
            description = "Size of cutline widget radius",
            default=50,
            min = 20,
            max = 100,
            )
    
    widget_radius_inner = IntProperty(
            name="Widget Inner Radius",
            description = "Size of cutline widget inner radius",
            default=15,
            min = 5,
            max = 30,
            )
    
    widget_thickness = IntProperty(
            name="Widget Line Thickness",
            description = "Width of lines used to draw widget",
            default=2,
            min = 1,
            max = 10,
            )
    
    widget_thickness2 = IntProperty(
            name="Widget 2nd Line Thick",
            description = "Width of lines used to draw widget",
            default=4,
            min = 1,
            max = 10,
            )
        
    arrow_size = IntProperty(
            name="Arrow Size",
            default=12,
            min=5,
            max=50,
            )   
    
    arrow_size2 = IntProperty(
            name="Translate Arrow Size",
            default=10,
            min=5,
            max=50,
            )      
    vertex_count = IntProperty(
            name = "Vertex Count",
            description = "The Number of Vertices Per Edge Ring",
            default=10,
            min = 3,
            max = 250,
            )
    
    cyclic = BoolProperty(
            name = "Cyclic",
            description = "Make Retopo Loops Cyclic",
            default = False)
    
    recover = BoolProperty(
            name = "Recover",
            description = "Recover strokes from last session",
            default = False)
    
    recover_clip = IntProperty(
            name = "Recover Clip",
            description = "Number of cuts to leave out, usually just 0 or 1",
            default=1,
            min = 0,
            max = 10,
            )
    
    search_factor = FloatProperty(
            name = "Search Factor",
            description = "percentage of object distance to search",
            default=.2,
            min = 0,
            max = 1,
            )
        
    intersect_factor = IntProperty(
            name = "Intersect Factor",
            description = "Stringence for connecting new loops",
            default=2,
            min = 1,
            max = 10,
            )
    
    
    
    def draw(self, context):
        layout = self.layout

        # Interaction Settings
        row = layout.row(align=True)
        row.prop(self, "auto_align")
        row.prop(self, "live_update")
        row.prop(self, "use_perspective")
        
        row = layout.row()
        row.prop(self, "use_x_ray", "Enable X-Ray at Mesh Creation")
        

        # Visualization Settings
        box = layout.box().column(align=False)
        row = box.row()
        row.label(text="Stroke And Loop Settings")

        row = box.row()
        row.prop(self, "stroke_rgb", text="Stroke Color")
        row.prop(self, "handle_rgb", text="Handle Color")
        row.prop(self, "actv_rgb", text="Hover Color")
        
        row = box.row()
        row.prop(self, "vert_rgb", text="Vertex Color")
        row.prop(self, "geom_rgb", text="Edge Color")
        

        row = box.row(align=False)
        row.prop(self, "handle_size", text="Handle Size")
        row.prop(self, "stroke_thick", text="Stroke Thickness")

        row = box.row(align=False)
        row.prop(self, "show_edges", text="Show Edge Loops")
        row.prop(self, "line_thick", text ="Edge Thickness")
        
        row = box.row(align=False)
        row.prop(self, "show_ring_edges", text="Show Edge Rings")
        row.prop(self, "vert_size")

        row = box.row(align=True)
        row.prop(self, "show_cut_indices", text = "Edge Indices")


        # Widget Settings
        box = layout.box().column(align=False)
        row = box.row()
        row.label(text="Widget Settings")

        row = box.row()
        row.prop(self,"draw_widget", text = "Display Widget")

        if self.draw_widget:
            row = box.row()
            row.prop(self, "widget_radius", text="Radius")
            row.prop(self,"widget_radius_inner", text="Active Radius")
            
            row = box.row()
            row.prop(self, "widget_thickness", text="Line Thickness")
            row.prop(self, "widget_thickness2", text="2nd Line Thickness")
            row.prop(self, "arrow_size", text="Arrow Size")
            row.prop(self, "arrow_size2", text="Translate Arrow Size")

            row = box.row()
            row.prop(self, "widget_color", text="Color 1")
            row.prop(self, "widget_color2", text="Color 2")
            row.prop(self, "widget_color3", text="Color 3")
            row.prop(self, "widget_color4", text="Color 4")
            row.prop(self, "widget_color5", text="Color 5")

        # Debug Settings
        box = layout.box().column(align=False)
        row = box.row()
        row.label(text="Debug Settings")

        row = box.row()
        row.prop(self, "show_debug", text="Show Debug Settings")
        
        if self.show_debug:
            row = box.row()
            row.prop(self, "debug")
            
            row = box.row()
            row.prop(self, "vert_inds", text="Show Vertex Indices")
            row.prop(self, "simple_vert_inds", text="Show Simple Indices")

            row = box.row()
            row.prop(self, "show_verts", text="Show Raw Vertices")
            row.prop(self, "raw_vert_size")

        
class CGCOOKIE_OT_retopo_contour_panel(bpy.types.Panel):
    '''Retopologize Forms with Contour Strokes'''
    bl_label = "Contour Retopolgy"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    @classmethod
    def poll(cls, context):
        mode = bpy.context.mode
        obj = context.active_object
        return (obj and obj.type == 'MESH' and mode in ('OBJECT', 'EDIT_MESH'))



    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("cgcookie.retop_contour", text="Draw Contours", icon='MESH_UVSPHERE')
        col.operator("cgcookie.retopo_poly_sketch", text="Sketch Poly Strips", icon='MESH_UVSPHERE')
        cgc_contour = context.user_preferences.addons['contour_tools'].preferences
        row = layout.row()
        row.prop(cgc_contour, "cyclic")
        row.prop(cgc_contour, "vertex_count")
        
        row = layout.row()
        row.prop(cgc_contour, "recover")
        row.prop(cgc_contour, "recover_clip")

class CGCOOKIE_OT_retopo_contour_menu(bpy.types.Menu):  
    bl_label = "Retopology"
    bl_space_type = 'VIEW_3D'
    bl_idname = "object.retopology_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'

        layout.operator("cgcookie.retop_contour", text="Draw Contours")  

def retopo_draw_callback(self,context):
    
    settings = context.user_preferences.addons['contour_tools'].preferences

    stroke_color = settings.stroke_rgb
    handle_color = settings.handle_rgb
    hover_color = settings.actv_rgb
    g_color = settings.geom_rgb
    v_color = settings.vert_rgb

    for cut_collection in [self.cut_lines]: #, self.valid_cuts]:
        if len(cut_collection) > 0:
            for i, c_cut in enumerate(cut_collection):
                if self.widget_interaction and self.drag_target == c_cut:
                    interact = True
                    #point1 = contour_utilities.get_com(c_cut.verts_simple)
                    #point2 = c_cut.plane_com
                    #point3 = c_cut.plane_com + c_cut.plane_no
                
                    #l_color = (settings.vert_rgb[0],settings.vert_rgb[1],settings.vert_rgb[2],1)
                    #v_color = (settings.geom_rgb[0],settings.geom_rgb[1],settings.geom_rgb[2],1)
                    #contour_utilities.draw_polyline_from_3dpoints(context, [point2,point1], l_color, settings.line_thick,"GL_LINE_STIPPLE")
                    #contour_utilities.draw_polyline_from_3dpoints(context, [point2,point3], l_color, settings.line_thick,"GL_LINE_STIPPLE")
                
                    #contour_utilities.draw_3d_points(context, [point1,point2,point3], v_color, settings.vert_size)

                else:
                    interact = False
                c_cut.draw(context, settings,three_dimensional = self.navigating, interacting = interact)
        
                if c_cut.verts_simple != [] and settings.show_cut_indices:
                    loc = location_3d_to_region_2d(context.region, context.space_data.region_3d, c_cut.verts_simple[0])
                    blf.position(0, loc[0], loc[1], 0)
                    blf.draw(0, str(i))

    if self.follow_lines != [] and settings.show_edges:
        for follow in self.follow_lines:
            contour_utilities.draw_polyline_from_3dpoints(context, follow, (g_color[0], g_color[1], g_color[2], 1), settings.line_thick,"GL_LINE_STIPPLE")

    if self.cut_line_widget and settings.draw_widget:
        self.cut_line_widget.draw(context)
        
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
        settings = context.user_preferences.addons['contour_tools'].preferences
        
        
        if event.type == 'Z' and event.ctrl and event.value == 'PRESS':
            self.undo_action(context)
        
        if event.type in {'G','R','K'} and event.value == 'PRESS' and not self.hot_key and self.selected:
            
            self.hot_key = event.type
            
            #UNDO CODE
            self.create_undo_entry('TRANSFORM', self.selected)
            
            if event.type == 'G' and self.selected:
                self.widget_interaction = True
                if self.valid_cuts and len(self.valid_cuts) and self.selected in self.valid_cuts:
                    ind = self.valid_cuts.index(self.selected)
                    ahead = ind + 1
                    behind = ind - 1
                
                    if ahead < len(self.cut_lines):
                        a_line = self.valid_cuts[ahead]
                    else:
                        a_line = None
                
                    if behind > - 1:
                        b_line = self.valid_cuts[behind]
                    else:
                        b_line = None
                        
                else:
                    a_line = None
                    b_line = None
                    
                self.cut_line_widget = CutLineManipulatorWidget(context, settings, self.selected,
                                                                 event.mouse_region_x,event.mouse_region_y,
                                                                 cut_line_a = a_line, cut_line_b = b_line,
                                                                 hotkey = 'G')
                self.cut_line_widget.transform_mode = 'EDGE_SLIDE'
                self.cut_line_widget.derive_screen(context)
                
            elif event.type == 'R' and self.selected:
                
                screen_loc = location_3d_to_region_2d(context.region, context.space_data.region_3d, self.selected.plane_com)
                self.cut_line_widget = CutLineManipulatorWidget(context, settings, self.selected,
                                                                 screen_loc[0], screen_loc[1],
                                                                 cut_line_a = None, cut_line_b = None,
                                                                 hotkey = 'R')
                self.cut_line_widget.initial_x = event.mouse_region_x
                self.cut_line_widget.initial_y = event.mouse_region_y
                self.cut_line_widget.transform_mode = 'ROTATE_VIEW'
                self.cut_line_widget.derive_screen(context)
            
            
            #elif event.type == 'K' and self.selected:
                
                #self.selected.adjust_cut_to_object_surface(self.original_form)
                #self.selected.generic_3_axis_from_normal()
                #self.selected.hit_object(context, self.original_form, method = '3_AXIS_COM')
                #self.selected.cut_object(context, self.original_form, self.bme)
                #self.selected.simplify_cross(self.segments)
                #self.selected.update_com()
                #self.align_cut(self.selected, 'BETWEEN')         
                #self.selected.update_screen_coords(context)
                #self.connect_valid_cuts_to_make_mesh()
                
        if not self.hot_key and event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            
            
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
                print('we must bridge')
                bridge =True
                a = len(self.sel_verts)
                if not context.tool_settings.mesh_select_mode[0]:
                    context.tool_settings.mesh_select_mode[0] = True
                    restore_vert_mode = True
                else:
                    restore_vert_mode = False
                    
            for i, vert in enumerate(self.verts):
                new_vert = bm.verts.new(tuple(reto_imx * (orig_mx * vert)))
                bmverts.append(new_vert)
                
                #because of the way the verts are ordered
                #the first loop will be verts [0:a-1]
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
            
            #used to free the bmesh, now it stays in cache
            #self.dest_bme.free()
            #self.bme.free()
            #if self.tmp_ob:
                #context.scene.objects.unlink(self.tmp_ob)
                #me = self.tmp_ob.data
                #self.tmp_ob.user_clear()
                #bpy.data.objects.remove(self.tmp_ob)
                #bpy.data.meshes.remove(me)
            if back_to_edit:
                #not sure why this is necessary?
                #TODO:  make this bmesh data manipulation instead of bpy.ops
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle()
                if self.sel_verts and len(self.sel_verts):
                    bpy.ops.mesh.bridge_edge_loops(type='SINGLE', use_merge=False, merge_factor=0.5, number_cuts=0, interpolation='PATH', smoothness=1, profile_shape_factor=0, profile_shape='SMOOTH')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    if restore_vert_mode:
                        context.tool_settings.mesh_select_mode[0] = False
            return{'FINISHED'}
        
        elif event.type == 'S' and event.value == 'PRESS':
            if self.selected and self.selected in self.cut_lines:
                context.scene.cursor_location = self.selected.plane_com
                action = 'Snap cursor to selected loop'
                message = "%s: %s" % (event.type, action)
                context.area.header_text_set(text = message)
        
        elif event.type == 'C' and event.value == 'PRESS':
            bpy.ops.view3d.view_center_cursor()
            action = 'Center cursor'
            message = "%s: %s" % (event.type, action)
            context.area.header_text_set(text = message)
            
        elif event.type == 'A' and event.value == 'PRESS':
            #verify the correct circumstance
            
            #strings to build report message
            if event.ctrl:
                ctrl_str = 'Ctrl + '
            else:
                ctrl_str = ''
                
            if event.shift:
                shift_str = 'Shift + '
            else:
                shift_str = ''
                
            if len(self.valid_cuts) and self.selected and self.selected.desc == 'CUT_LINE' and not self.widget_interaction:
                
                #UNDO CODE
                self.create_undo_entry('ALIGN', self.selected)
            
                if not event.ctrl and not event.shift:
                    action = 'Align to neighbors'
                    act = 'BETWEEN'
                    print('between')
                        
                #align ahead    
                elif event.ctrl and not event.shift:
                    
                    action = 'Align to next cut'
                    act = 'FORWARD'
                    print('FORWARD')
                    
                #align behind    
                elif event.shift and not event.ctrl:
                    action = 'Align to previous cut'
                    act = 'BACKWARD'
                    print('BACKWARD')

                print('ALIGNING CUT LINE 786 with hotkey A')
                self.align_cut(self.selected, mode = act, fine_grain = True)
                self.selected.simplify_cross(self.segments)
                
                self.selected.update_screen_coords(context)
                self.connect_valid_cuts_to_make_mesh()
                
                message = ctrl_str + shift_str + event.type + ' :  ' + action
                context.area.header_text_set(text = message)
                
        elif event.type == 'MOUSEMOVE':
                
            if self.drag and self.drag_target:
            
                if self.drag_target.desc == 'CUT_LINE' and self.widget_interaction:
                    
                    #[new_com, new_no, new_tan]
                    recalc_vals = self.cut_line_widget.user_interaction(context, event.mouse_region_x,event.mouse_region_y)

                    if settings.live_update:     
                            self.drag_target.hit_object(context, self.original_form, method = '3_AXIS_COM')
                            self.drag_target.cut_object(context, self.original_form, self.bme)
                            self.hover_target.simplify_cross(self.segments)
                            if 'REHIT' in recalc_vals:
                                print('updating the com')
                                self.hover_target.update_com()
                                
                            self.hover_target.update_screen_coords(context)
                            
                    message = "Widget interaction: " + str(self.cut_line_widget.transform_mode)
                    context.area.header_text_set(text = message)

                elif self.drag_target.desc == 'CONTROL_POINT':
                    self.drag_target.x = event.mouse_region_x
                    self.drag_target.y = event.mouse_region_y
                    self.drag_target.screen_to_world(context)
            
            elif self.hot_key and self.selected: 
                recalc_vals = self.cut_line_widget.user_interaction(context, event.mouse_region_x,event.mouse_region_y)
                if settings.live_update:     
                    self.selected.hit_object(context, self.original_form, method = '3_AXIS_COM')
                    self.selected.cut_object(context, self.original_form, self.bme)
                    self.selected.simplify_cross(self.segments)
                    if 'REHIT' in recalc_vals:
                        self.selected.update_com()
                        
                    self.selected.update_screen_coords(context)
        
                   
            #else detect proximity to items around
            else:
                #identify hover target for highlighting
                if self.cut_lines != []:
                    new_target = False
                    target_at_all = False
                    prospective_targets = []
                    for c_cut in self.cut_lines:
                        c_cut.geom_color = (settings.actv_rgb[0],settings.actv_rgb[1],settings.actv_rgb[2],1) 
                        h_target = c_cut.active_element(context,event.mouse_region_x,event.mouse_region_y)
                        if h_target:
                            target_at_all = True
                            new_target = h_target != self.hover_target
                            if new_target:
                                prospective_targets.append(h_target)
                                self.hover_target = h_target
                                if self.hover_target.desc == 'CUT_LINE':
                                    
                                    if self.valid_cuts and len(self.valid_cuts) and self.hover_target in self.valid_cuts:
                                        ind = self.valid_cuts.index(self.hover_target)
                                        ahead = ind + 1
                                        behind = ind - 1
                                    
                                        if ahead < len(self.cut_lines):
                                            a_line = self.valid_cuts[ahead]
                                        else:
                                            a_line = None
                                    
                                        if behind > - 1:
                                            b_line = self.valid_cuts[behind]
                                        else:
                                            b_line = None
                                            
                                    else:
                                        a_line = None
                                        b_line = None
                                        
                                    self.cut_line_widget = CutLineManipulatorWidget(context, settings, self.hover_target, event.mouse_region_x,event.mouse_region_y,cut_line_a = a_line, cut_line_b = b_line)
                                    self.cut_line_widget.derive_screen(context)
                                    
                            else:
                                if self.cut_line_widget:
                                    self.cut_line_widget.x = event.mouse_region_x
                                    self.cut_line_widget.y = event.mouse_region_y
                                    self.cut_line_widget.derive_screen(context)
                        elif not c_cut.select:
                            c_cut.geom_color = (settings.geom_rgb[0],settings.geom_rgb[1],settings.geom_rgb[2],1)          
                    if not target_at_all:
                        self.hover_target = None
                        self.cut_line_widget = None
                        context.area.header_text_set(self.header_message)
                                
            if self.navigating:
                for cut in self.cut_lines:
                    cut.update_screen_coords(context)
                    
            return {'RUNNING_MODAL'}
        
        #escape
        elif event.type== 'ESC' and not self.hot_key and event.value == 'PRESS':
            #TODO:  Delete the destination ob in case we dont need it
            #need to carefully implement this so people dont delete their wok
            
            #clean up callbacks to prevent crash
            context.area.header_text_set()
            contour_utilities.callback_cleanup(self,context)
            
            #don't free it anymore, let the clear cache do that
            #self.bme.free()
            #if self.tmp_ob:
                #context.scene.objects.unlink(self.tmp_ob)
                #me = self.tmp_ob.data
                #self.tmp_ob.user_clear()
                #bpy.data.objects.remove(self.tmp_ob)
                #bpy.data.meshes.remove(me)
            return {'CANCELLED'}  
        
        elif event.type in {'MIDDLEMOUSE', 'NUMPAD_2', 'NUMPAD_4', 'NUMPAD_6', 'NUMPAD_8', 'NUMPAD_1', 'NUMPAD_3', 'NUMPAD_5', 'NUMPAD_7', 'NUMPAD_9'}:

            if event.value == 'PRESS':
                self.navigating = True
                
            else:
                self.navigating = False
                
            for cut_line in self.cut_lines:
                if cut_line.head and cut_line.head.world_position:
                    cut_line.head.screen_from_world(context)
                    cut_line.tail.screen_from_world(context)
                    cut_line.update_screen_coords(context)
            return {'PASS_THROUGH'}
        
        
        elif event.type == 'RIGHTMOUSE' and event.value == 'PRESS' and self.hover_target and not self.hot_key or \
             event.type == 'X' and event.value == 'PRESS' and self.selected and not self.hot_key:
            
            if self.hover_target and event.type == 'RIGHTMOUSE':
                
                #UNDO CODE
                self.create_undo_entry('DELETE', self.hover_target)
                
                if self.hover_target in self.valid_cuts:
                    self.valid_cuts.remove(self.hover_target)
                self.cut_lines.remove(self.hover_target)
                self.hover_target = None
                self.widget_interaction = False
                self.cut_line_widget = None
                self.selected = None
            
            elif self.selected and event.type == 'X':
                
                #UNDO CODE
                self.create_undo_entry('DELETE', self.selected)
                
                if self.selected in self.valid_cuts:
                    self.valid_cuts.remove(self.selected)
                    
                self.cut_lines.remove(self.selected)
                self.hover_target = None
                self.widget_interaction = False
                self.cut_line_widget = None
                self.selected = None

            
                  
            self.connect_valid_cuts_to_make_mesh()
            
            action = 'Delete selected loop'
            message = "%s: %s" % (event.type, action)
            context.area.header_text_set(text = message)  
            return {'RUNNING_MODAL'}
            
    

        elif  event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS' and self.hot_key:
            
            self.cut_line_widget.cancel_transform()
            
            #the widget puts the item back so we can pop an undo stack
            contour_undo_cache.pop()
            
            self.selected.cut_object(context, self.original_form, self.bme)
            self.selected.simplify_cross(self.segments)
            self.selected.update_com()
            self.selected.update_screen_coords(context)
            
            self.hot_key = False
            self.cut_line_widget = None
            self.widget_interaction = False
            

        if event.type in {'LEFT_ARROW','RIGHT_ARROW'} and event.value == 'PRESS':
            if self.selected and self.selected.desc == 'CUT_LINE':
                
                #UNDO CODE
                if len(contour_undo_cache) > 0:
                    #make sure we aren't stacking a ton of shift undos
                    if contour_undo_cache[-1]['action'] != 'SHIFT' and contour_undo_cache[-1]['cut'] != self.cut_lines.index(self.selected):
                        self.create_undo_entry('SHIFT', self.selected)
                        
                else:
                    self.create_undo_entry('SHIFT', self.selected)
                
                
                print('shift before: %f', self.selected.shift)
                if event.type == 'LEFT_ARROW':
                    
                    self.selected.shift -= .05
                    action = 'Decrease'
                    if self.selected.shift < -1:
                        self.selected.shift = -1   
                
                if event.type == 'RIGHT_ARROW':
                    action = 'Increase'
                    self.selected.shift += .05
                    if self.selected.shift > 1:
                        self.selected.shift = 1
                
                print('shift after: %f', self.selected.shift)
                self.selected.simplify_cross(self.segments)
                self.align_cut(self.selected, mode = 'BETWEEN', fine_grain = False)
                self.selected.update_screen_coords(context)
                self.connect_valid_cuts_to_make_mesh()
                message = "%s: %s shift to %f" % (event.type, action, self.selected.shift)
                context.area.header_text_set(text = message)

        
        
        if event.type in {'WHEELDOWNMOUSE','WHEELUPMOUSE','NUMPAD_PLUS','NUMPAD_MINUS'}:
            
            if (event.type == 'WHEELUPMOUSE' and event.ctrl) or (event.type == 'NUMPAD_PLUS' and event.value == 'PRESS'):
                
                #UNDO CODE
                if len(contour_undo_cache) > 0:
                    #make sure we aren't stacking a ton of segment undos
                    if contour_undo_cache[-1]['action'] != 'SEGMENT':
                        self.create_undo_entry('SEGMENT', None)
                        
                else:
                    self.create_undo_entry('SEGMENT', None)
                

                if not self.sel_verts: #used to be elif
                    self.segments += 1

                
                    for cut_line in self.cut_lines:
                        if not cut_line.verts:
                            print('recutting this line because it has no freaking verts?')
                            hit = cut_line.hit_object(context, self.original_form)
                            if hit:
                                cut_line.cut_object(context, self.original_form, self.bme)
                                cut_line.simplify_cross(self.segments)
                                cut_line.update_com()
                                cut_line.update_screen_coords(context)
                            else:
                                self.cut_lines.remove(cut_line)
    
                        else:
                            new_bulk_shift = round((cut_line.int_shift + cut_line.shift) * self.segments/(self.segments - 1))
                            new_fine_shift = self.segments/(self.segments - 1) * (cut_line.shift + cut_line.int_shift) - new_bulk_shift
                            print('bulk shift:  %i and fine shift:  %f' % (new_bulk_shift, new_fine_shift))
                            cut_line.int_shift = new_bulk_shift
                            cut_line.shift = new_fine_shift
                            
                            cut_line.simplify_cross(self.segments)
                            cut_line.update_screen_coords(context)
                
                message = "%s: Set segments to %i" % (event.type, self.segments)
                context.area.header_text_set(text = message)
                
                self.connect_valid_cuts_to_make_mesh()
                return {'RUNNING_MODAL'}
            
            elif (event.type == 'WHEELDOWNMOUSE' and event.ctrl) or (event.type == 'NUMPAD_MINUS' and event.value == 'PRESS'):
                
                #UNDO CODE
                if len(contour_undo_cache) > 0:
                    #make sure we aren't stacking a ton of segment undos
                    if contour_undo_cache[-1]['action'] != 'SEGMENT':
                        self.create_undo_entry('SEGMENT', None)
                        
                else:
                    self.create_undo_entry('SEGMENT', None)
                
                if not self.sel_verts and self.segments >= 4:
                    self.segments -= 1
                    
                    for cut_line in self.cut_lines:
                        if not cut_line.verts:
                            hit = cut_line.hit_object(context, self.original_form)
                            if hit:
                                cut_line.cut_object(context, self.original_form, self.bme)
                                cut_line.simplify_cross(self.segments)
                                cut_line.update_com()
                                cut_line.update_screen_coords(context)
                            else:
                                self.cut_lines.remove(cut_line)
                            
                        else:
                            new_bulk_shift = round((cut_line.int_shift + cut_line.shift) * self.segments/(self.segments + 1))
                            new_fine_shift = self.segments/(self.segments + 1) * (cut_line.shift + cut_line.int_shift) - new_bulk_shift
                            print('bulk shift:  %i and fine shift:  %f' % (new_bulk_shift, new_fine_shift))
                            cut_line.int_shift = new_bulk_shift
                            cut_line.shift = new_fine_shift
                            cut_line.simplify_cross(self.segments)
                            cut_line.update_screen_coords(context)
                    
                #else:  #redundant, 
                    #self.segments = len(self.sel_edges)
        
                #message = "Segments: %i" % self.segments
                message = "%s: Set segments to %i" % (event.type, self.segments)
                context.area.header_text_set(text = message)
                
                self.connect_valid_cuts_to_make_mesh()
                
                return {'RUNNING_MODAL'}
            
            
            else:
                for cut_line in self.cut_lines:
                    if cut_line.verts_simple != []:
                        #cut_line.head.screen_from_world(context)
                        #cut_line.tail.screen_from_world(context)
                        cut_line.update_screen_coords(context)
                return{'PASS_THROUGH'}  
        
        #event click
        elif event.type == 'LEFTMOUSE':
            
            if event.value == 'RELEASE':
                if self.drag and self.drag_target:
                    
                    #user just finished using the widget
                    if self.drag_target.desc == 'CUT_LINE' and self.widget_interaction:
                        if not settings.live_update:
                            self.drag_target.hit_object(context, self.original_form, method = '3_AXIS_COM')
                            self.drag_target.cut_object(context, self.original_form, self.bme)
                            self.hover_target.simplify_cross(self.segments)    
                            self.hover_target.update_com()        
                            self.hover_target.update_screen_coords(context)
                           
                        self.align_cut(self.drag_target, mode = 'BETWEEN')
                        self.connect_valid_cuts_to_make_mesh()

                        
                    #a new cut is made and this is the release of the handle
                    #the handle is the drag_target    
                    elif self.drag_target.desc != 'CUT_LINE' and not self.widget_interaction:
                        self.drag_target.x = event.mouse_region_x
                        self.drag_target.y = event.mouse_region_y
                        new_cut = self.drag_target.parent
                        
                        #hit the mesh for the first time
                        hit = new_cut.hit_object(context, self.original_form, method = 'VIEW')
                        
                        if hit:
                            
                            new_cut.cut_object(context, self.original_form, self.bme)
                            new_cut.simplify_cross(self.segments)
                            new_cut.update_com()
                            new_cut.update_screen_coords(context)
                            new_cut.head = None
                            new_cut.tail = None
                            
                            #TODO...delete this and see what happens
                            if self.new:
                                self.new = False
                            
                            #try to insert the new cut into the existing cut chain    
                            #self.insert_new_cut(new_cut, self.settings.search_factor)
                            
                            self.sort_cuts()
                            if new_cut in self.valid_cuts:
                                self.align_cut(new_cut, mode = 'BETWEEN')
                                
                                #UNDO CODE
                                self.create_undo_entry('CREATE', new_cut)
                        
                                self.connect_valid_cuts_to_make_mesh()
                        else:
                            self.cut_lines.remove(new_cut)
                            self.drag_target = None
                            if self.new:
                                self.new = False

                
                #clear the drag and hover
                self.drag = False
                self.hover_target = None
                if self.widget_interaction:
                    self.widget_interaction = False
    
                return {'RUNNING_MODAL'}
        
            if event.value == 'PRESS':
                
                if not self.hot_key:
                    
                    #make sure we have something under there
                    if self.hover_target:
                        
                        #we drag until we release unless we are just selecting
                        #this initiates 
                        if not event.ctrl:
                            self.drag = True
                            self.drag_target = self.hover_target
                            
                            ###Implied that we are on a cut_line here
                            #TODO if we have other objects available to use
                            self.widget_interaction = True
                            
                            self.create_undo_entry('TRANSFORM', self.drag_target)
                            
                        #we are just selecting    
                        else:
                            self.drag = False
                            self.drag_target = None
                            self.widget_interaction = False
                            
                            #perhaps this is neeed to crush the widget?
                            if self.cut_line_widget:
                                del self.cut_line_widget
                                self.cut_line_widget = None
                    
                        self.hover_target.select = True
                        self.selected = self.hover_target    
                        for cut in self.cut_lines:
                            if cut != self.hover_target:
                                cut.select = False
    
                    #No active cut line under mouse -> make a new one
                    #we don't carer about ctrl
                    elif not self.hover_target:
                        v3d = context.space_data
                        self.drag = True
                        
                        
                        #clear selection (perhaps self.selected.select = False, self.selected = None)
                        for cut in self.cut_lines:
                            cut.select = False
                            
                        s_color = (settings.stroke_rgb[0],settings.stroke_rgb[1],settings.stroke_rgb[2],1)
                        h_color = (settings.handle_rgb[0],settings.handle_rgb[1],settings.handle_rgb[2],1)
                        g_color = (settings.geom_rgb[0],settings.geom_rgb[1],settings.geom_rgb[2],1)
                        v_color = (settings.vert_rgb[0],settings.vert_rgb[1],settings.vert_rgb[2],1)
    
                        self.cut_lines.append(ContourCutLine(event.mouse_region_x, event.mouse_region_y,# view,
                                                             stroke_color = s_color,
                                                             handle_color = h_color,
                                                             geom_color = g_color,
                                                             vert_color = v_color))
                        self.drag_target = self.cut_lines[-1].tail
                        self.new = True
                        self.selected = self.cut_lines[-1]
                        
                        #UNDO CODE
                        #the undo for creation will be in the mouse release
                    
                    return {'RUNNING_MODAL'}
                
                elif self.hot_key and self.selected: #self.hotkey exists.
                    
                    self.selected.hit_object(context, self.original_form, method = '3_AXIS_COM')
                    self.selected.cut_object(context, self.original_form, self.bme)
                    self.selected.simplify_cross(self.segments)
                            
                    self.selected.update_com()
                    self.align_cut(self.selected, mode='BETWEEN', fine_grain = True)      
                    self.selected.update_screen_coords(context)
                            
                            
                    self.hot_key = None
                    self.widget_interaction = False
                    self.cut_line_widget = None
                    
                    self.connect_valid_cuts_to_make_mesh()
                    return {'RUNNING_MODAL'}
                  
            return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}
        #ret_val = retopo_modal(self, context, event)
        #print('modal ret val')
        #print(ret_val)
        #return ret_val
    def write_to_cache(self,tool_type):
        global contour_cache
        
        if tool_type in contour_cache:
            del contour_cache[tool_type]
            
        if len(self.valid_cuts):
            normals = [cut.plane_no for cut in self.valid_cuts]
            x_vecs = [cut.vec_x for cut in self.valid_cuts]
            y_vecs = [cut.vec_y for cut in self.valid_cuts]
            plane_pts = [cut.plane_pt for cut in self.valid_cuts]
            seeds = [cut.seed_face_index for cut in self.valid_cuts]
            fine_shifts = [cut.shift for cut in self.valid_cuts]
            int_shifts = [cut.int_shift for cut in self.valid_cuts]
            verts = [cut.verts for cut in self.valid_cuts]
            verts_simple = [cut.verts_simple for cut in self.valid_cuts]
            
            
            #todo, make this a little betetr
            validate = [self.original_form.name, len(self.bme.faces), len(self.bme.verts)]
            contour_cache[tool_type] = {'validate': validate,
                                        'normals': normals,
                                        'x_vecs':x_vecs,
                                        'y_vecs':y_vecs,
                                        'plane_pts':plane_pts,
                                        'seeds':seeds,
                                        'shifts':fine_shifts,
                                        'int_shifts':int_shifts,
                                        'segments': self.segments}#,
                                        #'verts':verts,
                                        #'verts_simple':verts_simple}
    
    def load_from_cache(self,context, tool_type,clip):
        settings = context.user_preferences.addons['contour_tools'].preferences
        if tool_type not in contour_cache:
            return None
        else:
            data = contour_cache[tool_type]
            if [self.original_form.name, len(self.bme.faces), len(self.bme.verts)] == data['validate']:
                normals = data['normals']
                x_vecs = data['x_vecs']
                y_vecs = data['y_vecs']
                plane_pts = data['plane_pts']
                #verts = data['verts']
                #verts_simple = data['verts_simple']
                seeds = data['seeds']
                shifts = data['shifts']
                int_shifts = data['int_shifts']
                segments = data['segments']
                
                
                #settings and things
                (settings.geom_rgb[0],settings.geom_rgb[1],settings.geom_rgb[2],1)
                gc = settings.geom_rgb
                lc = settings.stroke_rgb
                vc = settings.vert_rgb
                hc = settings.handle_rgb
                
                g_color = (gc[0],gc[1],gc[2],1)
                l_color = (lc[0],lc[1],lc[2],1)
                v_color = (vc[0],vc[1],vc[2],1)
                h_color = (hc[0],hc[1],hc[2],1)
        
                for i, plane_no in enumerate(normals):
                    if i > (len(normals) - 1- clip): continue
                    cut = ContourCutLine(0, 0, line_width = settings.line_thick, stroke_color = l_color, handle_color = h_color, geom_color = g_color, vert_color = v_color)
                    cut.plane_no = plane_no
                    cut.seed_face_index = seeds[i]
                    cut.vec_x = x_vecs[i]
                    cut.vec_y = y_vecs[i]
                    cut.plane_pt = plane_pts[i]
                    cut.shift = shifts[i]
                    cut.int_shift = int_shifts[i]
                    
                    cut.cut_object(context, self.original_form, self.bme)
                    cut.simplify_cross(segments)
                    cut.update_com()   
                    #cut.verts = verts[i]
                    #cut.verts_simple = verts_simple[i]     
                    cut.update_screen_coords(context) 
                    cut.select = False  
                    self.cut_lines.append(cut)
                    self.valid_cuts.append(cut)
                    
                self.connect_valid_cuts_to_make_mesh()
                    
            
    def create_undo_entry(self, action, cut):
    
        available_actions = {'CREATE','DELETE','TRANSFORM','SHIFT','ALIGN','SEGMENT'}
        if action not in available_actions:
            return None
        
        print('undo push %s' % action)
        #it's a dictionary
        undo = {}
        
        #record what kind of action it is
        undo['action'] = action
        #how many segments are
        undo['segments'] = self.segments
        
        #these are the props we will record about a cut
        cut_props = ['plane_com',
                     'plane_no',
                     'plane_pt',
                     'seed_face_index',
                     'shift',
                     'int_shift',
                     'vec_x',
                     'vec_y']
    
        #record the relevant props
        if cut:
            for prop in cut_props:
                undo[prop] = getattr(cut, prop) 
            
        if action in {'DELETE'}:
            #Special case, we will actually keep the cut in cache
            #to put it back later
            undo['cut'] = cut
            
        elif action == 'SEGMENT':
            undo['cut'] = None
        else:
            undo['cut'] = self.cut_lines.index(cut)
            
        contour_undo_cache.append(undo)
        print('the undo cache grew, but this size may be irrelevant because of containers etc')
        print(sys.getsizeof(contour_undo_cache))
    
    def undo_action(self,context):
        
        if len(contour_undo_cache) > 0:
            undo = contour_undo_cache.pop()
            
            action = undo['action']
            
            #this may be an actual cut line
            #or it may be an index?
            
            #these are the props we will recorded about a cut
            cut_props = ['plane_com',
                         'plane_no',
                         'plane_pt',
                         'seed_face_index',
                         'shift',
                         'int_shift',
                         'vec_x',
                         'vec_y']
            
            if action == 'CREATE':
                cut = self.cut_lines[undo['cut']]
                if cut in self.valid_cuts:
                    self.valid_cuts.remove(cut)
                if cut in self.cut_lines:
                    self.cut_lines.remove(cut)
                    
                self.connect_valid_cuts_to_make_mesh()
                    
            elif action == 'DELETE':
                #in this circumstance...it's actually a cut
                cut = undo['cut']
                self.cut_lines.append(cut)
                self.sort_cuts()
                self.connect_valid_cuts_to_make_mesh()
                
                
            elif action in {'TRANSFORM', 'SHIFT','ALIGN'}:
                cut = self.cut_lines[undo['cut']]
                for prop in cut_props:
                    setattr(cut, prop, undo[prop])
                    
                    
                self.selected.cut_object(context, self.original_form, self.bme)
                self.selected.simplify_cross(self.segments)
                self.selected.update_screen_coords(context)
                self.connect_valid_cuts_to_make_mesh()
                
            elif action == 'SEGMENT':
                old_segments = self.segments
                self.segments = undo['segments']
                ratio = self.segments/old_segments
                for cut_line in self.cut_lines:
                    new_bulk_shift = round((cut_line.int_shift + cut_line.shift) * ratio)
                    new_fine_shift = ratio * (cut_line.shift + cut_line.int_shift) - new_bulk_shift
                                
                    cut_line.int_shift = new_bulk_shift
                    cut_line.shift = new_fine_shift
                                
                    cut_line.simplify_cross(self.segments)
                    cut_line.update_screen_coords(context)
                
                self.connect_valid_cuts_to_make_mesh()
            
            
            
    def insert_new_cut(self,new_cut, search_rad = 1/8):
        print('beta testing')
        
        #the first cut
        if len(self.valid_cuts) == 0:
            print('welcome to the party')
            self.valid_cuts.append(new_cut)
            self.cut_lines.remove(new_cut)
            
            
            
        #make sure the cut is reasonably close
        #and oriented with the other one.
        elif len(self.valid_cuts) == 1:
            print('It takes 2 to the tango')
            established_cut = self.valid_cuts[0]
            
            insert = contour_utilities.com_mid_ray_test(new_cut, established_cut, 
                                                        self.original_form,
                                                        search_factor = self.settings.search_factor)
            if insert:
                self.valid_cuts.append(new_cut)
                self.cut_lines.remove(new_cut)        
                
                
        else:
            
            pt = new_cut.plane_com
            no = new_cut.plane_no
            
            test_ends = True
            #test in between to insert somewhere
            for i in range(0,len(self.valid_cuts)-1):
                
                com1 = self.valid_cuts[i].plane_com
                com2 = self.valid_cuts[i+1].plane_com
                
                
                insert = contour_utilities.com_line_cross_test(com1, com2, pt, no, self.settings.intersect_factor)
                
                if insert:
                    print('found a place to put it!')
                    self.valid_cuts.insert(i + 1, new_cut)
                    self.cut_lines.remove(new_cut)
                    test_ends = False
                    break
            
            #we didn't find a place to put it in between
            #now we should check the ends
            if test_ends:
                print('to the end (or start) of the line')
                insert_start = contour_utilities.com_mid_ray_test(new_cut, self.valid_cuts[0], 
                                                            self.original_form,
                                                            self.settings.search_factor)
                
                insert_end = contour_utilities.com_mid_ray_test(new_cut, self.valid_cuts[-1], 
                                                            self.original_form,
                                                            self.settings.search_factor)
                
                if insert_start and not insert_end:
                    self.valid_cuts.insert(0, new_cut)
                    
                elif insert_end: #if it works for both ends....still put it at end
                    self.valid_cuts.insert(len(self.valid_cuts) -1, new_cut)
                    
        print(self.cut_lines)
        print(self.valid_cuts)
                            
            
    def align_cut(self, cut, mode = 'BETWEEN', fine_grain = True):
        
        if len(self.valid_cuts) < 2:
            print('nothing to align with')
            return
        
        if cut not in self.valid_cuts:
            print('this cut is not connected to anything yet')
            return
        
        
        ind = self.valid_cuts.index(cut)
        ahead = ind + 1
        behind = ind - 1
                
        if ahead != len(self.valid_cuts):
            cut.align_to_other(self.valid_cuts[ahead], auto_align = fine_grain)
            shift_a = cut.shift
        else:
            shift_a = False
                    
        if behind != -1:
            cut.align_to_other(self.valid_cuts[behind], auto_align = fine_grain)
            shift_b = cut.shift
        else:
            shift_b = False    
        
        #align between
        if mode == 'BETWEEN':      
            if shift_a and shift_b:
                #In some circumstances this may be a problem if there is
                #an integer jump of verts around the ring
                self.selected.shift = .5 * (shift_a + shift_b)
                        
            #align ahead anyway
            elif shift_a:
                self.selected.shift = shift_a
            #align behind anyway
            else:
                self.selected.shift = shift_b
    
        #align ahead    
        elif mode == 'FORWARD':
            if shift_a:
                self.selected.shift = shift_a
                                
        #align behind    
        elif mode == 'BACKWARD':
            if shift_b:
                self.selected.shift = shift_b

    def sort_cuts(self):
        
        if len(self.cut_lines) < 2:
            print('waiting on other cut lines')
            self.verts = []
            self.edges = []
            self.face = []
            self.follow_lines = []
            return
        
        imx = self.original_form.matrix_world.inverted()
        
        #first criteria is check for lines which have succesfully cut
        #a mesh
        valid_cuts = [c_line for c_line in self.cut_lines if c_line.verts != [] and c_line.verts_simple != []]
        self.cut_lines = valid_cuts
        if len(valid_cuts) < 2:
            return
        


        #####order the cuts####
        
        #first make a list of the cut Center of Mass and normals
        #in the same order as valid cuts
        planes = [(cut.plane_com, cut.plane_no) for cut in valid_cuts]
        
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
                    C = .5 * (A + B)  #the midpoint of the line between them
                    
                    #we know the plane_pt is ON the mesh
                    #vs the COM of the loop which is inside the mesh (potentially)
                    #TODO: make this way beeter
                    
                    n = math.floor(len(valid_cuts[i].verts_simple)/3)
                    ray = A - valid_cuts[i].verts_simple[n]
                    #ray1 = A - valid_cuts[i].plane_pt  #valid_cuts[i].plane_tan.world_position
                    #ray2 = B - valid_cuts[m].plane_pt  #plane_tan.world_position
                    #ray = ray1.lerp(ray2,.5).normalized()
                    
                    #TODO: make 100 here actually be the approx radius of the two cuts :-)
                    hit = self.original_form.ray_cast(imx * (C + 100 * ray), imx * (C - 100 * ray))
                    
                    
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
                                #than this pair is invalide because there is a loop
                                #in between
                                check = intersect_point_line(v,A,B)
                                pair_length = (B - A).length/2
                                inval_length = (v - pt).length
                                if (check[1] >= 0 and check[1] <= 1 and inval_length < pair_length) or hit[2] == -1:
                                    print('invalid pair %s' % str(pair))
                                    print('the hit face index is value is %i' % hit[2])
                                    
                                    if pair in valid_pairs:
                                        valid_pairs.remove(pair)
        print('found valid pairs as follows')       
        print(valid_pairs)
        
        #TODO disect and comment this code
        if len(valid_pairs) == 0:
            print('no valid pairs!!')
        if len(valid_pairs) > 0:
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
            
            
            #clean out bad connections
            n_doubles = len(new_order) - len(set(new_order))
            if n_doubles > 0 + 1*self.settings.cyclic:
                print('we have some connectivity problems, doing our best')
                doubles = []
                for i in new_order:
                    if new_order.count(i) > 1 and i not in doubles:
                        doubles.append(i)
                        
                print(doubles)
                for repeat in doubles:
                    first = new_order.index(repeat)
                    n = new_order.index(repeat,first+1)
                    
                    print('The offending location is %i' % n)
                    #take out the 2nd occurence of the loop
                    #as long it's not the beginning/end of the loop
                    if n == len(new_order) - 1:
                        if not self.settings.cyclic:
                            new_order.pop(n)
                    else:
                        new_order.pop(n)
                        
                
                #resort based on first stroke drawn
                if 0 in new_order and new_order[0] != 0:
                    print('preshifted')
                    print(new_order)
                    
                    print('shifted verts')
                    
                    new_order = contour_utilities.list_shift(new_order, new_order.index(0))
                    print(new_order)
                        
            cuts_copy = valid_cuts.copy()
            valid_cuts = []
            for i, n in enumerate(new_order):
                
                valid_cuts.append(cuts_copy[n])
            
            #guaranteed editmode for this to happen
            #this makes sure we bridge the correct end
            #when we are done
            if self.sel_edges and len(self.sel_edges) and self.sel_verts and len(self.sel_verts) and self.existing_cut:
                
                #bridge_vert_vecs = [mx * v.co for v in self.sel_verts]
                bridge_loop_location = contour_utilities.get_com(self.existing_cut.verts_simple)
                
                loop_0_loc = contour_utilities.get_com(valid_cuts[0].verts_simple)
                loop_1_loc = contour_utilities.get_com(valid_cuts[-1].verts_simple)
                
                dist_0 = bridge_loop_location - loop_0_loc
                dist_1 = bridge_loop_location - loop_1_loc
                
                if dist_1.length < dist_0.length:
                    valid_cuts.reverse()
                self.existing_cut.align_to_other(valid_cuts[0], auto_align = False)
                    
                    
            del cuts_copy
            self.valid_cuts = valid_cuts
            
                
    
    def connect_valid_cuts_to_make_mesh(self):
        total_verts = []
        total_edges = []
        total_faces = []
        
        if len(self.valid_cuts) < 2:
            print('waiting on other cut lines')
            self.verts = []
            self.edges = []
            self.face = []
            self.follow_lines = []
            return
        
        imx = self.original_form.matrix_world.inverted()
        n_rings = len(self.valid_cuts)
        n_lines = len(self.valid_cuts[0].verts_simple)
        
        
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
        
        cyclic = 0 in self.valid_cuts[0].eds_simple[-1]
        
        #work out the connectivity faces:
        for j in range(0,n_rings - 1):
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
        
        self.write_to_cache('CUT_LINES')
  
    def invoke(self, context, event):
        #TODO Settings harmon CODE REVIEW
        settings = context.user_preferences.addons['contour_tools'].preferences
        
        self.valid_cut_inds = []
        
        #clear the undo cache
        contour_undo_cache = []
        
        #TODO Settings harmon CODE REVIEW
        self.settings = settings
        
        #if edit mode
        if context.mode == 'EDIT_MESH':
            
            #the active object will be the retopo object
            #whose geometry we will be augmenting
            self.destination_ob = context.object
            
            #get the destination mesh data
            self.dest_me = self.destination_ob.data
            
            #we will build this bmesh using from editmesh
            self.dest_bme = bmesh.from_edit_mesh(self.dest_me)
            
            #the selected object will be the original form
            #or we wil pull the mesh cache
            target = [ob for ob in context.selected_objects if ob.name != context.object.name][0]
            
            validation = object_validation(target)
            if 'valid' in contour_mesh_cache and contour_mesh_cache['valid'] == validation:
                use_cache = True
                print('willing and able to use the cache!')
            
            else:
                use_cache = False  #later, we will double check for ngons and things
                clear_mesh_cache()
                self.original_form = target
                
            
            #count and collect the selected edges if any
            ed_inds = [ed.index for ed in self.dest_bme.edges if ed.select]
            
            if len(ed_inds):
                vert_loops = contour_utilities.edge_loops_from_bmedges(self.dest_bme, ed_inds)
                if len(vert_loops) > 1:
                    self.report({'ERROR'}, 'single edge loop must be selected')
                    #TODO: clean up things and free the bmesh
                    return {'CANCELLED'}
                
                else:
                    best_loop = vert_loops[0]
                    if best_loop[-1] != best_loop[0]: #typically this means not cyclcic unless there is a tail []_
                        if len(list(set(best_loop))) == len(best_loop): #verify no tail
                            self.sel_edges = [ed for ed in self.dest_bme.edges if ed.select]
                        
                        else:
                            self.report({'ERROR'}, 'Edge loop selection has extra parts')
                            #TODO: clean up things and free the bmesh
                            return {'CANCELLED'}
                    else:
                        self.sel_edges = [ed for ed in self.dest_bme.edges if ed.select]
            else:
                self.sel_edges = None
                
            if self.sel_edges and len(self.sel_edges):
                self.sel_verts = [vert for vert in self.dest_bme.verts if vert.select]
                self.segments = len(self.sel_edges)
                self.existing_cut = ExistingVertList(self.sel_verts, self.sel_edges,self.destination_ob.matrix_world)
            else:
                self.existing_cut = None
                self.sel_verts = None
                self.segments = settings.vertex_count
            
        elif context.mode == 'OBJECT':
            
            #make the irrelevant variables None
            self.sel_edges = None
            self.sel_verts = None
            self.existing_cut = None
            
            #the active object will be the target
            target = context.object
            
            validation = object_validation(target)
            
            if 'valid' in contour_mesh_cache and contour_mesh_cache['valid'] == validation:
                use_cache = True
            
            else:
                use_cache = False
                self.original_form  = target
            
            #no temp bmesh needed in object mode
            #we will create a new obeject
            self.tmp_bme = None
            
            #new blank mesh data
            self.dest_me = bpy.data.meshes.new(target.name + "_recontour")
            
            #new object to hold mesh data
            self.destination_ob = bpy.data.objects.new(target.name + "_recontour",self.dest_me) #this is an empty currently
            self.destination_ob.matrix_world = target.matrix_world
            self.destination_ob.update_tag()
            
            #destination bmesh to operate on
            self.dest_bme = bmesh.new()
            self.dest_bme.from_mesh(self.dest_me)
            
            #default segments (spans)
            self.segments = settings.vertex_count
        
        #get the info about the original form
        #and convert it to a bmesh for fast connectivity info
        #or load the previous bme to save even more time
        
        
        
        if use_cache:
            start = time.time()
            print('the cache is valid for use!')
            
            self.bme = contour_mesh_cache['bme']
            print('loaded old bme in %f' % (time.time() - start))
            
            start = time.time()
            
            self.tmp_ob = contour_mesh_cache['tmp']
            print('loaded old tmp ob in %f' % (time.time() - start))
            
            if self.tmp_ob:
                self.original_form = self.tmp_ob
            else:
                self.original_form = target
              
        else:
    
            start = time.time()
            
            #clear any old saved data
            clear_mesh_cache()
            
            me = self.original_form.to_mesh(scene=context.scene, apply_modifiers=True, settings='PREVIEW')
            me.update()
            
            self.bme = bmesh.new()
            self.bme.from_mesh(me)
             
            #check for ngons, and if there are any...triangulate just the ngons
            #this mainly stems from the obj.ray_cast function returning triangulate
            #results and that it makes my cross section method easier.
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
                
                
                #I think this is needed to generate the data for raycasting
                #there may be some other way to update the object
                context.scene.objects.link(self.tmp_ob)
                self.tmp_ob.update_tag()
                context.scene.update() #this will slow things down
                context.scene.objects.unlink(self.tmp_ob)
                self.tmp_ob.matrix_world = self.original_form.matrix_world
                
                
                ###THIS IS A HUGELY IMPORTANT THING TO NOTICE!###
                #so maybe I need to make it more apparent or write it differnetly#
                #We are using a temporary duplicate to handle ray casting
                #and triangulation
                self.original_form = self.tmp_ob
                
            else:
                self.tmp_ob = None
            
            
            #store this stuff for next time.  We will most likely use it again
            #keep in mind, in some instances, tmp_ob is self.original orm
            #where as in others is it unique.  We want to use "target" here to
            #record validation because that is the the active or selected object
            #which is visible in the scene with a unique name.
            write_mesh_cache(target, self.tmp_ob, self.bme)
            print('derived new bme and any triangulations in %f' % (time.time() - start))

        message = "Segments: %i" % self.segments
        context.area.header_text_set(text = message)
            
        #temporary variable for testing
        self.ring_shift = 0
            
        #here is where we will cache verts edges and faces
        #unti lthe user confirms and we output a real mesh.
        self.verts = []
        self.edges = []
        self.faces = []
            
       
        if settings.use_x_ray:
            self.orig_x_ray = self.destination_ob.show_x_ray
            self.destination_ob.show_x_ray = True
            
            
        #These are all variables/values used in the user interaction
        #and drawing
        
        
        #is the user moving an existing entity or a new one.
        self.new = False 
        #is the mouse clicked and held down
        self.drag = False
        self.navigating = False
        
        #what is the user dragging..a cutline, a handle etc
        self.drag_target = None
        #what is the mouse over top of currently
        self.hover_target = None
        #keep track of selected cut_line (perhaps
        self.selected = None
        
        #Keep reference to a cutline widget
        #an keep track of whether or not we are
        #interacting with a widget.
        self.cut_line_widget = None
        self.widget_interaction = False
        self.hot_key = None
        
        #at the begniinging of a drag, we want to keep track
        #of where things started out
        self.initial_location_head = None
        self.initial_location_tail = None
        self.initial_location_mouse = None
        
        #This is a cache for any cut line whose connectivity
        #has not been established.
        self.cut_lines = []
        
        #this is a list of valid, ordered cuts.
        self.valid_cuts = []
    
        #this iw a collection of verts used for open GL drawing the spans
        self.follow_lines = []
        
        
        self.header_message = 'LMB: Select Stroke, RMB / X: Delete Sroke, , G: Translate, R: Rotate, A / Ctrl+A / Shift+A: Align, S: Cursor to Stroke, C: View to Cursor'
        context.area.header_text_set(self.header_message)
        if settings.recover:
            print('loading cache!')
            print(contour_cache['CUT_LINES'])
            self.load_from_cache(context, 'CUT_LINES', settings.recover_clip)
        #add in the draw callback and modal method
        self._handle = bpy.types.SpaceView3D.draw_handler_add(retopo_draw_callback, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}
    
    def execute(self,context):
        for line in self.cut_lines:
            print(line.view_dir)


def poly_sketch_draw_callback(self,context):
                
    if len(self.draw_cache):
        contour_utilities.draw_polyline_from_points(context, self.draw_cache, (1,.5,1,.8), 2, "GL_LINE_SMOOTH")
    
    if len(self.sketch_lines):    
        for line in self.sketch_lines:
            line.draw(context)

class CGCOOKIE_OT_retopo_poly_sketch(bpy.types.Operator):
    '''Sketch Toplogy on Forms with Contour Strokes'''
    bl_idname = "cgcookie.retopo_poly_sketch"
    bl_label = "Contour Poly Sketch"    
    
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
        settings = context.user_preferences.addons['contour_tools'].preferences
        
        
        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'MIDDLEMOUSE', 'NUMPAD_2', 'NUMPAD_4', 'NUMPAD_6', 'NUMPAD_8', 'NUMPAD_1', 'NUMPAD_3', 'NUMPAD_5', 'NUMPAD_7', 'NUMPAD_9'}:
            
            return {'PASS_THROUGH'}
            
            
        elif event.type == 'D':
            
            #toggle drawing
            if event.value == 'PRESS':
                self.draw = self.draw == False
            
            
            if self.draw:
                message = "Stick draw on"
                
            else:
                message = "Experimental poly_sketch 'D' to draw"
            context.area.header_text_set(text = message)    
            #else:
                #self.draw = False
                #self.draw_cache = []
                
            return {'RUNNING_MODAL'}
                
        elif event.type == 'MOUSEMOVE':
            
            if self.drag and self.draw:
                
                self.draw_cache.append((event.mouse_region_x,event.mouse_region_y))
                
            return {'RUNNING_MODAL'}
                    
                    
        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.drag = True
            else:
                if self.draw:
                    if len(self.draw_cache) > 10:
                        sketch = PolySkecthLine(self.draw_cache)
                        
                        print('raycasting now')
                        sketch.ray_cast_path(context, self.original_form)
                        sketch.find_knots()
                        sketch.smooth_path(ob = self.original_form)
                        sketch.create_vert_nodes()
                        
                        self.sketch_lines.append(sketch)
                    
                        self.draw_cache = []
                
                self.drag = False
                
            return {'RUNNING_MODAL'}
        
        elif event.type == 'ESC':
            contour_utilities.callback_cleanup(self,context)
            context.area.header_text_set()
            return {'CANCELLED'}
            
            
        else:
            return {'RUNNING_MODAL'}
    def invoke(self, context, event):
        #HINT you are in the poly sketch code
        
        #TODO Settings harmon CODE REVIEW
        settings = context.user_preferences.addons['contour_tools'].preferences
        
        #TODO Settings harmon CODE REVIEW
        self.settings = settings
        
        #if edit mode
        if context.mode == 'EDIT_MESH':
            
            #the active object will be the retopo object
            #whose geometry we will be augmenting
            self.destination_ob = context.object
            
            #get the destination mesh data
            self.dest_me = self.destination_ob.data
            
            #we will build this bmesh using from editmesh
            self.dest_bme = bmesh.from_edit_mesh(self.dest_me)
            
            #the selected object will be the original form
            #or we wil pull the mesh cache
            target = [ob for ob in context.selected_objects if ob.name != context.object.name][0]
            
            validation = object_validation(target)
            if 'valid' in contour_mesh_cache and contour_mesh_cache['valid'] == validation:
                use_cache = True
                print('willing and able to use the cache!')
            
            else:
                use_cache = False  #later, we will double check for ngons and things
                clear_mesh_cache()
                self.original_form = target
                
            
            #count and collect the selected edges if any
            ed_inds = [ed.index for ed in self.dest_bme.edges if ed.select]
            
            if len(ed_inds):
                vert_loops = contour_utilities.edge_loops_from_bmedges(self.dest_bme, ed_inds)
                if len(vert_loops) > 1:
                    self.report({'ERROR'}, 'single edge loop must be selected')
                    #TODO: clean up things and free the bmesh
                    return {'CANCELLED'}
                
                else:
                    best_loop = vert_loops[0]
                    if best_loop[-1] != best_loop[0]: #typically this means not cyclcic unless there is a tail []_
                        if len(list(set(best_loop))) == len(best_loop): #verify no tail
                            self.sel_edges = [ed for ed in self.dest_bme.edges if ed.select]
                        
                        else:
                            self.report({'ERROR'}, 'Edge loop selection has extra parts')
                            #TODO: clean up things and free the bmesh
                            return {'CANCELLED'}
                    else:
                        self.sel_edges = [ed for ed in self.dest_bme.edges if ed.select]
            else:
                self.sel_edges = None
                
            if self.sel_edges and len(self.sel_edges):
                self.sel_verts = [vert for vert in self.dest_bme.verts if vert.select]
                
                #TODO...allow extnesion of selections
                #self.segments = len(self.sel_edges)
                #self.existing_cut = ExistingVertList(self.sel_verts, self.sel_edges,self.destination_ob.matrix_world)
            else:
                #self.existing_cut = None
                self.sel_verts = None
                self.segments = settings.vertex_count
            
        elif context.mode == 'OBJECT':
            
            #make the irrelevant variables None
            self.sel_edges = None
            self.sel_verts = None
            #self.existing_cut = None
            
            #the active object will be the target
            target = context.object
            
            validation = object_validation(target)
            
            if 'valid' in contour_mesh_cache and contour_mesh_cache['valid'] == validation:
                use_cache = True
            
            else:
                use_cache = False
                self.original_form  = target
            
            #no temp bmesh needed in object mode
            #we will create a new obeject
            self.tmp_bme = None
            
            #new blank mesh data
            self.dest_me = bpy.data.meshes.new(target.name + "_recontour")
            
            #new object to hold mesh data
            self.destination_ob = bpy.data.objects.new(target.name + "_recontour",self.dest_me) #this is an empty currently
            self.destination_ob.matrix_world = target.matrix_world
            self.destination_ob.update_tag()
            
            #destination bmesh to operate on
            self.dest_bme = bmesh.new()
            self.dest_bme.from_mesh(self.dest_me)
            
            #default segments (spans)
            self.segments = settings.vertex_count
        
        #get the info about the original form
        #and convert it to a bmesh for fast connectivity info
        #or load the previous bme to save even more time
        
        
        
        if use_cache:
            start = time.time()
            print('the cache is valid for use!')
            
            self.bme = contour_mesh_cache['bme']
            print('loaded old bme in %f' % (time.time() - start))
            
            start = time.time()
            
            self.tmp_ob = contour_mesh_cache['tmp']
            print('loaded old tmp ob in %f' % (time.time() - start))
            
            if self.tmp_ob:
                self.original_form = self.tmp_ob
            else:
                self.original_form = target
              
        else:
    
            start = time.time()
            
            #clear any old saved data
            clear_mesh_cache()
            
            me = self.original_form.to_mesh(scene=context.scene, apply_modifiers=True, settings='PREVIEW')
            self.bme = bmesh.new()
            self.bme.from_mesh(me)
             
            #check for ngons, and if there are any...triangulate just the ngons
            #this mainly stems from the obj.ray_cast function returning triangulate
            #results and that it makes my cross section method easier.
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
                
                
                #I think this is needed to generate the data for raycasting
                #there may be some other way to update the object
                context.scene.objects.link(self.tmp_ob)
                self.tmp_ob.update_tag()
                context.scene.update() #this will slow things down
                context.scene.objects.unlink(self.tmp_ob)
                self.tmp_ob.matrix_world = self.original_form.matrix_world
                
                
                ###THIS IS A HUGELY IMPORTANT THING TO NOTICE!###
                #so maybe I need to make it more apparent or write it differnetly#
                #We are using a temporary duplicate to handle ray casting
                #and triangulation
                self.original_form = self.tmp_ob
                
            else:
                self.tmp_ob = None
            
            
            #store this stuff for next time.  We will most likely use it again
            #keep in mind, in some instances, tmp_ob is self.original orm
            #where as in others is it unique.  We want to use "target" here to
            #record validation because that is the the active or selected object
            #which is visible in the scene with a unique name.
            write_mesh_cache(target, self.tmp_ob, self.bme)
            print('derived new bme and any triangulations in %f' % (time.time() - start))

        message = "Segments: %i" % self.segments
        context.area.header_text_set(text = message)
            
            
        #here is where we will cache verts edges and faces
        #unti lthe user confirms and we output a real mesh.
        self.verts = []
        self.edges = []
        self.faces = []
        
        #store points
        self.draw_cache = []
            
       
        if settings.use_x_ray:
            self.orig_x_ray = self.destination_ob.show_x_ray
            self.destination_ob.show_x_ray = True
            
        #is the mouse clicked and held down
        self.drag = False
        self.navigating = False
        self.draw = False
        
        #what is the user dragging..a cutline, a handle etc
        self.drag_target = None
        #what is the mouse over top of currently
        self.hover_target = None
        #keep track of selected cut_line (perhaps
        self.selected = None
        
        
        
        self.sketch_lines = []
        
        
        
        self.header_message = 'Experimental sketcying. D + LMB to draw'
        context.area.header_text_set(self.header_message)
        #if settings.recover:
            #print('loading cache!')
            #print(contour_cache['CUT_LINES'])
            #self.load_from_cache(context, 'CUT_LINES', settings.recover_clip)
        #add in the draw callback and modal method
        self._handle = bpy.types.SpaceView3D.draw_handler_add(poly_sketch_draw_callback, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}
# Used to store keymaps for addon
addon_keymaps = []


#resgistration
def register():
    bpy.utils.register_class(ContourToolsAddonPreferences)
    bpy.utils.register_class(CGCOOKIE_OT_retopo_contour_panel)
    bpy.utils.register_class(CGCOOKIE_OT_retopo_contour)
    bpy.utils.register_class(CGCOOKIE_OT_retopo_poly_sketch)
    bpy.utils.register_class(CGCOOKIE_OT_retopo_contour_menu)

    # Create the addon hotkeys
    kc = bpy.context.window_manager.keyconfigs.addon
   
    # create the mode switch menu hotkey
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu', 'V', 'PRESS', ctrl=True, shift=True)
    kmi.properties.name = 'object.retopology_menu' 
    kmi.active = True
    addon_keymaps.append((km, kmi))
    

#unregistration
def unregister():
    bpy.utils.unregister_class(CGCOOKIE_OT_retopo_contour)
    bpy.utils.unregister_class(CGCOOKIE_OT_retopo_contour_panel)
    bpy.utils.unregister_class(CGCOOKIE_OT_retopo_contour_menu)
    bpy.utils.unregister_class(CGCOOKIE_OT_retopo_poly_sketch)
    bpy.utils.unregister_class(ContourToolsAddonPreferences)

    # Remove addon hotkeys
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
