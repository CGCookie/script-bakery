import bpy
import bmesh

bm = bmesh.new()

me = bpy.data.meshes.new("myMesh")

bmesh.ops.create_grid(
        bm,
        x_segments = 4,
        y_segments = 4,
        size = 2,)
        
geo_edges = bm.edges[:]
geo_verts = bm.verts[:]
geo_faces = bm.faces[:]

bmesh.ops.extrude_face_region(
        bm,
        geom = geo_faces,
        )
bmesh.ops.translate(
        bm,
        verts = geo_verts,
        vec = (0.0, 0.0, 1.0))
        
bmesh.ops.inset(
        bm,
        faces = geo_faces,
        use_boundary = True,
        use_even_offset = True,
        use_relative_offset = True,
        thickness = 0.5,
        )

bm.to_mesh(me)  
bm.free()

scene = bpy.context.scene
obj = bpy.data.objects.new("Grid", me)
scene.objects.link(obj)

scene.objects.active = obj
obj.select = True


