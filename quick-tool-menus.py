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

### New Operators ###

# creates an operator for applying subsurf modifiers
class applySubsurf(bpy.types.Operator):
    bl_label = "Apply Only Subsurf Modifiers"
    bl_idname = "object.apply_subsurf"
    bl_options = {'REGISTER', 'UNDO'}
    
    # test if it is possible to apply a subsurf modifier, thanks to Richard Van Der Oost
    @classmethod
    def poll(cls, context):
       
       # get the active object
       obj = scene.objects.active
       
       # test if there's an active object
       if obj:
           
           # find modifiers with "SUBSURF" type
           for mod in obj.modifiers:
               if mod.type == 'SUBSURF':
                   return True
       return False
    
    def execute(self, context):
        
        applyModifier = bpy.ops.object.modifier_apply
        
        # If any subsurf modifiers exist on object, apply them.
        for mod in obj.modifiers:
            if mod.type=='SUBSURF':

        # Old code that was dependent on names, rather than type. So if the modifier was renamed it would fail.
#        for mod in obj.modifiers:
#            if "Subsurf" in mod.name:
                print (mod)
                applyModifier(apply_as='DATA', modifier=mod.name)
        return {"FINISHED"}

# creates an operator for toggling Sculpt Symmetry
class sculptSymmetryX(bpy.types.Operator):
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
    bl_label = "Toggle Z-axis Symmetry"
    bl_idname = "sculpt.symmetry_z"
    
    def execute(self, context):
        
        symmetry_z = bpy.context.tool_settings.sculpt.use_symmetry_z
        if symmetry_z:
            context.tool_settings.sculpt.use_symmetry_z = False
        else:
            context.tool_settings.sculpt.use_symmetry_z = True
        
        return {"FINISHED"}       

### Creating the Menus for each mode ###

# adds a Mode switch menu
class ModeSwitch(bpy.types.Menu):
    bl_label = "Quick Mode Switch Menu"
    bl_idname = "mode.switch_menu"
    
    def draw(self, context):
        layout = self.layout

# attempting to check the current mode to display the relative operator        
        if bpy.context.mode:
            context.mode == 'OBJECT'
            layout.operator("object.editmode_toggle", 'Edit Mode', icon='EDITMODE_HLT')
        else:
            layout.operator("object.editmode_toggle", 'Object Mode', icon='OBJECT_DATAMODE')
#        current_mode = bpy.context.mode
#        if current_mode == 'EDIT_MESH'
#        
#        return {"FINISHED"}
        
                 

#        layout.operator("object.editmode_toggle", 'Object Mode', icon='OBJECT_DATAMODE')
        layout.operator("sculpt.sculptmode_toggle", 'Sculpt Mode', icon='SCULPTMODE_HLT')


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


# creates a menu for Sculpt mode tools
class JWSculptTools(bpy.types.Menu):
    bl_label = "Jonathan's Sculpt Tools"
    bl_idname = "sculpt.tools_menu"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.modifier_add", 'Add Subsurf', icon='MOD_SUBSURF').type='SUBSURF'
        layout.operator("object.apply_subsurf", 'Apply Subsurf', icon='MOD_SUBSURF')
        
        layout.separator()
        
        layout.operator("sculpt.symmetry_x", icon='MOD_MIRROR')
        layout.operator("sculpt.symmetry_y")
        layout.operator("sculpt.symmetry_z")
        
        
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

### Creating the hotkeys ###

addon_keymaps = []

def register():
    #register the new menus
    bpy.utils.register_class(JWMeshTools)
    bpy.utils.register_class(JWObjectTools)
    bpy.utils.register_class(JWSculptTools)
    bpy.utils.register_class(ModeSwitch)
    
    #register the new operators
    bpy.utils.register_class(applySubsurf)
    bpy.utils.register_class(sculptSymmetryX)
    bpy.utils.register_class(sculptSymmetryY)
    bpy.utils.register_class(sculptSymmetryZ)
    
    wm = bpy.context.window_manager
    
    # create the mode switcher menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu', 'TAB', 'PRESS', alt=True)
    kmi.properties.name = 'mode.switch_menu'
    
    # create the object mode menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'T', 'PRESS', oskey=True)
    kmi.properties.name = 'object.tools_menu'
    
    # create the sculpt mode menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Sculpt', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'T', 'PRESS', oskey=True)
    kmi.properties.name = 'sculpt.tools_menu'
    
    # create the Sculpt symmetry hotkeys
    kmi = km.keymap_items.new('sculpt.symmetry_x', 'X', 'PRESS', shift=True)
    kmi = km.keymap_items.new('sculpt.symmetry_y', 'Y', 'PRESS', shift=True)
    kmi = km.keymap_items.new('sculpt.symmetry_z', 'Z', 'PRESS', shift=True)
    
    
    # creatue the edit mode menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'T', 'PRESS', oskey=True)
    kmi.properties.name = 'mesh.tools_menu'

    addon_keymaps.append(km)

def unregister():
    #unregister the new menus
    bpy.utils.unregister_class(JWMeshTools)
    bpy.utils.unregister_class(JWObjectTools)
    bpy.utils.register_class(JWSculptTools)
    bpy.utils.register_class(ModeSwitch)
    
    #unregister the new operators
    bpy.utils.register_class(applySubsurf)
    bpy.utils.register_class(sculptSymmetryX)
    bpy.utils.register_class(sculptSymmetryY)
    bpy.utils.register_class(sculptSymmetryZ)
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


if __name__ == "__main__":
    register()
    
    
       