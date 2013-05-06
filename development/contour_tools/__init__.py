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


def retopo_draw_callback(self,context):
    if self.cut_lines:
        for c_cut in self.cut_lines:
            c_cut.draw(context)
    

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
    '''Delete Menu'''
    bl_idname = "cgcookie.retop_contour"
    bl_label = "Contour Retopologize"    
    
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == 'MOUSEMOVE':
            
            if self.drag and self.drag_target:
            
                if hasattr(self.drag_target,"head"): #then it's a  line, we need to move both?
                    delta = Vector((event.mouse_region_x,event.mouse_region_y)) - Vector((self.initial_location_mouse))
                    self.drag_target.head.x = self.initial_location_head[0] + delta[0]
                    self.drag_target.head.y = self.initial_location_head[1] + delta[1]
                    self.drag_target.tail.x = self.initial_location_tail[0] + delta[0]
                    self.drag_target.tail.y = self.initial_location_tail[1] + delta[1]
                
                else:
                    self.drag_target.x = event.mouse_region_x
                    self.drag_target.y = event.mouse_region_y
                
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
            #clean up callbacks to prevent crash
            contour_utilities.callback_cleanup(self,context)
            self.bme.free()
            return {'CANCELLED'}  
        
        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}
        
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
                        
                        self.drag_target.hit_object(context)
                        self.drag_target.cut_object(context, self.bme)
                else:
                    self.drag_target.x = event.mouse_region_x
                    self.drag_target.y = event.mouse_region_y
                    self.drag_target.parent.hit_object(self,context)
                
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
                    self.initial_location_mouse = (event.mouse_region_x,event.mouse_region_y)
                
                if not self.drag_target:
                    v3d = context.space_data
                    region = v3d.region_3d 
                    view = region.view_rotation * Vector((0,0,1))
                    self.cut_lines.append(ContourCutLine(event.mouse_region_x, event.mouse_region_y, view))
                    self.drag_target = self.cut_lines[-1].tail
            
                    return {'RUNNING_MODAL'}
                return {'RUNNING_MODAL'}
            return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}
        #ret_val = retopo_modal(self, context, event)
        #print('modal ret val')
        #print(ret_val)
        #return ret_val
    
    def invoke(self, context, event):
        
        if context.object:
            ob = context.object
            me = ob.to_mesh(scene=context.scene, apply_modifiers=True, settings='PREVIEW')
            self.bme = bmesh.new()
            self.bme.from_mesh(me)
            #self.bme.normal_update() #necessary?  nope...we don't need normals..save some time
        
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