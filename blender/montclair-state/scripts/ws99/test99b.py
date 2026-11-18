import bpy, bmesh, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Terrain_LiDAR_DTM_1m','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS81_lot_seam_underlay_asphalt','WS94_lot_slit_filler_asphalt_UNVERIFIED','WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020','WS96_lot_E_edge_gap_filler_asphalt_UNVERIFIED','WS98_lotE_raised_concrete_walk_pad_LiDAR15cm_curb_ortho2020_UNVERIFIED','WS98_lotE_entry_aisle_asphalt_OSMparkingaisle_LiDAR_ortho2020_UNVERIFIED']
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in names if n in s.objects]
sc=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name.startswith(('Cube','Light','Camera')): bpy.data.objects.remove(o)
for o in d.objects: sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
bvh=BVHTree.FromObject(T,dg)  # object space; terrain matrix assumed identity, check
print('T99 mw identity', T.matrix_world==T.matrix_world.Identity(4) if hasattr(T.matrix_world,'Identity') else T.matrix_world)
def above(pt):
    hit=bvh.ray_cast(Vector((pt.x,pt.y,pt.z+50)),Vector((0,0,-1)),200)
    return None if hit[0] is None else pt.z-hit[0].z
W80=bpy.data.objects['WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges']
W75=bpy.data.objects['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges']
W77=bpy.data.objects['WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020']
b75=BVHTree.FromObject(W75,dg); b77=BVHTree.FromObject(W77,dg)
def covered(b,c):
    h=b.ray_cast(Vector((c.x,c.y,c.z+30)),Vector((0,0,-1)),60); return h[0] is not None
rep={}
def cand(o,X=-217.6,Y0=-97.5,Y1=-89.2):
    mw=o.matrix_world; out=[]
    for f in o.data.polygons:
        c=mw@f.center
        if c.x>X and Y0<c.y<Y1 and not covered(b75,c):
            out.append((f.index,round(c.x,2),round(c.y,2),round(above(c) or -99,3)))
    return out
r80=cand(W80); W81=bpy.data.objects['WS81_lot_seam_underlay_asphalt']; r81=cand(W81); W94=bpy.data.objects['WS94_lot_slit_filler_asphalt_UNVERIFIED']; r94=cand(W94); print('T99 WS94',len(r94),r94)
print('T99 WS80 cand',len(r80),r80[:50]); print('T99 WS81 cand',len(r81),[x for x in r81 if x[3]>-0.02][:40])
json.dump({'ws80':r80,'ws81':r81,'ws94':r94},open('/workspace/nj-scenes/montclair-state/scripts/ws99/cand99.json','w'))
# render before/after probes, real-ish look (object colour)
sh=sc.display.shading; sc.render.engine='BLENDER_WORKBENCH'; sh.light='STUDIO'; sh.color_type='OBJECT'; sh.show_cavity=True
C={'Terrain':(0.3,0.5,0.25,1),'WS81':(1,0.1,0.1,1),'WS79_lot':(0.1,0.3,1,1),'WS76':(0.9,0.9,0.2,1),'WS75':(0.6,0.6,0.6,1),'WS80':(1,0.5,0,1),'WS94':(1,0,1,1),'WS77':(0.4,0.25,0.1,1),'WS96':(0,1,1,1),'WS98_lotE_raised':(1,1,1,1),'WS98_lotE_entry':(0.2,0.2,0.2,1)}
for o in d.objects:
    for k,c in C.items():
        if o.name.startswith(k): o.color=c
cd=bpy.data.cameras.new('c'); cam=bpy.data.objects.new('c',cd); sc.collection.objects.link(cam); sc.camera=cam
cam.location=(-210.5,-91.5,129.9); dd=Vector((-218.5,-85,127.0))-cam.location; cam.rotation_euler=dd.to_track_quat('-Z','Y').to_euler(); cd.lens=28
sc.render.resolution_x=1000; sc.render.resolution_y=560
D='/workspace/nj-scenes/montclair-state/scripts/ws99/'
sc.render.filepath=D+'probe_before.png'; bpy.ops.render.render(write_still=True)
cam2=cam.copy(); sc.collection.objects.link(cam2); cam2.location=(-212.5,-99.5,127.6); dd=Vector((-217.5,-92,126.3))-cam2.location; cam2.rotation_euler=dd.to_track_quat('-Z','Y').to_euler()
sc.camera=cam2; sc.render.filepath=D+'probe2_before.png'; bpy.ops.render.render(write_still=True)
# apply deletion of WS80 candidates
kill=[]
for O,R in ((W80,r80),(W81,r81),(W94,r94)):
    bm=bmesh.new(); bm.from_mesh(O.data); bm.faces.ensure_lookup_table()
    k=[bm.faces[i] for i,_,_,_ in R]; kill+=k
    bmesh.ops.delete(bm,geom=k,context='FACES'); bm.to_mesh(O.data); bm.free()
sc.camera=cam; sc.render.filepath=D+'probe_after2.png'; bpy.ops.render.render(write_still=True)
sc.camera=cam2; sc.render.filepath=D+'probe2_after2.png'; bpy.ops.render.render(write_still=True)
print('T99 DONE deleted',len(kill))
