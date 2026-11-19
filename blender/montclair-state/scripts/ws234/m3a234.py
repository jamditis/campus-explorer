# ws234 ONE-SCENE M3a (north terrain extension, first slice): main's ground north of y≈515 was only the 4 km 3DEP context skirt
# (coarse; probe234b: Montclair Line ballast median -1.2 m / up to -5.4 m buried, station platform -0.3..-3.4 m buried,
# canopy columns 0.7-2.3 m over it). The north file's North_terrain_LiDAR_1m (1 m LiDAR DTM, x -447..141, y -116..1238) is the
# ground the station/rail kit and the Children's Center were built on. Append it as ONE main object, keep only faces whose
# vertices are all at y >= 515 (main-native content - WF patch, Blanton - ends at y 509; nothing of main's is touched), and
# lower the skirt wherever it would poke above the extension (raise-only for paving elsewhere is unaffected: the skirt is ground).
import bpy, bmesh, mathutils
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
Y0=515.0
import os
V2=os.environ.get('M3A_RULE')=='v2'
# MAIN (ws234b/c/e) = rule v1: keep a face only if every vertex has y >= 515.
# REJECTED ws234d = rule v2 (M3A_RULE=v2): also y>=280 & x<=-282 or y>=40 & x<=-325 (west rail corridor; its edge ran along the rail).
NAME='M3a_north_LiDAR_DTM_1m_ext_UNVERIFIED_seam' if V2 else 'M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam'
def outside(w): return w.y>=Y0 or (V2 and ((w.y>=280 and w.x<=-282) or (w.y>=40 and w.x<=-325)))
if NAME in bpy.data.objects: raise SystemExit('F234 already there')
with bpy.data.libraries.load(MS+'north/montclair_north.blend',link=False) as (s,d): d.objects=['North_terrain_LiDAR_1m']
o=d.objects[0]; o.name=NAME
print('F234 north terrain mods',[(m.type,m.name) for m in o.modifiers],'mats',[m.name if m else None for m in o.data.materials],flush=True)
for m in list(o.modifiers): o.modifiers.remove(m)
me=o.data; me.name=NAME+'_mesh'
bm=bmesh.new(); bm.from_mesh(me); mw=o.matrix_world.copy()
dl=[f for f in bm.faces if not all(outside(mw@v.co) for v in f.verts)]
bmesh.ops.delete(bm,geom=dl,context='FACES')
lone=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lone,context='VERTS')
bm.to_mesh(me); bm.free()
T=bpy.data.collections.get('Terrain'); NT=bpy.data.collections.get('N_terrain') or bpy.data.collections.new('N_terrain')
NM=bpy.data.collections.get('NORTH_MERGE')
if NT.name not in [c.name for c in NM.children]: NM.children.link(NT)
NT.objects.link(o)
ws=[mw@v.co for v in me.vertices]
print('F234 ext verts',len(me.vertices),'faces',len(me.polygons),'x',round(min(v.x for v in ws),1),round(max(v.x for v in ws),1),'y',round(min(v.y for v in ws),1),round(max(v.y for v in ws),1),'z',round(min(v.z for v in ws),1),round(max(v.z for v in ws),1),flush=True)
bvh=BVHTree.FromPolygons([v[:] for v in ws],[p.vertices[:] for p in me.polygons])
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
print('F234 skirt mods',[(m.type,m.name,m.show_render) for m in sk.modifiers],'users',sk.data.users,flush=True)
smw=sk.matrix_world; inv=smw.inverted(); n=0; dz=[]
for v in sk.data.vertices:
    w=smw@v.co
    if w.y<(38 if V2 else Y0-2) or w.x<-460 or w.x>145: continue
    h=bvh.ray_cast(mathutils.Vector((w.x,w.y,400)),mathutils.Vector((0,0,-1)))
    if not h[0]:
        # just outside the extension edge: probe 1.5 m around so the skirt can't stand up along the boundary
        best=None
        for dx,dy in ((1.5,0),(-1.5,0),(0,1.5),(0,-1.5)):
            hh=bvh.ray_cast(mathutils.Vector((w.x+dx,w.y+dy,400)),mathutils.Vector((0,0,-1)))
            if hh[0] and (best is None or hh[0].z<best): best=hh[0].z
        if best is None: continue
        g=best
    else: g=h[0].z
    tgt=g-0.35
    if w.z>tgt:
        dz.append(w.z-tgt); w.z=tgt; v.co=inv@w; n+=1
sk.data.update()
print('F234 skirt verts lowered',n,'max',round(max(dz),2) if dz else 0,'med',round(sorted(dz)[len(dz)//2],2) if dz else 0,flush=True)
