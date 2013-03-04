bl_info = {
    "name": "Boolean Operators",
    "location": "View3D > Toolbar",
    "description": "Add Boolean Operators",
    "author": "Jonathan Williamson",
    "version": (0,3),
    "blender": (2, 6, 6),
    "category": "3D View",
    }

import bpy



###------ Create Boolean Operators -------###
   
class boolean(bpy.types.Operator):
    """Boolean the currently selected objects"""
    bl_idname = "mesh.boolean"
    bl_label = "Boolean Operator"
    bl_options = {'REGISTER', 'UNDO'}     
            
    modOp = bpy.props.StringProperty()
            
    def execute(self, context):
         
        modName = "Bool"
    
        activeObj = context.active_object
        selected = context.selected_objects

        if selected:
            if len(selected) > 1:
                if len(selected) == 2:
                    for ob in selected:
                        if ob != bpy.context.active_object:
                            nonActive = ob
    
                    bpy.ops.object.modifier_add(type="BOOLEAN")   
                    activeMod = bpy.context.active_object.modifiers
                    
                    for mod in activeObj.modifiers:
                        if mod.type == 'BOOLEAN':
                            activeMod[mod.name].operation = self.modOp
                            activeMod[mod.name].object = nonActive
                            activeMod[mod.name].name = modName
                    
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modName)
                    bpy.context.scene.objects.active = nonActive 
                    activeObj.select = False
                    bpy.ops.object.delete(use_global=False)
                    activeObj.select = True
                    bpy.context.scene.objects.active = activeObj
                else:
                    self.report({'INFO'}, "Select only 2 objects at a time")
            else:
                self.report({'INFO'}, "Only 1 object selected")
        else:
            self.report({'INFO'}, "No objects selected")
                
        return {"FINISHED"}     


###------- Create the Boolean Menu --------###          

class booleanMenu(bpy.types.Menu):
    bl_label = "Boolean Tools"
    bl_idname = "object.boolean_menu"
       
    def draw(self, context):
        layout = self.layout
        
        union = layout.operator("mesh.boolean", "Union")
        union.modOp = 'UNION'
        
        intersect = layout.operator("mesh.boolean", "Intersect")
        intersect.modOp = 'INTERSECT'
        
        difference = layout.operator("mesh.boolean", "Difference")
        difference.modOp = 'DIFFERENCE'


###------- Create the Boolean Toolbar --------###          

class booleanToolbar(bpy.types.Panel):
    bl_label = "Boolean Tools"
    bl_idname = "object.boolean_toolbar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        
        col.label(text="Operation:", icon="MOD_BOOLEAN")
        
        row = col.row()
        union = row.operator("mesh.boolean", "Union")
        union.modOp = 'UNION'
        
        intersect = row.operator("mesh.boolean", "Intersect")
        intersect.modOp = 'INTERSECT'
        
        difference = row.operator("mesh.boolean", "Difference")
        difference.modOp = 'DIFFERENCE'
    
###------- Define the Hotkeys and Register Operators ---------###

addon_keymaps = []
    
            
def register():
    bpy.utils.register_class(boolean)
    bpy.utils.register_class(booleanMenu)
    bpy.utils.register_class(booleanToolbar)
    
    wm = bpy.context.window_manager
    
    # create the boolean menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'B', 'PRESS', ctrl=True, shift=True)
    kmi.properties.name = 'object.boolean_menu'


    addon_keymaps.append(km)
    
def unregister():
    bpy.utils.unregister_class(boolean)
    bpy.utils.unregister_class(booleanMenu)
    bpy.utils.unregister_class(booleanToolbar)
    
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]
    
if __name__ == "__main__":
    register()