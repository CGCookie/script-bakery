import bpy

### ------------ New Operators ------------ ###

        
################################################### 
# Add empty at cursor, making it inactively selected   
################################################### 
class addTarget(bpy.types.Operator):
    """Add an inactive, selected Empty Object as a modifier target"""
    bl_label = "Add an unactive Empty Object"""
    bl_idname = "object.empty_add_unactive"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        # Get the currently active object
        activeObj = context.active_object
        
        # Store the current object
        currentObj = activeObj
        
        # Check to see if a target exists, if it does not then create one
        selectedObj = context.selected_objects
        for obj in selectedObj:
            if obj.type == 'EMPTY':
                break
            elif obj.type != 'EMPTY':
                bpy.ops.object.empty_add(type='PLAIN_AXES')
                selectedObj = context.selected_objects
            
        # Check if a mirror modifier exists, if it does then assign the empty
        for mod in currentObj.modifiers:
            if mod.type == 'MIRROR':
                for obj in selectedObj:
                    if obj.type == 'EMPTY':
                        mod.mirror_object = bpy.data.objects[obj.name]
                        obj.select = False    

        # Select the previously stored current object and make it active                    
        scene.objects.active = currentObj
        currentObj.select = True
     
        return {"FINISHED"}

        
################################################### 
# Add a Subsurf Modifier at level 2 and optimal display enabled   
################################################### 

class addSubsurf(bpy.types.Operator):
    """Add a Subsurf modifier at level 2 with Optimal Display"""
    bl_label = "Add a Subsurf Modifier"
    bl_idname = "object.add_subsurf"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0
    
    def execute(self, context):
        
    #    obj = context.active_object
        scene = bpy.context.scene
        sel = context.selected_objects
        
        for obj in sel:
            scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SUBSURF')
            print("Added Subsurf Modifier")
        
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.show_only_control_edges = True
                    mod.levels = 2
                
        return {"FINISHED"}
        
        
################################################### 
# Add a Mirror Modifier with clipping enabled   
################################################### 
    
class addMirror(bpy.types.Operator):
    """Add a Mirror modifier with clipping, use 2nd selected object as Mirror center"""
    bl_label = "Add Mirror Modifier"
    bl_idname = "object.add_mirror"
    bl_options = {'REGISTER', 'UNDO'}
       
    
    # Check to see if an object is selected
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0
    
    # Add the modifier
    def execute(self, context):
              
        scene = bpy.context.scene
        
        # Check for active object
        activeObj = context.active_object
        
        # Find all selected objects
        targetObj = context.selected_objects
        
        # Add a mirror modifier
        bpy.ops.object.modifier_add(type='MIRROR')
                
        # Store the mesh object
        selectedObj = activeObj
        print("Selected:", selectedObj)
        print("Active:", activeObj)
        
        
        useMirrorObj = False
        
        # If an second object is not selected, don't use mirror object
        if len(targetObj) > 1:
            useMirrorObj = True
            
        ### No long needed, used for auto-creation of the mirror empty    
#            if not [obj for obj in targetObj if obj.type == 'EMPTY']:
#                bpy.ops.object.empty_add(type='PLAIN_AXES')

        # Make the targetObj active
        try:
            scene.objects.active = [obj for obj in targetObj if obj != activeObj][0]
        except:
            pass
        
        print("Scene Active:", scene.objects.active)
                
        # Check for active object
        activeObj = context.active_object
        print("Active:", activeObj)
        
        # Swap the selected and active objects
        (selectedObj, activeObj) = (activeObj, selectedObj)
        print("Swapped Active:", activeObj)
        print("Swapped Selected:", selectedObj)
        
        # Deselect the empty object and select the mesh object again, making it active
        selectedObj.select = False
        activeObj.select = True
        scene.objects.active = activeObj
        
        # Find the added modifier, enable clipping, set the mirror object
        for mod in activeObj.modifiers:
            if mod.type == 'MIRROR':
                mod.use_clip = True
                if useMirrorObj == True:
                    mod.mirror_object = bpy.data.objects[selectedObj.name]      

        return {"FINISHED"}
    


################################################### 
# Apply only subsurf modifiers   
################################################### 

class applySubsurf(bpy.types.Operator):
    """Apply only Subsurf Modifiers"""
    bl_label = "Apply Only Subsurf Modifiers"
    bl_idname = "object.apply_subsurf"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Test if it is possible to apply a subsurf modifier, thanks to Richard Van Der Oost
    @classmethod    
    def poll(cls, context):
       
       # Get the active object
       obj = context.active_object
       
       # Test if there's an active object
       if obj:
           
           # Find modifiers with "SUBSURF" type
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
            if mod.type == 'SUBSURF':
                applyModifier(apply_as='DATA', modifier=mod.name)
        
        return {"FINISHED"}
    
    
################################################### 
# Add a Remesh Modifier with Smooth set as the type   
################################################### 

class smoothRemesh(bpy.types.Operator):
    """Add a Smooth Remesh Modifier"""
    bl_label = "Smooth Remesh"
    bl_idname = "object.smooth_remesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
    
        bpy.ops.object.modifier_add(type='REMESH')
        bpy.context.object.modifiers['Remesh'].mode = 'SMOOTH'
    
        return {"FINISHED"}



################################################### 
# Apply any remesh modifiers   
################################################### 

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
            if mod.type == 'REMESH':
                applyModifier(apply_as='DATA', modifier=mod.name)
        
        return {"FINISHED"}
    
    
################################################### 
# Apply all modifiers on the active object
################################################### 

class applyModifiers(bpy.types.Operator):
    """Apply all modifiers on selected objects"""
    bl_label = "Apply All Modifiers"
    bl_idname = "object.apply_modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and len(context.active_object.modifiers) > 0
   
    def execute(self, context):
        
        # find all selected objects
        sel = context.selected_objects
        
        applyModifier = bpy.ops.object.modifier_apply
        
        # loop through all selected objects
        for obj in sel:
            # set the current object in the loop to active
            bpy.context.scene.objects.active = obj
            
            # If any modifiers exist on current object object, apply them.
            for mod in obj.modifiers:
                applyModifier(apply_as='DATA', modifier=mod.name)
        
        return {"FINISHED"}    


    
################################################### 
# Creating operators for toggling Sculpt Symmetry
################################################### 

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
    
################################################### 
# Creating operators for toggling Axis Locks
################################################### 

class sculptAxisLockX(bpy.types.Operator):
    """Toggle X-axis Locking"""
    bl_label = "Toggle X-axis Lock"
    bl_idname = "sculpt.axislock_x"
    
    def execute(self, context):
       
       # checks the current state of x-axis symmetry then toggles it. 
        axisLock_x = bpy.context.tool_settings.sculpt.lock_x
        if axisLock_x:
            context.tool_settings.sculpt.lock_x = False
        else:
            context.tool_settings.sculpt.lock_x = True
        
        return {"FINISHED"}      
    
class sculptAxisLockY(bpy.types.Operator):
    """Toggle Y-axis Locking"""
    bl_label = "Toggle Y-axis Lock"
    bl_idname = "sculpt.axislock_y"
    
    def execute(self, context):
       
       # checks the current state of y-axis lock then toggles it. 
        axisLock_y = bpy.context.tool_settings.sculpt.lock_y
        if axisLock_y:
            context.tool_settings.sculpt.lock_y = False
        else:
            context.tool_settings.sculpt.lock_y = True
        
        return {"FINISHED"}    
    
class sculptAxisLockZ(bpy.types.Operator):
    """Toggle Z-axis Locking"""
    bl_label = "Toggle Z-axis Lock"
    bl_idname = "sculpt.axislock_z"
    
    def execute(self, context):
       
       # checks the current state of z-axis lock then toggles it. 
        axisLock_z = bpy.context.tool_settings.sculpt.lock_z
        if axisLock_z:
            context.tool_settings.sculpt.lock_z = False
        else:
            context.tool_settings.sculpt.lock_z = True
        
        return {"FINISHED"}   
    
class sculptCollapseShortEdges(bpy.types.Operator):
    """"Toggle Collapse Short Edges Option"""
    bl_label = "Toggle Collapse Short Edges"
    bl_idname = "sculpt.collapse_short_edges"
    
    # test if it is possible to toggle short edge collapse
    @classmethod    
    def poll(cls, context):
       
       # get the active object
       dyntopo = bpy.context.sculpt_object.use_dynamic_topology_sculpting
       
       # test if there's an active object
       if dyntopo:
           context.sculpt_object.use_dynamic_topology_sculpting = False
           return True
       return False
   
    def execute(self, context):
        
        shortEdges = bpy.context.scene.tool_settings.sculpt.use_edge_collapse
        if shortEdges:
            context.scene.tool_settings.sculpt.use_edge_collapse = False
        else:
            context.scene.tool_settings.sculpt.use_edge_collapse = True
            
        return {"FINISHED"}


######### Register and unregister the operators ###########

def register():
    bpy.utils.register_class(addTarget)
    bpy.utils.register_class(addSubsurf)
    bpy.utils.register_class(addMirror)
    bpy.utils.register_class(applySubsurf)
    bpy.utils.register_class(applyRemesh)
    bpy.utils.register_class(applyModifiers)
    bpy.utils.register_class(smoothRemesh)
    bpy.utils.register_class(sculptSymmetryX)
    bpy.utils.register_class(sculptSymmetryY)
    bpy.utils.register_class(sculptSymmetryZ)
    bpy.utils.register_class(sculptAxisLockX)
    bpy.utils.register_class(sculptAxisLockY)
    bpy.utils.register_class(sculptAxisLockZ)
    bpy.utils.register_class(sculptCollapseShortEdges)

    
def unregister():
    bpy.utils.unregister_class(addTarget)
    bpy.utils.unregister_class(addSubsurf)
    bpy.utils.unregister_class(addMirror)
    bpy.utils.unregister_class(applySubsurf)
    bpy.utils.unregister_class(applyRemesh)
    bpy.utils.unregister_class(applyModifiers)
    bpy.utils.unregister_class(smoothRemesh)
    bpy.utils.unregister_class(sculptSymmetryX)
    bpy.utils.unregister_class(sculptSymmetryY)
    bpy.utils.unregister_class(sculptSymmetryZ)
    bpy.utils.unregister_class(sculptAxisLockX)
    bpy.utils.unregister_class(sculptAxisLockY)
    bpy.utils.unregister_class(sculptAxisLockZ)
    bpy.utils.unregister_class(sculptCollapseShortEdges)
    

    
if __name__ == "__main__":
    register()