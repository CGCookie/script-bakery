import bpy
import os
import random
import math

#-------------------------------------------------------
#-------------- RENDER ---------------------------------
#-------------------------------------------------------

#SNAPSHOT

class OBJECT_OT_ssAddCamera(bpy.types.Operator):
    bl_idname = "render.ss_add_camera"
    bl_label = "Add Camera Object"
    
    def execute(self, context):
        bpy.ops.object.camera_add()
        #maybe change clipping end to 10000 upon creation              
        return {'FINISHED'} 

class OBJECT_OT_ssAngleAdd(bpy.types.Operator):
    bl_idname = "render.ss_angle_add"
    bl_label = "Add Camera Angle"
    bl_description = "Add a new angle preset based on the scene camera's current position"
    
    def execute(self, context):
        scn = bpy.context.scene
        
        if scn.camera == None:
            self.report({'INFO'}, 'No camera in the scene')
        else:
            angle = scn.ss_camAngles.add()
            angNo = len(scn.ss_camAngles)
            angle.name = "ssAng.%.3d" % angNo
            angle.angleName = "Angle.%.3d" % angNo
            angle.camLoc = str(list(scn.camera.location))
            angle.camRot = str(list(scn.camera.rotation_euler))
            angle.camFL = scn.camera.data.lens
                       
        return {'FINISHED'}
    
class OBJECT_OT_ssAngleReset(bpy.types.Operator):
    bl_idname = "render.ss_angle_reset"
    bl_label = "Angle Reset"
    bl_description = "Reset camera angle based on scene camera's current position"
    
    angleN = bpy.props.IntProperty()
    
    def execute(self, context):
        scn = bpy.context.scene
        
        scn.ss_camAngles[self.angleN].camLoc = str(list(scn.camera.location))
        scn.ss_camAngles[self.angleN].camRot = str(list(scn.camera.rotation_euler))
        scn.ss_camAngles[self.angleN].camFL = scn.camera.data.lens
                       
        return {'FINISHED'}    
    
class OBJECT_OT_ssAngleRemove(bpy.types.Operator):
    bl_idname = "render.ss_angle_remove"
    bl_label = "Remove Camera Angle"
    
    angleN = bpy.props.IntProperty()
    
    def execute(self, context):
        scn = bpy.context.scene
        angRemove = scn.ss_camAngles.remove(self.angleN)
        
        #print (angleN)
                       
        return {'FINISHED'}    


class OBJECT_OT_ssAnglePreview(bpy.types.Operator):
    bl_idname = "render.ss_angle_preview"
    bl_label = "Preview Camera Angle"
    
    angleN = bpy.props.IntProperty()
    
    def execute(self, context):
        scn = bpy.context.scene
        
        scn.camera.location = eval(scn.ss_camAngles[self.angleN].camLoc)
        scn.camera.rotation_euler = eval(scn.ss_camAngles[self.angleN].camRot)
        scn.camera.data.lens = scn.ss_camAngles[self.angleN].camFL
        
        view = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                view = area.spaces.active.region_3d.view_perspective
                
        if view != 'CAMERA':        
            bpy.ops.view3d.viewnumpad(type='CAMERA')
                       
        return {'FINISHED'}
    
class OBJECT_OT_ssSetScaler(bpy.types.Operator):
    bl_idname = "render.ss_set_scaler"
    bl_label = "Set SS Scaler"
    
    def execute(self, context):
        scn = bpy.context.scene
        ktScn = scn.kt_scene_props

        focusOb = None      
        if len(bpy.context.selected_objects) != 1:
            self.report({'INFO'}, 'Only one object can be the focus object')
        else:    
            for ob in scn.objects:
                if ob.select == True:
                    focusOb = ob
                    
            ktScn.ssScaler = str(focusOb.name)
                       
        return {'FINISHED'}    
    
    
class OBJECT_OT_ssSetSpinners(bpy.types.Operator):
    bl_idname = "render.ss_set_spinners"
    bl_label = "Set SS Spinners"
    
    def execute(self, context):
        scn = bpy.context.scene
        ktScn = scn.kt_scene_props

        spinnerNames = []       
        
        for ob in scn.objects:
            if ob.select == True:
                spinnerNames.append(ob.name)
                
        ktScn.ssSpinners = str(spinnerNames)
                       
        return {'FINISHED'}
    

class OBJECT_OT_guessAssetName(bpy.types.Operator):
    bl_idname = "render.ss_guess_name"
    bl_label = "Guess Asset Name"
    bl_description = "Guess the desired asset's name based on file name"
    
    def execute(self, context):
        scn = bpy.context.scene
        ktScn = scn.kt_scene_props
        
        path = bpy.data.filepath
        fileName = os.path.basename(path)
        name = fileName.split('.')[0]
        
        if "_" in name:
            asset = name.split('_')[0]
        else:
            asset = "assetName"    
        
        ktScn.ssAssetName = asset
                       
        return {'FINISHED'}
    
class OBJECT_OT_guessAssetVersion(bpy.types.Operator):
    bl_idname = "render.ss_guess_version"
    bl_label = "Guess Asset Version"
    bl_description = "Guess the desired asset's version based on file name"
    
    def execute(self, context):
        scn = bpy.context.scene
        ktScn = scn.kt_scene_props
        
        path = bpy.data.filepath
        fileName = os.path.basename(path)
        name = fileName.split('.')[0]
        
        if "_" in name:
            version = name.split('_')[1]
        else:
            version = "v01"    
        
        ktScn.ssAssetVersion = version
                       
        return {'FINISHED'}
    

class OBJECT_OT_ssFrameRatio(bpy.types.Operator):
    bl_idname = "render.ss_frame_ratio"
    bl_label = "Set Render Frame Ratio"
    
    ratio = bpy.props.StringProperty()
    
    def execute(self, context):
        scn = bpy.context.scene
        ktScn = scn.kt_scene_props
        
        if self.ratio == 'WIDE':
            scn.render.resolution_x = 1920
            scn.render.resolution_y = 1080
            
        if self.ratio == 'SQUARE':
            scn.render.resolution_x = 1080
            scn.render.resolution_y = 1080
                       
        return {'FINISHED'}   

def getBoundBoxDimensions(focusOb):
    scn = bpy.context.scene
    selOb = []
    tempNameB = 'kysk'
    bbName = 'ss_boundBox'
    #determine whether the focus object has children or not   
    for ob in scn.objects:
            ob.select = False
    
    '''if len(focusOb.children) == 0:
        dim = max(focusOb.dimensions)
    else:'''
        
    focusOb.select = True
    scn.objects.active = focusOb
    bpy.ops.object.select_grouped(extend=True,type="CHILDREN_RECURSIVE")
    
    for ob in bpy.context.selected_objects:
        selOb.append(ob)

    if selOb == []:
        print ("NO FOCUS OBJECT DESIGNATED")
    else:    
        ###### START BOUND BOX GENERATION
        #duplicate selected objects and convert to mesh to avoid modifier trouble
        scn.objects.active = selOb[0] #make sure a member of selOb is the active object before this starts
        bpy.ops.object.duplicate(linked=False)
        dupSel = bpy.context.selected_objects #define dupSel list
        bpy.ops.object.convert(target='MESH', keep_original=False)
    
        for ob in dupSel: #single out objects WITHOUT dimensions
            if ob.type == 'MESH' or ob.type=='CURVE' or ob.type=='SURFACE' or ob.type=='META' or ob.type=='FONT':
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')   
                
                cubeA = bpy.ops.mesh.primitive_cube_add()
                actOb = scn.objects.active #redefine active object variable
                actOb.name = tempNameB + ob.name
                actOb.dimensions = ob.dimensions
                actOb.location = ob.location
                
            elif ob.ktgroup == True:
                continue   
                
            else:
                cubeA = bpy.ops.mesh.primitive_cube_add()
                actOb = scn.objects.active #redefine active object variable
                actOb.name = tempNameB + ob.name
                actOb.scale = ob.scale
                actOb.location = ob.location
                
        for ob in scn.objects:
            if tempNameB in ob.name:
                ob.select = True
            else:
                ob.select = False
        if len(bpy.context.selected_objects) > 1:        
            bpy.ops.object.join() #combine duplicates into a temp object
            
        scn.objects.active.name = bbName    
        
        # SINGLE OUT AND REMOVE FIRST SET OF CUBES -----------------
        for ob in scn.objects:
            if ob in dupSel or tempNameB in ob.name:
                ob.select = True
            else:
                ob.select = False
                
        bpy.ops.object.delete() #delete first set of cubes
        
        # ------------------------------------------------------------
        bb = scn.objects[bbName]
        dim = max(bb.dimensions)
        wmtx =  bb.matrix_world
        worldVerts = [(wmtx * vertex.co) for vertex in bb.data.vertices]
        vertsZ = []
        for v in worldVerts:
            vertsZ.append(v[2])
            
        minZ = min(vertsZ)
            
        scn.objects.active = bb
        scn.objects.active.select = True    
        bpy.ops.object.delete()
            
    return dim, minZ


def spinnerSetup(spinnerNames):
    scn = bpy.context.scene
    spinnerOb = []
    
    for ob in scn.objects:
        if ob.name in spinnerNames:
            spinnerOb.append(ob)
        if ob.name == "ss_spinner.001":
            ob.select = True
            scn.objects.active = ob
        else:
            ob.select = False #at this point only the original spinner ctrl is selected and active
                 
    for ob in spinnerOb:
        bpy.ops.object.duplicate(linked=False)
        actOb = scn.objects.active
        actOb.name = "ss_spinner_" + ob.name
        actOb.location = ob.location
        
        ob.select = True
        actOb.select = True
        
        bpy.ops.object.parent_set(type='OBJECT',keep_transform=True)
        
        ob.select = False    

    
class OBJECT_OT_ssAngleDoRender(bpy.types.Operator):
    bl_idname = "render.ss_do_render"
    bl_label = "Render Snapshot"
    bl_description = "Render enabled Snapshot camera angles"
           
    def append(self):
        blend = 'ss_scene_A.blend'
        path = bpy.utils.script_paths('addons/katietools/snapshot')
        pathStr = ''.join(path) #convert list object to string
        filepath = str(pathStr + '/' + blend)
        
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.scenes = ["kt_ssSetup"]              
    
    def execute(self, context):
        scn = bpy.context.scene
        kt = bpy.context.window_manager.katietools
        ktScn = scn.kt_scene_props
        
        #-------SPINNER STRING CHECK-------------------------------------------
        if "[" not in ktScn.ssSpinners:
            self.report({'INFO'}, 'Spinners must be a list of objects')
        else:
            spinnerNames = eval(ktScn.ssSpinners)
            
            #make sure all spinner objects are visible lest parenting will fail
            for ob in scn.objects:
                if ob.name in spinnerNames:
                    ob.hide = False
            
            #-------SCALER CHECK-------------------------------------------
            if ktScn.ssScaler not in scn.objects:
                self.report({'INFO'}, 'Scaler is not an object')
            else:  
                spinTest = True
                for s in spinnerNames:
                    if s not in scn.objects:
                        spinTest = False
                
                #-------SPINNER OB CHECK-------------------------------------------        
                if spinTest == False:
                    self.report({'INFO'}, 'One or more spinners are not objects')           
                else:#all spinner objects exist in the scene, therefore continue
                    
                    #-------OUTPUT FORMAT CHECK-------------------------------------------
                    if scn.render.image_settings.file_format != 'JPEG' and scn.render.image_settings.file_format != 'PNG':
                        self.report({'INFO'}, 'Please use JPEG or PNG image format for render output')
                    else:    
                        print ('file format is good to go')
                        #-------FRAME RATIO CHECK-------------------------------------------    
                        scnRatio = scn.render.resolution_x / scn.render.resolution_y
                        if (scnRatio == (16/9)) or (scnRatio == (1)):
                            scalerOb = scn.objects[ktScn.ssScaler]
                            selObToLink = []
                            origScnName = scn.name
                            origScn = bpy.data.scenes[origScnName]
                            scnSS = 'kt_ssSetup'
                            
                            ssDim = getBoundBoxDimensions(scalerOb)
                            #self.report({'INFO'}, str(ssDim))
                            
                            self.append() #APPEND THE SNAPSHOT SCENE ------------------------------------
                            
                            bpy.ops.object.select_all(action='DESELECT')
                                    
                            for s in spinnerNames:
                                scn.objects[s].select = True
                                scn.objects.active = scn.objects[s]
                                bpy.ops.object.select_grouped(extend=True,type="CHILDREN_RECURSIVE")
                            
                            bpy.ops.object.make_links_scene(scene=scnSS)#link selection to ss scene
                            
                            bpy.context.screen.scene = bpy.data.scenes[scnSS] #change 'active' scene to Snapshot Scene
                            
                            scn = bpy.context.scene # REDEFINE 'SCN'
                            ground = scn.objects["ss_groundPlane"]
                            
                            origCamAngles = origScn.ss_camAngles
                            
                            for i, cam in enumerate(origScn.ss_camAngles): #recreate camera angles from original scene
                                angle = scn.ss_camAngles.add()
                                angNo = len(scn.ss_camAngles)
                                angle.name = origCamAngles[i].name
                                angle.angleName = origCamAngles[i].angleName
                                angle.camLoc = origCamAngles[i].camLoc
                                angle.camRot = origCamAngles[i].camRot
                                angle.camFL = origCamAngles[i].camFL 
                              
                            for ob in scn.objects:
                                if 'ss_scaler' in ob.name: #get scaler object from appended scene
                                    scalerOb = ob
                                if 'ss_cam' in ob.name: #get ss camera
                                    ssCam = ob
                                    
                            multV = ssDim[0]/scalerOb.dimensions[0]
                            
                            #------------------COPY A BUNCH OF SETTINGS TO SNAPSHOT SCENE--------------------
                            scalerOb.dimensions = scalerOb.dimensions * multV #match scale
                            scalerOb.location[2] = ssDim[1] #move scaler to the bottom of focus object
                            ssCam.data.clip_start = ssCam.data.clip_start * multV
                            ssCam.data.clip_end = ssCam.data.clip_end * multV
                            ground.scale = ground.scale * multV
                            ground.location[2] = ssDim[1]
                            scn.render.resolution_x = origScn.render.resolution_x
                            scn.render.resolution_y = origScn.render.resolution_y
                            scn.render.resolution_percentage = origScn.render.resolution_percentage
                            scn.frame_current = origScn.frame_current
                            origFF = origScn.render.image_settings.file_format
                            origCM = origScn.render.image_settings.color_mode
                            origQ = origScn.render.image_settings.quality
                            scn.frame_start = 1
                            scn.frame_end = origScn.kt_scene_props.ssAnimRange
                            scn.kt_scene_props.ssRelative = origScn.kt_scene_props.ssRelative
                            
                            if kt.ren_type == "Internal":
                                if scn.render.engine != "BLENDER_RENDER":
                                    scn.render.engine = "BLENDER_RENDER"
                                for ob in scn.objects:
                                    if 'ss_c_' in ob.name:
                                        ob.hide_render = True
                                    if 'ss_bi_' in ob.name:
                                        ob.hide_render = False    
                            elif kt.ren_type == "Cycles":
                                if scn.render.engine != "CYCLES":
                                    scn.render.engine = "CYCLES"
                                for ob in scn.objects:
                                    if 'ss_bi_' in ob.name:
                                        ob.hide_render = True
                                    if 'ss_c_' in ob.name:
                                        ob.hide_render = False
                                        
                            if scnRatio == (1):
                                for ob in scn.objects:
                                    if 'ss_text' in ob.name:
                                        ob.select = True
                                    else:
                                        ob.select = False
                                txtGrpScale = round(scn.objects["ss_text_GRP"].scale[0], 2)
                                zTrans = (-6.55 * txtGrpScale)                  
                                bpy.ops.transform.translate(value=(0,0,zTrans)) #position text overlay objects for square ratio 
                            
                            spinnerSetup(spinnerNames)
                            
                            origFR = origScn.kt_scene_props.ssAnimRange      
                            for ob in scn.objects:
                                if 'ss_spinner' in ob.name:
                                    for f in ob.animation_data.action.fcurves:
                                        for k in f.keyframe_points:
                                            if k.co[0] == 101:
                                                k.co[0] = (origFR + 1)
                                               
                            if ktScn.ssRelative == False:
                                scalerOb.constraints['ss_con_trackTo'].mute = True
                            else:
                                scalerOb.constraints['ss_con_trackTo'].mute = False
                                
                            if ktScn.ssRenType == "Engine" and ktScn.ssGround == True:
                                ground.hide_render = False
                            else:
                                ground.hide_render = True          
                                
                            renders = []
                            
                            #--------------------LOOP THOUGH AND RENDER EACH CAM ANGLE-----------------------------
                            for i, cam in enumerate(scn.ss_camAngles):  #loop through current scene's camAngles
                                cam.toggle_still = origScn.ss_camAngles[i-1].toggle_still
                                cam.toggle_turn = origScn.ss_camAngles[i-1].toggle_turn
                                scn.objects['ss_text_A'].data.body = ktScn.ssAssetName + "_" + ktScn.ssAssetVersion + "_" + "%03d"%ktScn.ssDeviation
                                scn.objects['ss_text_B'].data.body = scn.ss_camAngles[i-1].angleName
                                scn.objects['ss_text_C'].data.body = 'Kent Trammell'
                                bpy.ops.render.ss_angle_preview(angleN=i-1)
                                
                                if cam.toggle_still == True:
                                    scn.frame_current = 1        
                                    scn.render.image_settings.file_format = origFF  
                                    scn.render.image_settings.color_mode = origCM
                                    scn.render.image_settings.quality = origQ
                                    fileName = ktScn.ssAssetName + "_" + ktScn.ssAssetVersion + "_" + "%03d"%ktScn.ssDeviation + "_" + scn.ss_camAngles[i-1].angleName + scn.render.file_extension
                                    filePath = origScn.render.filepath + fileName
                                    scn.render.filepath = filePath
                                    
                                    if ktScn.ssRenType == "OpenGL":
                                        bpy.ops.render.opengl(animation=False, write_still=True)
                                    else:    
                                        bpy.ops.render.render(animation=False, write_still=True)
                                    renders.append(filePath)
                                                                    
                                if cam.toggle_turn == True:
                                    scn.render.image_settings.file_format = "FFMPEG"
                                    scn.render.ffmpeg.format = 'QUICKTIME'
                                    scn.render.ffmpeg.codec = 'H264'
                                    scn.render.ffmpeg.video_bitrate = 9000
                                    scn.render.ffmpeg.minrate = 9000
                                    scn.render.ffmpeg.maxrate = 12000
                                    scn.render.ffmpeg.buffersize = 2500
                                    scn.render.ffmpeg.use_lossless_output = True
                                    fileName = ktScn.ssAssetName + "_" + ktScn.ssAssetVersion + "_" + "%03d"%ktScn.ssDeviation + "_" + scn.ss_camAngles[i-1].angleName + ".mov"
                                    filePath = origScn.render.filepath + fileName
                                    scn.render.filepath = filePath
                                    
                                    if ktScn.ssRenType == "OpenGL":
                                        bpy.ops.render.opengl(animation=True)
                                    else:    
                                        bpy.ops.render.render(animation=True)
                                    renders.append(filePath)                   
                                       
                            bpy.ops.scene.delete()    
                            bpy.context.screen.scene = origScn #change 'active' scene to original
                            bpy.ops.data.clean_data(key='ss_') #clean remaining data from snapshot scene
                            
                            if len(renders) > 0:
                                origScn.kt_scene_props.ssDeviation = origScn.kt_scene_props.ssDeviation + 1    
                                self.report({'INFO'}, str(len(renders)) + ' Snapshot angles finished:  ' + renders[0])
                            else:
                                self.report({'INFO'}, 'No Snapshots angles enabled for rendering')    
                        
                        else:
                            self.report({'INFO'}, 'Please use a wide or square frame radio')  
                            
        return {'FINISHED'}    
    

#INTERNAL TOOLS

class OBJECT_OT_engineSetBI(bpy.types.Operator):
    bl_idname = "render.engine_set_bi"
    bl_label = "Activate Internal"
    bl_description = "Activates BLENDER RENDER renderengine"
    
    def execute(self, context):
        bpy.context.scene.render.engine = "BLENDER_RENDER"
                       
        return {'FINISHED'}


#CYCLES TOOLS
    
class OBJECT_OT_engineSetC(bpy.types.Operator):
    bl_idname = "render.engine_set_c"
    bl_label = "Activate Cycles"
    bl_description = "Activates CYCLES render engine"
    
    def execute(self, context):
        bpy.context.scene.render.engine = "CYCLES"
                       
        return {'FINISHED'}   

    
class OBJECT_OT_cyclesMaterialFoundation(bpy.types.Operator):
    bl_idname = "matlib.c_create_mat"
    bl_label = "Create Material"
    bl_description = "Add material foundation to selected objects"
    
    def execute(self, context):
        selOb = bpy.context.selected_objects
        kt = bpy.context.window_manager.katietools

        matName = "kt" + str(kt.matlib_type)
        
        if kt.matlib_type == "Glossy":
            diffColor = kt.matlib_color
            glossColor = (1,1,1,1)
            mixA_col1 = (0.03,0.03,0.03,1)
            mixA_col2 = (0.7,0.7,0.7,1)
            mixB_col1 = (0.2,0.2,0.2,1)
            mixB_col2 = (0.1,0.1,0.1,1)
            rampPos1 = 0.67
        elif kt.matlib_type == "Chrome":
            diffColor = (0,0,0,1)
            glossColor = kt.matlib_color
            mixA_col1 = (0.5,0.5,0.5,1)
            mixA_col2 = (1,1,1,1)
            mixB_col1 = (.05,.05,.05,1)
            mixB_col2 = (.001,.001,.001,1)
            rampPos1 = 0   
        
        if matName in bpy.data.materials:
            dupMat = bpy.data.materials[matName]
            dupMat.name = matName + ".000"
                
        mat = bpy.data.materials.new(matName)
        mat.use_nodes = True
        
        tree = bpy.data.materials[matName].node_tree
        links = tree.links
        
        output = tree.nodes['Material Output']
        
        diffuse = tree.nodes['Diffuse BSDF']
        diffuse.inputs[0].default_value = diffColor
        diffuse.location = -235,300
        
        glossy = tree.nodes.new('ShaderNodeBsdfGlossy')
        glossy.inputs[0].default_value = glossColor
        glossy.location = -235,150
        
        mixShader = tree.nodes.new('ShaderNodeMixShader')
        mixShader.location = 40,340
        
        layWeight = tree.nodes.new('ShaderNodeLayerWeight')
        layWeight.location = -1080,300
        
        ramp = tree.nodes.new('ShaderNodeValToRGB')
        ramp.location = -800,300
        ramp.color_ramp.interpolation = 'B_SPLINE'
        elements = ramp.color_ramp.elements
        elements[0].position = rampPos1
        
        mixA = tree.nodes.new('ShaderNodeMixRGB')
        mixA.location = -435,475
        mixA.inputs[1].default_value = mixA_col1
        mixA.inputs[2].default_value = mixA_col2
        
        mixB = tree.nodes.new('ShaderNodeMixRGB')
        mixB.location = -435,150
        mixB.inputs[1].default_value = mixB_col1
        mixB.inputs[2].default_value = mixB_col2
        
        links.new(layWeight.outputs[1],ramp.inputs[0])
        links.new(ramp.outputs[0],mixA.inputs[0])
        links.new(ramp.outputs[0],mixB.inputs[0])
        links.new(mixA.outputs[0],mixShader.inputs[0])
        links.new(mixB.outputs[0],glossy.inputs[1])
        links.new(diffuse.outputs[0],mixShader.inputs[1])
        links.new(glossy.outputs[0],mixShader.inputs[2])
        links.new(mixShader.outputs[0],output.inputs[0])
        
        for ob in selOb:
            ob.active_material = bpy.data.materials[matName]
            
                       
        return {'FINISHED'}     

class OBJECT_OT_renRvSet(bpy.types.Operator):
    bl_idname = "object.ren_rv_set"
    bl_label = "Set RV"
    bl_description = "Sets ray visibility for selected objects"
    
    def execute(self, context):
        kt = bpy.context.window_manager.katietools
        selOb = bpy.context.selected_objects
        engine = bpy.context.scene.render.engine
        
        if selOb:
            for ob in selOb:
                if kt.rvCam == True:
                    ob.cycles_visibility.camera = True
                else:
                    ob.cycles_visibility.camera = False
                if kt.rvDif == True:
                    ob.cycles_visibility.diffuse = True
                else:
                    ob.cycles_visibility.diffuse = False
                if kt.rvGlo == True:
                    ob.cycles_visibility.glossy = True
                else:
                    ob.cycles_visibility.glossy = False
                if kt.rvTra == True:
                    ob.cycles_visibility.transmission = True
                else:
                    ob.cycles_visibility.transmission = False
                if kt.rvSha == True:
                    ob.cycles_visibility.shadow = True
                else:
                    ob.cycles_visibility.shadow = False
        else:
            self.report({'INFO'}, "Nothing selected")                          
                    
        # Silly way to force all windows to refresh
        bpy.context.scene.frame_current = bpy.context.scene.frame_current             
        
        return {'FINISHED'}
    
class OBJECT_OT_rvSelCam(bpy.types.Operator):
    bl_idname = "object.rv_sel_cam"
    bl_label = "RV Select Camera"
    bl_description = "Select objects with CAMERA ray visibility disabled"
    
    def execute(self, context):
        scnOb = bpy.context.scene.objects
        for ob in scnOb:
            ob.select = False
            if ob.cycles_visibility.camera == False:
                ob.select = True
        if bpy.context.selected_objects:                
            scnOb.active = bpy.context.selected_objects[0]
        self.report({'INFO'}, str(len(bpy.context.selected_objects)) + " objects selected")
        return {'FINISHED'}
    
class OBJECT_OT_rvSelDif(bpy.types.Operator):
    bl_idname = "object.rv_sel_dif"
    bl_label = "RV Select Diffuse"
    bl_description = "Select objects with DIFFUSE ray visibility disabled"
    
    def execute(self, context):
        scnOb = bpy.context.scene.objects
        for ob in scnOb:
            ob.select = False
            if ob.cycles_visibility.diffuse == False:
                ob.select = True
        if bpy.context.selected_objects:              
            scnOb.active = bpy.context.selected_objects[0]
        self.report({'INFO'}, str(len(bpy.context.selected_objects)) + " objects selected")
        return {'FINISHED'}
    
class OBJECT_OT_rvSelGlo(bpy.types.Operator):
    bl_idname = "object.rv_sel_glo"
    bl_label = "RV Select Glossy"
    bl_description = "Select objects with GLOSSY ray visibility disabled"
    
    def execute(self, context):
        scnOb = bpy.context.scene.objects
        for ob in scnOb:
            ob.select = False
            if ob.cycles_visibility.glossy == False:
                ob.select = True
        if bpy.context.selected_objects:              
            scnOb.active = bpy.context.selected_objects[0]
        self.report({'INFO'}, str(len(bpy.context.selected_objects)) + " objects selected")
        return {'FINISHED'}
    
class OBJECT_OT_rvSelTra(bpy.types.Operator):
    bl_idname = "object.rv_sel_tra"
    bl_label = "RV Select Transmission"
    bl_description = "Select objects with TRANSMISSION ray visibility disabled"
    
    def execute(self, context):
        scnOb = bpy.context.scene.objects
        for ob in scnOb:
            ob.select = False
            if ob.cycles_visibility.transmission == False:
                ob.select = True
        if bpy.context.selected_objects:              
            scnOb.active = bpy.context.selected_objects[0]
        self.report({'INFO'}, str(len(bpy.context.selected_objects)) + " objects selected")
        return {'FINISHED'}

class OBJECT_OT_rvSelSha(bpy.types.Operator):
    bl_idname = "object.rv_sel_sha"
    bl_label = "RV Select Shadow"
    bl_description = "Select objects with SHADOW ray visibility disabled"
    
    def execute(self, context):
        scnOb = bpy.context.scene.objects
        for ob in scnOb:
            ob.select = False
            if ob.cycles_visibility.shadow == False:
                ob.select = True
        if bpy.context.selected_objects:              
            scnOb.active = bpy.context.selected_objects[0]
        self.report({'INFO'}, str(len(bpy.context.selected_objects)) + " objects selected")
        return {'FINISHED'}     