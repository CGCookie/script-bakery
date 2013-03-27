# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
"""
Author:
    script by Alex Telford | CG Cookie | www.blendercookie.com | www.metalix.co.nz
Description:
    This script will create a panel in the sculpt menu that will all triming objects by creating a boolean based on a grease pencil stroke or a curve.
Warning:
    This script is currently in a public Beta release, there are bugs and I recommend you take a backup of your work, I take no responsibility in any part either direct or in-direct at the loss of any work. Use at your own risk.
KNOWN BUGS:
    On line 290-ish I extrude away from the camera, this needs to be reworked as it is un-predictable.
"""
bl_info = {
    "name": "Sculpt trim curve",
    "author": "Alex Telford",
    "version": (0, 7),
    "blender": (2, 6, 6),
    "location": "View3D > Toolshelf",
    "description": "Trims mesh based on curve or grease pencil stroke",
    "warning": "Public Beta",
    "wiki_url": "",
    "tracker_url": "",
    "category": "View3D"}
    
# import modules
import bpy
from bpy.props import *
from math import *
from mathutils import *


class initialize(bpy.types.Panel):
    """
    Creates the panel with controls, inherits from bpy.types.Panel
    """
    bl_label = "Trim Curves Utility"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    # Our class method will specify which modes this script can be executed in, EDIT has been omitted for cleanliness, but would work.
    @classmethod
    def poll(self, context):
        return(bpy.context.mode == 'OBJECT' or 'SCULPT')

    def propCalls():
        """
        create props for layout
        a prop is an input field
        this is not required to be in a function, but I like to keep the code clean.
        """
        # create object and curve slot for dropdown
        bpy.types.Object.TCinitObject = bpy.props.StringProperty()
        bpy.types.Object.TCinitCurve = bpy.props.StringProperty()
        # curve or grease pencil enum
        bpy.types.Scene.TCinitCurveType = bpy.props.EnumProperty(
        items = [('1', 'Grease Pencil', 'grease'), 
                 ('2', 'Curve', 'curve')],
        name = "curveType")
        # create initial value boxes
        bpy.types.Scene.TCinitDepth = FloatProperty(name = "Depth", description = "depth from view", default = 5.00, min = -100, max = 100)
        bpy.types.Scene.TCinitDivision = FloatProperty(name = "Division", description = "Division Spacing", default = 0.5, min = -100, max = 100)
        bpy.types.Scene.TCinitExtrusion = FloatProperty(name = "Extrusion", description = "Extrusion Depth", default = 5, min = -100, max = 100)
        # axis enum
        bpy.types.Scene.TCinitAxis = bpy.props.EnumProperty(
        items = [('1', '3D Cursor', 'cursor'),
                 ('2', 'X', 'x'), 
                 ('3', 'Y', 'y')],
        name = "axisType")
        # apply modifier
        bpy.types.Scene.TCinitApplyMod = BoolProperty(
            name = "Apply Boolean", 
            description = "Apply Boolean?",
            default = True)
        # is cyclic or extrude
        bpy.types.Scene.TCinitCyclic = BoolProperty(
            name = "Cyclic", 
            description = "Disable extrusion and enable cyclic hole?",
            default = False)
        # reverse direction
        bpy.types.Scene.TCinitReverseDir = BoolProperty(
            name = "Reverse Direction", 
            description = "Reverse Direction",
            default = False)
        # reverse depth
        bpy.types.Scene.TCinitReverseDepth=  BoolProperty(
            name = "Reverse Depth", 
            description = "Reverse Depth of extrusion",
            default = False)
        # reverse trim
        bpy.types.Scene.TCinitReverseTrim = BoolProperty(
            name = "Reverse Trim", 
            description = "Reverse Trim",
            default = False)
        # return to mode enum
        bpy.types.Scene.TCinitReturnMode = bpy.props.EnumProperty(
        items = [('1', 'Sculpt', 'sculpt'), 
                 ('2', 'Object', 'object'), 
                 ('3', 'Edit', 'edit')],
        name = "returnMode")
    # Initiate prop calls
    propCalls()
    def draw(self, context):
        """
        draw will create our panel using the pre-defined settings from propCalls
        """
        # Short Code
        obj = context.object
        scn = context.scene
        # create column layout
        layout = self.layout
        col = layout.column()
        # Create layout in a try except so we can return a custom error
        try:
            # layout items
            col.label("Curve Type")
            col.prop(scn, 'TCinitCurveType', text = '')
            # object
            col.label("Object")
            col.prop_search(obj, "TCinitObject",  scn, "objects", text = '', icon = 'MESH_DATA')
            # curve
            if scn.TCinitCurveType == '2':
                col.label("Curve")
                col.prop_search(obj, "TCinitCurve",  scn, "objects", text = '', icon = 'CURVE_DATA')
            # options
            col.prop(scn, "TCinitCyclic")
            col.label("Depth Cut")
            col.prop(scn, "TCinitDepth", text = '')
            col.label("Division Spacing")
            col.prop(scn, "TCinitDivision", text = '')
            # if not cyclic show these options
            if scn.TCinitCyclic == False:
                col.label("Extrusion Depth")
                col.prop(scn, "TCinitExtrusion", text = '')
                col.prop(scn, "TCinitAxis")
            # more options
            col.prop(scn, "TCinitApplyMod")
            col.prop(scn, "TCinitReverseDir")
            col.prop(scn, "TCinitReverseDepth")
            col.prop(scn, "TCinitReverseTrim")
            col.prop(scn, "TCinitReturnMode")
            # execute button
            layout.operator("trim.curves")
        except:
            # if fail there were no objects
            col.label("No Objects in Scene")

class OBJECT_OT_trimCurve(bpy.types.Operator):
    """
    This class will execute our script, options will be taken from props
    """
    bl_idname = "trim.curves"
    bl_label = "Trim Curve"
    
    def execute(self, context):
        """
        We execute all the code here based on props
        """
        # short code
        obj = context.object
        scn = context.scene
        
        # Trim function #
        # convert pencil to curve or return curve
        bpy.ops.object.mode_set(mode='OBJECT')
        # 1 = pencil stroke
        if scn.TCinitCurveType == '1':
            # check if stroke exists
            try:
                bpy.ops.gpencil.convert(type='PATH')
            except:
                print('Stroke does not exist')
                self.report({'WARNING'}, "No strokes found.")
                return{'FINISHED'}
            # loop through strokes
            for ob in bpy.context.selected_objects:
                    # all strokes start with GP_Layer
                    if ob != bpy.context.scene.objects.active and ob.name.startswith("GP_Layer"):
                        # create curve variable
                        curve = ob
                        bpy.ops.object.select_all(action='DESELECT') 
                        # set curve resolution from default 12 to 1
                        curve.select = True
                        bpy.context.scene.objects.active = curve
                        bpy.context.object.data.resolution_u = 1
        else:
            # check if curve exists
            try:
                # create curve variable
                curve = bpy.data.objects[obj.TCinitCurve]
            except:
                print('curve does not exist')
                self.report({'WARNING'}, "No curve selected.")
                return{'FINISHED'}
        
        # check if mesh exists
        try:
            # create mesh variable
            mesh = bpy.data.objects[obj.TCinitObject]
        except:
            print('mesh does not exist')
            self.report({'WARNING'}, "No mesh selected.")
            return{'FINISHED'}
            
        # select curve
        bpy.ops.object.select_all(action='DESELECT') 
        curve.select = True
        bpy.context.scene.objects.active = curve
        # edit curve
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        # if cyclic set to cyclic
        if scn.TCinitCyclic == True:
            for spline in curve.data.splines:
                spline.use_cyclic_u = True
        # object mode and convert to mesh
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='MESH', keep_original=False)
        
        # rotate curve pivot to view for local transformations #    
            
        # select curve
        bpy.ops.object.select_all(action='DESELECT') 
        curve.select = True
        bpy.context.scene.objects.active = curve
        # center origin
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        # get cursor location, set to vector to break link
        cursorInit = Vector(bpy.context.scene.cursor_location)
        # add temporary empty
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=True)
        # assign the emtpy to a variable
        for ob in bpy.context.selected_objects:
                if ob.name.startswith("Empty"):
                    empty = ob
        
        # get pivot
        pivotPoint = context.space_data.pivot_point
        # set cursor location to curve
        bpy.context.scene.cursor_location = curve.location
        # rotate around cursor
        context.space_data.pivot_point = "CURSOR"
        # select none
        bpy.ops.object.select_all(action='DESELECT')
        # select curve
        curve.select = True
        bpy.context.scene.objects.active = curve
        # apply rotation
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        # rotate pivot of curve to rotation of empty
        rotatePivot(empty.rotation_euler)
        # set pivot point back to original
        context.space_data.pivot_point = pivotPoint
        # set cursor location back to original
        bpy.context.scene.cursor_location = cursorInit
        
        # delete empty
        bpy.ops.object.select_all(action='DESELECT')
        empty.select = True
        bpy.context.scene.objects.active = empty
        bpy.ops.object.delete(use_global=False)
        
        # select curve
        curve.select = True
        bpy.context.scene.objects.active = curve
        
        # move curve towards camera #
        # calculate correct xyz values based on view angle #
        
        # enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # get initial curve location
        Ci = Vector(curve.location)
        
        # Create transformation matrix
        localTranslationForward = Matrix.Translation((0, 0, scn.TCinitDepth/2))
        # move along local coordinates
        curve.matrix_world = curve.matrix_world * localTranslationForward
        
        # extrude from camera enough times to make divisions #
        # fill first face if cyclic
        if scn.TCinitCyclic == True:
           bpy.ops.mesh.fill(use_beauty=True)
        # calculate number of extrusions required, minimum 1
        extrusions = max(1,round(scn.TCinitDepth/scn.TCinitDivision))
        # get depth of each extrusion
        extrusionDepth = scn.TCinitDepth/extrusions
        
        # calculate translation for edit mode #
        # new curve location
        Co = Vector(curve.location)
        # BUG option to reverse depth if required
        if scn.TCinitReverseDepth == True:
            # get local space transformations
            distVecCam = world2local(Ci,Co,extrusionDepth)
        else:
            # get invertes local space transformations
            distVecCam = world2local(Ci,Co,-extrusionDepth)
        # extrude for each extrusion
        i = 1
        while i <= extrusions:
            bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":distVecCam, "constraint_axis":(False, False, True), "constraint_orientation":'LOCAL'})
            i += 1
            # fill end cap if it is cyclic to retain whole mesh
            if i == extrusions and scn.TCinitCyclic == True:
               bpy.ops.mesh.fill(use_beauty=True)
        # select all mesh
        bpy.ops.mesh.select_all(action='SELECT')
        # calculate extrusion depth from point
        extrusions = max(1,round(scn.TCinitExtrusion/extrusionDepth))
        
        # Where are we extruding from #
        i = 1
        # are we reversing direction
        if scn.TCinitReverseDir == True:
            dir = -1
        else:
            dir = 1
        # only do this if cyclic is false
        if scn.TCinitCyclic == False:
            if scn.TCinitAxis == '1':
                # cursor #
                # calculate local transforms
                distVecCursor = world2local(curve.location,cursorInit,extrusionDepth) * dir
                # set pivot to cursor
                context.space_data.pivot_point = "CURSOR"
                # extrude until extrusion depth
                while i <= extrusions:
                    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0)})
                    bpy.ops.transform.translate(value=distVecCursor, constraint_axis=(True, True, True), constraint_orientation='LOCAL')
                    i += 1
                # set pivot to original
                context.space_data.pivot_point = pivotPoint
            elif scn.TCinitAxis == '2':
                # X #
                # Create transformation matrices
                localTranslationX = Matrix.Translation((10, 0, 0))
                localTranslationXi = Matrix.Translation((-10, 0, 0))
                # move to new location
                curve.matrix_world = curve.matrix_world * localTranslationX
                # store new location
                localTargetX = Vector(curve.location)
                # move back
                curve.matrix_world = curve.matrix_world * localTranslationXi
                # get local transform direction
                distX = world2local(Ci,localTargetX, extrusionDepth) * dir
                # extrude in this new direction
                while i <= extrusions:
                    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0)})
                    bpy.ops.transform.translate(value=distX, constraint_axis=(True, False, False), constraint_orientation='LOCAL')
                    i += 1
            elif scn.TCinitAxis == '2':
                # Y #
                # Create transformation matrix
                localTranslationY = Matrix.Translation((0, 10, 0))
                localTranslationYi = Matrix.Translation((0, -10, 0))
                # move to new location
                curve.matrix_world = curve.matrix_world * localTranslationY
                # store new location
                localTargetY = Vector(curve.location)
                # move back
                curve.matrix_world = curve.matrix_world * localTranslationYi
                # extrude in this new direction
                distY = world2local(Ci,localTargetY, extrusionDepth) * dir
                while i <= extrusions:
                    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0)})
                    bpy.ops.transform.translate(value=distY, constraint_axis=(False, True, False), constraint_orientation='LOCAL')
                    i += 1
        # set object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # create boolean #
        # set mesh as active
        bpy.context.scene.objects.active = mesh
        # add boolean modifier
        bpy.ops.object.modifier_add(type='BOOLEAN')
        # if reverse is true set to intersect
        if scn.TCinitReverseTrim == True:
            bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
        else:
            bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
        bpy.context.object.modifiers["Boolean"].object = curve

        # apply boolean object
        if scn.TCinitApplyMod == True:
            # set mesh as active
            bpy.context.scene.objects.active = mesh
            # apply all boolean modifiers
            for mod in bpy.context.object.modifiers:
                if mod.type == 'BOOLEAN':
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
            # deselect mesh
            bpy.ops.object.select_all(action='DESELECT') 
            # select curve
            curve.select = True 
            # delete curve
            bpy.ops.object.delete(use_global=False)
        
        # return to mode
        if scn.TCinitReturnMode == '1':
            bpy.ops.sculpt.sculptmode_toggle()
        elif scn.TCinitReturnMode == '3':
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            bpy.ops.object.mode_set(mode='OBJECT')
        # set pivot to cursor
        context.space_data.pivot_point = "BOUNDING_BOX_CENTER"
        return{'FINISHED'}
# functions #
def rotatePivot(rotation):
    """
    rotatePivot(Vector rotation)
    This function will take a vector rotation and rotate the curently selected objects pivot to match without affecting their physical display
    Make sure that you rotate around the cursor and have the entire mesh selected or this will not work.
    This operates on an xyz euler.
    """
    # Rotate in object mode X
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.transform.rotate(value=rotation.x, axis=(1,0,0), constraint_orientation='GLOBAL')
    # rotate in edit mode X
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.rotate(value=-rotation.x, axis=(1,0,0), constraint_orientation='GLOBAL')
    # Rotate in object mode Y
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.transform.rotate(value=rotation.y, axis=(0,1,0), constraint_orientation='GLOBAL')
    # rotate in edit mode Y
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.rotate(value=-rotation.y, axis=(0,1,0), constraint_orientation='GLOBAL')
    # Rotate in object mode Z
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.transform.rotate(value=rotation.z, axis=(0,0,1), constraint_orientation='GLOBAL')
    # rotate in edit mode Z
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.rotate(value=-rotation.z, axis=(0,0,1), constraint_orientation='GLOBAL')
    # return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

def world2local(a,b, depth):
    """
    world2local(Vector  a,Vector b, float depth)
    This function will create a vector to translate between points a and b based on a depth.
    """
    # calculate angles based on 3 dimensional trigonometry
    thetaA = atan( (a.z-b.z)/( sqrt( pow(a.x-b.x,2) + pow(a.y-b.y,2) ) ) )
    thetaB = atan( (a.y-b.y)/(a.x-b.x) )
    # calculate the vector
    distVec = Vector([cos(thetaB) * cos(thetaA) * depth,
    sin(thetaB) * cos(thetaA) * depth,
    sin(thetaA) * depth])
    # return the vector
    return distVec
# Register functions #
def register():
    # initialize classes #
    bpy.utils.register_class(initialize)
    bpy.utils.register_class(OBJECT_OT_trimCurve)
def unregister():
    # uninitialize classes #
    bpy.utils.unregister_class(initialize)
    bpy.utils.register_class(OBJECT_OT_trimCurve)