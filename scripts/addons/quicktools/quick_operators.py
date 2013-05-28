import bpy
from bpy import ops

################################################### 
# Convienence variables
################################################### 

applyModifier = ops.object.modifier_apply


### ------------ New Operators ------------ ###


################################################### 
# Set object origin to center of current mesh selection in edit mdoe   
################################################### 

class setObjectOrigin(bpy.types.Operator):
    """Set Object Origin To Center Of Current Mesh Selection"""
    bl_idname = "mesh.set_object_origin"
    bl_label = "Set origin to the selection center"
    bl_options = {'REGISTER', 'UNDO'}    
    
    def execute(self, context):
        mode = bpy.context.object.mode
        if mode != 'EDIT':
            # If user is not in object mode, don't run the operator and report reason to the Info header
            self.report({'INFO'}, "Must be run in Edit Mode")
        else:
            # Set the 3D Cursor to the selected mesh and then center the origin in object mode, followed by returning to edit mode.
            ops.view3d.snap_cursor_to_selected()
            ops.object.mode_set(mode='OBJECT')
            ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            ops.object.mode_set(mode='EDIT')
            
        return {"FINISHED"}


################################################### 
# Add empty at cursor, making it inactively selected   
################################################### 
class addTarget(bpy.types.Operator):
    """Add an inactive, selected Empty Object as a modifier target"""
    bl_label = "Add an unactive Empty Object"""
    bl_idname = "object.empty_add_unactive"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) > 0:
            return True
        return False

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
                ops.object.empty_add(type='PLAIN_AXES')
                selectedObj = context.selected_objects
            
        # Check if a mirror modifier exists, if it does then assign the empty
        for mod in currentObj.modifiers:
            if mod.type == 'MIRROR':
                for obj in selectedObj:
                    if obj.type == 'EMPTY':
                        mod.mirror_object = bpy.data.objects[obj.name]
                        obj.select = False
                        self.report({'INFO'}, "Assigned target object to existing modifier")       

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
            ops.object.modifier_add(type='SUBSURF')
            print("Added Subsurf Modifier")
        
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.show_only_control_edges = True
                    mod.levels = 2
                
        return {"FINISHED"}
        
       
################################################### 
# Add Modifier function, for use with smart mod classes.  
################################################### 

def addMod(modifier):
    ops.object.modifier_add(type=modifier)
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
              
        scene = context.scene
        
        # Check for active object
        activeObj = context.active_object
        
        # Find all selected objects
        targetObj = context.selected_objects
        
        # Add a mirror modifier
        addMod("MIRROR")
                
        # Store the mesh object
        selectedObj = activeObj        
        
        # Set status of mirror object usage
        useMirrorObj = False
        
        # If a second object is not selected, don't use mirror object
        if len(targetObj) > 1:
            useMirrorObj = True

        # Make the targetObj active
        try:
            scene.objects.active = [obj for obj in targetObj if obj != activeObj][0]
        except:
            pass
                
        # Check for active object
        activeObj = context.active_object
        
        # Swap the selected and active objects
        selectedObj, activeObj = activeObj, selectedObj
        
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
                    self.report({'INFO'}, "Assigned target object to modifier")      

        return {"FINISHED"}
    
################################################### 
# Add a Lattice with auto assigning of the lattice object   
################################################### 


class addLattice(bpy.types.Operator):
    """Add a Lattice Modifier and auto-assign to selected lattice object"""
    bl_idname = "object.add_lattice"
    bl_label = "Add a lattice modifier"
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
        
        # Add a lattice modifier
        addMod("LATTICE")

        # Store the mesh object
        selectedObj = activeObj

        # Set status of lattice object usage
        useLatticeObj = False

        # If an second object is not selected, don't use lattice object
        if len(targetObj) > 1:
            useLatticeObj = True

        # Make the targetObj active
        try:
            scene.objects.active = [obj for obj in targetObj if obj != activeObj][0]
        except:
            pass
                
        # Check for active object
        activeObj = context.active_object
        
        # Swap the selected and active objects
        (selectedObj, activeObj) = (activeObj, selectedObj)
        
        # Deselect the empty object and select the mesh object again, making it active
        selectedObj.select = False
        activeObj.select = True
        scene.objects.active = activeObj
        
        # Find the added modifier, set the lattice object
        for mod in activeObj.modifiers:
            if mod.type == 'LATTICE':
                if useLatticeObj == True:
                    mod.object = bpy.data.objects[selectedObj.name]
                    self.report({'INFO'}, "Assigned lattice object to modifier")         

        return {"FINISHED"}

################################################### 
# Add an Array modifier with object offset enabled 
###################################################      

class addArray(bpy.types.Operator):
    """Add a Array modifier with object offset, use 2nd selected object as offset object"""
    bl_label = "Add Array Modifier"
    bl_idname = "object.add_array"
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
        
        # Add a array modifier
        addMod("ARRAY")

        # ops.object.modifier_add(type='ARRAY')
                
        # Store the mesh object
        selectedObj = activeObj        
        
        # Set status of array object usage
        useArrayObj = False
        
        # If a second object is not selected, don't use mirror object
        if len(targetObj) > 1:
            useArrayObj = True

        # Make the targetObj active
        try:
            scene.objects.active = [obj for obj in targetObj if obj != activeObj][0]
        except:
            pass
                
        # Check for active object
        activeObj = context.active_object
        
        # Swap the selected and active objects
        selectedObj, activeObj = activeObj, selectedObj
        
        # Deselect the empty object and select the mesh object again, making it active
        selectedObj.select = False
        activeObj.select = True
        scene.objects.active = activeObj
        
        # Find the added modifier, and check for status of useArrayObj
        if useArrayObj == True:
            for mod in activeObj.modifiers:
                if mod.type == 'ARRAY':
                    mod.use_relative_offset = False
                    mod.use_object_offset = True
                    if useArrayObj == True:
                        mod.offset_object = bpy.data.objects[selectedObj.name]
                        self.report({'INFO'}, "Assigned target object to modifier")      

        return {"FINISHED"}


################################################### 
# Add a Screw modifier with an object axis set  
################################################### 

class addScrew(bpy.types.Operator):
    """Add a Screw modifier, use 2nd selected object as object axis"""
    bl_label = "Add Screw Modifier"
    bl_idname = "object.add_screw"
    bl_options = {'REGISTER', 'UNDO'}
       
    
    # Check to see if an object is selected
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0
    
    # Add the modifier
    def execute(self, context):
              
        scene = context.scene
        
        # Check for active object
        activeObj = context.active_object
        
        # Find all selected objects
        targetObj = context.selected_objects
        
        # Add a screw modifier
        addMod("SCREW")
                
        # Store the mesh object
        selectedObj = activeObj        
        
        # Set status of screw object usage
        useScrewObj = False
        
        # If a second object is not selected, don't use screw object
        if len(targetObj) > 1:
            useScrewObj = True

        # Make the targetObj active
        try:
            scene.objects.active = [obj for obj in targetObj if obj != activeObj][0]
        except:
            pass
                
        # Check for active object
        activeObj = context.active_object
        
        # Swap the selected and active objects
        (selectedObj, activeObj) = (activeObj, selectedObj)
        
        # Deselect the empty object and select the mesh object again, making it active
        selectedObj.select = False
        activeObj.select = True
        scene.objects.active = activeObj
        
        # Find the added modifier, enable clipping, set the mirror object
        for mod in activeObj.modifiers:
            if mod.type == 'SCREW':
                if useScrewObj == True:
                    mod.object = bpy.data.objects[selectedObj.name]
                    self.report({'INFO'}, "Assigned target axis object to modifier")      

        return {"FINISHED"}

################################################### 
# Halve the mesh and add a Mirror modifier   
################################################### 

def halve_mesh(self, context):

    obj = context.active_object.data

    for verts in obj.vertices:
        if verts.co.x < -0.001:    
            verts.select = True


class halveMesh(bpy.types.Operator):    
    """Delete all vertices on the -X side of center"""
    bl_idname = "object.mesh_halve"
    bl_label = "Halve and mirror mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):

        if bpy.context.active_object.type == 'MESH':
            return True
        return False

    def execute(self, context):
        
        obj = context.active_object.data
        selected = context.selected_objects
        # Go to edit mode and ensure all vertices are deselected, preventing accidental deletions
        
        if context.object.mode == 'OBJECT':
        
            for obj in selected:
                if obj.type == 'MESH':
                    context.scene.objects.active = obj

                    ops.object.mode_set(mode='EDIT')
                    ops.mesh.select_all(action='DESELECT')
                    ops.object.mode_set(mode='OBJECT')
                    
                    # Find verts left of center and select them
                    halve_mesh(self, context)

                    # for verts in obj.vertices:
                    #     if verts.co.x < -0.001:    
                    #         verts.select = True
                            
                    # Toggle edit mode and delete the selection
                    ops.object.mode_set(mode='EDIT')
                    ops.mesh.delete(type='VERT')
                    
                    # Switch back to object mode and add the mirror modifier
                    ops.object.mode_set(mode='OBJECT')
                    addMod("MIRROR")

                    self.report({'INFO'}, "Mesh half removed and Mirror modifier added")
                else:
                    self.report({'INFO'}, "Only works on mesh objects")


        elif bpy.context.object.mode == 'EDIT':
            ops.mesh.select_all(action='DESELECT')
            ops.object.mode_set(mode='OBJECT')
            
            # Find verts left of center and select them
            halve_mesh(self, context)
                    
            # Toggle edit mode and delete the selection
            ops.object.mode_set(mode='EDIT')
            ops.mesh.delete(type='VERT')

            self.report({'INFO'}, "Mesh half removed")

        return {'FINISHED'}
    
    
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

        # If any subsurf modifiers exist on object, apply them.
        for mod in obj.modifiers:
            if mod.type == 'SUBSURF':
                applyModifier(apply_as='DATA', modifier=mod.name)
                self.report({'INFO'}, "Applied Subsurf modifier(s)")   
        
        return {"FINISHED"}
    
    
################################################### 
# Add a Remesh Modifier with Smooth set as the type   
################################################### 

class addRemesh(bpy.types.Operator):
    """Add a Smooth Remesh Modifier"""
    bl_label = "Smooth Remesh"
    bl_idname = "object.smooth_remesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # 
        return not context.sculpt_object.use_dynamic_topology_sculpting

    def execute(self, context):
        ops.object.modifier_add(type='REMESH')
        context.object.modifiers['Remesh'].mode = 'SMOOTH'
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

        # If any remesh modifiers exist on object, apply them.
        for mod in obj.modifiers:
            if mod.type == 'REMESH':
                applyModifier(apply_as='DATA', modifier=mod.name)
                self.report({'INFO'}, "Applied remesh modifier(s)")   

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
        # Make sure there's a selected object and that that object has modifiers to apply
        return len(context.selected_objects) > 0 and len(context.active_object.modifiers) > 0
   
    def execute(self, context):

        sel = context.selected_objects
        for obj in sel:
            # set the current object in the loop to active
            context.scene.objects.active = obj
            
            # If any modifiers exist on current object object, apply them.
            for mod in obj.modifiers:
                applyModifier(apply_as='DATA', modifier=mod.name)

            # maybe for debug you might do an 'applied to obj.name' in before
            # iterating to the next
            
        self.report({'INFO'}, "Applied all modifiers on selected objects")   
        return {"FINISHED"}    

    
################################################### 
# Creating operators for toggling Sculpt Symmetry
################################################### 

class sculptSymmetry(bpy.types.Operator):
    """Toggle Symmetry For Sculpting"""
    bl_idname = "sculpt.symmetry"
    bl_label = "Toggle Sculpt Symmetry"

    
    axis = bpy.props.IntProperty(name = "Axis",
                    description = "switch between symmetry axis'",
                    default = 0)

    def execute(self, context):
        if self.axis == -1:
            symmetry_x = context.tool_settings.sculpt.use_symmetry_x
            context.tool_settings.sculpt.use_symmetry_x = not symmetry_x
        if self.axis == 0:
            symmetry_y = context.tool_settings.sculpt.use_symmetry_y
            context.tool_settings.sculpt.use_symmetry_y = not symmetry_y
        if self.axis == 1:
            symmetry_z = context.tool_settings.sculpt.use_symmetry_z
            context.tool_settings.sculpt.use_symmetry_z = not symmetry_z
        return {"FINISHED"}


################################################### 
# Creating operators for toggling Axis Locks
################################################### 

class sculptAxisLockX(bpy.types.Operator):
    """Toggle X-axis Locking"""
    bl_label = "Toggle X-axis Lock"
    bl_idname = "sculpt.axislock_x"
    
    def execute(self, context):
        axisLock_x = context.tool_settings.sculpt.lock_x
        context.tool_settings.sculpt.lock_x = not axisLock_x
        return {"FINISHED"}      
    
class sculptAxisLockY(bpy.types.Operator):
    """Toggle Y-axis Locking"""
    bl_label = "Toggle Y-axis Lock"
    bl_idname = "sculpt.axislock_y"
    
    def execute(self, context):
        axisLock_y = context.tool_settings.sculpt.lock_y
        context.tool_settings.sculpt.lock_y = not axisLock_y
        return {"FINISHED"}    
    
class sculptAxisLockZ(bpy.types.Operator):
    """Toggle Z-axis Locking"""
    bl_label = "Toggle Z-axis Lock"
    bl_idname = "sculpt.axislock_z"
    
    def execute(self, context):
        axisLock_z = context.tool_settings.sculpt.lock_z
        context.tool_settings.sculpt.lock_z = not axisLock_z
        return {"FINISHED"}   
    

################################################### 
# Creating operator for toggling collapse short edges
################################################### 

class sculptCollapseShortEdges(bpy.types.Operator):
    """"Toggle Collapse Short Edges Option"""
    bl_label = "Toggle Collapse Short Edges"
    bl_idname = "sculpt.collapse_short_edges"
    
    # test if it is possible to toggle short edge collapse
    @classmethod    
    def poll(cls, context):
        # if dyntopo True, returns True, else returns False :)
        return context.sculpt_object.use_dynamic_topology_sculpting
   
    def execute(self, context):
        #invert current state
        shortEdges = context.scene.tool_settings.sculpt.use_edge_collapse
        context.scene.tool_settings.sculpt.use_edge_collapse = not shortEdges
        return {"FINISHED"}

################################################### 
# Creating operator for toggling double sided
################################################### 

class objectDoubleSided(bpy.types.Operator):
    """Toggle Double Sided Option"""
    bl_label = "Toggle Double Sided"
    bl_idname = "object.double_sided"
    bl_description = "Toggle double-sided on all selected objects"

    def execute(self, context):

        scene = context.scene
        selected = context.selected_objects
        origActive = context.active_object
        doubleSided = context.object.data.show_double_sided

        for obj in selected:
            scene.objects.active = obj
            context.object.data.show_double_sided = not doubleSided

        scene.objects.active = origActive
        return {"FINISHED"}

################################################### 
# Creating operator for toggling all edges wire
################################################### 

class allEdgesWire(bpy.types.Operator):
    """Toggle Wire Display With All Edges"""
    bl_label = "Toggle All Edges Wire"
    bl_idname = "object.all_edges_wire"
    bl_description = "Toggle all-edges wireframe on all selected objects"

    def execute(self, context):

        scene = context.scene
        selected = context.selected_objects
        origActive = context.active_object
        
        allEdges = context.object.show_all_edges
        wire = context.object.show_wire

        for obj in selected:
            scene.objects.active = obj
            context.object.show_all_edges = not allEdges
            context.object.show_wire = not wire

        scene.objects.active = origActive
        return {"FINISHED"}


# boiler plate: register / unregister

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
