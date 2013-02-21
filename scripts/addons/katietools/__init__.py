bl_info = {
    "name": "Katie Tools",
    "description": "A collection of simple scene tools",
    "author": "Kent Trammell",
    "version": (1,0),
    "blender": (2,6,3),
    "api": 46461,
    "location": "View3D > Toolshelf",
    "warning": 'work in progrss',
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"}

# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
    import imp
    imp.reload(tools_display)
    imp.reload(tools_relationship)
    imp.reload(tools_names)
    imp.reload(tools_mesh)
    imp.reload(tools_sculpt)
    imp.reload(tools_materials)
    imp.reload(tools_cleanup)
    imp.reload(tools_render)
    print("Reloaded multifiles")
else:
    from . import tools_display, tools_relationship, tools_names, tools_mesh, tools_sculpt, tools_materials, tools_cleanup, tools_render
                  
    print("Imported multifiles")

import bpy
import os
import random
import math
#import time
#from operator import itemgetter

EDIT = ["EDIT_MESH", "EDIT_CURVE", "EDIT_SURFACE", "EDIT_METABALL", "EDIT_TEXT", "EDIT_ARMATURE"]

#-------------------------------------------------------
#-------------- PANEL DRAW------------------------------
#-------------------------------------------------------

class OBJECT_PT_sceneToolboxPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_scene_toolbox"
    bl_label = "Katie Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_context = "objectmode"
    
    '''@classmethod
    def poll(self, context):
        try:
            return (context.mode not in EDIT)
        except (AttributeError, KeyError, TypeError):
            return False'''
    
    def draw(self, context):
        kt = bpy.context.window_manager.katietools
        engine = bpy.context.scene.render.engine
        layout = self.layout
        scn = bpy.context.scene
        ktScn = scn.kt_scene_props
                
        #DISPLAY
        if context.mode not in EDIT:
            col = layout.column(align=True)
            
            if kt.display_display == True:
                col.prop(kt, 'display_display', icon='RIGHTARROW')
            else:
                col.prop(kt, 'display_display', icon='DOWNARROW_HLT')
                
                box = layout.column(align=True).box().column()
                    
                box_col = box.column(align=True)
                box_col.label(text="OpenGL Presets:")
                   
                if kt.ogl_toggle == False:
                    box_col = box.column(align=True)
                    split = box_col.split(percentage=0.7,align=True)
                    colL = split.column()
                    colR = split.row(align=True)
                
                    colL.prop(kt,"ogl_preset_enum","") 
                    colR.operator("system.ogl_apply_preset",'',"LAMP_SUN")
                    colR.prop(kt,"ogl_toggle",'','ZOOMIN')
                    colR.operator("system.ogl_delete_preset",'','ZOOMOUT')
                    
                if kt.ogl_toggle == True:
                    box_col = box.column(align=True)
                    split = box_col.split(percentage=0.8,align=True)
                    colL = split.column()
                    colR = split.row(align=True)
                    
                    colL.prop(kt,"ogl_name","")
                    colR.operator("system.ogl_add_preset",'',"FILE_TICK")
                    colR.prop(kt,"ogl_toggle",'',"CANCEL")
                      
                
                box_col = box.column(align=True)
                box_col = box.column(align=True)
                box_col.label(text="Toggles:")
                box_col.operator("object.double_sided_toggle")#icon="CHECKBOX_DEHLT"       
                box_col.operator("object.all_edges_toggle")
                box_col.operator("object.wire_only")
                box_col.operator("object.all_names_toggle")
                box_col.operator("object.all_axis_toggle")                
                box_col.operator("object.all_transparent_toggle")
                
                box_col = box.column(align=False)
                box_col = box.column(align=True)
                
                
                # Filter Visible
                box_col.label(text="Filter Visible:")
                
                if len(kt.ob_fvStore) > 0:
                    storeCb = "CHECKBOX_HLT"
                    storeLabel = "Clear Stored"
                else:
                    storeCb = "CHECKBOX_DEHLT"
                    storeLabel = "Store"
                
                box_col = box.column(align=False)      
                box_col.operator("object.fv_store",storeLabel, icon=storeCb)
                
                box_col = box.column(align=False)
                box_col = box.column(align=True)
                box_row = box_col.row(align=True)
                
                if kt.fvMESH == True:
                    icn = "OUTLINER_OB_MESH"
                else:
                    icn = "OUTLINER_DATA_MESH"      
                toggMesh = box_row.operator("object.fv_toggle","",icon=icn) 
                toggMesh.fvType = "MESH"
                
                if kt.fvCURVE == True:
                    icn = "OUTLINER_OB_CURVE"
                else:
                    icn = "OUTLINER_DATA_CURVE"
                toggCurve = box_row.operator("object.fv_toggle","",icon=icn)
                toggCurve.fvType = "CURVE"
                
                if kt.fvSURFACE == True:
                    icn = "OUTLINER_OB_SURFACE"
                else:
                    icn = "OUTLINER_DATA_SURFACE" 
                toggSurf = box_row.operator("object.fv_toggle","",icon=icn)
                toggSurf.fvType = "SURFACE"
                
                if kt.fvMETA == True:
                    icn = "OUTLINER_OB_META"
                else:
                    icn = "OUTLINER_DATA_META" 
                toggMeta = box_row.operator("object.fv_toggle","",icon=icn)
                toggMeta.fvType = "META"
                
                if kt.fvFONT == True:
                    icn = "OUTLINER_OB_FONT"
                else:
                    icn = "OUTLINER_DATA_FONT" 
                toggFont = box_row.operator("object.fv_toggle","",icon=icn)
                toggFont.fvType = "FONT"
                
                #box_row = box_col.row(align=True)
                
                if kt.fvARMATURE == True:
                    icn = "OUTLINER_OB_ARMATURE"
                else:
                    icn = "OUTLINER_DATA_ARMATURE" 
                toggArm = box_row.operator("object.fv_toggle","",icon=icn)
                toggArm.fvType = "ARMATURE"
                
                if kt.fvLATTICE == True:
                    icn = "OUTLINER_OB_LATTICE"
                else:
                    icn = "OUTLINER_DATA_LATTICE" 
                toggLat = box_row.operator("object.fv_toggle","",icon=icn)
                toggLat.fvType = "LATTICE"
                
                if kt.fvEMPTY == True:
                    icn = "OUTLINER_OB_EMPTY"
                else:
                    icn = "OUTLINER_DATA_EMPTY" 
                toggEmpty = box_row.operator("object.fv_toggle","",icon=icn)
                toggEmpty.fvType = "EMPTY"
                
                if kt.fvCAMERA == True:
                    icn = "OUTLINER_OB_CAMERA"
                else:
                    icn = "OUTLINER_DATA_CAMERA" 
                toggCam = box_row.operator("object.fv_toggle","",icon=icn)
                toggCam.fvType = "CAMERA"
                
                if kt.fvLAMP == True:
                    icn = "OUTLINER_OB_LAMP"
                else:
                    icn = "OUTLINER_DATA_LAMP" 
                toggLamp = box_row.operator("object.fv_toggle","",icon=icn)
                toggLamp.fvType = "LAMP"
                
                if kt.fvSPEAKER == True:
                    icn = "OUTLINER_OB_SPEAKER"
                else:
                    icn = "OUTLINER_DATA_SPEAKER" 
                toggSpeak = box_row.operator("object.fv_toggle","",icon=icn)
                toggSpeak.fvType = "SPEAKER"
    
                box_col = box.column(align=False)
    
                box_col.label(text="Smoothing:")
                box_row = box.row(align=True)
                
                box_row.prop(kt,"subD_val",'')
                box_row.prop(kt,"subD_val_ren",'')
                box_row.operator("object.mod_add_subsurf")
                box_row.operator("object.mod_remove_subsurf")
                
                box_col = box.column(align=True)
                
                split = box_col.split(percentage=1,align=True)
                split.prop(kt, 'subD_limit', 'Limit')
                
                split = box_col.split(percentage=0.8,align=True)
                colL = split.column()
                colR = split.row(align=True)
                
                unsmoothToggle = []
                for ob in scn.objects:
                    if ob.unsmoothable == True:
                        unsmoothToggle.append(ob)
                            
                if len(unsmoothToggle) == 0:
                    box_col.operator("object.tag_unsmooth")
                else:    
                    colL.operator("object.tag_unsmooth")
                    colR.operator("object.select_unsmooth","",icon='HAND')
                    colR.operator("object.clear_unsmooth","",icon='PANEL_CLOSE')
                
                #box_col.prop(scn, "disp_unsmoothable","")
            
            
        #RELATIONSHIP
        if context.mode == 'OBJECT':
            col = layout.column(align=True)
            
            if kt.display_relationship == True:
                col.prop(kt, 'display_relationship', icon='RIGHTARROW')   
            else:
                col.prop(kt, 'display_relationship', icon='DOWNARROW_HLT') 
            
                box = layout.column(align=True).box().column()
                box_col = box.column(align=True) 
                box_row = box.row(align=True)
                
                box_col.label(text="ktGroups:")
                box_row.operator("object.create_ktgroup","ktGroup",icon="ZOOMIN")
                box_row.operator("object.ungroup_ktgroup","Ungroup",icon="ZOOMOUT")
                
                box_col = box.column(align=True)
                box_col = box.column(align=True)
                
                box_col.operator("object.center_ktgroup","Center to Cursor",icon="OUTLINER_OB_EMPTY")        
                box_col.operator("object.duplicate_ktgroup","Duplicate",icon="OUTLINER_OB_EMPTY")
                box_col.operator("object.merge_ktgroup","Merge",icon="OUTLINER_OB_EMPTY")
                box_col.operator("object.delete_ktgroup","Delete",icon="OUTLINER_OB_EMPTY")
                box_col = box.column(align=True)            
                box_col.label(text="Buddy Meshes:")
                box_col.operator("object.combine_meshes",icon="OBJECT_DATAMODE")
                box_col.operator("object.split_posemesh",icon="OBJECT_DATAMODE")       

        
        #NAMES
        if context.mode == 'OBJECT':
            col = layout.column(align=False)
                    
            if kt.display_naming == True:
                col.prop(kt, 'display_naming', icon='RIGHTARROW')
            else:
                col.prop(kt, 'display_naming', icon='DOWNARROW_HLT')
            
                box = layout.column(align=True).box().column()
                box_col = box.column(align=True)
                split = box_col.split(percentage=1)
                              
                split.prop(kt,'rename_base', '')
                
                split = box_col.split(percentage=0.5)
                
                split.operator("object.renamer_base")
                split.operator("object.select_by_base")
                
                box_row = box.row(align=True)
                box_row = box.row(align=True)
                
                box_colB = box.column(align=True)
                box_rowB = box_colB.row()            
                box_rowB.prop(kt,'rename_prefix', '')                
                box_rowB.operator("object.add_prefix")
                box_rowB = box_colB.row()
                box_rowB.prop(kt,'rename_suffix', '')      
                box_rowB.operator("object.add_suffix")
                
                box_row = box.row(align=True)
                box_row = box.row(align=True)
                
                box_col = box.column(align=False)
                box_col.operator("object.copy_data_names",icon="MESH_DATA")
            
            
        #MESH
        if context.mode == 'OBJECT' or context.mode == 'EDIT_MESH':
            col = layout.column(align=False)
                    
            if kt.display_mesh == True:
                col.prop(kt, 'display_mesh', icon='RIGHTARROW')
            else:
                col.prop(kt, 'display_mesh', icon='DOWNARROW_HLT')
            
                box = layout.column(align=True).box().column()
                box_col = box.column(align=True)
                box_row = box.row(align=True)
                              
                box_col.operator("mesh.calc_total_edge_length","Edge Length",icon="EDGESEL")
                box_col.operator("object.reset_normals","Reset Normals",icon="FACESEL")
                box_col.operator("object.copy_vertex_order_by_uvs","Copy Vert Order",icon="EDITMODE_HLT")
                
                if context.mode == 'OBJECT':
                    box_col = box.column(align=True)
                    box_col.label(text="Shape Keys:")
                    
                    box_col.operator("object.sk_select", "Select Ob with SKs", icon="HAND")
                    box_col.operator("data.shapekey_apply","Apply SKs",icon="SHAPEKEY_DATA")
                    box_col.operator("object.sk_symmetrize",icon="MOD_MIRROR")
                    
                    box_col2 = box.column(align=False)
                    box_col2 = box.column(align=True)
                    split = box_col2.split(percentage=0.5,align=True)
                    colL = split.column()
                    colR = split.row()
                    
                    colL.prop(kt,'cl_skFix', '')
                    colR.prop(kt,'cl_skTrans', '')
                    if kt.cl_absTrans == False:
                        icn = "CHECKBOX_DEHLT"
                    else:
                        icn = "CHECKBOX_HLT"
                    colR.prop(kt, 'cl_absTrans', '',icon=icn)
                    box_col2.operator("data.shapekey_split",icon="SHAPEKEY_DATA") 
                
        #SCULPT
        if context.mode == 'SCULPT':
            col = layout.column(align=False)
                    
            if kt.display_sculpt == True:
                col.prop(kt, 'display_sculpt', icon='RIGHTARROW')
            else:
                col.prop(kt, 'display_sculpt', icon='DOWNARROW_HLT')
            
                box = layout.column(align=True).box().column()
                box_col = box.column(align=True)
                box_row = box.row(align=True)
                              
                box_col.operator("sculpt.lock_axis_x","Lock X",icon="EDGESEL")            
        
        #MATERIALS
        if context.mode not in EDIT:
            col = layout.column(align=False)
                    
            if kt.display_materials == True:
                col.prop(kt, 'display_materials', icon='RIGHTARROW')
            else:
                col.prop(kt, 'display_materials', icon='DOWNARROW_HLT')
            
                box = layout.column(align=True).box().column()
                box_row = box.row(align=True)
                box_col = box.column(align=True)
                box_col = box.column(align=True)
                splitter = box_col.split(percentage=0.9,align=True)
                rowL = splitter.column()
                rowR = splitter.column()
                #------------changing settings
                
                box_row.prop(kt,"mat_type", expand=True)
                    
                if kt.mat_type == 'Color':
                    if kt.mat_colors_exist == False:
                        box_col.operator("material.create_color_mats",icon="COLOR")  
                    elif kt.mat_colors_exist == True:
                        rowL.prop(kt,"mat_color","")
                        rowR.operator("object.mat_spec_toggle",'S') 
                        box_col.operator("material.assign_mat",icon="MATERIAL")
                elif kt.mat_type == 'MatCap':
                    if kt.mat_matcaps_exist == False or kt.mat_matcap == '':
                        box_col.operator("object.create_matcaps",icon="TEXTURE_SHADED")
                    elif kt.mat_matcaps_exist == True or kt.mat_matcap != '':
                        rowL.prop(kt,"mat_matcap","")
                        rowR.operator("object.refresh_matcap",'',icon="FILE_REFRESH")
                        box_col.operator("object.assign_matcap",icon="MATERIAL")
    
                box_col = box.column(align=False)
                box_col = box.column(align=False)
                box_col = box.column(align=True)
                
                box_col.operator("object.clear_mats",icon="X")
                box_col.operator("object.select_by_mat",icon="HAND")
                box_col.operator("object.mat_link_switch",icon="ARROW_LEFTRIGHT")  
                   
                
        #CLEANUP
        if context.mode == 'OBJECT':
            col = layout.column(align=False)
                    
            if kt.display_cleanup == True:
                col.prop(kt, 'display_cleanup', icon='RIGHTARROW')
            else:
                col.prop(kt, 'display_cleanup', icon='DOWNARROW_HLT')
            
                box = layout.column(align=True).box().column()
                box_col = box.column(align=True)
                split = box_col.split(percentage=0.9)
                
                split.operator("object.apply_mirror_mods",icon="MOD_MIRROR")
                split.operator("object.select_mirror_mods",icon="HAND")
                split = box_col.split(percentage=0.9)
                split.operator("object.apply_solidify_mods",icon="MOD_SOLIDIFY")
                split.operator("object.select_solidify_mods",icon="HAND")
                split = box_col.split(percentage=0.9)
                split.operator("data.uv_nuke",icon="GROUP_UVS")
                split.operator("object.select_uv",icon="HAND")
                split = box_col.split(percentage=0.9)
                split.operator("data.vg_nuke","Nuke V Groups",icon="GROUP_VERTEX")
                split.operator("object.select_vg",icon="HAND")
                split = box_col.split(percentage=0.9)
                split.operator("data.vc_nuke",'Nuke V Colors',icon="GROUP_VCOL")
                split.operator("object.vc_select",icon="HAND")
                split = box_col.split(percentage=1)
                split.operator("mat.delete_unused",icon="MATERIAL")
                
                box_col = box.column(align=False)
                box_col = box.column(align=False)
                split = box_col.split(percentage=0.4,align=True)
                split.prop(kt,"cl_clearDataKey",'')
                clearData = split.operator("data.clean_data")
                clearData.key = kt.cl_clearDataKey
            
            
        #RENDER
        if context.mode == 'OBJECT':
            col = layout.column(align=False)
                    
            if kt.display_render == True:
                col.prop(kt, 'display_render', icon='RIGHTARROW')
            else:
                col.prop(kt, 'display_render', icon='DOWNARROW_HLT')
                
                col = layout.column(align=True)
                row = layout.row(align=True)
                
                row.prop(kt,"ren_type", expand=True) #Engine selector
                
                #-------------SNAPSHOT --------------------
                col = layout.column(align=True)         
                col.label(text="Snapshot:")
                
                box = layout.box()
                box_col = box.column(align=True)
                
                if scn.camera == None:
                    box_col.operator('render.ss_add_camera','Add Camera',icon="CAMERA_DATA")
                else:    
                    if len(scn.ss_camAngles) == 0:
                        box_col.operator('render.ss_angle_add',icon="ZOOMIN")
                    else:
                        box_col.operator('render.ss_angle_add',icon="ZOOMIN")    
                        box_col = box.column(align=True)
            
                        for i, cam in enumerate(scn.ss_camAngles):
                            box_row = box_col.row(align=True)
                            box_row.prop(cam, "angleName","")   
                            box_row.prop(cam, "toggle_still","",icon="RENDER_STILL")
                            box_row.prop(cam, "toggle_turn","",icon="RENDER_ANIMATION")
                            preview = box_row.operator("render.ss_angle_preview","",icon="RESTRICT_VIEW_OFF")
                            preview.angleN = i
                            reset = box_row.operator("render.ss_angle_reset","",icon="FILE_REFRESH")
                            reset.angleN = i
                            remove = box_row.operator("render.ss_angle_remove","",icon="X")
                            remove.angleN = i
                        
                        box_col = box.column(align=True)
                        split = box_col.split(percentage=0.35,align=True)
                        split.operator('render.ss_set_scaler','Scaler')
                        split.prop(ktScn, 'ssScaler','')
                        split = box_col.split(percentage=0.35,align=True)
                        split.operator('render.ss_set_spinners','Spinners')
                        split.prop(ktScn, 'ssSpinners','')
                        box_row = box.row()
                        box_row.prop(ktScn,"ssRenType", expand=True) #Engine or OpenGL selector
                        box_row = box.row()
                        
                        if ktScn.ssRenType == "Engine":
                            box_row.prop(ktScn,"ssRelative","Relative")
                            box_row.prop(ktScn,"ssGround","Ground")
                        
                        box_col = box.column(align=True)
                        box_row = box_col.row(align=True)
                        if (scn.render.resolution_x / scn.render.resolution_y) == (16/9):
                            icnW = "CHECKBOX_HLT"
                        else:
                            icnW = "CHECKBOX_DEHLT"   
                        if (scn.render.resolution_x / scn.render.resolution_y) == (1):
                            icnS = "CHECKBOX_HLT"
                        else:
                            icnS = "CHECKBOX_DEHLT"      
                        wide = box_row.operator("render.ss_frame_ratio",'Wide',icon=icnW)
                        wide.ratio = 'WIDE'
                        square = box_row.operator("render.ss_frame_ratio",'Square',icon=icnS)
                        square.ratio = 'SQUARE'
                        box_col.prop(ktScn,"ssAnimRange","Range")
                        
                        box_col = box.column(align=True)
                        split = box_col.split(percentage=0.35,align=True)
                        split.operator('render.ss_guess_name', 'Name')
                        split.prop(ktScn,"ssAssetName","")
                        split = box_col.split(percentage=0.35,align=True)
                        split.operator('render.ss_guess_version', 'Version')
                        split.prop(ktScn,"ssAssetVersion",'')
                        box_col.prop(ktScn,"ssDeviation")
                        box_col = box.column(align=False)
                        box_col.scale_y = 2
                        box_col.operator('render.ss_do_render',icon="FILE_TICK")   
                
                #-------------ENGINE TOOLS --------------------
                box = layout.column(align=True).box().column()    
                if kt.ren_type == 'Internal':
                    box_col = box.column(align=True)
                    if engine != 'BLENDER_RENDER':
                        box_col.operator('render.engine_set_bi',icon="SCENE")
                    else:
                        box_col.label(text="BI TOOLS GO HERE")
                elif kt.ren_type == 'Cycles':
                    box_col = box.column(align=True)
                    if engine != 'CYCLES':
                        box_col.operator('render.engine_set_c',icon="SCENE")
                    else:
                        
                        if kt.rvCam == False:
                            cIcon = "CHECKBOX_DEHLT"
                        else:
                            cIcon = "CHECKBOX_HLT"
                        
                        box_col = box.column(align=True) 
                        box_col.label(text="Material Base:")
                        
                        split = box_col.split(percentage=.8,align=True)
                        colL = split.column()
                        colR = split.row()
                        colL.prop(kt, 'matlib_type','')                    
                        colR.prop(kt, 'matlib_color','')                    
                        box_col.operator("matlib.c_create_mat",icon="ZOOMIN")
                        
                        box_col = box.column(align=False)
                        box_col = box.column(align=True)
                        box_col.label(text="Ray Visibility:")
                        box_row = box_col.row(align=True)
                        split = box_col.split(percentage=0.9)     
                        split.prop(kt, 'rvCam',toggle=True)
                        split.operator("object.rv_sel_cam",icon="HAND")
                        split = box_col.split(percentage=0.9)     
                        split.prop(kt, 'rvDif',toggle=True)
                        split.operator("object.rv_sel_dif",icon="HAND")
                        split = box_col.split(percentage=0.9)
                        split.prop(kt, 'rvGlo',toggle=True)
                        split.operator("object.rv_sel_glo",icon="HAND")
                        split = box_col.split(percentage=0.9) 
                        split.prop(kt, 'rvTra',toggle=True)
                        split.operator("object.rv_sel_tra",icon="HAND")
                        split = box_col.split(percentage=0.9) 
                        split.prop(kt, 'rvSha',toggle=True)
                        split.operator("object.rv_sel_sha",icon="HAND")
                        split = box_col.split(percentage=1) 
                        split.operator("object.ren_rv_set",icon="RESTRICT_VIEW_OFF")
                
                

#print (OBJECT_OT_createMatCaps.execute(self.imported))

class KatieToolsProps(bpy.types.PropertyGroup):
    oglNames = [('Blender Default','Blender Default','OpenGL preset'),
                ('Head Light','Head Light','OpenGL preset'),
                ('3 Point','3-Point','OpenGL preset'),
                ('Silhouette','Silhouette','OpenGL preset')]
    
    ogl_preset_enum = bpy.props.EnumProperty(name='OpenGL Presets',default='Head Light',items=oglNames)
    ogl_toggle = bpy.props.BoolProperty(name='OpenGL Add Preset Toggle', default=False, description='Add new OpenGL preset toggle')
    ogl_name = bpy.props.StringProperty(name='New OpenGL Preset Name', default='', description='Custom text for new OpenGL Preset')
    
    fvMESH = bpy.props.BoolProperty(name='Mesh', default=True, description='Show Meshes')
    fvCURVE= bpy.props.BoolProperty(name='Curve', default=True, description='Show Curves')
    fvSURFACE= bpy.props.BoolProperty(name='Surface', default=True, description='Show Surfaces')
    fvMETA= bpy.props.BoolProperty(name='Metaball', default=True, description='Show Metaballs')
    fvFONT = bpy.props.BoolProperty(name='Font', default=True, description='Show Fonts')
    fvARMATURE= bpy.props.BoolProperty(name='Armature', default=True, description='Show Armatures')
    fvLATTICE= bpy.props.BoolProperty(name='Lattice', default=True, description='Show Lattices')
    fvEMPTY= bpy.props.BoolProperty(name='Empty', default=True, description='Show Empties')
    fvCAMERA = bpy.props.BoolProperty(name='Camera', default=True, description='Show Cameras')
    fvLAMP = bpy.props.BoolProperty(name='Lamp', default=True, description='Show Lamps')
    fvSPEAKER = bpy.props.BoolProperty(name='Speaker', default=True, description='Show Speakers')
    
    ob_fvStore = []               

    subD_val = bpy.props.IntProperty(name='Levels', default=2, min=0, max=2, description='Number of vewport subdivision levels for MySubsurf Modifier')
    subD_val_ren = bpy.props.IntProperty(name='Render Levels', default=2, min=1, max=4, description='Number of render subdivision levels for MySubsurf Modifier')
    subD_limit = bpy.props.IntProperty(name='SubD Limit', default=20000, min=1, max=50000, description='Objects with a polycount higher than this value will be ignored when adding MySubsurf')
    
    rename_base = bpy.props.StringProperty(name='rename_base_string', default='**BASE STRING**', description='Custom text for renaming selected objects. Use * and ? characters as wildcards')
    rename_start = bpy.props.IntProperty(name='Start', default=1, description='Number to start counting from')
    rename_pad = bpy.props.IntProperty(name='Padding', default=2, description='Number of Zeros to add before count')
    rename_prefix = bpy.props.StringProperty(name='renamer_prefix_string', default='**PREFIX**', description='Custom text for adding a prefix to selected objects')
    rename_suffix = bpy.props.StringProperty(name='renamer_suffix_string', default='**SUFFIX**', description='Custom text for adding a suffix to selected objects')
    matTypes = [('Color','Color','Material Type'),('MatCap','MatCap','Material Type')]
    mat_type = bpy.props.EnumProperty(name='Type',items=matTypes)
    matNames = [('RED','Red','Material Color'),
                ('ORANGE','Orange','Material Color'),
                ('YELLOW','Yellow','Material Color'),
                ('GREEN','Green','Material Color'),
                ('CYAN','Cyan','Material Color'),
                ('BLUE','Blue','Material Color'),
                ('PURPLE','Purple','Material Color'),
                ('BROWN','Brown','Material Color'),
                ('BLACK','Black','Material Color'),
                ('WHITE','White','Material Color'),
                ('GREY','Grey','Material Color'),
                ('SKIN','Skin','Material Color'),
                ('RANDOM','Random','Material Color')]
    blankEnum = [('','','')]            
    mat_color = bpy.props.EnumProperty(name='Color',default='GREY',items=matNames)
    mat_colors_exist = bpy.props.BoolProperty(name='Colors Exist', default=False, description='Do colors exist?')
    mat_matcap = bpy.props.EnumProperty(name='Matcap',items=blankEnum)
    mat_matcaps_exist = bpy.props.BoolProperty(name='Matcaps Exist', default=False, description='Do matcaps exist?')
    mat_spec = bpy.props.BoolProperty(name='Specular', default=False, description='When checked material will have a specular value')
    
    
    cl_skFix = bpy.props.StringProperty(name='Fix Shape', default='**FIXERS**', description='Paste the name(s) of the SKs you want propogated before separating.  Separate multiple shapes with a comma')
    cl_skTrans = bpy.props.FloatProperty(name='Translation Multiplier', default=1, description="Translation value of separated shapekeys. By default, value is multiplied by objects dimensions.  If checked, value is used as Blender units")
    cl_absTrans = bpy.props.BoolProperty(name='Absolute Translate', default=False, description='Translates separated shapekeys by the value instead of the objects dimension')
    
    cl_clearDataKey= bpy.props.StringProperty(name='Clear Data Key', default='**KEY**', description='Key for destroying unused data blocks')
    
    renTypes = [('Internal','Internal','Render Engine'),('Cycles','Cycles','Render Engine')]
    
    ren_type = bpy.props.EnumProperty(name='Render Engine',items=renTypes)
    rvCam = bpy.props.BoolProperty(name="Camera",description="toggle camera ray visibility",default=True)
    rvDif = bpy.props.BoolProperty(name="Diffuse",description="toggle diffuse ray visibility",default=True)
    rvGlo = bpy.props.BoolProperty(name="Glossy",description="toggle glossy ray visibility",default=True)
    rvTra = bpy.props.BoolProperty(name="Transmission",description="toggle transmission ray visibility",default=True)
    rvSha = bpy.props.BoolProperty(name="Shadows",description="toggle shadow ray visibility",default=True)
    
    matlibTypes = [('Glossy','Glossy','Matlib Foundation Preset'),('Chrome','Chrome','Matlib Foundation Preset')]
    matlib_type = bpy.props.EnumProperty(name='Matlib Type',items=matlibTypes)
    matlib_color = bpy.props.FloatVectorProperty(subtype='COLOR',min=0,max=1,size=4,default=(0.5,0.5,0.5,1))
    
    
    display_relationship = bpy.props.BoolProperty(name="Relationship",description="Reveal relationship tools",default=True)
    display_display = bpy.props.BoolProperty(name="Display",description="Reveal display tools",default=True)
    display_filtVis = bpy.props.BoolProperty(name="Filter Visible",description="Limit Visibility Options",default=True)
    display_mesh = bpy.props.BoolProperty(name="Mesh",description="Reveal Mesh tools",default=True)
    display_sculpt = bpy.props.BoolProperty(name="Sculpt",description="Reveal Sculpt tools",default=True)
    display_naming = bpy.props.BoolProperty(name="Names",description="Reveal naming tools",default=True)
    display_materials = bpy.props.BoolProperty(name="Materials",description="Reveal materials tools",default=True) 
    display_cleanup = bpy.props.BoolProperty(name="Cleanup",description="Reveal cleanup tools",default=True)
    display_render = bpy.props.BoolProperty(name="Render",description="Reveal Render tools",default=True)


class ssCamAnglesPG(bpy.types.PropertyGroup): 
    angleName = bpy.props.StringProperty(name="Angle Name",description="Name of the chosen camera angle",default="Angle.000")
    toggle_still = bpy.props.BoolProperty(name="Still",description="Render still frame based on angle",default=False)
    toggle_turn = bpy.props.BoolProperty(name="Turn",description="Render turntable based on angle",default=False)
    camLoc = bpy.props.StringProperty()
    camRot = bpy.props.StringProperty()
    camFL = bpy.props.IntProperty()
    
class ktSceneProps(bpy.types.PropertyGroup):
    ssRenTypes = [('Engine','Engine','Render snapshot with the render engine'),('OpenGL','OpenGL','Render snapshot with OpenGL shading')]   
    
    ssAnimRange = bpy.props.IntProperty(name='Frame Range', default=100, min=4, description='Frame range for rendering turntables')
    ssAssetName = bpy.props.StringProperty(name='Asset Name', default='myModel', description='Name of the Asset')
    ssAssetVersion = bpy.props.StringProperty(name='Version', default='v01', description='Version of the Asset')
    ssDeviation = bpy.props.IntProperty(name='Deviation', default=1, min=1, description='Deviation of the Snapshot')
    ssScaler = bpy.props.StringProperty(name='Scaler', default='**SCALER**', description='Object used for setting the scale of the snapshot scene')
    ssSpinners = bpy.props.StringProperty(name='Targets', default='**SPINNERS**', description='Objects used for rotational pivots')
    ssRenType = bpy.props.EnumProperty(name='SS Type',items=ssRenTypes)
    ssRelative = bpy.props.BoolProperty(name='Relative Lights', default=True, description="Keep the lights' position relative to camera angle")
    ssGround = bpy.props.BoolProperty(name='Ground Plane', default=True, description="Render ground plane")
        
       
def register():
    bpy.types.Object.unsmoothable = bpy.props.BoolProperty(name='obUnsmoothable', default=False, description='is this object unsmoothable to kt smoothing?')
    bpy.types.Object.ktgroup = bpy.props.BoolProperty(name='ktGroup', default=False, description='is this object a ktGroup?')
    bpy.types.UserPreferences.ogl_presets = {"Blender Default":{"a_use":True, "a_dc":(.8,.8,.8), "a_sc":(.8,.8,.8), "a_dir":(-0.6792,0.2264,0.6981),
                                                           "b_use":True, "b_dc":(.498,.5,.6), "b_sc":(.2,.2,.2), "b_dir":(0.5880,0.4600,0.2480),
                                                           "c_use":True, "c_dc":(.798,.838,1), "c_sc":(.066,0,0), "c_dir":(0.2160,-0.3920,-0.2160)},
                                             "Head Light":{"a_use":True, "a_dc":(.8,.8,.8), "a_sc":(.5,.5,.5), "a_dir":(0.0189,0.0472,0.9987),
                                                           "b_use":False, "b_dc":(0,0,0), "b_sc":(0,0,0), "b_dir":(0,0,0),
                                                           "c_use":False, "c_dc":(0,0,0), "c_sc":(0,0,0), "c_dir":(0,0,0)},
                                             "3 Point":{"a_use":True, "a_dc":(.8,.8,.8), "a_sc":(.5,.5,.5), "a_dir":(0.4340,0.1981,0.8789),
                                                           "b_use":True, "b_dc":(.678,.84,1), "b_sc":(.5,.5,.5), "b_dir":(-0.7673,0.2264,-0.6),
                                                           "c_use":True, "c_dc":(1,.853,.853), "c_sc":(.5,.5,.5), "c_dir":(0.6498,-0.2399,-0.7213)},
                                             "Silhouette":{"a_use":True, "a_dc":(0,0,0), "a_sc":(0,0,0), "a_dir":(0,0,0),
                                                           "b_use":False, "b_dc":(0,0,0), "b_sc":(0,0,0), "b_dir":(0,0,0),
                                                           "c_use":False, "c_dc":(0,0,0), "c_sc":(0,0,0), "c_dir":(0,0,0)}}
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.katietools = bpy.props.PointerProperty(type = KatieToolsProps)
    bpy.types.Scene.ss_camAngles = bpy.props.CollectionProperty(type=ssCamAnglesPG)
    bpy.types.Scene.ss_camAngles_index = bpy.props.IntProperty() #needed for col prop to work (?)
    bpy.types.Scene.kt_scene_props = bpy.props.PointerProperty(type=ktSceneProps)
    
    pass
def unregister():
    try:
        del bpy.types.WindowManager.katietools
    except:
        pass    
    bpy.utils.unregister_module(__name__)
    pass    

if __name__ == "__main__":
    register()
    
#KEY MAP SET    
'''def register():
    bpy.utils.register_module(__name__)
   
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('wm.call_menu', \
                                  'T', 'PRESS', oskey=True)
        kmi.properties.name = 'OBJECT_MT_jonathan_object_tools'
   
def unregister():
    bpy.utils.unregister_module(__name__)
   
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps["3D View"]
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu':
                km.keymap_items.remove(kmi)
                break'''   