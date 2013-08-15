#script by Your Alex Telford | www.blendercookie.com
#Description:
#Rotates the pivot of an object without effecting the object itself, caution: slow on heavy objects.
bl_info = {
    "name": "Rotate Pivot",
    "author": "Alex Telford",
    "version": (0, 3),
    "blender": (2, 6, 6),
    "location": "View3D > Toolshelf",
    "description": "Rotate the pivot of an object",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "View3D"}
    
#import modules
import bpy
from bpy.props import *

class rotatePivotInit(bpy.types.Panel):
    bl_label = "Rotate Pivot"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #mode that the panel will show in, OBJECT, SCULPT or EDIT
    @classmethod
    def poll(self, context):
       return(bpy.context.mode == 'OBJECT')

    #check box
    bpy.types.Scene.applyRotationFirst= BoolProperty(
        name = "Apply Rotation", 
        description = "Apply Rotation before rotating",
        default = True)
        
    def draw(self, context):
        obj = context.object
        scn = context.scene
        
        layout = self.layout
        col = layout.column()
        #try to layout, otherwise say something else
        try:
            selected = bpy.context.scene.objects.active.name
            failCheck = bpy.context.selected_objects[1]
            #layout items
            col.label("Copy Rotation from active(last selected) to all other selected")
            col.label("Copy Rotation From:")
            col.label('>>'+selected)
            col.label("Copy Rotation To:")
            for ob in bpy.context.selected_objects:
                if ob != bpy.context.scene.objects.active:
                    col.label('>>'+ob.name)
            
            col.label("Apply initial rotation")
            col.prop(scn, "applyRotationFirst", text = '')
            #execute button
            layout.operator("copyrotation.toselected")
        except:
            #couldn't fill object list
            col.label("Select an object")

#run
class OBJECT_OT_rotatePivot(bpy.types.Operator):
    bl_idname = "copyrotation.toselected"
    bl_label = "Rotate"
    
    def execute(self, context):
        obj = context.object
        scn = context.scene
        
        ###Run Script
        #active
        active = bpy.context.scene.objects.active
        selection = bpy.context.selected_objects
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        pivotPoint = context.space_data.pivot_point
        context.space_data.pivot_point = "CURSOR"
        for ob in selection:
            if ob != active:
                print(ob)
                bpy.context.scene.objects.active = ob
                ob.select = True
                if scn.applyRotationFirst == True:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                rotatePivot(active.rotation_euler)
                bpy.ops.object.select_all(action='DESELECT')
        context.space_data.pivot_point = pivotPoint
        #warnings use this context if you need them, here we just print the stuff
        self.report({'INFO'}, "Done!")
        
        return{'FINISHED'}
    
###functions
def rotatePivot(rotation):
    #rotate selected object based on a vector
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.transform.rotate(value=rotation.x, axis=(1,0,0), constraint_orientation='GLOBAL')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.rotate(value=-rotation.x, axis=(1,0,0), constraint_orientation='GLOBAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.transform.rotate(value=rotation.y, axis=(0,1,0), constraint_orientation='GLOBAL')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.rotate(value=-rotation.y, axis=(0,1,0), constraint_orientation='GLOBAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.transform.rotate(value=rotation.z, axis=(0,0,1), constraint_orientation='GLOBAL')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.rotate(value=-rotation.z, axis=(0,0,1), constraint_orientation='GLOBAL')
    bpy.ops.object.mode_set(mode='OBJECT')

def register():
    ###initialize classes
    bpy.utils.register_class(rotatePivotInit)
    bpy.utils.register_class(OBJECT_OT_rotatePivot)
def unregister():
    bpy.utils.unregister_class(rotatePivotInit)
    bpy.utils.register_class(OBJECT_OT_rotatePivot)