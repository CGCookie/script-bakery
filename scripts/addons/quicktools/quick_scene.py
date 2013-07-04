import bpy

class QuickSceneOptions(bpy.types.Menu):
	bl_idname = "scene.quick_options"
	bl_label = "Quick Scene Settings"

	def draw(self, context):
	    layout = self.layout

	    layout.operator("gpencil.active_frame_delete", "Delete Grease", icon='GREASEPENCIL')

def register():
	bpy.utils.register_class(QuickSceneOptions)


def unregister():
	bpy.utils.unregister_class(QuickSceneOptions)


if __name__ == "__main__":
	register()