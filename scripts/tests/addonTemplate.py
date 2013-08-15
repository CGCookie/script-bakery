#script template by Alex Telford | www.cgcookie.com
#script by Your name | Your site
#Description:
#Add in a description of your script here
bl_info = {
    "name": "Script Name",
    "author": "Your Name",
    "version": (0, 1),
    "blender": (2, 6, 6),
    "location": "View3D > Toolshelf",
    "description": "Description",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "View3D"}
    
#import modules
import bpy
from bpy.props import *

class myScriptInitialize(bpy.types.Panel):
    bl_label = "Panel Name"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #mode that the panel will show in, OBJECT, SCULPT or EDIT
#    @classmethod
#    def poll(self, context):
#        return(bpy.context.mode == 'OBJECT')
    #defing props for layout
    def propCalls():
        #create props for layout
        #examples
        #create object  slot for dropdown
        bpy.types.Object.myObject = bpy.props.StringProperty()
        #enum dropdown
        bpy.types.Scene.myEnum = bpy.props.EnumProperty(
        items = [('1', 'visible text', 'hover text'), 
                 ('1', 'visible text', 'hover text')],
        name = "enumName")
        #create float box
        bpy.types.Scene.myFloat = FloatProperty(name = "My Float", description = "My Float", default = 0.0, min = -10, max = 10)
        #check box
        bpy.types.Scene.myCheckBox= BoolProperty(
            name = "My CheckBox", 
            description = "My Check Box",
            default = True)
        
    #define props
    propCalls()
    def draw(self, context):
        obj = context.object
        scn = context.scene
        
        layout = self.layout
        col = layout.column()
        
        #try to layout, otherwise say something else
        try:
            #layout items
            col.label("My Object")
            col.prop_search(obj, "myObject",  scn, "objects", text = '', icon = 'MESH_DATA')

            col.label("My Enum")
            col.prop(scn, "myEnum", text = '')
            
            col.label("My Float")
            col.prop(scn, "myFloat", text = '')
            
            col.label("My Check Box")
            col.prop(scn, "myCheckBox", text = '')
            
            #execute button
            layout.operator("thisismyscript.withonedot")
        except:
            #couldn't fill object list
            col.label("No Objects in Scene")


#run
class OBJECT_OT_myScript(bpy.types.Operator):
    bl_idname = "thisismyscript.withonedot"
    bl_label = "Execute My Script"
    
    def execute(self, context):
        obj = context.object
        scn = context.scene
        
        ###Run Script
        print (obj.myObject)
        print (scn.myEnum)
        print (scn.myFloat)
        print (scn.myCheckBox)
        #warnings use this context if you need them, here we just print the stuff
        self.report({'WARNING'}, "Done!")
        return{'FINISHED'}

def register():
    ###initialize classes
    bpy.utils.register_class(myScriptInitialize)
    bpy.utils.register_class(OBJECT_OT_myScript)
def unregister():
    bpy.utils.unregister_class(myScriptInitialize)
    bpy.utils.register_class(OBJECT_OT_myScript)