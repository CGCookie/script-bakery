bl_info = {
    "name": "Add Poly Sphere",
    "location": "View3D > Add > Mesh > Add Poly Sphere",
    "description": "Adds a poly cube to the scene via Add > Mesh > Poly Sphere",
    "author": "Jonathan Williamson",
    "version": (0,3),
    "blender": (2, 6, 5),
    "category": "Add Mesh",
    }

import bpy

#Create the operator for adding a poly sphere
class addPolySphere(bpy.types.Operator):
    """Add a poly sphere to the scene"""
    bl_idname = "mesh.sphere_poly_add"
    bl_label = "Add Poly Sphere"
    bl_options = {'REGISTER', 'UNDO'}    
    
    #Add the subsurf modifier, apply it, and spherify the mesh
    def execute(self, context):
        obj = context.active_object
        
        #Add a cube starting point
        bpy.ops.mesh.primitive_cube_add(view_align=False)
        
        #Add a subsurf modifier to the cube
        bpy.ops.object.modifier_add(type='SUBSURF')
                
        #Find the current selection
        obj = context.active_object
        
        #Find modifiers added to current selection
        activeMod = obj.modifiers
        
        #Change settings on the modifier
        for mod in obj.modifiers:
            if mod.type == 'SUBSURF':
                activeMod[mod.name].show_only_control_edges = True
                activeMod[mod.name].levels = 2
                
                #Apply the subsurf modifier
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
        
        #Switch to Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        #Sphereize the mesh
        bpy.ops.transform.tosphere(value=1)
        
        #Switch back to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
    
        return {'FINISHED'}
 


#Create the Menu entry
def menu_func(self, context):
    self.layout.operator(addPolySphere.bl_idname, icon='MOD_SUBSURF')
                
def register():
    bpy.utils.register_class(addPolySphere)
    
    #Add the menu entry to the Add menu
    bpy.types.INFO_MT_mesh_add.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(addPolySphere)
    
    #remove the menu entry from the Add menu
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    
if __name__ == "__main__":
    register()