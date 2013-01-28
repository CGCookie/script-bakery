import bpy

### ------------ New Operators ------------ ###

### creates an operator for applying subsurf modifiers ###
class applySubsurf(bpy.types.Operator):
    """Apply only Subsurf Modifiers"""
    bl_label = "Apply Only Subsurf Modifiers"
    bl_idname = "object.apply_subsurf"
    bl_options = {'REGISTER', 'UNDO'}
    
    # test if it is possible to apply a subsurf modifier, thanks to Richard Van Der Oost
    @classmethod    
    def poll(cls, context):
       
       # get the active object
       obj = context.active_object
       
       # test if there's an active object
       if obj:
           
           # find modifiers with "SUBSURF" type
           for mod in obj.modifiers:
               if mod.type == 'SUBSURF':
                   return True
       return False
    
    def execute(self, context):
        
        #check for active object
        obj = context.active_object
        
        applyModifier = bpy.ops.object.modifier_apply
        
        # If any subsurf modifiers exist on object, apply them.
        for mod in obj.modifiers:
            if mod.type=='SUBSURF':
                applyModifier(apply_as='DATA', modifier=mod.name)
        
        return {"FINISHED"}

class applyRemesh(bpy.types.Operator):
    """Apply only Remesh Modifiers"""
    bl_label = "Apply Only Remesh Modifiers"
    bl_idname = "object.apply_remesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    # test if it is possible to apply a remesh modifier
    @classmethod    
    def poll(cls, context):
       
       # get the active object
       obj = context.active_object
       
       # test if there's an active object
       if obj:
           
           # find modifiers with "REMESH" type
           for mod in obj.modifiers:
               if mod.type == 'REMESH':
                   return True
       return False
    
    def execute(self, context):
        
        #check for active object
        obj = context.active_object
        
        applyModifier = bpy.ops.object.modifier_apply
        
        # If any remesh modifiers exist on object, apply them.
        for mod in obj.modifiers:
            if mod.type=='REMESH':
                applyModifier(apply_as='DATA', modifier=mod.name)
        
        return {"FINISHED"}
    
    

### Creating operators for toggling Sculpt Symmetry ###

class sculptSymmetryX(bpy.types.Operator):
    """Enable X-axis symmetry"""
    bl_label = "Toggle X-axis Symmetry"
    bl_idname = "sculpt.symmetry_x"
    
    def execute(self, context):
       
       # checks the current state of x-axis symmetry then toggles it. 
        symmetry_x = bpy.context.tool_settings.sculpt.use_symmetry_x
        if symmetry_x:
            context.tool_settings.sculpt.use_symmetry_x = False
        else:
            context.tool_settings.sculpt.use_symmetry_x = True
        
        return {"FINISHED"}

class sculptSymmetryY(bpy.types.Operator):
    """Enable Y-axis symmetry"""
    bl_label = "Toggle Y-axis Symmetry"
    bl_idname = "sculpt.symmetry_y"
    
    def execute(self, context):
        
        symmetry_y = bpy.context.tool_settings.sculpt.use_symmetry_y
        if symmetry_y:
            context.tool_settings.sculpt.use_symmetry_y = False
        else:
            context.tool_settings.sculpt.use_symmetry_y = True
        
        return {"FINISHED"}   
    
class sculptSymmetryZ(bpy.types.Operator):
    """Enable Z-axis symmetry"""
    bl_label = "Toggle Z-axis Symmetry"
    bl_idname = "sculpt.symmetry_z"
    
    def execute(self, context):
        
        symmetry_z = bpy.context.tool_settings.sculpt.use_symmetry_z
        if symmetry_z:
            context.tool_settings.sculpt.use_symmetry_z = False
        else:
            context.tool_settings.sculpt.use_symmetry_z = True
        
        return {"FINISHED"}       


######### Register and unregister the operators ###########

def register():
    bpy.utils.register_class(applySubsurf)
    bpy.utils.register_class(applyRemesh)
    bpy.utils.register_class(sculptSymmetryX)
    bpy.utils.register_class(sculptSymmetryY)
    bpy.utils.register_class(sculptSymmetryZ)

    
def unregister():
    bpy.utils.unregister_class(applySubsurf)
    bpy.utils.unregister_class(applyRemesh)
    bpy.utils.unregister_class(sculptSymmetryX)
    bpy.utils.unregister_class(sculptSymmetryY)
    bpy.utils.unregister_class(sculptSymmetryZ)

    
if __name__ == "__main__":
    register()