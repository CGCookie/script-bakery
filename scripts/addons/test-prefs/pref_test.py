import bpy

class printTest(bpy.types.Operator):
    bl_label = "Print Test"
    bl_idname = "view3d.print_test" 

    def execute(self, context):
        print("Test Print")

        return {"FINISHED"}


def register():
    bpy.utils.register_class(printTest)  

def unregister():
    bpy.utils.unregister_class(printTest)    