#script by Alex Telford | CG Cookie | www.blendercookie.com
#Description:
#This script will export a text file for use in pro builder for unity
#Usage:
#Load as an addon, it will appear in the 3D view tool shelf as a single button. Currently only works with one object at a time.
#version 1.1 - added support for triangles and ngons
#automatically creates quads and tris from nGons
bl_info = {
    "name": "Export Mesh Data for Pro Builder",
    "author": "Alex Telford",
    "version": (1, 1),
    "blender": (2, 6, 4),
    "api": 51026,
    "location": "View3D > Tool Shelf",
    "description": "Exports mesh data for Pro Builder",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}
#import data modules
import bpy
import os
#create data for panel
class exportData(bpy.types.Operator):
    bl_idname = "export.export_data"
    bl_label = "Export Data"
    #user specified file path for file output
        obV = bpy.context.active_object.data.vertices
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    #actual code for functions
    def execute(self, context):
		#store vertex and face data in variables
        obF = bpy.context.active_object.data.polygons
		#let's fix the model first
        bpy.ops.object.mode_set(mode='EDIT')
		#select nGons
        bpy.ops.mesh.select_by_number_vertices(number=4, type='GREATER')
		#convert nGons to triangles
        bpy.ops.mesh.quads_convert_to_tris(use_beauty=True)
		#convert triangles to quads, not pretty but is better than holes in the mesh.
        bpy.ops.mesh.tris_convert_to_quads(limit=0.698132, uvs=False, vcols=False, sharp=False, materials=False)
		#return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
		#create file to write
        file = open(self.filepath, 'w')
		#loop through each face
        for face in obF:
			#check if it is a triangle
            if len(face.vertices) == 3:
				#order for triangles
                vs = [face.vertices[1],face.vertices[0],face.vertices[2],face.vertices[1]]
            else:
				#order for quads
                vs = [face.vertices[3],face.vertices[0],face.vertices[2],face.vertices[1]]
			#loop through vertices in new face creation order
            for v in vs:
				#grab the vertex location
                crV = obV[v].co
				#output the vertices to probuilder data
                faces = ""
                faces += str(crV[0])
                faces += ","
                faces += str(crV[1])
                faces += ","
                faces += str(crV[2])
                faces += "\n"
				#write that data to the file
                file.write(str(faces))
                
        return {'FINISHED'}
    #the rest of this stuff is just initiating the panel.
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class exportDataPanel(bpy.types.Panel):
    bl_idname = "Export_Data"
    bl_label = "Export Data"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("export.export_data", text="Export Data")
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)