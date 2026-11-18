# ws158b on ws158a: rebuild gym roof/walls from the median-smoothed LiDAR grid; tone gym greys down to the cch_1/cch_3 off-white/grey
import bpy, json, bmesh, resource
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
J=json.load(open(M+'scripts/ws158/gym158.json'))
def rebuild(name,polys):
    o=bpy.data.objects[name]; me=o.data; verts=[];fs=[]
    for pts in polys:
        b=len(verts); verts+=pts; fs.append(list(range(b,b+len(pts))))
    nm=bpy.data.meshes.new(name+'_b'); nm.from_pydata(verts,[],fs)
    for m in me.materials: nm.materials.append(m)
    bm=bmesh.new(); bm.from_mesh(nm); bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(nm); bm.free()
    o.data=nm; bpy.data.meshes.remove(me); print('FIX158B',name,len(nm.polygons))
rebuild('WS158_Panzer_gym_roof_LiDAR2023_massing_UNVERIFIED',[[tuple(v) for v in f] for f in J['faces']])
rebuild('WS158_Panzer_gym_walls_OSM_LiDAR_massing_UNVERIFIED',[[(x0,y0,117.0),(x1,y1,117.0),(x1,y1,z1),(x0,y0,z0)] for x0,y0,z0,x1,y1,z1 in J['walls']])
def tone(n,rgb):
    b=bpy.data.materials[n].node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*rgb,1)
tone('WS158_gym_wall_lightgrey_UNVERIFIED',(0.50,0.50,0.48)); tone('WS158_gym_roof_grey_metal_UNVERIFIED',(0.30,0.31,0.31))
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws158b.blend',copy=True)
print('SAVED_WS158B RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
