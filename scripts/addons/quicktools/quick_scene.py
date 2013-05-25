import bpy

class QuickSceneOptions(bpy.types.Menu):
	bl_idname = "scene.quick_options"
	bl_label = "Quick Scene Settings"

	def draw(self, context):
	    layout = self.layout

	    layout.operator("gpencil.active_frame_delete", "Delete Grease", icon='GREASEPENCIL')

addon_keymaps = []

def register():
	bpy.utils.register_class(QuickSceneOptions)

	wm = bpy.context.window_manager

    # create the Scene Tools menu hotkey
	km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
	kmi = km.keymap_items.new('wm.call_menu', 'ACCENT_GRAVE', 'PRESS', shift=True)
	kmi.properties.name = 'scene.quick_options' 
	
	addon_keymaps.append(km)


def unregister():
	bpy.utils.unregister_class(QuickSceneOptions)

	# remove keymaps when add-on is deactivated
	wm = bpy.context.window_manager
	for km in addon_keymaps:
	    wm.keyconfigs.addon.keymaps.remove(km)
	del addon_keymaps[:]

if __name__ == "__main__":
	register()