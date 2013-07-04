import bpy

class QuickSceneOptions(bpy.types.Menu):
	bl_idname = "scene.quick_options"
	bl_label = "Quick Scene Settings"

	def draw(self, context):
	    layout = self.layout

	    layout.operator("gpencil.active_frame_delete", "Delete Grease", icon='GREASEPENCIL')

	    only_render = context.space_data.show_only_render
	    if only_render:
		    layout.operator("scene.show_only_render", "Disable Only Render")
	    else:
	    	layout.operator("scene.show_only_render", "Show Only Render")
	    	
def register():
	bpy.utils.register_class(QuickSceneOptions)


def unregister():
	bpy.utils.unregister_class(QuickSceneOptions)


if __name__ == "__main__":
	register()