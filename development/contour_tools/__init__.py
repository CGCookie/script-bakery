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
from mathutils import Vector
import contour_utilities
from contour_classes import ContourCutLine

methods = (('0','WALKING','0'),('1','BRUTE','1'))

def retopo_draw_callback(self,context):
    if self.cut_lines:
        for c_cut in self.cut_lines:
            c_cut.draw(context, debug = bpy.app.debug)
            
    
    if self.follow_lines != []:
        for follow in self.follow_lines:
            contour_utilities.draw_polyline_from_3dpoints(context, follow, (0,1,.2,1), 1,"GL_LINE_STIPPLE")
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
        if context.active_object:
            if len(context.selected_objects) > 0:
                return True
        return False
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == 'RET' and event.value == 'PRESS':
            self.push_mesh_data(context)
            return{'RUNNING_MODAL'}
            
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
                contour_utilities.callback_cleanup(self,context)
                self.bme.free()
                return {'CANCELLED'}  
        
        if event.type in {'MIDDLEMOUSE'}:
            for cut_line in self.cut_lines:
                if cut_line.head.world_position:
                    cut_line.head.screen_from_world(context)
                    cut_line.tail.screen_from_world(context)
            return {'PASS_THROUGH'}
        
        if event.type in {'WHEELDOWNMOUSE','WHEELUPMOUSE'}:
            if event.type == 'WHEELUPMOUSE':
                
                if self.segments >= .5 * len(self.cut_lines[0].verts):
                    return {'RUNNING_MODAL'}
                else:
                    self.segments += 1
            else:
                if self.segments < 4:
                    self.segments = 3
                else:
                    self.segments -= 1
            
            for cut_line in self.cut_lines:
                if not cut_line.verts:
                    cut_line.hit_object(context)
                    cut_line.cut_object(context, self.bme)
                cut_line.simplify_cross(self.segments)
            
            self.push_mesh_data(context)    
        
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
                            self.drag_target.hit_object(context,update_normal = False, method = 'HANDLE')
                        else:
                            self.drag_target.hit_object(context, update_normal = True, method = 'VIEW')
                            
                        self.drag_target.cut_object(context, self.bme)
                        self.drag_target.simplify_cross(self.segments)
                        self.push_mesh_data(context)
                    else:
                        self.drag_target.x = event.mouse_region_x
                        self.drag_target.y = event.mouse_region_y
                        if self.drag_target == self.drag_target.parent.plane_tan:
                            print('changing handle')
                            self.drag_target.screen_to_world(context)
                            self.drag_target.parent.hit_object(context, update_normal = False, method = 'HANDLE')
                        else:
                            self.drag_target.parent.hit_object(context, update_normal = True, method = 'VIEW')
                            
                        self.drag_target.parent.cut_object(context, self.bme)
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
    
    def push_mesh_data(self,context):
        
        if len(self.cut_lines) < 2:
            print('waiting on other cut lines')
            return
        imx = context.object.matrix_world.inverted()
        
        total_verts = []
        total_edges = []
        
        valid_cuts = [c_line for c_line in self.cut_lines if (c_line.verts != [] and c_line.verts_simple != [])]
        n_rings = len(valid_cuts)
        n_lines = len(valid_cuts[0].verts_simple)
        
        #align verts
        for i in range(0,n_rings-1):
            vs_1 = valid_cuts[i].verts_simple
            vs_2 = valid_cuts[i+1].verts_simple
            es_1 = valid_cuts[i].eds_simple
            es_2 = valid_cuts[i+1].eds_simple
            
            valid_cuts[i+1].verts_simple = contour_utilities.align_edge_loops(vs_1, vs_2, es_1, es_2)
        
                
        #work out the connectivity
        for i, cut_line in enumerate(valid_cuts):
            for v in cut_line.verts_simple:
                total_verts.append(imx * v)
            for ed in cut_line.eds_simple:
                total_edges.append((ed[0]+i*n_lines,ed[1]+i*n_lines))
            
            if i < n_rings - 1:
                #make connections between loops
                for j in range(0,n_lines):
                    total_edges.append((i*n_lines + j, (i+1)*n_lines + j))
                
        self.follow_lines = []
        for i in range(0,len(valid_cuts[0].verts_simple)):
            tmp_line = []
            for cut_line in valid_cuts:
                tmp_line.append(cut_line.verts_simple[i])
            self.follow_lines.append(tmp_line)
        
    def invoke(self, context, event):
        
        if context.object:
            ob = context.object
            me = ob.to_mesh(scene=context.scene, apply_modifiers=True, settings='PREVIEW')
            self.bme = bmesh.new()
            self.bme.from_mesh(me)
            self.segments = 10
            #self.bme.normal_update() #necessary?  nope...we don't need normals..save some time
            
            self.tmp_mesh = bpy.data.meshes.new(ob.name + "ctrt") 
            self.new_object = bpy.data.objects.new(ob.name + "ctrt", self.tmp_mesh)
            self.new_object.data = self.tmp_mesh
            self.new_object.show_wire = True
            self.new_object.matrix_world = ob.matrix_world
            scene = bpy.context.scene
            scene.objects.link(self.new_object)
            self.follow_lines = []
            self.new = False #a wway to keep track of if we are moving something or makig anew one.
 
        self._handle = bpy.types.SpaceView3D.draw_handler_add(retopo_draw_callback, (self, context), 'WINDOW', 'POST_PIXEL')

        self.drag = False
        self.cut_lines = []
        self.drag_target = None
        self.hover_target = None
        self.initial_location_head = None
        self.initial_location_tail = None
        self.initial_location_mouse = None
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self,context):
        for line in self.cut_lines:
            print(line.view_dir)

#resgistration
def register():
    bpy.utils.register_class(CGCOOKIE_OT_retopo_contour)

#unregistration
def unregister():
    bpy.utils.unregister_class(CGCOOKIE_OT_retopo_contour)