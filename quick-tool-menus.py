bl_info = {
    "name": "Quick Tool Menus",
    "description": "A series of quick tool menus for Object Mode, Edit Mode, and Sculpt Mode",
    "author": "Jonathan Williamson",
    "version": (0,3),
    "blender": (2, 6, 5),
    "category": "3D View",
}
  
import bpy
from bpy import context
 
scene = context.scene
obj = scene.objects.active

# adds an object mode menu 
class JWObjectTools(bpy.types.Menu):
    bl_label = "Jonathan's Object Tools"
    bl_idname = "object.tools_menu"
       
    def draw(self, context):
        layout = self.layout
        
        layout.operator_menu_enum("object.modifier_add", "type",
                                      icon='MODIFIER') 
        layout.separator() 
                
        layout.operator_menu_enum("object.origin_set", "type")
        
        layout.separator()
        
        layout.operator("object.shade_smooth")
        layout.operator("object.shade_flat")

# creates an operator for applying subsurf modifiers
class applySubsurf(bpy.types.Operator):
    bl_label = "Apply Only Subsurf Modifiers"
    bl_idname = "object.apply_subsurf"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        applyModifier = bpy.ops.object.modifier_apply
        
        # If any subsurf modifiers exist on object, apply them.
        for mod in obj.modifiers:
            if mod.type=='SUBSURF':
#        for mod in obj.modifiers:
#            if "Subsurf" in mod.name:
                print (mod)
                applyModifier(apply_as='DATA', modifier=mod.name)
        return {"FINISHED"}

# creates a menu for Sculpt mode tools
class JWSculptTools(bpy.types.Menu):
    bl_label = "Jonathan's Sculpt Tools"
    bl_idname = "sculpt.tools_menu"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.modifier_add", 'Add Subsurf', icon='MOD_SUBSURF').type='SUBSURF'
        layout.operator("object.apply_subsurf", 'Apply Subsurf', icon='MOD_SUBSURF')
        # trying to enable setting symmetry from the menu
#        layout.operator("bpy.types.Sculpt").use_symmetry_x=False
        
        
# creates a menu for edit mode tools         
class JWMeshTools(bpy.types.Menu):
    bl_label = "Jonathan's Mesh Tools"
    bl_idname = "mesh.tools_menu"
       
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.inset").use_boundary=False
        layout.operator("gpencil.surfsk_add_surface")
        layout.operator("mesh.subdivide")
        layout.operator("mesh.knife_tool")
        layout.operator("mesh.bridge_edge_loops")
        layout.operator("mesh.vert_connect")
        
        layout.separator()
        
        layout.operator("transform.edge_slide")
        layout.operator("mesh.vert_slide")
        layout.operator("mesh.vertices_smooth")       

addon_keymaps = []

def register():
    bpy.utils.register_class(JWMeshTools)
    bpy.utils.register_class(JWObjectTools)
    bpy.utils.register_class(JWSculptTools)
    bpy.utils.register_class(applySubsurf)
    
    # create the object mode menu hotkey
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'T', 'PRESS', oskey=True)
    kmi.properties.name = 'object.tools_menu'
    
    # create the sculpt mode menu hotkey
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Sculpt', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'T', 'PRESS', oskey=True)
    kmi.properties.name = 'sculpt.tools_menu'
    
    # creatue the edit mode menu hotkey
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'T', 'PRESS', oskey=True)
    kmi.properties.name = 'mesh.tools_menu'

    addon_keymaps.append(km)

def unregister():
    bpy.utils.unregister_class(JWMeshTools)
    bpy.utils.unregister_class(JWObjectTools)
    bpy.utils.register_class(JWSculptTools)
    bpy.utils.register_class(applySubsurf)
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


if __name__ == "__main__":
    register()
    
    
       