# ws235 ONE-SCENE M3b (west rail corridor, y -116..515): the Montclair Line between the Montclair Heights station and the
# M3a extension sat on the coarse 3DEP context skirt (probe234e: Ballast 1 median -3.1 m buried at y 450). Append the north
# file's 1 m LiDAR DTM again as ONE object and keep a face only if (a) it is NOT an M3a face (complement of M3a's rule, so the
# two share the y 515 vertex row exactly), (b) every vertex has x <= -200 (the rail in y<515 is at x -466..-215; a straight
# cut 13+ m east of it, crossing open ground, not along the rail - ws234d lesson), and (c) no vertex lies over main-native
# ground (Terrain_LiDAR_DTM_1m, WS60 apron, WS68 RHD ground, PK Feliciano fill, QG strip, WF patch) so the patch stops short
# of main's fine-tuned ground and never stacks on it. The skirt gets a second end-of-stack GN (copy of ws234h's feathered
# skirt-under group pointed at this object).
import bpy, bmesh, mathutils
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
NAME='M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam'
XMAX=-200.0
if NAME in bpy.data.objects: raise SystemExit('F235 already there')
MAING=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','PK_Feliciano_west_DTM_fill_UNVERIFIED','QG_north_strip_LiDAR_terrain_patch','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam']
MAING+=[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')]
B=[]
for n in MAING:
    o=bpy.data.objects.get(n)
    if not o: print('F235 missing ground',n,flush=True); continue
    m=o.data; mw=o.matrix_world
    B.append((n,BVHTree.FromPolygons([(mw@v.co)[:] for v in m.vertices],[p.vertices[:] for p in m.polygons])))
D=mathutils.Vector((0,0,-1))
def covered(w):
    for n,t in B:
        if n.startswith('M3a'): continue
        if t.ray_cast(mathutils.Vector((w.x,w.y,600)),D)[0]: return True
    return False
with bpy.data.libraries.load(MS+'north/montclair_north.blend',link=False) as (s,d): d.objects=['North_terrain_LiDAR_1m']
o=d.objects[0]; o.name=NAME
for m in list(o.modifiers): o.modifiers.remove(m)
me=o.data; me.name=NAME+'_mesh'
bm=bmesh.new(); bm.from_mesh(me); mw=o.matrix_world.copy()
cov={}
def vc(v):
    k=v.index
    if k not in cov:
        w=mw@v.co; cov[k]=(w.x>XMAX) or covered(w)
    return cov[k]
dl=[]
for f in bm.faces:
    ws=[mw@v.co for v in f.verts]
    if all(w.y>=515.0 for w in ws) or any(w.x>XMAX for w in ws) or any(vc(v) for v in f.verts): dl.append(f)
bmesh.ops.delete(bm,geom=dl,context='FACES')
lone=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lone,context='VERTS')
bm.to_mesh(me); bm.free()
bpy.data.collections['N_terrain'].objects.link(o)
ws=[mw@v.co for v in me.vertices]
print('F235 M3b verts',len(me.vertices),'faces',len(me.polygons),'x',round(min(v.x for v in ws),1),round(max(v.x for v in ws),1),'y',round(min(v.y for v in ws),1),round(max(v.y for v in ws),1),'z',round(min(v.z for v in ws),1),round(max(v.z for v in ws),1),'mats',[m.name if m else None for m in me.materials],flush=True)
# seam check vs M3a: shared verts on the y 515 row
m3a=bpy.data.objects['M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam']
ka={(round(v.co.x,2),round(v.co.y,2)):v.co.z for v in m3a.data.vertices if abs(v.co.y-515)<1.01}
kb=[(round(w.x,2),round(w.y,2),w.z) for w in ws if abs(w.y-515)<1.01]
sh=[abs(ka[(x,y)]-z) for x,y,z in kb if (x,y) in ka]
print('F235 seam y515 shared verts',len(sh),'max dz',round(max(sh),3) if sh else None,flush=True)
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
ng=bpy.data.node_groups['WS234_skirt_under_M3a_ext_feather'].copy(); ng.name='WS235_skirt_under_M3b_corridor_feather'
oi=[n for n in ng.nodes if n.bl_idname=='GeometryNodeObjectInfo'][0]; oi.inputs['Object'].default_value=o
mm=sk.modifiers.new('WS235_skirt_under_M3b_corridor','NODES'); mm.node_group=ng
print('F235 skirt stack tail',[x.name for x in sk.modifiers][-3:],flush=True)
