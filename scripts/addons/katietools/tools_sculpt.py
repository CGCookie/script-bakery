import bpy
import os
import random
import math

#--------------------------------------------------------------------------
#----------------------------- SCULPT OPERATORS -------------------------
#--------------------------------------------------------------------------

def lockAxis(axis):
    scn = bpy.context.scene
    sculpt = scn.tool_settings.sculpt
    
    if axis == 'x':
        sculpt.lock_x = True
    elif axis == 'y':
        sculpt.lock_y = True
    elif axis == 'z':
        sculpt.lock_z = True     

class SCULPT_lockX(bpy.types.Operator):
    bl_idname = "sculpt.lock_axis_x"
    bl_label = "Lock X Axis"
    bl_description = "Lock manipulation in the X axis"
           
    def execute(self, context):
        lockAxis('x')
                        
        return {'FINISHED'}
    